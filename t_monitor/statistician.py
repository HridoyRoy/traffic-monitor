import json
import threading
import os
from .globals import LOG_FILENUM
from .globals import LOG_FILENAME
from .globals import LOG_FILESIZE
from .globals import LOG_FILENUM_SWITCH_PAGE
from .globals import STATS_FILE

class Statistician:

    def __init__(self, logIndexer):
        self.logIndexer = logIndexer
        self.init_stats = {"most_hits_section" : "", "some_stat" : 5}
        self.init_section_hits = {}
        self.init_reverse_section_hits = {}
        self.log_line_read = 0


    def reset(self):
        self.init_stats["most_hits_section"] = ""
        self.init_stats["some_stat"] = 5
        self.init_section_hits = {}
        self.init_reverse_section_hits = {}
        self.log_line_read = 0

    '''
    Open log file and process from line saved_line_num and filename, along with other stats collected in stats file. Update saved_line_num and if saved_line_num is too large, open new file and change file name.

    This function assumes a statistics file is already initialized, so it is contingent on init_statistics being run..
    '''
    def aggregate_statistics(self):
        threading.Timer(10.0, self.aggregate_statistics).start()
        global LOG_FILESIZE

        # should we use stats file that we sdaved? NOTE: TODO:

        # print("aggregating stats but not past the first return val")

        # check if we need to read next log file
        if self.log_line_read >= LOG_FILESIZE:
           self.update_read_logfile()

        # create logfile
        # open log
        log_filename = self.create_logfile_name()
        
        if not os.path.isfile(log_filename):
            # just wait
            return
        
        # print("aggregating stats")
        self.assimilate_logs_into_stats(log_filename)

        # update most_hits
        self.update_most_hits_section()

        # redisplay alert threshold crossing history
        print("----- PAST LOG ALERT LIST ----- ")
        self.print_alert_history()

        print("--------------------------------")

        # TODO: Displaying full url hits here -- need to display and return stats only for sections, not full urls
        print(" ------ STATISTICS GENERATED ------ ")
        print("website section with most hits: " + str(self.init_stats["most_hits_section"]))
        print("------------------------------------")

        # write to stats
        # TODO: We are saving the stats dicts, but not using the saved values anywhere. Tbd if we ever want to load the stats from memory in case the program crashes, or if we just want to begin again from scratch
        with open("./saved/stats.txt", "w") as stats_out:
            json.dump([self.init_stats, self.init_section_hits, self.init_reverse_section_hits], stats_out)

    def print_alert_history(self):
        last_line = None
        if not os.path.isfile("./saved/alerts.txt"):
            return
        with open("./saved/alerts.txt", "r") as alerts:
            for last_line in alerts:
                print(last_line)
            if not last_line.startswith("Recovered"):
                print("--------------------------------")
                print("Last alert currently unrecovered. See alert history above for more details.")
            
    def create_logfile_name(self):
        global LOG_FILENAME
        return LOG_FILENAME + str(self.logIndexer.log_filenum) + ".txt"

    def update_most_hits_section(self):
        # print("hi")
        # get because we cannot get None's as return values
        # print("init_reverse_section hits are: ", self.init_reverse_section_hits)
        self.init_stats["most_hits_section"] = self.init_reverse_section_hits.get(max(list(self.init_reverse_section_hits)))[0]

    def assimilate_logs_into_stats(self, log_filename):
        # print("hiii")
        with open(log_filename) as log_file:
            for i, line in enumerate(log_file):
                # print("values are:" )
                # print(self.init_section_hits)
                # print(self.init_reverse_section_hits)
                if i == self.log_line_read:
                    # print("i is to be read: " + str(i))
                    # read and update read counter, and add to appropriate log locations
                    log_vals = line.split(":")
                    url = log_vals[0]
                    if url in self.init_section_hits:
                        num_hits = self.init_section_hits[url]
                        self.init_reverse_section_hits[num_hits].remove(url)
                        if self.init_reverse_section_hits.get(num_hits + 1):
                            self.init_reverse_section_hits[num_hits + 1].append(url)
                        else:
                            self.init_reverse_section_hits[num_hits + 1] = [url]
                        self.init_section_hits[url] += 1
                    else:
                        self.init_section_hits[url] = 1
                        if self.init_reverse_section_hits.get(1):
                            self.init_reverse_section_hits[1] += [url]
                        else:
                            self.init_reverse_section_hits[1] = [url]
                    #  update read counter
                    self.log_line_read += 1

    def init_statistics(self):
        stats_list = [self.init_stats, self.init_section_hits, self.init_reverse_section_hits]
        if not os.path.exists('./saved'):
            os.makedirs('./saved')
        if os.path.exists("./saved/stats.txt"):
            os.remove("./saved/stats.txt")
        with open("./saved/stats.txt", "w") as stats:
            json.dump(stats_list, stats, indent=2)
        return

    # Read the next logfile
    def update_read_logfile(self):
        # print("log filenum in statistician is: " + str(self.logIndexer.log_filenum))
        # print("log filenum switch page in statistician is: " + str(self.logIndexer.log_filenum_switch_page))

        # Check if the log writer has switched to the next page, and if so, update read.
        if self.logIndexer.log_filenum_switch_page > self.logIndexer.log_filenum:
            self.log_line_read = 0
            self.logIndexer.log_filenum += 1
