from .globals import LOG_COUNTER
from .globals import ROLLING_LOG_ALERT_THRESHOLD
from .globals import LOG_COUNTER_MAX_SIZE
import threading

class Averager:

    # List of max size 121 which has the number of logs seen in the last 120 seconds
    rolling_log_count_list = []


    # The rolling sum for current average
    rolling_sum = 0

    # This keeps track of the number of logs seen by the averager every second
    log_counter_update_per_second = 0


    def rolling_avg(self):
        threading.Timer(1.0, self.rolling_avg).start()
        global LOG_COUNTER
        global LOG_COUNTER_MAX_SIZE
        global ROLLING_LOG_ALERT_THRESHOLD

        print("log counter and per second counter are:" + str(LOG_COUNTER) + " " + str(Averager.log_counter_update_per_second))

        Averager.logs_in_last_second = LOG_COUNTER - Averager.log_counter_update_per_second
        Averager.log_counter_update_per_second = LOG_COUNTER

        Averager.rolling_log_count_list.append(Averager.logs_in_last_second)
        Averager.rolling_sum += Averager.logs_in_last_second

        Averager.rolling_avg_val = Averager.rolling_sum / (len(Averager.rolling_log_count_list))
        print("rolling average value is: " + str(Averager.rolling_avg_val))

        if ROLLING_LOG_ALERT_THRESHOLD < Averager.rolling_avg_val:
            print("OH NO!!! CROSSED THE LINE BUDDY BOI")

        if len(Averager.rolling_log_count_list) > 120:
            Averager.rolling_log_count_list = Averager.rolling_log_count_list[-120:]

        # If too many logs, reset LOG_COUNTER. This is atomic.
        if LOG_COUNTER > LOG_COUNTER_MAX_SIZE:
            print("MAX SIZE HAS BEEN REACHED: RESETTING")
            LOG_COUNTER = 0
            Averager.log_counter_update_per_second = 0
