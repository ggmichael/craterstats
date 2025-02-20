#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import unittest
from unittest.mock import patch, mock_open
import textwrap

import numpy as np

import craterstats as cst

class TestCratercount(unittest.TestCase):

    def test_ReadStatFile(self):
        f = r'd:\tmp\test.stat'
        c = textwrap.dedent("""
            # D        F(D)    N_dif    Error       C(D)    N_cum    Error 
            .0600       10  2.93E+00  9.28E-01      477  1.40E+00  6.41E-02
            .0700       12  3.52E+00  1.02E+00      467  1.37E+00  6.34E-02
            """)
        with patch('builtins.open', mock_open(read_data=c)):
            cc = cst.Cratercount(f)
        # check correctly read
        self.assertTrue(np.array_equal(cc.binned['d_min'],[0.06, 0.07]))
        self.assertTrue(np.array_equal(cc.binned['ncum'], [477, 467]))
        # check initialisation
        self.assertEqual(cc.binning,'pseudo-log')
        self.assertTrue(cc.prebinned)
        # check derived values - tests MakeBinGeometricMean()
        self.assertAlmostEqual(cc.area, 477/1.40e+00) # area found from C(D)/N_cum
        self.assertTrue(np.allclose(cc.binned['d_max'], [0.07, .07*(.07/.06)])) # extrapolated last bin width
        self.assertAlmostEqual(cc.binned['d_mean'][0], np.sqrt(.06*.07))
        self.assertAlmostEqual(cc.binned['bin_width'][0], .07-.06)

    def test_ReadDiamFile1(self):
        c = textwrap.dedent("""
            # comment
            area = 100.
            crater = {diameter
            1.1
            2.3
            3.0
            1.4
            }
            """)
        with patch('builtins.open', mock_open(read_data=c)):
            cc = cst.Cratercount('test.diam')
        # check correctly read
        self.assertTrue(np.array_equal(cc.diam, [3., 2.3, 1.4, 1.1]))
        self.assertEqual(cc.area, 100.)
        # check initialisation
        self.assertEqual(cc.binning, None)
        self.assertFalse(cc.prebinned)
        self.assertFalse(cc.buffered)
        self.assertEqual(cc.perimeter, None)
        self.assertTrue(np.array_equal(cc.fraction, [1., 1., 1., 1.]))

    def test_ReadDiamFile2(self):
        c = textwrap.dedent("""
            area = 100.
            crater = {diameter, fraction, lon, lat
            1.1 0.3 127.3 -52.8
            }
            """)
        with patch('builtins.open', mock_open(read_data=c)):
            cc = cst.Cratercount('test.diam')
        # check correctly read (lat/lon not used here)
        self.assertEqual(cc.diam[0], 1.1)
        self.assertEqual(cc.fraction[0], .3)

    def test_ReadDiamFile3(self): # buffered count (indicated by presence of 'reference_area')
        c = textwrap.dedent("""
            crater = {diameter, reference_area
            1.1 24.3
            }
            """)
        with patch('builtins.open', mock_open(read_data=c)):
            cc = cst.Cratercount('test.diam')
        # check correctly read
        self.assertEqual(cc.diam[0], 1.1)
        # check initialisation
        self.assertEqual(cc.area, 1.) # crater densities relative to 1 km2 for buffered
        self.assertTrue(cc.buffered)
        # check derived values
        self.assertEqual(cc.fraction[0], 1/24.3)

    def test_ReadSCCfile(self):
        c = textwrap.dedent("""
            Total_area = 224669.2 <km^2>
            Perimeter = 1605.7
            # crater_diameters:
            crater = {diam,lon,lat
            33.58 -126.0 16.81
            40.40 -124.4 16.95
            }
            """)
        with patch('builtins.open', mock_open(read_data=c)):
            cc = cst.Cratercount('test.scc')
        # check correctly read
        self.assertTrue(np.array_equal(cc.diam, [33.58, 40.40]))
        self.assertEqual(cc.area, 224669.2)
        self.assertEqual(cc.perimeter, 1605.7)
        # check initialisation
        self.assertEqual(cc.binning, None)
        self.assertFalse(cc.prebinned)
        self.assertFalse(cc.buffered)
        self.assertTrue(np.array_equal(cc.fraction, [1., 1.]))

    def make_flat_distribution(self):
        self.N_CRATERS=100
        cc = cst.Cratercount('')
        cc.diam=10**np.linspace(.001,.999,self.N_CRATERS)
        cc.fraction=[1.]*(self.N_CRATERS-2)+[.3]*2
        cc.area = 10.
        return cc

    def test_apply_binning(self):
        cc=self.make_flat_distribution()
        cc.apply_binning('pseudo-log')
        self.assertEqual(cc.binned['d_min'][0], 1.)
        self.assertEqual(cc.binned['d_max'][-1], 10.)
        self.assertEqual(len(cc.binned['d_min']), 18)
        self.assertLess(max(cc.binned['n'])/min(cc.binned['n']), 3.4)
        self.assertEqual(cc.binned['ncum_event'][0], self.N_CRATERS)
        self.assertEqual(cc.binned['ncum'][0], self.N_CRATERS-1.4)
        self.assertAlmostEqual(cc.binned['d_mean'][0], np.sqrt(1.1))
        self.assertAlmostEqual(cc.binned['bin_width'][0], .1)
        cc.apply_binning('root-2')
        self.assertAlmostEqual(cc.binned['d_min'][1], np.sqrt(2))
        self.assertAlmostEqual(cc.binned['bin_width'][0], np.sqrt(2)-1)
        self.assertEqual(cc.binned['ncum_event'][0], self.N_CRATERS)
        self.assertLess(max(cc.binned['n'][0:-1])-min(cc.binned['n'][0:-1]), 2) # last bin may be cut
        b2=sum(cc.binned['n'][0:2])
        cc.apply_binning('x2')
        self.assertEqual(cc.binned['n'][0], b2) # encompasses 2 bins of previous
        self.assertLess(max(cc.binned['n'][0:-1]) - min(cc.binned['n'][0:-1]), 2)  # last bin may be cut
        cc.apply_binning('4th root-2')
        self.assertEqual(sum(cc.binned['n'][0:4]), b2)
        cc.apply_binning('10/decade')
        self.assertEqual(len(cc.binned['d_min']), 10)
        self.assertLess(max(cc.binned['n'][0:-1]) - min(cc.binned['n'][0:-1]), 2)  # last bin may be cut
        self.assertEqual(cc.binned['ncum_event'][0], self.N_CRATERS)
        cc.apply_binning('none')
        self.assertEqual(cc.binned['ncum_event'][0], self.N_CRATERS)
        self.assertEqual(cc.binned['ncum'][0], self.N_CRATERS-1.4)

    def test_getplotdata(self):
        cc = self.make_flat_distribution()
        p = cc.getplotdata('cumulative','none')
        self.assertEqual(p['bin_range'], (cc.diam[0],cc.diam[-1]))
        self.assertEqual(p['d'][0], cc.diam[0])
        self.assertEqual(p['y'][0], (self.N_CRATERS-1.4)/cc.area )
        p = cc.getplotdata('cumulative', 'pseudo-log',range=[1.02,4.98])
        self.assertEqual(p['bin_range'], (1.,5.))

    def test_generate_bins(self):
        cc = self.make_flat_distribution()
        self.assertEqual(cc.generate_bins('none',[.33,.44]),[.33,.44])
        np.testing.assert_allclose(cc.generate_bins('pseudo-log', [.33, .34]), [.3, .35])
        np.testing.assert_allclose(cc.generate_bins('pseudo-log', [.33, .35]), [.3, .35,.4])
        np.testing.assert_allclose(cc.generate_bins('pseudo-log', [.33, .35], expand=False), [.3, .35])
        np.testing.assert_allclose(cc.generate_bins('root-2', [1.1, 1.2]), [1., np.sqrt(2)])
        np.testing.assert_allclose(cc.generate_bins('root-2', [1.2, 1.3], offset=.5), [2**.25,2**.75])
        bins=cc.generate_bins('10/decade', cc.diam)
        self.assertEqual(len(bins),11)
        np.testing.assert_allclose(bins[[0,-1]],[1.,10.])
        self.assertEqual(len(cc.generate_bins('20/decade', cc.diam)),21)

if __name__ == '__main__':
    unittest.main()