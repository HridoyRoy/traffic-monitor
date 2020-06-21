from scapy.all import *
from scapy.layers.http import HTTPRequest # import HTTP packet
from .globals import LOG_FILENAME
from .globals import LOG_FILESIZE
# from scapy import *
from colorama import init, Fore

"""
The Logger class uses scapy to MITM requests and log them to log files. 
"""
class Logger:

    def __init__(self, logIndexer):
        # log indexer to keep track of logging info and share between threads and classes. 
        self.logIndexer = logIndexer

        # a count for the line number of the currently written log. 
        self.log_line_write = 0

    # NOTE: MAKING THE SAVED DIR MANUALLY FOR NOW. Writing to files with append (a+) creates a file if none exists, but the dir needs to be made manually. Else python throws an error.
    # NOTE: TODO: Log file being reset makes it difficult to read old log file. We need to fix this.

    def process_packet(self, packet):
        """
        This function is executed whenever a packet is sniffed
        """
        global LOG_FILENAME
        global LOG_FILESIZE

        # Check if we are writing to a different log file than the one statistician is reading.
        log_filename = LOG_FILENAME + str(self.logIndexer.log_filenum) + ".txt"
        if self.logIndexer.log_filenum < self.logIndexer.log_filenum_switch_page:
            log_filename = LOG_FILENAME + str(self.logIndexer.log_filenum_switch_page) + ".txt"

        # Open the logfile and write relevant info from packet to log. 
        logfile = open(log_filename, 'a+')
        # Make sure the packet is an HTTP request. 
        if packet.haslayer(HTTPRequest):
            # Get URL from the packet
            url = packet[HTTPRequest].Host.decode() + packet[HTTPRequest].Path.decode()
            # Get the url section to write to log
            url_section = self.get_section_from_url(url)
            
            # get source IP. 
            # NOTE: I included this in the logs so we could distinguish between inbound and outbound logs by comparing this IP to our local IP, but did not get to implement that functionality. 
            ip = packet[IP].src

            # write logs to logfile
            logline = url_section + ":" + ip + "\n"
            logfile.write(logline)
            self.log_line_write += 1

            # add 1 to log counter
            self.logIndexer.log_counter += 1

            # check if we need a new logfile
            if self.log_line_write >= LOG_FILESIZE:
                self.reset_logfile()

        if not logfile.closed:
            logfile.close()

    """
    scapy handler for socket stuff that MITMs HTTP requests and forwards them for processing.
    """
    def sniff_reqs(self):
        # sniff is the scapy function. Without an iface parameter, it will sniff on all interfaces, on port 80 (http port): https://scapy.readthedocs.io/en/latest/
        sniff(filter="port 80", prn=self.process_packet, store=False)

    """
    Gets url section from a url. A url section is everything before the second slash of the url. For example, https://www.google.com/pages/hello corresponds to the section https://www.google.com/pages. 
    """
    def get_section_from_url(self, url):
        url_parts = url.split("/")
        section = None
        url_parts_len = len(url_parts)
        if (url_parts_len > 2) and (url_parts[0] == "http:" or url_parts[0] == "https:") and (url_parts[1] == ""):
            # http or https://blah splits to [http, '', other stuff]. In this case, we want to split up until the 4th slash.
            if url_parts_len >= 4:
                section = "/".join(url_parts[:4])
            else:
                # Just join everything, the entire url is just a section. 
                section = "/".join(url_parts)
        elif url_parts_len > 2:
            # No http:// in the url. In this case we just include everything before the 2nd slash. 
            section = "/".join(url_parts[:2])
        else:
            # Less than 2 slashes in the entire url. We just join everything.
            section = "/".join(url_parts)
        return section
        
    # Create new log file and set all global values appropriately
    def reset_logfile(self):
        global LOG_FILENUM_SWITCH_PAGE
        # Change global values so process_packet will create and write to new logfile
        # LOG_FILENUM_SWITCH_PAGE = LOG_FILENUM at this point
            # change LOG_FILENUM_SWITCH_PAGE to be 1 greater than LOG_FILENUM. NOTE that when reading the logs to aggregate stats, when the last line of the old file is read, LOG_FILENUM will be incremented. When writing, if LOG_FILENUM_SWITCH_PAGE > LOG_FILENUM, write to LOG_FILENUM_SWITCH_PAGE
        self.logIndexer.log_filenum_switch_page += 1
        # reset LOG_LINE_WRITE
        self.log_line_write = 0
