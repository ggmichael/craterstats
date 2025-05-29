#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import craterstats.cli as cli
import craterstats.gm as gm
from pathlib import Path
import glob
import os

def main():
    root = 'https://ggmichael.github.io/craterstats/'
    os.makedirs('gallery', exist_ok=True)
    os.chdir('gallery')

    n = None #[5,6,7,24]
    n=cli.demo(n)

    s=['''
# Gallery

This gallery shows the types of plots produced by Craterstats-III, and the command options used to produce them.
These may be typed on single line following the command `craterstats`, or saved in a file with `.cs` extension
and run with the command `craterstats -i <filename>.cs`.
''']

    for i in n:
        fn = '{:02d}-demo'.format(i)
        cs = gm.read_textfile('demo/'+fn+'.cs')
        im = glob.glob("demo/"+fn+"*.p*")
        im = [Path(p).as_posix() for p in im]
        lnk = ['!['+fn+']('+root+e+')' if gm.filename(e,'e')=='.png' else f'[View the PDF]({e})' for e in im]
        s+=[*lnk,
            f'\nDemo {i}\n',
            "```", *cs[1:], "```\n"]

    gm.write_textfile(r'../docs/gallery.md',s)

if __name__ == '__main__':
    main()

