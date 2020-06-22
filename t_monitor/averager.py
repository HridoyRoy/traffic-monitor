from .globals import ROLLING_LOG_ALERT_THRESHOLD
from .globals import LOG_COUNTER_MAX_SIZE
import threading
import datetime

"""
The Averager class calculates the rolling average of the number of requests seen by the application, and alerts and logs the alerts when necessary. It also alerts on recovery. 
"""
class Averager:

    def __init__(self, logIndexer):
        self.logIndexer = logIndexer

        # List of max size 121 which has the number of logs seen in the last 120 seconds
        self.rolling_log_count_list = []
        
        # The rolling sum for current average
        self.rolling_sum = 0

        # This keeps track of the number of logs seen by the averager every second
        self.log_counter_update_per_second = 0
        
        # Alert flag makes sure that an alert doesn't refire infinitely
        self.alert_flag = 0

    def rolling_avg(self):
        threading.Timer(1.0, self.rolling_avg).start()
        global LOG_COUNTER_MAX_SIZE
        global ROLLING_LOG_ALERT_THRESHOLD
        
        # calculate rolling average
        self.calc_rolling_average()

        # check if the rolling average has crossed our alerting threshold
        self.check_alert_threshold()
        
        # reset the log counter if it has crossed the max allowed value -- this is to prevent buffer overflow. NOTE: the current max value is set very low for demonstration purposes. In production, it would be something like 2 ^ 20 or something closer to 2 ^ 32. 
        self.reset_log_counters()

    """
    Write line to file
    """
    def write_averager_out(self, line):
        with open("./saved/alerts.txt", "a+") as averager_file:
            averager_file.write(line)

    """
    Calculate rolling average
    """
    def calc_rolling_average(self):
        # Calculate the number of logs seen in the last second (since the last poll of the averager) by subtracting the current log count from the previous log counter value. 
        self.logs_in_last_second = self.logIndexer.log_counter - self.log_counter_update_per_second
        
        # Update previously seen log vounter value to currently seen value
        self.log_counter_update_per_second = self.logIndexer.log_counter

        # Add the number of logs seen this second to a list of max size 121
        self.rolling_log_count_list.append(self.logs_in_last_second)

        # Add the current number of logs seen this second to a rolling sum. 
        self.rolling_sum += self.logs_in_last_second

        # Prune rolling log counts if more than 2 minutes of logs remove the first value from the rolling sum.
        while len(self.rolling_log_count_list) > 120:
            self.rolling_sum -= self.rolling_log_count_list[0]
            del self.rolling_log_count_list[0]

        # Divide the rolling sum by the length of the counts list. Note that each entry of this list corresponds to the number of logs seen in 1 second, as an entry is filled every time the Averager polls, and the Averager polls every second. Since the size of rolling_counts_list < 121, this value will be the average number of requests over the last 2 minutes (120 seconds). 
        self.rolling_avg_val = self.rolling_sum / (len(self.rolling_log_count_list))

    """
    Check if rolling average is too large
    """
    def check_alert_threshold(self):
        global ROLLING_LOG_ALERT_THRESHOLD
        
        # DEBUG LINES
        # print(self.rolling_avg_val)
        # print(self.rolling_log_count_list)
        
        # If we are currently not in an alert mode and the rolling average has exceeded our threshold, alert and update the alert flag to signify that we have currently exceeded the threshold. 
        if ROLLING_LOG_ALERT_THRESHOLD < self.rolling_avg_val and self.alert_flag == 0:
            log_ln = "High traffic generated an alert - hits=" + str(self.rolling_sum) + ",triggered at " + str(datetime.datetime.now()) + "\n"
            print(" ------- NEW ALERT ------- ")
            print(log_ln)
            print(" ------------------------ ")
            self.write_averager_out(log_ln)
            self.alert_flag = 1

        # If we are currently in alert mode, but the rolling average is less than the alerting threshold, signal that we have recovered, and update the alert flag to signify recovery.  
        if ROLLING_LOG_ALERT_THRESHOLD > self.rolling_avg_val and self.alert_flag == 1:
            log_ln = "Recovered: high traffic alert has recovered - hits=" + str(self.rolling_sum) + ",recovered at " + str(datetime.datetime.now()) + "\n"
            print(" ------- NEW RECOVERY ALERT ------- ")
            print(log_ln)
            print(" ---------------------------------- ")
            self.write_averager_out(log_ln)
            self.alert_flag = 0

    """
    If the log_counter is in danger of overflowing and crosses the max size, reset the log counter (both the copy in the Averager, log_counter_update_per_second, and the shared log_counter in the global logIndexer which is currently being incremented by the Logger class.

    NOTE: This is an atomic operation, and therefore should not need locking. See writeup.txt for details. 
    """
    def reset_log_counters(self):
        global LOG_COUNTER_MAX_SIZE
        # If too many logs, reset LOG_COUNTER. This is atomic.
        if self.logIndexer.log_counter > LOG_COUNTER_MAX_SIZE:
            self.logIndexer.log_counter = 0
            self.log_counter_update_per_second = 0
