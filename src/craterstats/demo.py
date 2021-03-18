#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import os
import gm

import cli


def demo(d=None,src='config/demo_commands.txt'):
    cmd= gm.read_textfile(src, ignore_blank=True, ignore_hash=True)
    out='demo/'
    os.makedirs(out,exist_ok=True)
    f = '-o '+out+'{:02d}-demo '

    if d is None:
        d=range(0,len(cmd))

    for i in d:
        c=cmd[i]
        print(f'\nDemo {i}\npython craterstats.py '+c)
        a= cli.parse_args((f.format(i) + c).split())
        cli.main(a)

    print('\n\nDemo output written to: '+out)

if __name__ == '__main__':
    indices=None
    #indices = [0]
    demo(indices)



