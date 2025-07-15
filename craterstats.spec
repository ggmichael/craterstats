# -*- mode: python ; coding: utf-8 -*-

import glob
import os
import shutil
import platform

def abs_glob(patterns):
    return [file for pattern in patterns for file in glob.glob(pattern)]

config_files = abs_glob(['src/craterstats/config/*.txt'])
sample_files = abs_glob([f'src/craterstats/sample/*.{ext}' for ext in ['scc', 'diam', 'r', 'stat', 'binned', 'md']])
font_files = abs_glob([f'src/craterstats/fonts/*.{ext}' for ext in ['txt', 'ttf']])

a = Analysis(
    ['src/craterstats/cli.py'],
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
    #contents_directory='.'
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
