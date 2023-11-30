from .common.logger import Logger
from twitter.scraper import Scraper
from .common.config.source.tw_loader import *
from .common.config.core_loader import *
from .source.twitter.actions import *


logger = Logger("main")
def main():
    # Initialize the system
    init() 

def init():
    init_logger = logger.child("init")

    init_logger.info("Initializing the system")

    # Load the config
    init_logger.info("Loading the config")
    
    coreConfig = YamlConfigLoader("./I-504/config/config.yml").load() 

    init_logger.succ("Loaded Core Config")

    twitterSourceConfig = TwitterSourceConfigLoader("./I-504/config/source/twitter.yml").load()

    twitterActions = TwitterActions(tw_cookie=twitterSourceConfig.auth_cookie, update_limit=twitterSourceConfig.update_limit, target_user_rest_id=1267154527750258689)

    tweets = twitterActions.get_tweets()

    print(type(tweets))
    print(len(tweets))

    for tweet in tweets:
        print(tweet.entry_id + ": " + tweet.full_text)
