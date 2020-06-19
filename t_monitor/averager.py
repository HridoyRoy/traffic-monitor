from .globals import LOG_COUNTER
from .globals import ROLLING_LOG_ALERT_THRESHOLD
from .globals import LOG_COUNTER_MAX_SIZE
import threading

# List of max size 121 which has the number of logs seen in the last 120 seconds
ROLLING_LOG_COUNT_LIST = []


# The rolling sum for current average
ROLLING_SUM = 0

# This keeps track of the number of logs seen by the averager every second
LOG_COUNTER_UPDATE_PER_SECOND = 0


def rolling_avg():
    threading.Timer(1.0, rolling_avg).start()
    global LOG_COUNTER_UPDATE_PER_SECOND
    global LOG_COUNTER
    global ROLLING_LOG_COUNT_LIST
    global LOG_COUNTER_MAX_SIZE
    global ROLLING_SUM

    print("log counter and per second counter are:" + str(LOG_COUNTER) + " " + str(LOG_COUNTER_UPDATE_PER_SECOND))

    logs_in_last_second = LOG_COUNTER - LOG_COUNTER_UPDATE_PER_SECOND
    LOG_COUNTER_UPDATE_PER_SECOND = LOG_COUNTER

    ROLLING_LOG_COUNT_LIST.append(logs_in_last_second)
    ROLLING_SUM += logs_in_last_second

    rolling_avg_val = ROLLING_SUM / (len(ROLLING_LOG_COUNT_LIST))
    print("rolling average value is: " + str(rolling_avg_val))

    if ROLLING_LOG_ALERT_THRESHOLD < rolling_avg_val:
        print("OH NO!!! CROSSED THE LINE BUDDY BOI")

    if len(ROLLING_LOG_COUNT_LIST) > 120:
        ROLLING_LOG_COUNT_LIST = ROLLING_LOG_COUNT_LIST[-120:]

    # If too many logs, reset LOG_COUNTER. This is atomic.
    if LOG_COUNTER > LOG_COUNTER_MAX_SIZE:
        print("MAX SIZE HAS BEEN REACHED: RESETTING")
        LOG_COUNTER = 0
        LOG_COUNTER_UPDATE_PER_SECOND = 0
