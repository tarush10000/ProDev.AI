# ui.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ui.py', 'code_generation.py', 'demohistory.py', 'documentation2.py', 'store.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('images/*', 'images'),
        ('embeddings_cache/*', 'embeddings_cache'),
        ('documentations/*', 'documentations')
    ],
    hiddenimports=['scipy._lib.array_api_compat.numpy.fft', 'scipy.special._ufuncs_cxx', 'scify', 'scipy.special._special_ufuncs'],
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
    name='ProDev.AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want a console window, False for a windowed app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ProDev.AI',
)
