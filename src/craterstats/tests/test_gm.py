#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import unittest
from unittest.mock import patch, mock_open

import numpy as np
import colorama

import craterstats.gm as gm

class Testgm(unittest.TestCase):

    # maths

    def test_scl(self):
        a=np.linspace(2, 7, 4)
        self.assertTrue(np.allclose(gm.scl(a, out_range=[10., 20.]), [10., 13.333333, 16.666666, 20.]))
        self.assertTrue(np.array_equal(gm.scl(a, out_range=[10, 20]), [10, 13, 16, 20]))
        self.assertTrue(np.array_equal(gm.scl(a, tname='byte'), [  0,  85, 170, 255]))
        self.assertTrue(np.array_equal(gm.scl(a, tname='int16'), [-32768, -10922, 10922, 32767]))
        self.assertTrue(np.array_equal(gm.scl(a, tname='uint16'), [0, 21845, 43690, 65535]))

    def test_range(self):
        self.assertEqual(gm.range([3, 7, 2]),(2,7))
        self.assertEqual(gm.range([3.5, -7, 2]), (-7, 3.5))

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

    # plotting

    def test_mpl_check_font(self):
        fontnamelist=['Myriad Pro','Verdana','DejaVu Sans','Tahoma']
        self.assertIn(gm.mpl_check_font(fontnamelist),fontnamelist)

    def test_ticks(self):
        self.assertTrue(np.array_equal(gm.ticks([0,4.5],3), [0., 5.]))
        self.assertTrue(np.array_equal(gm.ticks([0, .9], 3), [0. , 0.5, 1. ]))
        self.assertTrue(np.array_equal(gm.ticks([0.5, 3.5], 3), [0., 2., 4.]))

    # string

    def test_bright(self):
        self.assertEqual(gm.bright('test'), colorama.Style.BRIGHT+'test'+colorama.Style.RESET_ALL)
        self.assertTrue(gm.bright.init)

    def test_strip_quotes(self):
        self.assertEqual(gm.strip_quotes('"test"'),'test')
        self.assertEqual(gm.strip_quotes("'test'"), 'test')
        self.assertEqual(gm.strip_quotes('"'), '"')
        self.assertEqual(gm.strip_quotes(''), '')

    def test_quoted_split(self):
        self.assertEqual(gm.quoted_split('"test"  0'),['test', '0'])
        self.assertEqual(gm.quoted_split('test'), ['test'])
        self.assertEqual(gm.quoted_split(r"9684  0 Inf 'test data' 1.76e+04 'D:\tmp\test.scc'"),
                         ['9684', '0', 'Inf', 'test data', '1.76e+04', r'D:\tmp\test.scc'])
        self.assertEqual(gm.quoted_split(r"9684,  0, Inf, 'test, data', 1.76e+04 'D:\tmp\test.scc'",separator=r'\s,'),
                         ['9684', '0', 'Inf', 'test, data', '1.76e+04', r'D:\tmp\test.scc'])

    def test_sigfigs(self):
        self.assertEqual(gm.sigfigs(3.14159, 3),'3.14')
        self.assertEqual(gm.sigfigs(3.14159, 2), '3.1')
        self.assertEqual(gm.sigfigs(112.14159, 2), '110')
        self.assertEqual(gm.sigfigs(-.0314159, 3), '-0.0314')
        self.assertEqual(gm.sigfigs(314759, 3), '315000')
        self.assertEqual(gm.sigfigs(31.4759, 1), '30')
        self.assertEqual(gm.sigfigs([243.3, 0.3422], 2), ['240', '0.34'])

    def test_scientific_notation(self):
        self.assertEqual(gm.scientific_notation(10 ** 3 * np.pi, sf=2),'$3100$')
        self.assertEqual(gm.scientific_notation(10 ** 3 * np.pi, sf=2, force=True), r'$3.1\cdot10^{3}$')
        self.assertEqual(gm.scientific_notation(10 ** -2 * np.pi, sf=2),'$0.031$')
        self.assertEqual(gm.scientific_notation(10 ** -3 * -np.pi, sf=3), r'$-3.14\cdot10^{-3}$')

    def test_diameter_range(self):
        self.assertEqual(gm.diameter_range(np.array([.65, 1.2])),'0.65–1.2 km')
        self.assertEqual(gm.diameter_range([1.1, 1.7]),'1.1–1.7 km')
        self.assertEqual(gm.diameter_range([.65, .95]),'650–950 m')

    def test_percentile_sigfigs(self):
        self.assertEqual(gm.percentile_sigfigs(0.01567,2), '0.016')
        self.assertEqual(gm.percentile_sigfigs(0.01567, 3), '0.0157')
        self.assertEqual(gm.percentile_sigfigs(43.01567, 2), '43')
        self.assertEqual(gm.percentile_sigfigs(53.01567, 2), '53')
        self.assertEqual(gm.percentile_sigfigs(99.5301567, 2), '99.53')
        self.assertEqual(gm.percentile_sigfigs(99.995301567, 2), '99.9953')
        self.assertEqual(gm.percentile_sigfigs(100, 2), '100')

    #file

    def test_filename(self):
        f=r'd:\aaa\bbb\test.txt'
        self.assertEqual(gm.filename(f, 'n'), 'test')
        self.assertEqual(gm.filename(f, 'e'), '.txt')
        self.assertEqual(gm.filename(f, 'p'), 'd:\\aaa\\bbb\\')
        self.assertEqual(gm.filename(f, 'b'), 'bbb\\')
        self.assertEqual(gm.filename(f, 'u'), 'd:\\aaa\\')
        self.assertEqual(gm.filename(f, 'pn12e', '_tag','(1)'), r'd:\aaa\bbb\test_tag(1).txt')

    def test_write_textfile(self):
        m = mock_open()
        f = r'd:\tmp\test.txt'
        with patch('builtins.open', m):
            gm.write_textfile(f,'test-string')
            m.assert_called_once_with(f, 'w', encoding='utf-8')
            m().writelines.assert_called_once_with('test-string')

            gm.write_textfile(f, ['a','b'])
            m().writelines.assert_called_with('a\nb')

    def test_read_textfile(self):
        f = r'd:\tmp\test.txt'
        c = '1\n2\n#test\n\n5 ;comment'
        with patch('builtins.open', mock_open(read_data=c)) as m:
            self.assertEqual(gm.read_textfile(f),['1', '2', '#test', '', '5 ;comment'])
            m.assert_called_once_with(f, 'r', encoding='utf-8-sig')
            self.assertEqual(gm.read_textfile(f, as_string=True),c)
            self.assertEqual(gm.read_textfile(f, n_lines=2), ['1', '2'])
            self.assertEqual(gm.read_textfile(f, ignore_hash=True), ['1', '2', '', '5 ;comment'])
            self.assertEqual(gm.read_textfile(f, ignore_blank=True), ['1', '2', '#test', '5 ;comment'])
            self.assertEqual(gm.read_textfile(f, strip=';'), ['1', '2', '#test', '','5 '])

    def test_read_textstructure(self):
        self.assertEqual(gm.read_textstructure('scalar=10', from_string=True), {'scalar': '10'})
        self.assertEqual(gm.read_textstructure("string='this is a string.'", from_string=True), {'string': 'this is a string.'})
        self.assertEqual(gm.read_textstructure('array=[1.3,15.7,6,14]', from_string=True), {'array': ['1.3', '15.7', '6', '14']})
        self.assertEqual(gm.read_textstructure('array=[1,2,\n3,4]', from_string=True), {'array': ['1', '2', '3', '4']})
        self.assertEqual(gm.read_textstructure('pointer=*[1,2,3]', from_string=True), {'pointer': ['1', '2', '3']})
        self.assertEqual(gm.read_textstructure('boundary = {lon,lat\n-126.97	17.35\n-124.45	18.94\n}',
            from_string=True), {'boundary': {'lat': ['17.35', '18.94'], 'lon': ['-126.97', '-124.45']}})
        self.assertEqual(gm.read_textstructure('wifi={mac,name\n04f02a418c2e "ABC Wi-Fi"\n}',
            from_string=True), {'wifi': {'mac': ['04f02a418c2e'], 'name': ['ABC Wi-Fi']}})
        self.assertEqual(gm.read_textstructure('text_block=""As the sun set and the moon rose,\n'
                                               'she happened upon a splendid castle."\n"',from_string=True),
            {'text_block': '"As the sun set and the moon rose,\nshe happened upon a splendid castle."\n'})
        self.assertEqual(gm.read_textstructure('dict={\n  a=30\n  b=[2,3]\n}', from_string=True), {'dict': {'a': '30', 'b': ['2', '3']}})
        self.assertEqual(gm.read_textstructure('implied=1\nimplied=2\nimplied=3', from_string=True), {'implied': ['1', '2', '3']})

        # nested table
        test = """
m2cnd={
    trials = 50
    results={bin, n_sigma
    -3.5    -3.19
    -3      -0.218
    }
}
"""
        self.assertEqual(gm.read_textstructure(test, from_string=True),{'m2cnd': {'trials':'50', 'results':{'bin':['-3.5','-3'], 'n_sigma':['-3.19','-0.218']}}})

if __name__ == '__main__':
    unittest.main()
