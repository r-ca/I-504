# Config Loader
from .common.config.core_loader import YamlConfigLoader

# Logger
from .common.logger import Logger

from .job.debug_tw_mk import debug_tw_mk

import time

from queick import JobQueue
from queick import SchedulingTime
from queick import cli
import queick

main_logger = Logger("main")
def main():
    core_init()
    # Register debug job
    queue = JobQueue()

    test_job_interval = SchedulingTime()
    test_job_interval.every(minutes=1).starting_from(time.time() + 10)
    queue.cron(test_job_interval, debug_tw_mk, args=())
    main_logger.info("Registered debug job")

    print(queick.JobQueue.mro())

def core_init():
    logger = main_logger.child("init")
    # Load Config
    config = YamlConfigLoader("./I-504/config/config.yml").load()
    logger.info("Loaded config")

