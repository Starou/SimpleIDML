# -*- coding: utf-8 -*-

import unittest
import re


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

    def test_increment_xmltag_id(self):
        from simple_idml.utils import increment_xmltag_id
        self.assertEqual(increment_xmltag_id("di3i4", "sibling"), "di3i5")
        self.assertEqual(increment_xmltag_id("di3i4i10", "sibling"), "di3i4i11")

        self.assertEqual(increment_xmltag_id("MyL33tPrefixdi3i4", "sibling"), "MyL33tPrefixdi3i5")
        self.assertEqual(increment_xmltag_id("MyL33tPrefixdi3i4i10", "sibling"), "MyL33tPrefixdi3i4i11")

        self.assertEqual(increment_xmltag_id("di3i4", "child"), "di3i4i1")
        self.assertEqual(increment_xmltag_id("di3i4i10", "child"), "di3i4i10i1")

        self.assertEqual(increment_xmltag_id("MyL33tPrefixdi3i4", "child"), "MyL33tPrefixdi3i4i1")
        self.assertEqual(increment_xmltag_id("MyL33tPrefixdi3i4i10", "child"), "MyL33tPrefixdi3i4i10i1")

    def test_prefix_content_filename(self):
        from simple_idml.utils import prefix_content_filename

        # Prefix stories and spread filename references.
        rx = re.compile(r"^(Stories/Story_|Spreads/Spread_)(.+\.xml)$")
        
        src = "Stories/Story_u139.xml"
        result = prefix_content_filename(src, "MyPrefix", rx)
        self.assertEqual(result, "Stories/Story_MyPrefixu139.xml")
        
        src="Spreads/Spread_ub6.xml"
        result = prefix_content_filename(src, "MyPrefix", rx)
        self.assertEqual(result, "Spreads/Spread_MyPrefixub6.xml")

        # Prefix filenames.
        rx = re.compile(r"^(Story_|Spread_)(.+\.xml)$")
        
        src = "Story_u139.xml"
        result = prefix_content_filename(src, "MyPrefix", rx)
        self.assertEqual(result, "Story_MyPrefixu139.xml")
        
        src="Spread_ub6.xml"
        result = prefix_content_filename(src, "MyPrefix", rx)
        self.assertEqual(result, "Spread_MyPrefixub6.xml")


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(UtilsTestCase)
    return suite
