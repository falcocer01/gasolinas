import mysql.connector
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Configuración conexión MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Sistemas321',
    'database': 'gasolinas1',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

# Clase PDF personalizada
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Reporte de Ventas por Estación y Producto", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(0, 8, f"Del {self.fecha_inicio} al {self.fecha_fin}", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

    def set_fechas(self, inicio, fin):
        self.fecha_inicio = inicio
        self.fecha_fin = fin

def generar_pdf(df, fecha_inicio, fecha_fin, archivo='reporte_ventas.pdf'):
    pdf = PDF(orientation="L", unit="mm", format="A4")
    pdf.set_fechas(fecha_inicio, fecha_fin)
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    columnas = ["Estación", "Producto", "Fecha", "Galones", "Total S/"]
    anchos = [40, 40, 30, 30, 40]

    for i, col in enumerate(columnas):
        pdf.cell(anchos[i], 10, col, border=1, align="C")
    pdf.ln()

    for _, row in df.iterrows():
        pdf.cell(anchos[0], 10, row["estacion"], border=1)
        pdf.cell(anchos[1], 10, row["producto"], border=1)
        pdf.cell(anchos[2], 10, str(row["fecha"]), border=1)
        pdf.cell(anchos[3], 10, f"{row['total_galones']:.2f}", border=1, align="R")
        pdf.cell(anchos[4], 10, f"{row['total_ventas']:.2f}", border=1, align="R")
        pdf.ln()

    pdf.output(archivo)
    print(f"\n✅ PDF generado exitosamente: {archivo}")

def main():
    print("=== Generador de Reporte PDF de Ventas por Rango de Fechas ===")
    try:
        fecha_inicio = input("📅 Ingrese la fecha de inicio (YYYY-MM-DD): ").strip()
        fecha_fin = input("📅 Ingrese la fecha de fin    (YYYY-MM-DD): ").strip()

        # Validación de fechas
        datetime.strptime(fecha_inicio, "%Y-%m-%d")
        datetime.strptime(fecha_fin, "%Y-%m-%d")

        conn = mysql.connector.connect(**DB_CONFIG)
        query = f"""
            SELECT estacion, producto, fecha, total_galones, total_ventas
            FROM vista_ventas_por_producto_estacion_fecha
            WHERE fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
            ORDER BY fecha DESC, estacion, producto
        """
        df = pd.read_sql(query, conn)
        conn.close()

        if not df.empty:
            generar_pdf(df, fecha_inicio, fecha_fin)
        else:
            print("⚠️ No se encontraron datos en ese rango de fechas.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()