# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['reporte1_ventas_tkinter_por_estacion.py'],
    pathex=['C:\\Users\\fedy\\Desktop\\gasolinas'],
    binaries=[],
    datas=[],
    hiddenimports=['tkcalendar'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ReporteVentasEstacion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # ventana sin consola
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ReporteVentasEstacion',
)
