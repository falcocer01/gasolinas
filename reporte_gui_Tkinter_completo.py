import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import mysql.connector
from fpdf import FPDF
from datetime import datetime

# Estaciones y productos
ESTACIONES = {1: "La Rinconada", 3: "America Soler", 4: "El Porvenir"}
PRODUCTOS = {1: "GLP", 2: "PREMIUM", 3: "REGULAR", 4: "DB5"}

def obtener_datos(estacion_id, producto_id, fecha_ini, fecha_fin):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',         # 👈 CAMBIA ESTO
        password='Sistemas321',  # 👈 CAMBIA ESTO
        database='gasolinas1',
      
    )
    query = """
    SELECT d.fecha, e.nombre AS estacion, p.nombre AS producto,
           d.compra_planta, d.prueba_surtidor, d.total_ventas,
           d.invent_final, d.varillaje_inicial, d.varillaje_final, d.dif
    FROM detalle_dia d
    JOIN estacion e ON d.estacionid = e.id
    JOIN productos p ON d.productoid = p.id
    WHERE d.estacionid = %s AND d.productoid = %s
      AND d.fecha BETWEEN %s AND %s
    ORDER BY d.fecha
    """
    df = pd.read_sql(query, conn, params=(estacion_id, producto_id, fecha_ini, fecha_fin))
    conn.close()
    return df

def generar_pdf(df, estacion, producto, fecha_ini, fecha_fin):
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Reporte por Producto", ln=True, align="C")
            self.set_font("Arial", "", 12)
            self.cell(0, 10, f"Estación: {estacion} | Producto: {producto}", ln=True, align="C")
            self.cell(0, 10, f"Periodo: {fecha_ini} a {fecha_fin}", ln=True, align="C")
            self.ln(5)

        def table_header(self):
            self.set_font("Arial", "B", 8)
            headers = ["Fecha", "Compra", "Surtidor", "Ventas", "Invent. Fin", "Var. Ini", "Var. Fin", "Dif"]
            for col in headers:
                self.cell(25, 6, col, border=1, align='C')
            self.ln()

        def table_row(self, row):
            self.set_font("Arial", "", 8)
            self.cell(25, 6, str(row['fecha']), border=1)
            self.cell(25, 6, f"{row['compra_planta']:.3f}" if pd.notna(row['compra_planta']) else "", border=1)
            self.cell(25, 6, f"{row['prueba_surtidor']:.3f}" if pd.notna(row['prueba_surtidor']) else "", border=1)
            self.cell(25, 6, f"{row['total_ventas']:.3f}" if pd.notna(row['total_ventas']) else "", border=1)
            self.cell(25, 6, f"{row['invent_final']:.3f}" if pd.notna(row['invent_final']) else "", border=1)
            self.cell(25, 6, f"{row['varillaje_inicial']:.3f}" if pd.notna(row['varillaje_inicial']) else "", border=1)
            self.cell(25, 6, f"{row['varillaje_final']:.3f}" if pd.notna(row['varillaje_final']) else "", border=1)
            self.cell(25, 6, f"{row['dif']:.3f}" if pd.notna(row['dif']) else "", border=1)
            self.ln()

    pdf = PDF()
    pdf.add_page()
    pdf.table_header()
    for _, row in df.iterrows():
        pdf.table_row(row)

    nombre = f"reporte_{estacion.replace(' ', '_')}_{producto}_{fecha_ini}_a_{fecha_fin}.pdf"
    pdf.output(nombre)
    return nombre

def generar_excel(df, estacion, producto, fecha_ini, fecha_fin):
    nombre = f"reporte_{estacion.replace(' ', '_')}_{producto}_{fecha_ini}_a_{fecha_fin}.xlsx"
    df.to_excel(nombre, index=False)
    return nombre

def generar_archivo(tipo):
    estacion_id = int(estacion_cb.get().split(" - ")[0])
    producto_id = int(producto_cb.get().split(" - ")[0])
    fecha_ini = fecha_ini_entry.get()
    fecha_fin = fecha_fin_entry.get()

    try:
        datetime.strptime(fecha_ini, '%Y-%m-%d')
        datetime.strptime(fecha_fin, '%Y-%m-%d')
    except ValueError:
        messagebox.showerror("Error", "Fechas inválidas. Use formato YYYY-MM-DD.")
        return

    df = obtener_datos(estacion_id, producto_id, fecha_ini, fecha_fin)
    if df.empty:
        messagebox.showinfo("Sin datos", "No se encontraron registros.")
        return

    estacion = ESTACIONES[estacion_id]
    producto = PRODUCTOS[producto_id]

    if tipo == "pdf":
        archivo = generar_pdf(df, estacion, producto, fecha_ini, fecha_fin)
    else:
        archivo = generar_excel(df, estacion, producto, fecha_ini, fecha_fin)

    messagebox.showinfo("Reporte generado", f"Archivo creado:\n{archivo}")

# Interfaz gráfica
root = tk.Tk()
root.title("Reporte de Ventas por Producto")

tk.Label(root, text="Estación:").grid(row=0, column=0, sticky="e")
estacion_cb = ttk.Combobox(root, values=[f"{k} - {v}" for k, v in ESTACIONES.items()])
estacion_cb.grid(row=0, column=1)
estacion_cb.current(0)

tk.Label(root, text="Producto:").grid(row=1, column=0, sticky="e")
producto_cb = ttk.Combobox(root, values=[f"{k} - {v}" for k, v in PRODUCTOS.items()])
producto_cb.grid(row=1, column=1)
producto_cb.current(0)

tk.Label(root, text="Fecha inicio (YYYY-MM-DD):").grid(row=2, column=0, sticky="e")
fecha_ini_entry = tk.Entry(root)
fecha_ini_entry.grid(row=2, column=1)

tk.Label(root, text="Fecha fin (YYYY-MM-DD):").grid(row=3, column=0, sticky="e")
fecha_fin_entry = tk.Entry(root)
fecha_fin_entry.grid(row=3, column=1)

frame_botones = tk.Frame(root)
frame_botones.grid(row=4, column=0, columnspan=2, pady=10)

tk.Button(frame_botones, text="Generar PDF", command=lambda: generar_archivo("pdf")).grid(row=0, column=0, padx=10)
tk.Button(frame_botones, text="Exportar Excel", command=lambda: generar_archivo("excel")).grid(row=0, column=1, padx=10)

root.mainloop()
