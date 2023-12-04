# Config Loader
from .common.config.core_loader import YamlConfigLoader

# Logger
from .common.logger import Logger

# Job Manager
from .process.job_manager import JobManager
from .types.job import *
from .enums.job import *

# DB Access Manager
from .process.db_access_manager import *

# Session Pool
from .process.session_pool import *

# Debug
from .job.debug_tw_mk import debug_tw_mk
from .debug.test_stub import ProcessTest
from .debug.test_sock_serv import testserv

# WebAPI server
from .fastapi.entry import run as fastapi_run

# Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .db_model.base import Base

# Utils
import pickle
import uuid
from multiprocessing import Pipe, Process, Value, Array
# import multiprocess as multiprocess
from .common.dill_multiprocessing import DillProcess
import time
import socket
import os
import json

main_logger = Logger("main")
def main():
    core_init()

    # DB Init
    engine = create_engine("sqlite:///./db.sqlite3", echo=False)
    Base.metadata.create_all(engine)
    engine.dispose()

    # Session Pool Init
    session_pool = SessionPool()
    DillProcess(target=session_pool.init, kwargs={"engine_url": "sqlite:///./db.sqlite3"}).start()

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect("/tmp/session_pool.sock")

    client.sendall("connection_test".encode("utf-8"))
    client.recv(1024).decode("utf-8")
    client.close()

    time.sleep(2)

    #uvicorn.run(app, host="172.16.30.1", port=55555)

    DillProcess(target=fastapi_run, kwargs=({"host":"localhost", "port":44333})).start()

    time.sleep(2)

    socket_conf = json.loads(os.environ["I504_SOCKET_CONF"])

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(socket_conf["socket_path"])

    # テストリクエスト
    client.sendall(pickle.dumps(JobManagerRequest(
        job_req_type=JobReqType.CONTROL,
        job_req_body=JobReqBody_Control(
            command=JobManagerControlCommand.TEST
        )
    )))

    # pipe.send(JobManagerRequest(
    #     job_req_type=JobReqType.DEBUG,
    #     job_req_body=JobReqBody_Debug(
    #         dict={"test_target_method": pickle.dumps(ProcessTest.stub_cat)}
    #     )
    # ))

    # pipe.send(JobManagerRequest(
    #     job_req_type=JobReqType.REGISTER,
    #     job_req_body=JobReqBody_Register(
    #         job_id=uuid.uuid4().__str__(),
    #         job=Job(
    #             job_meta=JobMeta(
    #                 job_name="test_job",
    #                 job_desc="テスト",
    #                 priority=JobPriority.NORMAL,
    #                 job_status=JobStatus.ENABLED,
    #                 is_repeat=True,
    #                 can_retry=True,
    #                 retry_limit=3,
    #                 retry_interval=JobInterval(
    #                     interval=1,
    #                     unit=JobIntervalUnit.MINUTES
    #                 ),
    #                 job_interval=JobInterval(
    #                     interval=15,
    #                     unit=JobIntervalUnit.SECONDS
    #                 ),
    #                 has_depend_job=False
    #             ),
    #             job_func=ProcessTest.stub_cat,
    #             args=(),
    #             kwargs={
    #                 "is_cat": True
    #             }
    #         )
    #     )
    # ))

    # pipe.send(JobManagerRequest(
    #     job_req_type=JobReqType.CONTROL,
    #     job_req_body=JobReqBody_Control(
    #         command=JobManagerControlCommand.STOP
    #     )
    # ))



def core_init():
    logger = main_logger.child("core_init")
    # Load Config
    config = YamlConfigLoader("./I-504/config/config.yml").load()
    logger.info("Loaded config")

def job_manager_init(engine_url="sqlite:///./db.sqlite3"):
    logger = main_logger.child("job_manager_init")

    # パイプの作成
    pipe, child_pipe = Pipe()

    job_manager = JobManager(engine_url=engine_url)
    job_manager_process = Process(target=job_manager.initializer, args=(child_pipe, ))
    job_manager_process.start()

    logger.info("Waiting for message from Job Manager init process...")
    res = pipe.recv()
    if res == "ready":
        logger.info("Received ready message from Job Manager init process")
        pipe.send("ok")
        logger.info("Sent ok message to Job Manager init process")
    else:
        logger.error("Failed to connect to Job Manager init process")
        exit(1)

    socket_config = None

    # Socketのconfigを送る
    # TODO: Configから読み取る
    socket_mode = "unix" # TODO: Support IPv4, IPv6
    socket_path = "/tmp/socket_test.sock"
    socket_address = ""
    socket_port = 0
    socket_config = { # TODO: 型なんとかする
        "socket_path": socket_path,
        "socket_address": socket_address,
        "socket_port": socket_port
    }

    pipe.send(pickle.dumps(socket_config))
    logger.info("Sent socket config to Job Manager init process")

    res = pipe.recv()
    if res == "ok":
        logger.info("Received ok message from Job Manager init process")
    elif res == "ng":
        logger.error("Received ng message from Job Manager init process")
        # 既定値の使用を試みる
        logger.info("Trying to use default socket config")
        socket_mode = "unix"
        socket_path = "/tmp/socket_default.sock"
        socket_address = ""
        socket_port = 0
        socket_config = { # TODO: 型なんとかする
            "socket_path": socket_path,
            "socket_address": socket_address,
            "socket_port": socket_port
        }
        pipe.send(pickle.dumps(socket_config))
        logger.info("Sent socket config to Job Manager init process (default config))")
        res = pipe.recv()
        if res == "ok":
            logger.info("Received ok message from Job Manager init process (default config)")
        elif res == "ng":
            logger.error("Received ng message from Job Manager init process")
            logger.error("Failed to establish socket connection")
            exit(1)

    logger.info("Waiting socket_test_ready message from Job Manager init process...")
    res = pipe.recv()
    if res == "socket_test_ready":
        logger.info("Received socket_test_ready message from Job Manager init process")
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(socket_config["socket_path"])
        logger.info("Connected to socket")
        logger.info("Waiting for ready message from Job Manager init process...")
        res = client.recv(4096).decode("utf-8")
        if res == "ready":
            logger.info("Received ready message from Job Manager init process")
            client.sendall("ok".encode("utf-8"))
            logger.info("Sent ok message to Job Manager init process")
        else:
            logger.error("Failed to connect to Job Manager init process")
            exit(1)
    else:
        logger.error("Failed to connect to Job Manager init process")
        exit(1)

    client.close()
    return socket_config
