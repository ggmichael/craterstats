#  Copyright (c) 2021-2025, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.

import unittest

import craterstats.cli as cli

class Testcli(unittest.TestCase):

    def test_decode_abbreviation(self):
        s=['Red','Green','Blue','Moon, Neukum (1983)','Mars, Hartmann & Daubar (2016)']
        # self.assertEqual(cli.decode_abbreviation(s, '2'), 2)
        # self.assertEqual(cli.decode_abbreviation(s, '2', one_based=True), 1)

        self.assertEqual(cli.decode_abbreviation(s, 'gr'), 1)
        self.assertEqual(cli.decode_abbreviation(s, 'gn'), 1)
        self.assertEqual(cli.decode_abbreviation(s, 'neukum83'), 3)
        self.assertEqual(cli.decode_abbreviation(s, 'neukum83',one_based = True), 3)
        self.assertEqual(cli.decode_abbreviation(s, 'h&d'), 4)

        self.assertRaises(SystemExit,cli.decode_abbreviation, s, 'error')
        self.assertEqual(cli.decode_abbreviation(s, 'r', allow_ambiguous=True), 0)
        self.assertRaises(SystemExit, cli.decode_abbreviation, s, 'r')


if __name__ == '__main__':
    unittest.main()
