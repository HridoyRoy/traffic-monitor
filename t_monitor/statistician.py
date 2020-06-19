import json
import threading
import os
from .globals import LOG_FILENUM
from .globals import LOG_FILENAME
from .globals import LOG_FILESIZE
from .globals import LOG_FILENUM_SWITCH_PAGE
from .globals import STATS_FILE

class Statistician:
    init_stats = {"most_hits_section" : "", "some_stat" : 5}
    init_section_hits = {}
    init_reverse_section_hits = {}
    log_line_read = 0


    def __init__(self, logIndexer):
        self.logIndexer = logIndexer

    '''
    Open log file and process from line saved_line_num and filename, along with other stats collected in stats file. Update saved_line_num and if saved_line_num is too large, open new file and change file name.

    This function assumes a statistics file is already initialized, so it is contingent on init_statistics being run..
    '''
    def aggregate_statistics(self):
        threading.Timer(10.0, self.aggregate_statistics).start()
        global LOG_FILENUM
        global LOG_FILENAME
        global LOG_FILESIZE

        # open stats TODO: (come back to this later, as for now you can just store in mem)

        print("aggregating stats but not past the first return val")

        # check if we need to read next log file
        if Statistician.log_line_read >= LOG_FILESIZE:
           self.update_read_logfile()

        # open log
        log_filename = LOG_FILENAME + str(self.logIndexer.log_filenum) + ".txt"
        if not os.path.isfile(log_filename):
            # just wait
            return
        print("aggregating stats")
        with open(log_filename) as log_file:
            for i, line in enumerate(log_file):
                print("values are:" )
                print(Statistician.init_section_hits)
                print(Statistician.init_reverse_section_hits)
                if i == Statistician.log_line_read:
                    print("i is to be read: " + str(i))
                    # read and update read counter, and add to appropriate log locations
                    log_vals = line.split(":")
                    url = log_vals[0]
                    if url in Statistician.init_section_hits:
                        num_hits = Statistician.init_section_hits[url]
                        Statistician.init_reverse_section_hits[num_hits].remove(url)
                        if Statistician.init_reverse_section_hits.get(num_hits + 1):
                            Statistician.init_reverse_section_hits[num_hits + 1].append(url)
                        else:
                            Statistician.init_reverse_section_hits[num_hits + 1] = [url]
                        Statistician.init_section_hits[url] += 1
                    else:
                        Statistician.init_section_hits[url] = 1
                        if Statistician.init_reverse_section_hits.get(1):
                            Statistician.init_reverse_section_hits[1] += [url]
                        else:
                            Statistician.init_reverse_section_hits[1] = [url]
                    #  update read counter
                    Statistician.log_line_read += 1
        # must use .get, not [] because don't want a keyError if this value doesn't exist. We want None.
        # TODO: All in 1 line. Break up for readability?
        Statistician.init_stats["most_hits_section"] = Statistician.init_reverse_section_hits.get(max(list(Statistician.init_reverse_section_hits)))[0]

        # display stats

        # TODO: Displaying full url hits here -- need to display and return stats only for sections, not full urls
        print("most hits were for the following URL")
        print(Statistician.init_stats["most_hits_section"])

        # write to stats
        # TODO: We are saving the stats dicts, but not using the saved values anywhere. Tbd if we ever want to load the stats from memory in case the program crashes, or if we just want to begin again from scratch
        with open("./saved/stats.txt", "w") as stats_out:
            json.dump([Statistician.init_stats, Statistician.init_section_hits, Statistician.init_reverse_section_hits], stats_out)

    def init_statistics(self):
        stats_list = [Statistician.init_stats, Statistician.init_section_hits, Statistician.init_reverse_section_hits]
        if not os.path.exists('./saved'):
            os.makedirs('./saved')
        if os.path.exists("./saved/stats.txt"):
            os.remove("./saved/stats.txt")
        with open("./saved/stats.txt", "w") as stats:
            json.dump(stats_list, stats, indent=2)
        return

    # Read the next logfile
    def update_read_logfile(self):
        global LOG_FILENUM
        global LOG_FILENUM_SWITCH_PAGE

        print("log filenum in statistician is: " + str(self.logIndexer.log_filenum))
        print("log filenum switch page in statistician is: " + str(self.logIndexer.log_filenum_switch_page))

        # Check if the log writer has switched to the next page, and if so, update read.
        if self.logIndexer.log_filenum_switch_page > self.logIndexer.log_filenum:
            Statistician.log_line_read = 0
            self.logIndexer.log_filenum += 1
