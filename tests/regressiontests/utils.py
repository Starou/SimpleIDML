# -*- coding: utf-8 -*-

import unittest


class UtilsTestCase(unittest.TestCase):
    def test_increment_filename(self):
        from simple_idml.utils import increment_filename
        filename = "/path/to/myfile.txt"
        self.assertEqual(increment_filename(filename), "/path/to/myfilf.txt")

        filename = "/path/to/myfilez.txt"
        self.assertEqual(increment_filename(filename), "/path/to/myfileza.txt")

        filename = "/path/to/myfileZ.txt"
        self.assertEqual(increment_filename(filename), "/path/to/myfileZa.txt")

        filename = "/path/to/myfile-200.txt"
        self.assertEqual(increment_filename(filename), "/path/to/myfile-201.txt")

        filename = "/path/to/myfile-299.txt"
        self.assertEqual(increment_filename(filename), "/path/to/myfile-300.txt")

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(UtilsTestCase)
    return suite
