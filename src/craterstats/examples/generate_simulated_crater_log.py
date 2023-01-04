#  Copyright (c) 2023, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

# This example illustrates how to generate a random sequence of crater diameters for
# specified time interval which will conform to a chosen chronology model


import numpy as np

import craterstats as cst


def pf_inverse(pf,y,tol=1e-6): # provides the inverse function for the cumulative form of the PF
    log_y = np.log10(y)
    xrange = np.log10(pf.range)
    divisions = 9
    count = 0

    while True:
        x0 = np.linspace(xrange[1], xrange[0], divisions) # reverse order because np.interp() requires increasing 'x-values'
        y0 = np.log10(pf.evaluate("cumulative", 10.** x0))
        x = np.interp(log_y, y0, x0)
        y1 = np.log10(pf.evaluate("cumulative", 10.** x))
        q = np.searchsorted(y0, log_y)

        xrange = x0[[q,q-1]]
        count += 1
        if abs(y1 - log_y) < tol or count > 99: break

    return 10**x


def main():
    t_interval = [-1.,0.]       # time start, finish in Ga
    area = 100.                 # modelled area in km2
    poisson_intervals = True    # use Poisson spaced events? (otherwise just expectation interval)

    pf = cst.Productionfn(cst.PATH+"config/functions.txt", "Moon, Neukum (1983)") # specify chronology model
    cf = cst.Chronologyfn(cst.PATH+"config/functions.txt", "Moon, Neukum (1983)") # specify chronology model

    diameter_range = pf.range
    diameter_range[0] = .05     # set minimum diameter of interest

    N = pf.evaluate("cumulative", [1., diameter_range[0], diameter_range[1]])   # default a0
    N1_ratio = N[1] / N[0]

    t = t_interval[0]
    i = 0

    rng = np.random.default_rng()
    print(' Event       Time   Diameter')

    while t<=t_interval[1]:

        #generate crater diameter
        u = rng.uniform(0, 1)
        y = u * (N[1] - N[2]) + N[2]
        d = pf_inverse(pf, y)

        #time interval
        phi = cf.phi(t)
        lam = phi * N1_ratio * area
        if poisson_intervals:
            u = rng.uniform(0, 1)
            dt = -np.log(u) / lam #proper poisson interval
        else:
            dt = 1. / lam #mean interval

        t += dt
        i += 1

        print('{:6d} {:10.6f} {:10.4f}'.format(i, t, d))


if __name__ == '__main__':
    main()