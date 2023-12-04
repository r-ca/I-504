# Entry point

from ...common.logger import Logger

import pickle
from multiprocessing import Pipe
from multiprocessing.connection import Connection

from sqlalchemy.orm import sessionmaker, Session

import time
import socket

from ...types.job import *
from ...db_model.base import Base
from ...db_model.job_queue import QueueModel

job_mgr_init_logger = Logger("job_mgr_init")
class JobManagerInitializer:
    def __init__(self):
        self.Session = None # Initialized in init()

    def init(self, pipe: Connection, engine):
        """init"""
        logger = job_mgr_init_logger.child("init")
        logger.info("Job Manager Initializer started.")
        # connection test
        logger.debug("Trying to connect to parent process.")

        wait_flag = True
        while wait_flag:
            try:
                pipe.send("ready")
                logger.debug("Sent ready message.")
                received = pipe.recv()
                logger.debug(f"Received: {received}")
                if received == "ok":
                    logger.succ("IPC test succeeded.")
                    wait_flag = False
                else:
                    logger.error("IPC test failed.")
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Connection error: {e}")
                time.sleep(1)

        continue_flag = True
        while continue_flag:
            logger.info("Waiting config message from parent process...")
            config = pickle.loads(pipe.recv())
            logger.info("Received config message from parent process.")
            logger.debug(f"Config: {config}")
            try:
                server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                server.bind(config["socket_path"])
                server.listen(5) # TODO: configから読み取る
            except Exception as e:
                logger.error(f"Failed to bind socket: {e}")
                pipe.send("ng")
                # もう1度ループ
                continue
            else:
                logger.succ("Socket bind succeeded!")
                pipe.send("ok")
                logger.info("Sent ok message to parent process.")
                continue_flag = False

        time.sleep(1)
        pipe.send("socket_test_ready")

        # Socket通信のテスト
        logger.debug("Waiting for connection...")
        client, addr = server.accept()
        logger.debug(f"Connected from {addr}")
        logger.debug("Sending test message...")
        client.send("ready".encode("utf-8"))
        logger.debug("Waiting for response...")
        received = client.recv(1024).decode("utf-8")
        logger.debug(f"Received: {received}")
        if received == "ok":
            logger.succ("Socket test succeeded.")
        else:
            logger.error("Socket test failed.")
            exit(1)

        client.close()

        # Try to connect to DB
        logger.info("Trying to create session...")
        try:
            self.Session = sessionmaker(bind=engine)
            session: Session = self.Session()
            session.close()
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            exit(1)
        else:
            logger.succ("Session created.")

        # Queueのクリア
        logger.info("Clearing queue...")
        session: Session = self.Session()
        count = session.query(QueueModel).count()
        logger.info(f"Found {count} queues.")
        session.query(QueueModel).delete()
        logger.succ("Deleted all queues.")
        session.commit()
        session.close()

        # TODO EnabledなJobをQueueに登録

        self.init = True
#
