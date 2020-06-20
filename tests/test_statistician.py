import unittest
import sys
import os
sys.path.append('../')
import t_monitor
from t_monitor import statistician
from t_monitor import globals
import shutil

class TestStatistician(unittest.TestCase):

    def setUp(self):
        self.log_indexer = globals.LogIndexer()
        self.stat_master = statistician.Statistician(self.log_indexer)

    def test_update_read_logfile(self):
        self.assertEqual(self.log_indexer.log_filenum, 0)
        self.assertEqual(self.log_indexer.log_filenum_switch_page, 0)
        self.assertEqual(self.stat_master.log_line_read, 0)

        # So far so good, initial values are fine. Check if statement in the function.
        
        self.log_indexer.log_filenum_switch_page += 1
        self.stat_master.update_read_logfile()
        self.assertEqual(self.log_indexer.log_filenum, 1)
        self.assertEqual(self.stat_master.log_line_read, 0)

    def test_init_statistics(self):
        # No directories should exist here
        self.assertFalse(os.path.exists("./saved"))

        self.stat_master.init_statistics()
        # now the saved dir should exist
        self.assertTrue(os.path.exists("./saved"))
        self.assertTrue(os.path.exists("./saved/stats.txt"))

        # clean up
        shutil.rmtree("./saved")


    if __name__ == '__main__':
        unittest.main()                    
