# Config Loader
from .common.config.core_loader import YamlConfigLoader

# Logger
from .common.logger import Logger

from .types.job import *
from .enums.job import *

from .job.debug_tw_mk import debug_tw_mk

from .process.job_manager import JobManager

from .debug.test_stub import ProcessTest

import pickle

import uuid

from multiprocessing import Pipe, Process

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .db_model.base import Base

import time

from queick import JobQueue
from queick import SchedulingTime
from queick import cli
import queick

main_logger = Logger("main")
def main():
    core_init()
    # Register debug job
    # queue = JobQueue()

    # test_job_interval = SchedulingTime()
    # test_job_interval.every(minutes=1).starting_from(time.time() + 10)
    # queue.cron(test_job_interval, debug_tw_mk, args=())
    # main_logger.info("Registered debug job")

    # print(queick.JobQueue.mro())

    # パイプの作成
    pipe, child_pipe = Pipe()

    engine = create_engine("sqlite:///./db.sqlite3", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)

    job_manager = JobManager(pipe=child_pipe, engine=engine)

    job_manager_process = Process(target=job_manager.run, args=())

    job_manager_process.start()

    time.sleep(2)

    #テストリクエスト
    pipe.send(JobManagerRequest(
        job_req_type=JobReqType.CONTROL,
        job_req_body=JobReqBody_Control(
            command=JobManagerControlCommand.TEST
        )
    ))

    pipe.send(JobManagerRequest(
        job_req_type=JobReqType.DEBUG,
        job_req_body=JobReqBody_Debug(
            dict={"test_target_method": pickle.dumps(ProcessTest.stub_cat)}
        )
    ))

    pipe.send(JobManagerRequest(
        job_req_type=JobReqType.REGISTER,
        job_req_body=JobReqBody_Register(
            job_id=uuid.uuid4().__str__(),
            job=Job(
                job_meta=JobMeta(
                    job_name="test_job",
                    job_desc="テスト",
                    priority=JobPriority.NORMAL,
                    is_repeat=True,
                    can_retry=True,
                    retry_limit=3,
                    job_interval=JobInterval(
                        interval=1,
                        unit=JobIntervalUnit.MINUTES
                    ),
                    has_depend_job=False
                ),
                job_func=debug_tw_mk,
                kwargs={
                    "is_cat": True
                }
            )
        )
    ))

    pipe.send(JobManagerRequest(
        job_req_type=JobReqType.CONTROL,
        job_req_body=JobReqBody_Control(
            command=JobManagerControlCommand.STOP
        )
    ))



def core_init():
    logger = main_logger.child("init")
    # Load Config
    config = YamlConfigLoader("./I-504/config/config.yml").load()
    logger.info("Loaded config")

