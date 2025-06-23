import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
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
    return archivo

def obtener_estaciones():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT estacion FROM vista_ventas_por_producto_estacion_fecha")
    estaciones = [row[0] for row in cursor.fetchall()]
    conn.close()
    return estaciones

def generar_reporte():
    estacion = estacion_var.get()
    fecha_inicio = fecha_inicio_entry.get()
    fecha_fin = fecha_fin_entry.get()

    if not estacion:
        messagebox.showerror("Error", "Selecciona una estación.")
        return

    try:
        datetime.strptime(fecha_inicio, "%Y-%m-%d")
        datetime.strptime(fecha_fin, "%Y-%m-%d")

        conn = mysql.connector.connect(**DB_CONFIG)
        query = """
            SELECT estacion, producto, fecha, total_galones, total_ventas
            FROM vista_ventas_por_producto_estacion_fecha
            WHERE estacion = %s AND fecha BETWEEN %s AND %s
            ORDER BY fecha DESC, producto
        """
        df = pd.read_sql(query, conn, params=(estacion, fecha_inicio, fecha_fin))
        conn.close()

        if not df.empty:
            archivo = f"reporte_ventas_{estacion.replace(' ', '_')}.pdf"
            generar_pdf(df, fecha_inicio, fecha_fin, estacion, archivo)
            messagebox.showinfo("Éxito", f"PDF generado: {archivo}")
        else:
            messagebox.showwarning("Sin datos", "No se encontraron datos en ese rango para la estación seleccionada.")
    except Exception as e:
        import traceback
        messagebox.showerror("Error", f"Ocurrió un error al generar el reporte:\n{e}")
        print("❌ Error al generar reporte:")
        traceback.print_exc()

def cargar_estaciones():
    try:
        estaciones = obtener_estaciones()
        if estaciones:
            estaciones_combo['values'] = estaciones
            estaciones_combo.current(0)  # Selecciona la primera por defecto
            print("✅ Estaciones cargadas:", estaciones)
        else:
            messagebox.showwarning("Advertencia", "No hay estaciones disponibles en la base de datos.")
            print("⚠️ No se encontraron estaciones.")
    except Exception as err:
        import traceback
        messagebox.showerror("Error de conexión", f"Ocurrió un error al cargar las estaciones:\n{err}")
        print("❌ Error al cargar estaciones:")
        traceback.print_exc()

# Crear ventana principal
root = tk.Tk()
root.title("Generador de Reporte PDF por Estación")
root.geometry("400x300")
root.resizable(False, False)

# Variables
estacion_var = tk.StringVar()

# Widgets
tk.Label(root, text="Seleccione la estación:", font=("Arial", 10)).pack(pady=5)
estaciones_combo = ttk.Combobox(root, textvariable=estacion_var, state="readonly", width=35)
estaciones_combo.pack()

tk.Label(root, text="Fecha de inicio:", font=("Arial", 10)).pack(pady=5)
fecha_inicio_entry = DateEntry(root, date_pattern="yyyy-mm-dd", width=20)
fecha_inicio_entry.pack()

tk.Label(root, text="Fecha de fin:", font=("Arial", 10)).pack(pady=5)
fecha_fin_entry = DateEntry(root, date_pattern="yyyy-mm-dd", width=20)
fecha_fin_entry.pack()

tk.Button(root, text="Generar PDF", command=generar_reporte, bg="green", fg="white", width=20).pack(pady=20)

# Cargar estaciones al iniciar
cargar_estaciones()

# Ejecutar interfaz
root.mainloop()
    
