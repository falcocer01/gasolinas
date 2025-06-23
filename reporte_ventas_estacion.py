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
        self.cell(0, 10, f"Reporte de Ventas - {self.estacion}", ln=True, align="C")
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

    def set_estacion(self, estacion):
        self.estacion = estacion

def generar_pdf(df, fecha_inicio, fecha_fin, estacion, archivo='reporte_ventas.pdf'):
    pdf = PDF(orientation="L", unit="mm", format="A4")
    pdf.set_fechas(fecha_inicio, fecha_fin)
    pdf.set_estacion(estacion)
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
    print("=== Generador de Reporte PDF de Ventas por Estación y Fechas ===")
    try:
        estacion = input("🏪 Ingrese el nombre de la estación (ej. America Soler): ").strip()
        fecha_inicio = input("📅 Ingrese la fecha de inicio (YYYY-MM-DD): ").strip()
        fecha_fin = input("📅 Ingrese la fecha de fin    (YYYY-MM-DD): ").strip()

        # Validación de fechas
        datetime.strptime(fecha_inicio, "%Y-%m-%d")
        datetime.strptime(fecha_fin, "%Y-%m-%d")

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Validar si existe la estación
        cursor.execute("SELECT DISTINCT estacion FROM vista_ventas_por_producto_estacion_fecha")
        estaciones_disponibles = [row[0] for row in cursor.fetchall()]
        if estacion not in estaciones_disponibles:
            print(f"❌ La estación '{estacion}' no existe en la base de datos.")
            return

        query = f"""
            SELECT estacion, producto, fecha, total_galones, total_ventas
            FROM vista_ventas_por_producto_estacion_fecha
            WHERE estacion = %s AND fecha BETWEEN %s AND %s
            ORDER BY fecha DESC, producto
        """
        df = pd.read_sql(query, conn, params=(estacion, fecha_inicio, fecha_fin))
        conn.close()

        if not df.empty:
            archivo_pdf = f"reporte_ventas_{estacion.replace(' ', '_')}.pdf"
            generar_pdf(df, fecha_inicio, fecha_fin, estacion, archivo=archivo_pdf)

            with open("log_procesos.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} - Reporte PDF generado para {estacion} del {fecha_inicio} al {fecha_fin} - Registros: {len(df)}\n")
        else:
            print("⚠️ No se encontraron datos en ese rango de fechas para esa estación.")
            with open("log_procesos.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} - Reporte sin datos para {estacion} del {fecha_inicio} al {fecha_fin}\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        with open("log_procesos.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - Error generando reporte PDF: {e}\n")

if __name__ == "__main__":
    main()
