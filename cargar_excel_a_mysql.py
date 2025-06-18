import pandas as pd
import os
import hashlib
import mysql.connector
from openpyxl import load_workbook
from datetime import datetime

# CONFIGURACIÓN
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Sistemas321',
    'database': 'gasolinas1',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

# MAPA DE PRODUCTOS
PRODUCTOS = {
    'GLP': 1,
    'PREMIUM': 2,
    'REGULAR': 3,
    'DB5': 4
}

ESTACIONES = {
    'america': {'id': 3, 'nombre': 'America Soler'},
    'rinconada': {'id': 1, 'nombre': 'La Rinconada'},
    'porvenir': {'id': 4, 'nombre': 'El Porvenir'}
}

COLUMNAS_OBJETIVO = {
    'A': 'comb',
    'C': 'compra_planta',
    'D': 'prueba_surtidor',
    'G': 'total_ventas',
    'K': 'invent_final',
    'L': 'varillaje_inicial',
    'M': 'varillaje_final',
    'Q': 'dif'
}

def obtener_hash_archivo(nombre_archivo):
    with open(nombre_archivo, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def archivo_ya_procesado(cursor, nombre_archivo, hash_archivo):
    query = "SELECT COUNT(*) FROM archivos_procesados WHERE nombre_archivo = %s AND hash = %s"
    cursor.execute(query, (nombre_archivo, hash_archivo))
    return cursor.fetchone()[0] > 0

def registrar_archivo(cursor, nombre_archivo, hash_archivo):
    query = "INSERT INTO archivos_procesados (nombre_archivo, hash, fecha_procesado) VALUES (%s, %s, %s)"
    cursor.execute(query, (nombre_archivo, hash_archivo, datetime.now()))

def procesar_excel(nombre_archivo):
    base = os.path.basename(nombre_archivo).lower()
    prefijo = base.split('_')[0]

    if prefijo not in ESTACIONES:
        print(f"Estación desconocida en el archivo: {nombre_archivo}")
        return

    estacion_id = ESTACIONES[prefijo]['id']
    print(f"Procesando archivo para estación ID {estacion_id}: {ESTACIONES[prefijo]['nombre']}")

    hash_archivo = obtener_hash_archivo(nombre_archivo)
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    if archivo_ya_procesado(cursor, base, hash_archivo):
        print(f"⚠️ El archivo '{base}' ya fue procesado. Se omite.")
        conn.close()
        return

    xls = pd.ExcelFile(nombre_archivo)
    for hoja in xls.sheet_names:
        try:
            fecha = pd.to_datetime(hoja, dayfirst=True, errors='coerce')
            if pd.isna(fecha):
                print(f"⚠️ Hoja ignorada: {hoja} no representa una fecha válida.")
                continue

            df = pd.read_excel(xls, sheet_name=hoja, header=None, usecols='A,C,D,G,K,L,M,Q', skiprows=6, nrows=4)
            df.columns = COLUMNAS_OBJETIVO.values()

            for _, fila in df.iterrows():
                producto_nombre = str(fila['comb']).strip().upper()
                if producto_nombre not in PRODUCTOS:
                    print(f"Producto desconocido: {producto_nombre}")
                    continue

                productoid = PRODUCTOS[producto_nombre]
                cantidad = fila['total_ventas']

                if pd.isna(cantidad):
                    print(f"Cantidad vacía para {producto_nombre} el {hoja}")
                    continue

                query = """
                    INSERT INTO ventas (productoid, estacionid, dia_venta, cantidad)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (productoid, estacion_id, fecha.date(), cantidad))
                print(f"✅ Insertado: {producto_nombre} | {cantidad} gal. | {fecha.date()}")

        except Exception as e:
            print(f"Error procesando hoja '{hoja}': {e}")

    registrar_archivo(cursor, base, hash_archivo)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Archivo completado y registrado.")

# USO
if __name__ == "__main__":
    archivo = "AMERICA_MARZO_2025.xlsx"  # Reemplaza con la ruta correcta
    procesar_excel(archivo)
