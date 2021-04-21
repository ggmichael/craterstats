#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import numpy as np

from . import normal


def poisson(k,lam,cumulative=False,threshold=23):
    '''
    poisson mass function
    vectorised in lambda, but not k

    :param k:
    :param lam:
    :param cumulative: return cmf instead of pmf
    :param threshold: use normal approximation above threshold value of k
    :return: pmf
    '''

    if k<threshold:       # poisson
        if cumulative:
            res = 0.
            for i in range(k+1):
                res += (lam**i) / np.math.factorial(i)
            return np.exp(-lam) * res
        else:
            return lam**k * np.exp(-lam) / np.math.factorial(k)

    else:                 # normal
        if cumulative:
            return normal(lam, np.sqrt(lam), k, cumulative=True)
        else:
            return normal(lam, np.sqrt(lam), k)




#
# import matplotlib.pyplot as plt
#
# if __name__ == '__main__':
#
#     ns=1000
#     x=np.linspace(0,100,ns)
#     fig, (ax1, ax2) = plt.subplot(1, 2)
#     for i in range(1,99):
#         ax1.plot(x,poisson(i,x),color='0' if i<30 else '0.')
#     plt.show()



