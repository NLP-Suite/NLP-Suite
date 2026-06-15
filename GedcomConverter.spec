# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the standalone GEDCOM to CSV Converter."""

a = Analysis(
    ['src/gedcom_to_csv.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pandas', 'numpy', 'openpyxl'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'sklearn', 'stanza', 'spacy',
              'nltk', 'gensim', 'transformers', 'torch', 'tensorflow',
              'plotly', 'seaborn', 'folium', 'geopandas', 'PIL'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GedcomConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GedcomConverter',
)
