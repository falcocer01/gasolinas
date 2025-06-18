import pandas as pd
import os
import hashlib
import mysql.connector
from datetime import datetime
from glob import glob

# CONFIGURACIÓN DE BASE DE DATOS
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         # 👈 Cambia esto
    'password': 'Sistemas321',  # 👈 Cambia esto
    'database': 'gasolinas1',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

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

def crear_tabla_detalle(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_dia (
            id INT AUTO_INCREMENT PRIMARY KEY,
            estacionid INT NOT NULL,
            productoid INT NOT NULL,
            fecha DATE NOT NULL,
            compra_planta DECIMAL(10,2),
            prueba_surtidor DECIMAL(10,2),
            total_ventas DECIMAL(10,2),
            invent_final DECIMAL(10,2),
            varillaje_inicial DECIMAL(10,2),
            varillaje_final DECIMAL(10,2),
            dif DECIMAL(10,2),
            FOREIGN KEY (estacionid) REFERENCES estacion(id),
            FOREIGN KEY (productoid) REFERENCES productos(id)
        )
    """)

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

def procesar_excel(nombre_archivo, cursor):
    base = os.path.basename(nombre_archivo).lower()
    prefijo = base.split('_')[0]

    if prefijo not in ESTACIONES:
        print(f"⚠️ Archivo omitido, estación desconocida: {nombre_archivo}")
        return

    estacion_id = ESTACIONES[prefijo]['id']
    print(f"\n📄 Procesando archivo: {base} → estación {ESTACIONES[prefijo]['nombre']} (ID {estacion_id})")

    hash_archivo = obtener_hash_archivo(nombre_archivo)

    if archivo_ya_procesado(cursor, base, hash_archivo):
        print(f"⚠️ El archivo '{base}' ya fue procesado. Se omite.")
        return

    xls = pd.ExcelFile(nombre_archivo)
    for hoja in xls.sheet_names:
        try:
            fecha = pd.to_datetime(hoja, dayfirst=True, errors='coerce')
            if pd.isna(fecha):
                print(f"⏩ Hoja ignorada: '{hoja}' no representa una fecha válida.")
                continue

            df = pd.read_excel(xls, sheet_name=hoja, header=None, usecols='A,C,D,G,K,L,M,Q', skiprows=6, nrows=4)
            df.columns = COLUMNAS_OBJETIVO.values()

            for _, fila in df.iterrows():
                producto_nombre = str(fila['comb']).strip().upper()
                if producto_nombre not in PRODUCTOS:
                    print(f"⛔ Producto desconocido: '{producto_nombre}'")
                    continue

                productoid = PRODUCTOS[producto_nombre]
                cantidad = fila['total_ventas']
                if pd.isna(cantidad):
                    continue

                # Insertar en ventas
                cursor.execute("""
                    INSERT INTO ventas (productoid, estacionid, dia_venta, cantidad)
                    VALUES (%s, %s, %s, %s)
                """, (productoid, estacion_id, fecha.date(), cantidad))

                # Insertar en detalle_dia
                valores = [
                    estacion_id, productoid, fecha.date(),
                    fila['compra_planta'], fila['prueba_surtidor'], fila['total_ventas'],
                    fila['invent_final'], fila['varillaje_inicial'], fila['varillaje_final'], fila['dif']
                ]
                valores = [None if pd.isna(v) else v for v in valores]

                cursor.execute("""
                    INSERT INTO detalle_dia (
                        estacionid, productoid, fecha,
                        compra_planta, prueba_surtidor, total_ventas,
                        invent_final, varillaje_inicial, varillaje_final, dif
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, valores)

                print(f"✅ {fecha.date()} | {producto_nombre}: {cantidad} galones")

        except Exception as e:
            print(f"❌ Error en hoja '{hoja}': {e}")

    registrar_archivo(cursor, base, hash_archivo)
    print("📝 Archivo registrado como procesado.")

def main():
    archivos = glob("*.xlsx")
    if not archivos:
        print("⚠️ No hay archivos .xlsx en la carpeta.")
        return

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    crear_tabla_detalle(cursor)

    for archivo in archivos:
        procesar_excel(archivo, cursor)

    conn.commit()
    cursor.close()
    conn.close()
    print("\n✅ Todos los archivos fueron procesados.")

if __name__ == "__main__":
    main()
