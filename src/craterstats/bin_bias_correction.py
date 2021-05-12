#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np

def bin_bias_correction(beta,k):
    '''
    Correction for binning bias of log-log histogram of known slope (see Michael (2013), Eq. 2)

    :param beta: ratio between adjacent bin boundaries, e.g. sqrt(2)
    :param k: log-log slope (including minus sign, e.g. -2)
    :return: correction ratio
    '''

    g=beta**.5-beta**(-.5)
    with np.errstate(invalid='ignore'): # both vectors of conditional are evaluated:
        Fbin2F_ratio = np.where(abs(k) < 1e-5,1., (beta ** (k / 2.) - beta ** (-k / 2.)) / (g * k) )

    return Fbin2F_ratio