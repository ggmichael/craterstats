# -*- mode: python ; coding: utf-8 -*-

import glob
import os
import shutil
import platform

def abs_glob(root, extensions):
    return [file for ext in extensions for file in glob.glob(root + f"*.{ext}")]

config_files = abs_glob('src/craterstats/config/', ['txt', 'qml'])
sample_files = abs_glob('src/craterstats/sample/', ['scc', 'diam', 'r', 'stat', 'binned', 'md','txt'])
font_files = abs_glob('src/craterstats/fonts/', ['txt', 'ttf'])

a = Analysis(
    ['src/craterstats.py'],
    pathex=[os.path.abspath('src')],
    binaries=[],
    datas = [
        *[(f, "craterstats/config") for f in config_files],
        *[(f, "craterstats/sample") for f in sample_files],
        *[(f, "craterstats/fonts") for f in font_files],
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
