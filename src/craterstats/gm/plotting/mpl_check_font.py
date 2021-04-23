#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import matplotlib as mpl

def mpl_check_font(fontnamelist):
    '''
    matplotlib: return first available font from ordered preference list

    :param fontnamelist: e.g. ['Myriad Pro','Verdana','DejaVu Sans','Tahoma']
    :return: name of first available
    '''
    prop = mpl.font_manager.FontProperties(family=fontnamelist)
    fontfile= mpl.font_manager.findfont(prop)
    name=mpl.font_manager.get_font(fontfile).family_name
    return name