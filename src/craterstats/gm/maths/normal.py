#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np

def normal(m,s,x,cumulative=False):
    '''
    evaluate normal pdf at point(s) x

    :param m: mean
    :param s: sd
    :param x: point(s) to evaluate
    :param cumulative: return cdf instead of pdf
    :return: pdf
    '''

    if cumulative:
        return 0.5 * (1 + np.math.erf((x - m) / (s * np.sqrt(2.))))
    else:
        return np.exp(-((x-m)**2)/(2*s**2))/(s*np.sqrt(2*np.pi))

if __name__ == '__main__':
    pass
    # x=gm_scl(findgen(300),out_range=[0.,x_max])
    # plot,x,gm_normal(m,s,x,cumulative=cumulative)
