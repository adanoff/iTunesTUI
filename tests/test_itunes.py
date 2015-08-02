"""
test_itunes.py

Copyright © 2015 Alex Danoff. All Rights Reserved.
2015-08-02

This file tests the functionality provided by the itunes module.
"""

import unittest

from itunes.itunes import parse_value

class ITunesTests(unittest.TestCase):
    """
    Test cases for iTunes functionality.
    """

    def test_parse_value(self):
        self.assertEquals(parse_value("10"), 10)
        self.assertEquals(parse_value("1.0"), 1.0)
        self.assertTrue(parse_value("true"))
        self.assertFalse(parse_value("false"))
        self.assertIsNone(parse_value(""))
        self.assertIsNone(parse_value("missing value"))
