"""
test_itunes.py

Copyright © 2015 Alex Danoff. All Rights Reserved.
2015-08-02

This file tests the functionality provided by the itunes module.
"""

import unittest
from datetime import datetime

from itunes.itunes import parse_value, run_applescript, play_track
from itunes.exceptions import AppleScriptError, TrackError

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
        self.assertIsNone(parse_value('""'))
        self.assertIsNone(parse_value("missing value"))
        self.assertEquals(parse_value('date: "Saturday, March 13, 2010 at ' \
            '5:02:22 PM"'), datetime.fromtimestamp(1268517742))

    def test_run_applescript(self):
        self.assertRaises(AppleScriptError, run_applescript, "THIS IS INVALID" \
            " APPLESCRIPT")

    def test_play_track(self):
        self.assertRaises(TrackError, play_track, "~~~~---`-`-`")
