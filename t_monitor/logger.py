from scapy.all import *
from scapy.layers.http import HTTPRequest # import HTTP packet
from .globals import LOG_COUNTER
from .globals import LOG_FILENUM
from .globals import LOG_FILENAME
from .globals import LOG_FILENUM_SWITCH_PAGE
from .globals import LOG_LINE_WRITE
from .globals import SHOW_RAW
from .globals import LOG_FILESIZE
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

def process_packet(packet):
    """
    This function is executed whenever a packet is sniffed
    """
    global LOG_LINE_WRITE
    global LOG_FILENAME
    global LOG_FILENUM
    global LOG_FILENUM_SWITCH_PAGE
    global LOG_FILESIZE
    global LOG_COUNTER
    global SHOW_RAW

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

        # add 1 to log counter
        LOG_COUNTER += 1

        # check if we need a new logfile
        if LOG_LINE_WRITE >= LOG_FILESIZE:
            reset_logfile()

        if SHOW_RAW and packet.haslayer(Raw) and method == "POST":
            # if show_raw flag is enabled, has raw data, and the requested method is "POST"
            # then show raw
            print(f"\n{RED}[*] Some useful Raw data: {packet[Raw].load}{RESET}")
    if not logfile.closed:
        logfile.close()
    print("log counter is: " + str(LOG_COUNTER))

def sniff_packets(iface=None, show_raw=False):
    """
    Sniff 80 port packets with `iface`, if None (default), then the
    Scapy's default interface is used
    """
    global SHOW_RAW

    if show_raw:
        SHOW_RAW = True
    if iface:
        # port 80 for http (generally)
        # `process_packet` is the callback
        sniff(filter="port 80", prn=process_packet, iface=conf.iface, store=False)
    else:
         # sniff with default interface
        sniff(filter="port 80", prn=process_packet, store=False)

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
