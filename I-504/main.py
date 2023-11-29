from .common.logger import Logger
from twitter.scraper import Scraper
from .common.config_loader import *
from .common.config.mk_loader import *


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

    init_logger.info("CoreConfig: Loaded")

    # TEST
    from .common.dest.misskey.actions import StubMisskeyActions

    misskeyActions = StubMisskeyActions(coreConfig)

    from .debug.mkdriver import mk_post
    
    mk_post(misskeyActions)

    mkconfig = MisskeyConfigLoader("./I-504/config/dest/misskey.yml").load()

    init_logger.info("MisskeyConfig: Loaded")
    init_logger.debug("MisskeyConfig: {}".format(mkconfig))



