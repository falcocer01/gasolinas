# Proyecto: Automatización de Carga y Reportes para Estaciones de Servicio (Gasolineras)

Este proyecto tiene como objetivo centralizar y automatizar el proceso de carga de archivos Excel provenientes de diferentes estaciones de servicio, almacenarlos en una base de datos MySQL y generar reportes administrativos y regulatorios en PDF y Excel.

---

## Contenido del proyecto

### 1. Backup de la Base de Datos

- `gasolina1_18-06-2025.sql`: Backup completo de la base de datos `gasolinas1` que contiene las siguientes tablas:
  - `estacion`
  - `productos`
  - `ventas`
  - `detalle_dia`
  - `archivos_procesados`

### 2. Scripts Python

#### a. `cargar_excel_a_mysql.py`
Script que carga un archivo Excel mensual (una hoja por día) a la base de datos. Inserta datos en las tablas `ventas` y `detalle_dia` y evita duplicados mediante `archivos_procesados`.

#### b. `procesar_varios_excel.py`
Versión extendida del anterior que procesa automáticamente todos los archivos `.xlsx` del directorio para distintas estaciones.

#### c. `generar_reporte_osinergmi_pdf.py`
Genera un reporte mensual detallado de un producto para una estación específica en formato PDF.

#### d. `generar_reporte_pdf_interactivo.py`
Script de consola que permite al usuario elegir:
- Estación
- Producto
- Mes y Año
Y genera el reporte en PDF.

#### e. `reporte_gui_Tkinter_completo.py`
Interfaz gráfica con Tkinter que permite seleccionar filtros (estación, producto, rango de fechas) y generar:
- Reporte en PDF
- Reporte en Excel

#### f. `reporte_pdf_rango_de_fechas_interactivo.py`
(Script auxiliar usado en pruebas): Versión por consola que permite generar un reporte PDF por rango de fechas ingresado manualmente.

---

## Archivos de Entrada (Ejemplos)

- `AMERICA_MARZO_2025.xlsx`
- `RINCONADA_MARZO_2025.xlsx`
- `PORVENIR_MARZO_2025.xlsx`

Cada archivo representa un mes completo de ventas por estación, con una hoja por día. Las filas 7 a 10 contienen datos para los productos:
- GLP
- PREMIUM
- REGULAR
- DB5

Columnas clave importadas:
- A: `comb` (producto)
- C: `compra_planta`
- D: `prueba_surtidor`
- G: `total_ventas`
- K: `invent_final`
- L: `varillaje_inicial`
- M: `varillaje_final`
- Q: `dif`

---

## Reportes Generados

### Ejemplos:
- `reporte_America_Soler_GLP_2025_03.pdf`
- `reporte_La_Rinconada_PREMIUM_2025-03-01_a_2025-03-31.xlsx`

Todos los reportes incluyen:
- Cabecera con estación, producto y rango de fechas.
- Tabla con los campos cargados desde el Excel.
- Valores numéricos con tres decimales.

---

## Recursos visuales

- `relaciones_bd.png`: Diagrama relacional de la base de datos `gasolinas1`.
- `america_soler.jpg`, `rinconada.jpg`, `porvenir.jpg`: Imagen de cada estación para uso en documentación o interfaz.

---

## Requisitos del entorno

- Python >= 3.9
- MySQL Server o XAMPP
- Librerías Python:
  - `pandas`
  - `mysql-connector-python`
  - `fpdf`
  - `tkinter` (incluida en instalaciones oficiales de Python)

Instalación de librerías:
```bash
pip install pandas mysql-connector-python fpdf
```

---

## Objetivo del proyecto

Este sistema fue diseñado para ayudar a operadores de estaciones de servicio a:
- Controlar y almacenar mensualmente los datos de ventas.
- Detectar diferencias de inventario.
- Presentar reportes confiables a entes reguladores como OSINERGMIN.
- Optimizar el proceso de consolidación de datos multiestación.

---

## Créditos y contacto

Desarrollado por: [FREDY APOLINARIO ALCOCER / equipo]  
Fecha: Junio 2025  
Contacto: [fredyapolinario78@hotmail.com]
