from scapy.all import *
from scapy.layers.http import HTTPRequest # import HTTP packet
from .globals import LOG_COUNTER
from .globals import LOG_FILENUM
from .globals import LOG_FILENAME
from .globals import LOG_FILENUM_SWITCH_PAGE
from .globals import LOG_FILESIZE
# from scapy import *
from colorama import init, Fore

class Logger:

    log_line_write = 0
    show_raw = False

    def __init__(self, logIndexer):
        self.logIndexer = logIndexer


    # NOTE: MAKING THE SAVED DIR MANUALLY FOR NOW. Writing to files with append (a+) creates a file if none exists, but the dir needs to be made manually. Else python throws an error.
    # NOTE: TODO: Log file being reset makes it difficult to read old log file. We need to fix this.

    def process_packet(self, packet):
        """
        This function is executed whenever a packet is sniffed
        """
        global LOG_FILENAME
        global LOG_FILENUM
        global LOG_FILENUM_SWITCH_PAGE
        global LOG_FILESIZE
        global LOG_COUNTER

        # check if we need to open a new log file
        log_filename = LOG_FILENAME + str(self.logIndexer.log_filenum) + ".txt"
        if self.logIndexer.log_filenum < self.logIndexer.log_filenum_switch_page:
            log_filename = LOG_FILENAME + str(self.logIndexer.log_filenum_switch_page) + ".txt"

        logfile = open(log_filename, 'a+')
        if packet.haslayer(HTTPRequest):
            # if this packet is an HTTP Request
            # get the requested URL
            url = packet[HTTPRequest].Host.decode() + packet[HTTPRequest].Path.decode()
            # get the requester's IP Address
            ip = packet[IP].src
            # get the request method
            method = packet[HTTPRequest].Method.decode()
            print(str(ip) + " requested " + str(url))

            # write logs to logfile
            logline = url + ":" + ip + "\n"
            logfile.write(logline)
            Logger.log_line_write += 1

            # add 1 to log counter
            self.logIndexer.log_counter += 1

            # check if we need a new logfile
            if Logger.log_line_write >= LOG_FILESIZE:
                self.reset_logfile()

            if Logger.show_raw and packet.haslayer(Raw) and method == "POST":
                # if show_raw flag is enabled, has raw data, and the requested method is "POST"
                # then show raw
                print("Some useful Raw data: " + str(packet[Raw].load))
        if not logfile.closed:
            logfile.close()
        print("log counter is: " + str(self.logIndexer.log_counter))

    def sniff_packets(self, iface=None, show_raw_var=False):
        """
        Sniff 80 port packets with `iface`, if None (default), then the
        Scapy's default interface is used
    """
        if show_raw_var:
            Logger.show_raw = True
        if iface:
            # port 80 for http (generally)
            # `process_packet` is the callback
            sniff(filter="port 80", prn=self.process_packet, iface=conf.iface, store=False)
        else:
            # sniff with default interface
            sniff(filter="port 80", prn=self.process_packet, store=False)

    # Create new log file and set all global values appropriately
    def reset_logfile(self):
        global LOG_FILENUM_SWITCH_PAGE
        # Change global values so process_packet will create and write to new logfile
        # LOG_FILENUM_SWITCH_PAGE = LOG_FILENUM at this point
            # change LOG_FILENUM_SWITCH_PAGE to be 1 greater than LOG_FILENUM. NOTE that when reading the logs to aggregate stats, when the last line of the old file is read, LOG_FILENUM will be incremented. When writing, if LOG_FILENUM_SWITCH_PAGE > LOG_FILENUM, write to LOG_FILENUM_SWITCH_PAGE
        self.logIndexer.log_filenum_switch_page += 1
        print("log_filenum_switch_page is: " + str(self.logIndexer.log_filenum_switch_page))
        # reset LOG_LINE_WRITE
        Logger.log_line_write = 0
