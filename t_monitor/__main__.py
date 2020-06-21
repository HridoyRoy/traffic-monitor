from .statistician import Statistician
from .logger import Logger
from .averager import Averager
import argparse
from .globals import LogIndexer

logIndexer = LogIndexer()

statistician = Statistician(logIndexer)
logger = Logger(logIndexer)
averager = Averager(logIndexer)

statistician.init_statistics()
averager.rolling_avg()
statistician.aggregate_statistics()
logger.sniff_reqs()
