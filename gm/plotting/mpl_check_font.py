#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import matplotlib as mpl

# which font is selected when asking for fontname?

def mpl_check_font(fontname):
    prop = mpl.font_manager.FontProperties(family=fontname)
    fontfile= mpl.font_manager.findfont(prop)
    name=mpl.font_manager.get_font(fontfile).family_name
    return name