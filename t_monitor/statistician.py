import json
import threading
import os
from .globals import LOG_FILENAME
from .globals import LOG_FILESIZE

"""
The Statistician class reads from the log files every 10 seconds and aggregates logs into various statistics for display. 
"""
class Statistician:

    def __init__(self, logIndexer):

        # log indexer to keep track of logging info and share between threads and classes.
        self.logIndexer = logIndexer
        
        # This data structure keeps track of the section with the most hits. 
        self.stats_dict = {"most_hits_section" : ""}
        
        # This data structure has the number of hits for different sections that were seen by the logs
        self.section_hits = {}

        # This data structure holds num hits for section --> a list of sections. 
        self.reverse_section_hits = {}

        # This is the line that the Statistician has read in the current log file. 
        self.log_line_read = 0

    """
    Helper function to reset instance attributes for Statistician. 
    """
    def reset(self):
        self.stats_dict["most_hits_section"] = ""
        self.section_hits = {}
        self.reverse_section_hits = {}
        self.log_line_read = 0

    '''
    Open log file and process from line saved_line_num and filename, along with other stats collected in stats file. Update saved_line_num and if saved_line_num is too large, open new file and change file name.

    This function assumes a statistics file is already initialized, so it is contingent on init_statistics being run..
    '''
    def aggregate_statistics(self):
        threading.Timer(10.0, self.aggregate_statistics).start()
        global LOG_FILESIZE

        # NOTE: TODO: We should utilize the saved stats in './saved/stats.txt' so section_hits and reverse_section_hits don't get too large. 

        # check if we need to read next log file
        if self.log_line_read >= LOG_FILESIZE:
           self.update_read_logfile()

        # create logfile
        log_filename = self.create_logfile_name()
       
       # Check if logs have come in yet. If not, do not proceed further.
        if not os.path.isfile(log_filename):
            print(" ------ STATISTICS GENERATED ------ ")
            print("website section with most hits: NONE")
            print("number of different pages hit: 0")
            print("total number of requests seen: 0")
            print("------------------------------------")
            return
        
        # Add logs to stats
        self.assimilate_logs_into_stats(log_filename)

        # update most_hits
        self.update_most_hits_section()

        # redisplay alert threshold crossing history
        print("----- PAST LOG ALERT LIST ----- ")
        self.print_alert_history()

        print("--------------------------------")

        # TODO: Displaying full url hits here -- need to display and return stats only for sections, not full urls
        print(" ------ STATISTICS GENERATED ------ ")
        print("website section with most hits: " + str(self.stats_dict["most_hits_section"]))
        print("number of different pages hit: " + str(len(self.section_hits)))
        print("total number of requests seen: " + str(sum(self.section_hits.values())))
        print("------------------------------------")

        # write to stats
        # TODO: We are saving the stats dicts, but not using the saved values anywhere. Tbd if we ever want to load the stats from memory in case the program crashes, or if we just want to begin again from scratch
        with open("./saved/stats.txt", "w") as stats_out:
            json.dump([self.stats_dict, self.section_hits, self.reverse_section_hits], stats_out)

    """
    A bunch of print statements
    """
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
    
    """
    Create logfile name from the logIndexer and the LOG_FILENAME.
    """
    def create_logfile_name(self):
        global LOG_FILENAME
        return LOG_FILENAME + str(self.logIndexer.log_filenum) + ".txt"

    """
    Update most hits. 
    """
    def update_most_hits_section(self):
        # NOTE: We are using .get because we cannot get None's as return values for any of these statements. 
        self.stats_dict["most_hits_section"] = self.reverse_section_hits.get(max(list(self.reverse_section_hits)))[0]

    """
    Assimilate logs into stats
    """
    def assimilate_logs_into_stats(self, log_filename):
        with open(log_filename) as log_file:
            for i, line in enumerate(log_file):
                # Only read lines starting at the last line read by the Statistician.
                if i == self.log_line_read:
                    log_vals = line.split(":")
                    url = log_vals[0]
                    # Check if the url section has been seen in the section hits
                    if url in self.section_hits:
                        # If the url has been seen, add 1 to the section hits and move the url to the next key in reverse_section_hits. 
                        num_hits = self.section_hits[url]
                        self.reverse_section_hits[num_hits].remove(url)
                        if self.reverse_section_hits.get(num_hits + 1):
                            self.reverse_section_hits[num_hits + 1].append(url)
                        else:
                            self.reverse_section_hits[num_hits + 1] = [url]
                        self.section_hits[url] += 1
                    else:
                        # In this case, initialize the section in section_hits and update reverse_section_hits[1] to show that the current url section has been seen once. 
                        self.section_hits[url] = 1
                        if self.reverse_section_hits.get(1):
                            self.reverse_section_hits[1] += [url]
                        else:
                            self.reverse_section_hits[1] = [url]
                    #  update log read counter
                    self.log_line_read += 1

    """
    Initialize statistics file and saved folder. 
    """
    def init_statistics(self):
        stats_list = [self.stats_dict, self.section_hits, self.reverse_section_hits]
        if not os.path.exists('./saved'):
            os.makedirs('./saved')
        if os.path.exists("./saved/stats.txt"):
            os.remove("./saved/stats.txt")
        with open("./saved/stats.txt", "w") as stats:
            json.dump(stats_list, stats, indent=2)
        return

    """
    Update logIndexer to reflect whether or not the statistician has read the current logfile.
    """
    def update_read_logfile(self):
        # Check if the log writer has switched to the next page, and if so, update read.
        if self.logIndexer.log_filenum_switch_page > self.logIndexer.log_filenum:
            self.log_line_read = 0
            self.logIndexer.log_filenum += 1
