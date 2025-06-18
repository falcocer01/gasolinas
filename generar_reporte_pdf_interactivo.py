import mysql.connector
import pandas as pd
from fpdf import FPDF

# CONFIGURA TU CONEXIÓN
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         # 👈 CAMBIA ESTO
    'password': 'Sistemas321',  # 👈 CAMBIA ESTO
    'database': 'gasolinas1',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

# MAPEOS
ESTACIONES = {
    1: 'La Rinconada',
    3: 'America Soler',
    4: 'El Porvenir'
}

PRODUCTOS = {
    1: 'GLP',
    2: 'PREMIUM',
    3: 'REGULAR',
    4: 'DB5'
}

# ELEGIR OPCIONES
def seleccionar_opcion(mapa, texto):
    print(f"\nSeleccione {texto}:")
    for key, val in mapa.items():
        print(f"{key} - {val}")
    while True:
        try:
            opcion = int(input(f"Ingrese el número de {texto}: "))
            if opcion in mapa:
                return opcion
        except ValueError:
            pass
        print("❌ Opción inválida. Intente de nuevo.")

# CONSULTA A LA BD
def obtener_datos(estacion_id, producto_id, anio, mes):
    conn = mysql.connector.connect(**DB_CONFIG)
    query = """
    SELECT
        d.fecha,
        e.nombre AS estacion,
        p.nombre AS producto,
        d.compra_planta,
        d.prueba_surtidor,
        d.total_ventas,
        d.invent_final,
        d.varillaje_inicial,
        d.varillaje_final,
        d.dif
    FROM detalle_dia d
    JOIN estacion e ON d.estacionid = e.id
    JOIN productos p ON d.productoid = p.id
    WHERE d.estacionid = %s AND d.productoid = %s
      AND YEAR(d.fecha) = %s AND MONTH(d.fecha) = %s
    ORDER BY d.fecha
    """
    df = pd.read_sql(query, conn, params=(estacion_id, producto_id, anio, mes))
    conn.close()
    return df

# CLASE PDF
class PDF(FPDF):
    def __init__(self, estacion, producto):
        super().__init__()
        self.estacion = estacion
        self.producto = producto

    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Reporte Mensual por Producto", ln=True, align="C")
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Estación: {self.estacion}  |  Producto: {self.producto}", ln=True, align="C")
        self.ln(5)

    def table_header(self):
        self.set_font("Arial", "B", 9)
        for col in ["Fecha", "Compra", "Surtidor", "Ventas", "Invent. Fin", "Var. Ini", "Var. Fin", "Dif"]:
            self.cell(25, 6, col, border=1, align='C')
        self.ln()

    def table_row(self, row):
        self.set_font("Arial", "", 8)
        self.cell(25, 6, str(row['fecha']), border=1)
        self.cell(25, 6, f"{row['compra_planta']:.2f}" if pd.notna(row['compra_planta']) else "", border=1)
        self.cell(25, 6, f"{row['prueba_surtidor']:.2f}" if pd.notna(row['prueba_surtidor']) else "", border=1)
        self.cell(25, 6, f"{row['total_ventas']:.3f}" if pd.notna(row['total_ventas']) else "", border=1)
        self.cell(25, 6, f"{row['invent_final']:.2f}" if pd.notna(row['invent_final']) else "", border=1)
        self.cell(25, 6, f"{row['varillaje_inicial']:.2f}" if pd.notna(row['varillaje_inicial']) else "", border=1)
        self.cell(25, 6, f"{row['varillaje_final']:.2f}" if pd.notna(row['varillaje_final']) else "", border=1)
        self.cell(25, 6, f"{row['dif']:.2f}" if pd.notna(row['dif']) else "", border=1)
        self.ln()

# FLUJO PRINCIPAL
def main():
    print("📄 Generador de Reportes PDF")

    estacion_id = seleccionar_opcion(ESTACIONES, "la estación")
    producto_id = seleccionar_opcion(PRODUCTOS, "el producto")
    
    while True:
        try:
            anio = int(input("Ingrese el año (ej. 2025): "))
            mes = int(input("Ingrese el mes (1-12): "))
            if 1 <= mes <= 12:
                break
        except ValueError:
            pass
        print("❌ Año o mes inválido.")

    df = obtener_datos(estacion_id, producto_id, anio, mes)

    if df.empty:
        print("⚠️ No se encontraron datos para los filtros seleccionados.")
        return

    pdf = PDF(estacion=ESTACIONES[estacion_id], producto=PRODUCTOS[producto_id])
    pdf.add_page()
    pdf.table_header()

    for _, row in df.iterrows():
        pdf.table_row(row)

    filename = f"reporte_{ESTACIONES[estacion_id].replace(' ', '_')}_{PRODUCTOS[producto_id]}_{anio}_{mes:02}.pdf"
    pdf.output(filename)
    print(f"✅ PDF generado: {filename}")

if __name__ == "__main__":
    main()
