# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['爱丽丝QQ聊天AI.py'],
    pathex=[],
    binaries=[],
    datas=[('A:/Anaconda3/envs/Arisu/Lib/site-packages/comtypes', 'comtypes'), ('A:/Anaconda3/envs/Arisu/Lib/site-packages/uiautomation/bin', 'uiautomation/bin')],
    hiddenimports=['comtypes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='爱丽丝QQ聊天AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon=['resources\\Logo\\256.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='爱丽丝QQ聊天AI',
)
