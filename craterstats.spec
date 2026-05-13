#  Copyright (c) 2026, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import os
import shutil

datas = [
    ('src/craterstats/config/*', 'craterstats/config'),
    ('src/craterstats/sample/*', 'craterstats/sample'),
    ('src/craterstats/fonts/*', 'craterstats/fonts'),
    ('src/craterstats/scripts/*', 'craterstats/scripts'), # available for gui installer
]

datas += [('LICENSE.txt', '.')]
if os.name == 'nt':
    datas += [
        ('src/craterstats/scripts/create_desktop_shortcut.bat', '.'),
        ('src/craterstats/scripts/add_cs_path.bat', '.'),
        ]

a = Analysis(
    ['src/craterstatsCLI.py'],
    pathex=[os.path.abspath('src')],
    binaries=[],
    datas=datas,
    hiddenimports=[
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
    exclude_binaries=True,
    name='craterstats',
    console=True,
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

exedir = r'dist/craterstats/'
shutil.move(exedir + r'_internal/LICENSE.txt', exedir)
if os.name == 'nt':
    shutil.move(exedir + r'_internal/create_desktop_shortcut.bat', exedir)
