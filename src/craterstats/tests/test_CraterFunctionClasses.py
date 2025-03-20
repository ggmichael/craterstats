#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import unittest
import textwrap

import numpy as np

import craterstats as cst

class TestCraterFunctionObjects(unittest.TestCase):

    file_fns = cst.gm.filename(cst.__file__, 'p') + 'config/functions.txt'

    def test_Chronologyfn(self):
        cf = cst.Chronologyfn(self.file_fns, 'Moon, Neukum (1983)')
        self.assertEqual(cf.N1(0.),0.)
        N1=5.44E-14*(np.exp(6.93*3.)-1)+8.38E-4*3.
        self.assertEqual(cf.N1(3.), N1)
        self.assertEqual(cf.a0(3.), np.log10(N1))
        self.assertAlmostEqual(cf.phi(0.), 8.38E-4)
        self.assertAlmostEqual(cf.t(n1=N1), 3.,places=4)

        #user defined function
        f = textwrap.dedent("""
            chronology={
              name='user_function'
              n1_code="
                a=5.44E-14 * (exp(6.93*t)-1)
                b=8.38E-4 * t
                n1=a+b
                "
            }
            """)
        cf_user = cst.Chronologyfn(f, 'user_function')
        self.assertEqual(cf_user.N1(3.), N1)
        self.assertTrue(np.allclose(cf.getplotdata(), cf_user.getplotdata()))
        self.assertTrue(np.allclose(cf.getplotdata(phi=True),cf_user.getplotdata(phi=True))) # user fn same as pre-defined

    def test_Productionfn(self):
        Npf = cst.Productionfn(self.file_fns,'Moon, Neukum (1983)') # polynomial PF
        self.assertTrue(np.allclose(Npf.range,(.01, 300.)))
        self.assertTrue(np.allclose(Npf.a, [-2.5339, -3.6269, 0.43662, 0.79347, 0.086468, -0.26485, -0.066382, 0.037923,
                                           0.010596, -0.0022496, -0.00051797, 0.0000397]))
        Hpf = cst.Productionfn(self.file_fns, 'Mars, Hartmann (2005)')  # tabular PF
        test_a0=1.5
        for pf in [Npf,Hpf]:
            for presentation in ['cumulative','differential']:
                r=pf.getplotdata(presentation,a0=test_a0) # create isochron with given a0
                r['err']=np.ones(len(r['y']))
                self.assertAlmostEqual(pf.fit(r)[0],test_a0) # test whether fitting can recover a0

    def test_Equilibriumfn(self):
        ef = cst.Productionfn(self.file_fns,'Lunar equilibrium (Trask, 1966)',equilibrium=True)
        self.assertEqual(ef.evaluate('cumulative', 1., a0=ef.a[0]), 10 ** (-1.1 - 2. * np.log10(1.)))
        self.assertEqual(ef.evaluate('cumulative', 10., a0=ef.a[0]), 10 ** (-1.1 - 2. * np.log10(10.)))

    def test_Epochs(self):
        cf = cst.Chronologyfn(self.file_fns, 'Mars, Hartmann & Neukum (2001)')
        pf = cst.Productionfn(self.file_fns, 'Mars, Ivanov (2001)')
        ep = cst.Epochs(self.file_fns, 'Mars, Michael (2013)', pf, cf)
        self.assertTrue(np.allclose(ep.time,[0.0, 0.328, 1.23, 3.37, 3.61, 3.71, 3.83, 3.94],rtol=.01)) # (Michael, 2013)



if __name__ == '__main__':
    unittest.main()
