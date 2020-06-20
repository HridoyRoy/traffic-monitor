LOG_COUNTER = 0
LOG_FILENUM = 0
LOG_FILENAME = "./saved/log"
LOG_FILENUM_SWITCH_PAGE = 0
# Changing this to 10 for testing. I think 500 is decent irl
LOG_FILESIZE = 10

STATS_FILE = "./saved/stats.txt"

# The threshold of number of requests on avg in the last 2 min. This low value is for testing
ROLLING_LOG_ALERT_THRESHOLD = .5
LOG_COUNTER_MAX_SIZE = 5

class LogIndexer:
    log_counter = 0
    log_filenum = 0
    log_filenum_switch_page = 0

    def reset(self):
        self.log_counter = 0
        self.log_filenum = 0
        self.log_filenum_switch_page = 0
