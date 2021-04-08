#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np
import craterstats.gm as gm


def ticks(x, max_ticks, max_minor=None):
    # ;x - data
    # ;max_ticks - max no of major ticks
    # ;max_minor - max no of minor ticks (in total, i.e. n_ticks*minor_ticks) - optional

    if not max_ticks: max_ticks = 5
    max_ticks = np.clip(max_ticks, 2, None)

    range = gm.range(x)
    mag = gm.mag(range)

    multiplier = 1.

    while True:
        estimate = mag / float(max_ticks * multiplier)
        exponent = np.floor(np.log10(estimate))
        fraction = estimate / 10. ** exponent
        a = np.searchsorted([0, 1, 2, 5], fraction)-1
        nice_fraction = ([1, 2, 5, 10])[a]
        step = nice_fraction * 10. ** exponent
        i = [np.floor(range[0] / step), np.ceil(range[1] / step)]
        ticks = (i[0] + np.arange(gm.mag(i) + 1)) * step
        n_ticks = len(ticks)
        multiplier *= .9
        if n_ticks <= max_ticks:
            break

    if max_minor:
        choice = [1, 2, 4, 10] if nice_fraction==2 else [1,2,5,10]
        b=max_minor/(n_ticks-1)
        j = np.searchsorted(choice,b)
        minor_ticks=choice[j]
        return ticks,minor_ticks

    return ticks
