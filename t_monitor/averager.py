from .globals import LOG_COUNTER
from .globals import ROLLING_LOG_ALERT_THRESHOLD
from .globals import LOG_COUNTER_MAX_SIZE
import threading

class Averager:

    def __init__(self, logIndexer):
        self.logIndexer = logIndexer
        # List of max size 121 which has the number of logs seen in the last 120 seconds
        self.rolling_log_count_list = []
        
        # The rolling sum for current average
        self.rolling_sum = 0

        # This keeps track of the number of logs seen by the averager every second
        self.log_counter_update_per_second = 0

    def rolling_avg(self):
        threading.Timer(1.0, self.rolling_avg).start()
        global LOG_COUNTER_MAX_SIZE
        global ROLLING_LOG_ALERT_THRESHOLD

        print("log counter and per second counter are:" + str(self.logIndexer.log_counter) + " " + str(self.log_counter_update_per_second))

        self.calc_rolling_average()

        self.check_alert_threshold()
        
        self.update_rolling_counts()

        self.reset_log_counters()

    def calc_rolling_average(self):
        self.logs_in_last_second = self.logIndexer.log_counter - self.log_counter_update_per_second
        self.log_counter_update_per_second = self.logIndexer.log_counter

        self.rolling_log_count_list.append(self.logs_in_last_second)
        self.rolling_sum += self.logs_in_last_second

        self.rolling_avg_val = self.rolling_sum / (len(self.rolling_log_count_list))
        print("rolling average value is: " + str(self.rolling_avg_val))

    def check_alert_threshold(self):
        global ROLLING_LOG_ALERT_THRESHOLD
        if ROLLING_LOG_ALERT_THRESHOLD < self.rolling_avg_val:
            print("OH NO!!! CROSSED THE LINE BUDDY BOI")

    def update_rolling_counts(self):
        if len(self.rolling_log_count_list) > 120:
            self.rolling_log_count_list = self.rolling_log_count_list[-120:]

    def reset_log_counters(self):
        global LOG_COUNTER_MAX_SIZE
        # If too many logs, reset LOG_COUNTER. This is atomic.
        if self.logIndexer.log_counter > LOG_COUNTER_MAX_SIZE:
            print("MAX SIZE HAS BEEN REACHED: RESETTING")
            self.logIndexer.log_counter = 0
            self.log_counter_update_per_second = 0
