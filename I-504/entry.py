from .interface.system import *
from .common.config_loader import *
from .common.logger import Logger
#DEBUG
from .debug.get_tweet_driver import get_tweets

def entry():
    entry_logger = Logger("entry")

    get_tweets()
