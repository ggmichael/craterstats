#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import colorama

def bright(txt):
    '''
    Wrap string with control codes to cause bright display on console
    '''

    if "init" not in bright.__dict__:
        colorama.init()
        bright.init = True
    return colorama.Style.BRIGHT+txt+colorama.Style.RESET_ALL

if __name__ == '__main__':
    print(bright("bright") + " normal")
    print(bright.init)
    print(bright("bright") + " normal")