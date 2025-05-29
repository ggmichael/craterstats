#!/usr/bin/env python

import craterstats.cli as cli
import craterstats.gm as gm
import os
import glob

pngs = glob.glob("demo_*.png")


def main():
    d = r'D:\mydocs\code\pycharm\craterstats\docs'
    os.chdir(d)
    n = range(0,26) #None #[5,6,7,24]
    # n=cli.demo(n)

    s=['','# Gallery','']

    for i in n:
        fn = '{:02d}-demo'.format(i)
        cs = gm.read_textfile('demo/'+fn+'.cs')
        im = glob.glob("demo/"+fn+"*.p*")
        lnk = ['!['+fn+']('+e+')' if gm.filename(e,'e')=='.png' else f'[View the PDF]({e})' for e in im]
        s+=[*lnk,
            f'\nDemo {i}\n',
            "```", *cs[1:], "```\n"]

    gm.write_textfile(d+r'\gallery.md',s)


if __name__ == '__main__':
    main()



