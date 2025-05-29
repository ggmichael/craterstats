#!/usr/bin/env python

import craterstats.cli as cli
import craterstats.gm as gm
from pathlib import Path
import glob


def main():
    n = None #[5,6,7,24] range(0,26) #
    n=cli.demo(n)

    s=['','# Gallery','']

    for i in n:
        fn = '{:02d}-demo'.format(i)
        cs = gm.read_textfile('demo/'+fn+'.cs')
        im = glob.glob("demo/"+fn+"*.p*")
        im = [Path(p).as_posix() for p in im]
        lnk = ['!['+fn+']('+e+')' if gm.filename(e,'e')=='.png' else f'[View the PDF]({e})' for e in im]
        s+=[*lnk,
            f'\nDemo {i}\n',
            "```", *cs[1:], "```\n"]

    gm.write_textfile(r'docs/gallery.md',s)


if __name__ == '__main__':
    main()



