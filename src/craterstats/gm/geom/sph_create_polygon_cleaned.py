#  Copyright (c) 2026, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

from itertools import groupby
import spherely as sph

def sph_create_polygon_cleaned(shell, holes=None, oriented=False):
    """create spherely polygon, automatically removing duplicate vertices"""

    def clean(pts): # remove consecutive duplicates
        return [pt for pt, _ in groupby(pts)]

    if holes:
        holes = [clean(h) for h in holes]

    return sph.create_polygon(clean(shell),holes, oriented)
