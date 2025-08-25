#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import craterstats.cli as cli
import craterstats.gm as gm
from pathlib import Path
import glob
import os
import re

def main():
    root = 'https://ggmichael.github.io/craterstats/'
    os.makedirs('gallery', exist_ok=True)
    os.chdir('gallery')
    if os.path.isdir('demo'):
        fs = glob.glob("demo/*")
        for f in fs:
            Path(f).unlink()

    n = None #[5,6,7,24,25]
    n=cli.demo(n)


    s=['''---
layout: default
title: Gallery
---
    
# Gallery

This gallery shows the types of plots produced by Craterstats-III, and the command options used to produce them.
These may be typed on single line following the command `craterstats`, or saved in a file with `.cs` extension
and generated with the command `craterstats -i <filename>.cs`. 
''']

    for i in n:
        fn = f'{i:02d}-demo'
        cs = gm.read_textfile('demo/'+fn+'.cs')
        f = glob.glob(f"demo/{fn}*.*")
        pattern = re.compile(r"\.(png|pdf|svg)$", re.IGNORECASE)
        im0 = [e for e in f if pattern.search(e)]
        im1 = [Path(p).as_posix() for p in im0]
        lnks = []
        for im in im1:
            match gm.filename(im,'e'):
                case '.png':
                    lnk = f'![{fn}]({root}{im})'
                case '.pdf':
                    lnk = f'[View the PDF]({root}{im})'
                case '.svg':
                    lnk = f'<img src = "{root}{im}" width = "100%" />'
            lnks += [lnk]

        s+=[*lnks,
            f'\nDemo {i}\n',
            "```", *cs[1:], "```\n"]

    gm.write_textfile(r'gallery.md',s)

if __name__ == '__main__':
    main()
