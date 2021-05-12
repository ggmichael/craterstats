#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import unittest
from unittest.mock import patch
import textwrap

import io
import numpy as np

import craterstats as cst
import craterstats.gm as gm

class TestPlottingClasses(unittest.TestCase):

    root = cst.gm.filename(cst.__file__, 'p')
    file_fns = root + 'config/functions.txt'
    cf = cst.Chronologyfn(file_fns, 'Mars, Hartmann & Neukum (2001)')
    pf = cst.Productionfn(file_fns, 'Mars, Ivanov (2001)')
    cc = cst.Cratercount(root + 'sample/Pickering.scc')

    def test_Craterplotset_CreatePlotSpace(self):
        cps=cst.Craterplotset()
        cps.CreatePlotSpace()
        self.assertTrue(cps.fig)
        self.assertTrue(cps.ax)

    def test_Craterplot_get_data_range(self):
        cp = cst.Craterplot(cratercount=self.cc)
        cps = cst.Craterplotset(craterplot=[cp])

        res = cp.get_data_range(cps)
        self.assertTrue(np.allclose(res,(.1,2.7,6.5e-4,8.2),rtol=.05))

    def test_Craterplotset_autoscale(self):
        cp = cst.Craterplot(cratercount=self.cc)
        cps = cst.Craterplotset(craterplot=[cp])

        cps.autoscale()
        self.assertEqual(list(cps.xrange)+list(cps.yrange),[-2, 2, -5, 3])


    def test_Craterplotset_summary(self):
        cp = cst.Craterplot(cratercount=self.cc,range=[.2,.7],type='d-fit')
        cps = cst.Craterplotset(cf=self.cf,pf=self.pf,craterplot=[cp])

        def get_cps_summary():
            with patch('sys.stdout', new_callable=io.StringIO) as m:
                cps.create_summary_table()
                table=m.getvalue().split('\n')
                return table[1][:145] # trim off source file

        # the following results are not fundamental, but verified against CraterstatsII (see demo plots):
        # name,area,binning,d_min,d_max,method,resurf,n,n_event,age,age-,age+,a0,a0-,a0+,N(1)
        self.assertEqual(get_cps_summary(),
            'Pickering                  3036.6 pseudo-log   0.2   0.7     d-fit      0   313.0       313   0.668   0.613   0.722 -3.488 -3.525 -3.453 3.25e-04')
        cp.UpdateSettings(binning='10/decade')
        self.assertEqual(get_cps_summary(),
            'Pickering                  3036.6  10/decade   0.2  0.79     d-fit      0   313.0       313   0.645   0.593   0.697 -3.503 -3.539 -3.469 3.14e-04')
        cp.UpdateSettings(type='c-fit', resurf=1, binning='pseudo-log')
        self.assertEqual(get_cps_summary(),
            'Pickering                  3036.6 pseudo-log   0.2   0.7     c-fit      1   313.0       313   0.691   0.653   0.729 -3.472 -3.497 -3.449 3.37e-04')
        cp.UpdateSettings(type='poisson', range=[.22,.43], resurf=0)
        self.assertEqual(get_cps_summary(),
            'Pickering                  3036.6 pseudo-log  0.22  0.43   poisson      0     223       223   0.684    0.64   0.731 -3.477 -3.506 -3.448 3.34e-04')
        cp.UpdateSettings(type='poisson', range=[.22, .43], binning='none')
        self.assertEqual(get_cps_summary(),
            'Pickering                  3036.6       none  0.22  0.43   poisson      0     223       223   0.684    0.64   0.731 -3.477 -3.506 -3.448 3.34e-04')




