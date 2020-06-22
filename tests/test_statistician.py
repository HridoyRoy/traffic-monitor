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
        self.log_indexer.reset()
        self.stat_master.reset()

        if os.path.exists("./saved"):
            shutil.rmtree("./saved")

    def test_init_statistics(self):
        # No directories should exist here
        self.assertFalse(os.path.exists("./saved"))

        self.stat_master.init_statistics()
        # now the saved dir should exist
        self.assertTrue(os.path.exists("./saved"))
        self.assertTrue(os.path.exists("./saved/stats.txt"))

    def test_create_logfile_name(self):
        self.log_indexer.log_filenum = 11
        logfile_name = self.stat_master.create_logfile_name()
        self.assertEqual(logfile_name, "./saved/log11.txt")

    def test_update_most_hits_section(self):
        self.stat_master.reverse_section_hits[1] = ["hi", "bye"]
        self.stat_master.reverse_section_hits[2] = ["google"]
        self.stat_master.section_hits = {"hi":1, "bye":1, "google":2}
        self.stat_master.update_most_hits_section()
        self.assertEqual(self.stat_master.stats_dict["most_hits_section"], "google")

    def test_assimilate_logs_into_stats(self):
        os.makedirs("./saved")
        count = 0
        with open("./saved/log0.txt", "w+") as log_zero:
            while count < globals.LOG_FILESIZE:
                url_id = count
                if count > globals.LOG_FILESIZE / 2:
                    # int rounds up
                    url_id = int(count / 2)
                log_zero.write("url" + str(url_id) + ":ip\n")
                count += 1
        self.stat_master.assimilate_logs_into_stats("./saved/log0.txt")
       
        self.assertEqual(self.stat_master.section_hits["url0"], 1)
        self.assertEqual(self.stat_master.section_hits["url1"], 1)
        self.assertEqual(self.stat_master.section_hits["url2"], 1)
        self.assertEqual(self.stat_master.section_hits["url3"], 3)
        self.assertEqual(self.stat_master.section_hits["url4"], 3)
        self.assertEqual(self.stat_master.section_hits["url5"], 1)

    if __name__ == '__main__':
        unittest.main()                    
