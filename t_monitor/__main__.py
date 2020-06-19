from .statistician import init_statistics
from .statistician import aggregate_statistics
from .logger import sniff_packets
from .averager import rolling_avg
from .globals import initialize
import argparse

parser = argparse.ArgumentParser(description="HTTP Packet Sniffer, this is useful when you're a man in the middle." \
                                                 + "It is suggested that you run arp spoof before you use this script, otherwise it'll sniff your personal packets")
parser.add_argument("-i", "--iface", help="Interface to use, default is scapy's default interface")
parser.add_argument("--show-raw", dest="show_raw", action="store_true", help="Whether to print POST raw data, such as passwords, search queries, etc.")
# parse arguments
args = parser.parse_args()
iface = args.iface
show_raw = args.show_raw

initialize()
init_statistics()
rolling_avg()
aggregate_statistics()
sniff_packets(iface, show_raw)
