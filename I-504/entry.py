from .types import *
from .interface.system import *
from .common.config_loader import *
from .common.logger import Logger
from .main import main

def entry():
    entry_logger = Logger("entry")

    main()
