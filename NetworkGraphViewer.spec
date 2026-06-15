# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the standalone Network Graph Viewer."""

a = Analysis(
    ['src/network_graph_app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pandas', 'numpy'],
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
    name='NetworkGraphViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # windowed app, no console
    icon=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NetworkGraphViewer',
)
