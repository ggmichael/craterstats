#  Copyright (c) 2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np

def percentile_sigfigs(p, sf=2):
    """
    format string with equivalent differential precision approaching 100 as approaching 0
    p: percentile value between 0 and 100. i.e. 0.015 vs 99.985 as 2 s.f.
    sf: int sig figs
    """

    if p < 50:
        res = f"{p:.{sf}g}"
    else:
        digits = len(f"{100 - p:.{sf}g}")
        res = f"{p:.{max(digits - 2, 0)}f}"
    return res

