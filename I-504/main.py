from .common.logger import Logger
from twitter.scraper import Scraper
from .common.config_loader import *
from .types import *

logger = Logger("main")
def main():
    # Initialize the system
    init() 

def init():
    init_logger = logger.child("init")

    init_logger.info("Initializing the system")

    # Load the config
    init_logger.info("Loading the config")
    
    coreConfig = JsonConfigLoader("./I-504/config/cookie/cookie_.json").load() #TODO:　Configのローダー全体的になんとかする

    print(coreConfig.tw_cookie.ct0)
    print(coreConfig.tw_cookie.auth_token)

    scraper = Scraper(cookies="./I-504/config/cookie/cookie_.json")


    tweets = scraper.tweets_and_replies([1267154527750258689], limit=1)
    print(tweets)


