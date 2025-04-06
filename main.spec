# -*- mode: python ; coding: utf-8 -*-
import sys
sys.path.append(SPECPATH)

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['object_functions', 'card_functions']
hiddenimports += collect_submodules('object_functions')
hiddenimports += collect_submodules('card_functions')


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=hiddenimports,
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
    a.binaries,
    a.datas,
    [],
    name='nubbysbalatreglin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\ball.ico'],
)
