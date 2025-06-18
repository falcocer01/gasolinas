import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector
import pandas as pd
from fpdf import FPDF

# --- CONFIGURACIÓN ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Sistemas321',
    'database': 'gasolinas1',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

RUTA_EXCEL = r'C:\Users\fedy\Desktop\gasolinas'  # Cambia esta ruta si es necesario

# --- FUNCIONES DE BASE DE DATOS ---
def conectar():
    return mysql.connector.connect(**DB_CONFIG)

def obtener_estaciones():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM estacion")
    estaciones = cursor.fetchall()
    cursor.close()
    conn.close()
    return estaciones

def obtener_reporte(fecha_ini, fecha_fin):
    conn = conectar()
    cursor = conn.cursor()
    query = """
        SELECT estacion, producto, fecha, total_galones, total_ventas
        FROM vista_ventas_por_producto_estacion_fecha
        WHERE fecha BETWEEN %s AND %s
        ORDER BY fecha DESC
    """
    cursor.execute(query, (fecha_ini, fecha_fin))
    data = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return columnas, data

# --- CLASE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Reporte de Ventas", ln=True, align="C")
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

def generar_pdf(columnas, datos, fecha_ini, fecha_fin, archivo='reporte_ventas.pdf'):
    pdf = PDF(orientation="L", unit="mm", format="A4")
    pdf.set_fechas(fecha_ini, fecha_fin)
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    anchos = [40, 40, 30, 30, 40]
    for i, col in enumerate(columnas):
        pdf.cell(anchos[i], 10, col, border=1, align="C")
    pdf.ln()

    for fila in datos:
        for i, valor in enumerate(fila):
            alineacion = "R" if isinstance(valor, float) else "L"
            pdf.cell(anchos[i], 10, str(valor), border=1, align=alineacion)
        pdf.ln()

    pdf.output(archivo)
    print(f"✅ PDF generado: {archivo}")

# --- INTERFAZ TKINTER ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Gasolinas - Reportes")
        self.geometry("600x300")
        self.config(padx=20, pady=20)

        tk.Label(self, text="Empresa:").grid(row=0, column=0, sticky="w")
        self.empresa = ttk.Entry(self)
        self.empresa.grid(row=0, column=1, sticky="ew", columnspan=2)

        tk.Label(self, text="Estación:").grid(row=1, column=0, sticky="w")
        self.estaciones = obtener_estaciones()
        self.combo_estacion = ttk.Combobox(self, values=[f"{eid} - {nombre}" for eid, nombre in self.estaciones])
        self.combo_estacion.grid(row=1, column=1, sticky="ew", columnspan=2)

        tk.Label(self, text="Fecha inicio (YYYY-MM-DD):").grid(row=2, column=0, sticky="w")
        self.fecha_ini = ttk.Entry(self)
        self.fecha_ini.grid(row=2, column=1)

        tk.Label(self, text="Fecha fin (YYYY-MM-DD):").grid(row=3, column=0, sticky="w")
        self.fecha_fin = ttk.Entry(self)
        self.fecha_fin.grid(row=3, column=1)

        self.boton_reporte = ttk.Button(self, text="Generar Reporte PDF", command=self.generar_reporte)
        self.boton_reporte.grid(row=5, column=0, columnspan=3, pady=15)

    def generar_reporte(self):
        fi = self.fecha_ini.get()
        ff = self.fecha_fin.get()
        try:
            datetime.strptime(fi, "%Y-%m-%d")
            datetime.strptime(ff, "%Y-%m-%d")
            columnas, datos = obtener_reporte(fi, ff)
            if datos:
                generar_pdf(columnas, datos, fi, ff)
                messagebox.showinfo("Éxito", "PDF generado correctamente.")
            else:
                messagebox.showwarning("Sin datos", "No se encontraron ventas en ese rango.")
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {e}")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    app = App()
    app.mainloop()
