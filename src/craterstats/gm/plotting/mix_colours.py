#  Copyright (c) 2024, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import matplotlib.colors as mc

def mix_colours(c1, c2, amount=0.5):
    '''
    matplotlib: mix two colours to proportion (sometimes preferable to alpha over background)

    :param c1: first colour
    :param c2: second colour
    :param amount: fraction of first
    :return: name of first available
    '''
    c = tuple(map(lambda x, y: y * (1. - amount) + x * amount, mc.to_rgb(c1), mc.to_rgb(c2)))
    return c