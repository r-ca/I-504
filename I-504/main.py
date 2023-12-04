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
from .common.get_session import get_session

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
from multiprocessing.connection import Connection
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
    pipe, child_pipe = Pipe()
    session_pool = SessionPool()
    DillProcess(target=session_pool.init, kwargs={"engine_url": "sqlite:///./db.sqlite3", "pipe": child_pipe}).start()
    session_pool_conf = {
        "socket_path": "/tmp/session_pool.sock",
        "socket_listen": 5
    }
    session_pool_conf = ipc_init(pipe=pipe, socket_config=session_pool_conf)
    os.environ["I504_SESSION_POOL_CONF"] = json.dumps(session_pool_conf)

    # Job Manager Init
    pipe, child_pipe = Pipe()
    job_manager = JobManager()
    DillProcess(target=job_manager.init, kwargs={"engine_url": "sqlite:///./db.sqlite3", "pipe": child_pipe}).start()

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

def core_init():
    logger = main_logger.child("core_init")
    # Load Config
    config = YamlConfigLoader("./I-504/config/config.yml").load()
    logger.info("Loaded config")

def ipc_init(pipe: Connection, socket_config: dict):
    logger = main_logger.child("ipc_init")
    logger.info("IPC Initializer started.")
    # connection test
    logger.info("Waiting ready message from parent process...")
    res = pipe.recv()
    if res == "ready":
        logger.info("Received ready message from parent process")
        pipe.send("ok")
        logger.info("Sent ok message to target process")

    logger.info("Waiting socket_config_req message from target process...")
    res = pipe.recv()
    if res == "socket_config_req":
        logger.info("Received socket_config_req message from target process")
        # Socketのconfigを送る
        pipe.send(dill.dumps(socket_config))

    logger.info("Waiting socket_config_ok message from target process...")
    res = pipe.recv()
    if res == "socket_config_ok":
        logger.info("Received socket_config_ok message from target process")
    elif res == "socket_config_ng_48":
        logger.warn("Received socket_config_ng_48 message from target process")
        logger.warn("Trying to remove socket file...")
        try:
            os.remove(socket_config["socket_path"])
            logger.succ("Removed socket file")
            # 送り直す
            logger.info("Sending socket config again...")
            pipe.send(dill.dumps(socket_config))
            if pipe.recv() == "socket_config_ok": # TODO: ネスト深すぎるのでなんとかする
                logger.info("Received socket_config_ok message from target process")
            else:
                logger.error("Received unknown message from target process") # Fatal?
                exit(1)
        except Exception as e:
            logger.error(f"Failed to remove socket file: {e}")
            exit(1)
    elif res == "socket_config_ng":
        logger.error("Received socket_config_ng message from target process")
        exit(1)
    else:
        logger.error("Received unknown message from target process")
        exit(1)

    logger.info("Waiting socket_test_ready message from target process...")
    res = pipe.recv()
    if res == "socket_test_ready":
        logger.info("Received socket_test_ready message from target process")
        logger.debug("Trying to connect to target process (Config: {socket_config})".format(socket_config=socket_config))
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(socket_config["socket_path"])
        logger.info("Connected to target process")
        logger.info("Sending ready message to target process...")
        client.sendall("ready".encode("utf-8"))
        logger.info("Waiting for response from target process...")
        res = client.recv(1024).decode("utf-8")
        if res == "ready":
            logger.info("Received ready message from target process")
            client.sendall("ok".encode("utf-8"))
            logger.info("Sent ok message to target process")
        else:
            logger.error("Failed to connect to target process")
            exit(1)

    logger.succ("Socket IPC configured successfully!")

    logger.debug("Closing socket and pipe connection...")

    client.close()
    pipe.close()

    logger.succ("IPC Initializer finished.")

    return socket_config
