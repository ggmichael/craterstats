#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import unittest

import numpy as np

import craterstats as cst

class TestCraterstats(unittest.TestCase):

    def test_bin_bias_correction(self):
        self.assertEqual(cst.bin_bias_correction(np.sqrt(2), 0), 1.)
        self.assertAlmostEqual(cst.bin_bias_correction(np.sqrt(2), -2.), 1.015,places=3)

    def test_str_age(self):
        self.assertEqual(cst.str_age(.314, .11, .14),'$314^{+110}_{-140}$ Ma')
        self.assertEqual(cst.str_age(.314, .11, .14, ga=True, mu=True), '$\mu0.314^{+0.11}_{-0.14}$ Ga')
        self.assertEqual(cst.str_age(.314, simple=True), '314 Ma')
        self.assertEqual(cst.str_age(1.), '$1.00$ Ga')
        self.assertEqual(cst.str_age(1., simple=True), '1 Ga')
        self.assertEqual(cst.str_age(.314, .11, .14,sf=2),'$310^{+100}_{-100}$ Ma')

    def test_str_diameter_range(self):
        self.assertEqual(cst.str_diameter_range(np.array([.65, 1.2])),'0.65–1.2 km')
        self.assertEqual(cst.str_diameter_range([1.1, 1.7]),'1.1–1.7 km')
        self.assertEqual(cst.str_diameter_range([.65, .95]),'650–950 m')

if __name__ == '__main__':
    unittest.main()
