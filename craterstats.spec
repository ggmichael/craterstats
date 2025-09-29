# -*- mode: python ; coding: utf-8 -*-

import os
import shutil
import platform

a = Analysis(
    ['src/craterstats.py'],
    pathex=[os.path.abspath('src')],
    binaries=[],
    datas = [
        ('src/craterstats/config/*','craterstats/config'),
        ('src/craterstats/sample/*','craterstats/sample'),
        ('src/craterstats/fonts/*','craterstats/fonts'),
        ('scripts/create_desktop_shortcut.bat', '.'),
        ('scripts/add_cs_path.bat', '.'),
        ('LICENSE.txt', '.'),
    ],
    hiddenimports=['craterstats.config',
                   'matplotlib.backends.backend_svg',
                   'matplotlib.backends.backend_pdf',
                   'scipy.special.erf','scipy.special.factorial',
                   ],
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
    name='craterstats',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='craterstats',
)

shutil.move(r'dist/craterstats/_internal/LICENSE.txt', r'dist/craterstats')
if platform.system()=='Windows':
    shutil.move(r'dist/craterstats/_internal/create_desktop_shortcut.bat', r'dist/craterstats')
