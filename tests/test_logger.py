import unittest
import sys
import os
sys.path.append('../')
import t_monitor
from t_monitor import globals
from t_monitor import logger
import shutil

"""
This is a stub. The basic functionality of the logger is tested in the end to end test, found in traffic-monitor/end_to_end.py.
"""
class Testlogger(unittest.TestCase):
    def setUp(self):
        self.log_indexer = globals.LogIndexer()
        self.log_master = logger.Logger(self.log_indexer)
        self.log_indexer.reset()

    def test_get_section_from_url(self):
        url = "https://www.google.com/pages/hridoyroy"
        section = self.log_master.get_section_from_url(url)
        self.assertEqual(section, "https://www.google.com/pages")
        url = "www.google.com/pages"
        section = self.log_master.get_section_from_url(url)
        self.assertEqual(section, url)
        url = "www.google.com/pages/hridoyroy"
        section = self.log_master.get_section_from_url(url)
        self.assertEqual(section, "www.google.com/pages")
