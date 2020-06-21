# This is the prefix for log filenames.
LOG_FILENAME = "./saved/log"

# This is the size of each log file. 
# NOTE: We are putting this at 10 for demo purposes. In production, we will want much larger log files. 
LOG_FILESIZE = 10

# The threshold for alerting for high traffic in the last 2 min.
# NOTE: This low value is for demonstration purposes.
ROLLING_LOG_ALERT_THRESHOLD = .5

# The maximum value for LogIndexer.log_counter, before the Averager will reset the log_counter. 
# NOTE: In production, this value will be something like 2 ^ 30, and exists to guard against buffer overflow of the log_counter. For demonstration purposes, we are setting it to 5. 
LOG_COUNTER_MAX_SIZE = 5

"""
This class keeps track of the logline and logfile which is being written to and read from. These variables are shared across threads and files. For this reason, they are static variables, so when one thread changes a value, the value is updated for all instances.
"""
class LogIndexer:
    # A counter for the number of logs seen by the Logger. This number is consumed by the Averager when calculating the rolling average for seen requests, and periodically reset when it grows too large.  
    log_counter = 0

    # The current log file number being read from by the statistician. 
    log_filenum = 0

    # The log file number being written to by the logger.
    log_filenum_switch_page = 0

    """
    This function resets the static variables, and is only used in unit tests
    """
    def reset(self):
        self.log_counter = 0
        self.log_filenum = 0
        self.log_filenum_switch_page = 0
