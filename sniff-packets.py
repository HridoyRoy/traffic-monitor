import threading
import os
import json
from scapy.all import *
from scapy.layers.http import HTTPRequest # import HTTP packet
# from scapy import *
from colorama import init, Fore
# initialize colorama
init()
# define colors
GREEN = Fore.GREEN
RED   = Fore.RED
RESET = Fore.RESET

# NOTE: MAKING THE SAVED DIR MANUALLY FOR NOW. Writing to files with append (a+) creates a file if none exists, but the dir needs to be made manually. Else python throws an error. 
# NOTE: TODO: Log file being reset makes it difficult to read old log file. We need to fix this. 
LOG_FILENUM = 0
LOG_FILENAME = "./saved/log"
LOG_FILENUM_SWITCH_PAGE = 0
LOG_LINE_READ = 0
LOG_LINE_WRITE = 0
STATS_FILE = "./saved/stats.txt"
INIT_STATS = {"most_hits_section" : "", "some_stat" : 5}
INIT_SECTION_HITS = {}
INIT_REVERSE_SECTION_HITS = {}

# Changing this to 10 for testing. I think 500 is decent irl
LOG_FILESIZE = 10

def sniff_packets(iface=None):
    """
    Sniff 80 port packets with `iface`, if None (default), then the
    Scapy's default interface is used
    """
    if iface:
        # port 80 for http (generally)
        # `process_packet` is the callback
        sniff(filter="port 80", prn=process_packet, iface=conf.iface, store=False)
    else:
         # sniff with default interface
        sniff(filter="port 80", prn=process_packet, store=False)

def process_packet(packet):
    """
    This function is executed whenever a packet is sniffed
    """
    global LOG_LINE_WRITE
    global LOG_FILENAME
    global LOG_FILENUM
    global LOG_FILENUM_SWITCH_PAGE
    global LOG_FILESIZE

    # check if we need to open a new log file
    log_filename = LOG_FILENAME + str(LOG_FILENUM) + ".txt"
    if LOG_FILENUM < LOG_FILENUM_SWITCH_PAGE:
        log_filename = LOG_FILENAME + str(LOG_FILENUM_SWITCH_PAGE) + ".txt"
    
    logfile = open(log_filename, 'a+')
    if packet.haslayer(HTTPRequest):
        # if this packet is an HTTP Request
        # get the requested URL
        url = packet[HTTPRequest].Host.decode() + packet[HTTPRequest].Path.decode()
        # get the requester's IP Address
        ip = packet[IP].src
        # get the request method
        method = packet[HTTPRequest].Method.decode()
        print(f"\n{GREEN}[+] {ip} Requested {url} with {method}{RESET}")
        
        # write logs to logfile
        logline = url + ":" + ip + "\n"
        logfile.write(logline)
        LOG_LINE_WRITE += 1

        # check if we need a new logfile
        if LOG_LINE_WRITE >= LOG_FILESIZE:
            reset_logfile()

        if show_raw and packet.haslayer(Raw) and method == "POST":
            # if show_raw flag is enabled, has raw data, and the requested method is "POST"
            # then show raw
            print(f"\n{RED}[*] Some useful Raw data: {packet[Raw].load}{RESET}")
    if not logfile.closed:
        logfile.close()

# Create new log file and set all global values appropriately
def reset_logfile():
    global LOG_FILENUM_SWITCH_PAGE
    global LOG_LINE_WRITE
    # Change global values so process_packet will create and write to new logfile
    # LOG_FILENUM_SWITCH_PAGE = LOG_FILENUM at this point
        # change LOG_FILENUM_SWITCH_PAGE to be 1 greater than LOG_FILENUM. NOTE that when reading the logs to aggregate stats, when the last line of the old file is read, LOG_FILENUM will be incremented. When writing, if LOG_FILENUM_SWITCH_PAGE > LOG_FILENUM, write to LOG_FILENUM_SWITCH_PAGE
    LOG_FILENUM_SWITCH_PAGE += 1

    # reset LOG_LINE_WRITE
    LOG_LINE_WRITE = 0

# Read the next logfile
def update_read_logfile():
    global LOG_LINE_READ
    global LOG_FILENUM
    global LOG_FILENUM_SWITCH_PAGE

    # Check if the log writer has switched to the next page, and if so, update read. 
    if LOG_FILENUM_SWITCH_PAGE > LOG_FILENUM:
        LOG_LINE_READ = 0
        LOG_FILENUM += 1

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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="HTTP Packet Sniffer, this is useful when you're a man in the middle." \
                                                 + "It is suggested that you run arp spoof before you use this script, otherwise it'll sniff your personal packets")
    parser.add_argument("-i", "--iface", help="Interface to use, default is scapy's default interface")
    parser.add_argument("--show-raw", dest="show_raw", action="store_true", help="Whether to print POST raw data, such as passwords, search queries, etc.")
    # parse arguments
    args = parser.parse_args()
    iface = args.iface
    show_raw = args.show_raw
    init_statistics()
    aggregate_statistics()
    sniff_packets(iface)
