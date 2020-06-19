import json
import threading
import os
from .logger import LOG_FILENUM
from .logger import LOG_FILENAME
from .logger import LOG_FILESIZE
from .logger import LOG_FILENUM_SWITCH_PAGE

LOG_LINE_READ = 0
STATS_FILE = "./saved/stats.txt"
INIT_STATS = {"most_hits_section" : "", "some_stat" : 5}
INIT_SECTION_HITS = {}
INIT_REVERSE_SECTION_HITS = {}

'''
Open log file and process from line saved_line_num and filename, along with other stats collected in stats file. Update saved_line_num and if saved_line_num is too large, open new file and change file name.

This function assumes a statistics file is already initialized, so it is contingent on init_statistics being run..
'''
def aggregate_statistics():
    threading.Timer(10.0, aggregate_statistics).start()
    global LOG_FILENUM
    global LOG_FILENAME
    global LOG_LINE_READ
    global INIT_STATS
    global INIT_SECTION_HITS
    global INIT_REVERSE_SECTION_HITS
    global LOG_FILESIZE

    # open stats TODO: (come back to this later, as for now you can just store in mem)

    print("aggregating stats but not past the first return val")

    # check if we need to read next log file
    if LOG_LINE_READ >= LOG_FILESIZE:
       update_read_logfile()

    # open log
    log_filename = LOG_FILENAME + str(LOG_FILENUM) + ".txt"
    if not os.path.isfile(log_filename):
        # just wait
        return
    print("aggregating stats")
    with open(log_filename) as log_file:
        for i, line in enumerate(log_file):
            print("values are:" )
            print(INIT_SECTION_HITS)
            print(INIT_REVERSE_SECTION_HITS)
            if i == LOG_LINE_READ:
                print("i is to be read: " + str(i))
                # read and update read counter, and add to appropriate log locations
                log_vals = line.split(":")
                url = log_vals[0]
                if url in INIT_SECTION_HITS:
                    num_hits = INIT_SECTION_HITS[url]
                    INIT_REVERSE_SECTION_HITS[num_hits].remove(url)
                    if INIT_REVERSE_SECTION_HITS.get(num_hits + 1):
                        INIT_REVERSE_SECTION_HITS[num_hits + 1].append(url)
                    else:
                        INIT_REVERSE_SECTION_HITS[num_hits + 1] = [url]
                    INIT_SECTION_HITS[url] += 1
                else:
                    INIT_SECTION_HITS[url] = 1
                    if INIT_REVERSE_SECTION_HITS.get(1):
                        INIT_REVERSE_SECTION_HITS[1] += [url]
                    else:
                        INIT_REVERSE_SECTION_HITS[1] = [url]
                #  update read counter
                LOG_LINE_READ += 1
    # must use .get, not [] because don't want a keyError if this value doesn't exist. We want None.
    # TODO: All in 1 line. Break up for readability?
    INIT_STATS["most_hits_section"] = INIT_REVERSE_SECTION_HITS.get(max(list(INIT_REVERSE_SECTION_HITS)))[0]

    # display stats

    # TODO: Displaying full url hits here -- need to display and return stats only for sections, not full urls
    print("most hits were for the following URL")
    print(INIT_STATS["most_hits_section"])

    # write to stats
    # TODO: We are saving the stats dicts, but not using the saved values anywhere. Tbd if we ever want to load the stats from memory in case the program crashes, or if we just want to begin again from scratch
    with open("./saved/stats.txt", "w") as stats_out:
        json.dump([INIT_STATS, INIT_SECTION_HITS, INIT_REVERSE_SECTION_HITS], stats_out)

def init_statistics():
    global INIT_STATS
    global INIT_SECTION_HITS
    global INIT_REVERSE_SECTION_HITS

    stats_list = [INIT_STATS, INIT_SECTION_HITS, INIT_REVERSE_SECTION_HITS]
    if not os.path.exists('./saved'):
        os.makedirs('./saved')
    if os.path.exists("./saved/stats.txt"):
        os.remove("./saved/stats.txt")
    with open("./saved/stats.txt", "w") as stats:
        json.dump(stats_list, stats, indent=2)
    return

# Read the next logfile
def update_read_logfile():
    global LOG_LINE_READ
    global LOG_FILENUM
    global LOG_FILENUM_SWITCH_PAGE

    # Check if the log writer has switched to the next page, and if so, update read.
    if LOG_FILENUM_SWITCH_PAGE > LOG_FILENUM:
        LOG_LINE_READ = 0
        LOG_FILENUM += 1
