import pandas as pd
import mysql.connector
import os

# Configuración conexión a BD (base y tablas ya creadas)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Sistemas321',
    'database': 'gasolinas1',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

# Ruta base con archivos Excel
RUTA_BASE_EXCEL = r'C:\Users\fedy\Desktop\gasolinas'

def agregar_estaciones(estaciones):
    """Inserta estaciones si no existen."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        for estacion_id, nombre, direccion, tipo in estaciones:
            cursor.execute("""
                INSERT IGNORE INTO estacion (id, nombre, direccion, tipoestacion)
                VALUES (%s, %s, %s, %s)
            """, (estacion_id, nombre, direccion, tipo))
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Estaciones insertadas (si no existían).")
    except Exception as e:
        print(f"❌ Error insertando estaciones: {e}")

def obtener_estaciones():
    """Obtiene estaciones (id, nombre) de la BD."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM estacion")
        estaciones = cursor.fetchall()
        cursor.close()
        conn.close()
        return estaciones
    except Exception as e:
        print(f"❌ Error obteniendo estaciones: {e}")
        return []

def cargar_inventario_estacion(estacion_id, nombre_estacion):
    archivo_excel = os.path.join(RUTA_BASE_EXCEL, f"{estacion_id}.xlsx")
    if not os.path.exists(archivo_excel):
        print(f"⚠️ Archivo no encontrado para estación '{nombre_estacion}': {archivo_excel}")
        return False
    print(f"📊 Procesando estación: {nombre_estacion} (ID: {estacion_id})")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        xls = pd.ExcelFile(archivo_excel)
        registros_procesados = 0
        for nombre_hoja in xls.sheet_names:
            try:
                # Leer filas y columnas relevantes según tu archivo
                df = pd.read_excel(xls, sheet_name=nombre_hoja, skiprows=6, nrows=4, header=None)
                # Columnas: 0=producto, 12=cantidad galones, 13=precio venta, 14=venta soles
                df = df.iloc[:, [0, 12, 13, 14]]
                df.columns = ['producto', 'cantidad', 'precio_venta', 'venta_soles']
                df['fecha'] = pd.to_datetime(nombre_hoja, dayfirst=True, errors='coerce')
                df = df.dropna(subset=['producto', 'cantidad', 'precio_venta', 'venta_soles', 'fecha'])
                df[['cantidad', 'precio_venta', 'venta_soles']] = df[['cantidad', 'precio_venta', 'venta_soles']].apply(pd.to_numeric, errors='coerce')
                df = df.dropna()
                for _, fila in df.iterrows():
                    producto = str(fila['producto']).strip()
                    cantidad = float(fila['cantidad'])
                    precio_venta = float(fila['precio_venta'])
                    venta_soles = float(fila['venta_soles'])
                    fecha = fila['fecha'].date()
                    # Verificar o insertar producto
                    cursor.execute("SELECT id FROM productos WHERE nombre=%s", (producto,))
                    res = cursor.fetchone()
                    if res:
                        producto_id = res[0]
                    else:
                        cursor.execute("INSERT INTO productos (nombre, descripcion) VALUES (%s, '')", (producto,))
                        producto_id = cursor.lastrowid
                        print(f"    ➕ Nuevo producto insertado: {producto}")
                    # Insertar inventario con precio_venta y venta_soles (agrega esas columnas en inventario si no están)
                    cursor.execute("""
                        INSERT INTO inventario (productoid, estacionid, fecha, cantidad, precio_venta, venta_soles)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (producto_id, estacion_id, fecha, cantidad, precio_venta, venta_soles))
                    registros_procesados += 1
            except Exception as e:
                print(f"    ❌ Error procesando hoja '{nombre_hoja}': {e}")
                continue
        conn.commit()
        cursor.close()
        conn.close()
        print(f"  ✅ Estación procesada. Registros cargados: {registros_procesados}")
        return True
    except Exception as e:
        print(f"❌ Error procesando estación '{nombre_estacion}': {e}")
        return False

def procesar_todas_las_estaciones():
    estaciones = obtener_estaciones()
    if not estaciones:
        print("❌ No hay estaciones para procesar.")
        return
    print(f"📋 Se procesarán {len(estaciones)} estaciones...")
    exitosas = 0
    fallidas = 0
    for estacion_id, nombre_estacion in estaciones:
        print("\n"+"="*40)
        if cargar_inventario_estacion(estacion_id, nombre_estacion):
            exitosas += 1
        else:
            fallidas += 1
    print("\n"+"="*40)
    print(f"✅ Procesadas con éxito: {exitosas}")
    print(f"❌ Fallidas: {fallidas}")

if __name__ == "__main__":
    # Si quieres agregar estaciones nuevas, ponlas aquí:
    estaciones_ejemplo = [
        (1, 'La Rinconada', 'Av. Principal s/n', 'lima'),
        (2, 'America Soler', 'Av. Bolognesi s/n', 'trujillo'),
        (3, 'El Porvenir', 'Av. Porvenir s/n', 'trujillo')
       
    ]
    agregar_estaciones(estaciones_ejemplo)
    procesar_todas_las_estaciones()
