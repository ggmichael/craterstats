#  Copyright (c) 2021, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import unittest
import numpy as np

import craterstats.gm as gm

class Testgm(unittest.TestCase):
    def test_sigfigs(self):
        self.assertEqual(gm.sigfigs(3.14159, 3),'3.14')
        self.assertEqual(gm.sigfigs(3.14159, 2), '3.1')
        self.assertEqual(gm.sigfigs(112.14159, 2), '110')
        self.assertEqual(gm.sigfigs(-.0314159, 3), '-0.0314')
        self.assertEqual(gm.sigfigs(314759, 3), '315000')
        self.assertEqual(gm.sigfigs(31.4759, 1), '30')
        self.assertEqual(gm.sigfigs([243.3, 0.3422], 2), ['240', '0.34'])

    def test_scl(self):
        a=np.linspace(2, 7, 4)
        self.assertTrue(np.allclose(gm.scl(a, out_range=[10., 20.]), [10., 13.333333, 16.666666, 20.]))
        self.assertTrue(np.array_equal(gm.scl(a, out_range=[10, 20]), [10, 13, 16, 20]))
        self.assertTrue(np.array_equal(gm.scl(a, tname='byte'), [  0,  85, 170, 255]))
        self.assertTrue(np.array_equal(gm.scl(a, tname='int16'), [-32768, -10922, 10922, 32767]))
        self.assertTrue(np.array_equal(gm.scl(a, tname='uint16'), [0, 21845, 43690, 65535]))

    def test_range(self):
        self.assertEqual(gm.range([3, 7, 2]),(2,7))
        self.assertEqual(gm.range([3, -7, 2]), (-7, 3))

    def test_mag(self):
        self.assertEqual(gm.mag([3, 7, 2]),5)
        self.assertEqual(gm.mag([3, -7, 2]), 10)

    def test_poly(self):
        self.assertTrue(np.array_equal(gm.poly([2,3,1], [0,-1,2]), [2+0+0,2+3*(-1)+(-1)**2,2+3*2+2**2]))

    def test_poisson(self):
        lam=np.array([0.,1.,1.5])
        res=(0.,
             1.**3 * np.exp(-1.) / (3*2*1),
             1.5 ** 3 * np.exp(-1.5) / (3 * 2 * 1)
             )
        self.assertEqual(gm.poisson(3,0.),res[0])
        self.assertEqual(gm.poisson(3, 1.), res[1])
        self.assertEqual(gm.poisson(3, 1.5), res[2])
        self.assertTrue(np.array_equal(gm.poisson(3, lam), res))
        self.assertTrue(np.array_equal(gm.poisson(2, lam, cumulative=True),
                                       gm.poisson(0, lam)+gm.poisson(1, lam)+gm.poisson(2, lam) ))
        self.assertTrue(np.array_equal(gm.poisson(25, 3., threshold=23), gm.normal(3., np.sqrt(3.), 25)))
        self.assertTrue(np.array_equal(gm.poisson(25, 3., threshold=23, cumulative=True),
                                       gm.normal(3., np.sqrt(3.), 25, cumulative=True) ))

    def test_normal(self):
        self.assertGreater(gm.normal(10., 1., 10.),gm.normal(10., 1., 9.9))
        self.assertEqual(gm.normal(10.,1.,10.,cumulative=True),0.5)
        self.assertAlmostEqual(gm.normal(10., 1., 11., cumulative=True) - gm.normal(10., 1., 9., cumulative=True),
                               .683,places=3)



if __name__ == '__main__':
    unittest.main()
