#  Copyright (c) 2021-2025, Greg Michael
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
        self.assertEqual(cst.str_age(.314, .11, .14, unit='Ga', mu=True), r'$𝜇0.314^{+0.11}_{-0.14}$ Ga')
        self.assertEqual(cst.str_age(.314, simple=True), '314 Ma')
        self.assertEqual(cst.str_age(1.), '$1.00$ Ga')
        self.assertEqual(cst.str_age(1., simple=True), '1 Ga')
        self.assertEqual(cst.str_age(.314, .11, .14,sf=2),'$310^{+100}_{-100}$ Ma')

if __name__ == '__main__':
    unittest.main()
