import mysql.connector
import pandas as pd
from fpdf import FPDF

# CONFIGURACIÓN DE CONEXIÓN A MYSQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         # 👈 CAMBIA ESTO
    'password': 'Sistemas321',  # 👈 CAMBIA ESTO
    'database': 'gasolinas1',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

# FILTROS DEL REPORTE
estacion_id = 3       # America Soler
producto_id = 2       # GLP
anio = 2025
mes = 3

# CONEXIÓN Y CONSULTA
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

# CLASE PDF PERSONALIZADA
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Reporte Mensual por Producto", ln=True, align="C")
        self.set_font("Arial", "", 12)
        estacion = df['estacion'].iloc[0] if not df.empty else "N/A"
        producto = df['producto'].iloc[0] if not df.empty else "N/A"
        self.cell(0, 10, f"Estación: {estacion}  |  Producto: {producto}", ln=True, align="C")
        self.ln(5)

    def table_header(self):
        self.set_font("Arial", "B", 9)
        cols = ["Fecha", "Compra", "Surtidor", "Ventas", "Invent. Fin", "Var. Ini", "Var. Fin", "Dif"]
        for col in cols:
            self.cell(25, 6, col, border=1, align='C')
        self.ln()

    def table_row(self, row):
        self.set_font("Arial", "", 8)
        self.cell(25, 6, str(row['fecha']), border=1)
        self.cell(25, 6, f"{row['compra_planta']:.2f}" if pd.notna(row['compra_planta']) else "", border=1)
        self.cell(25, 6, f"{row['prueba_surtidor']:.2f}" if pd.notna(row['prueba_surtidor']) else "", border=1)
        self.cell(25, 6, f"{row['total_ventas']:.2f}" if pd.notna(row['total_ventas']) else "", border=1)
        self.cell(25, 6, f"{row['invent_final']:.2f}" if pd.notna(row['invent_final']) else "", border=1)
        self.cell(25, 6, f"{row['varillaje_inicial']:.2f}" if pd.notna(row['varillaje_inicial']) else "", border=1)
        self.cell(25, 6, f"{row['varillaje_final']:.2f}" if pd.notna(row['varillaje_final']) else "", border=1)
        self.cell(25, 6, f"{row['dif']:.2f}" if pd.notna(row['dif']) else "", border=1)
        self.ln()

# GENERAR PDF
pdf = PDF()
pdf.add_page()
pdf.table_header()

for _, row in df.iterrows():
    pdf.table_row(row)

pdf.output("reporte_producto_estacion.pdf")
print("✅ PDF generado: reporte_producto_estacion.pdf")


