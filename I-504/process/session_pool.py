from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

from ..common.logger import Logger

import time
import socket
import dill

sp_logger = Logger("session_pool")
class SessionPool:
    def __init__(self):
        self.Session = None
        self.engine = None
        self.init_flag = False

    def init(self, engine_url: str):
        logger = sp_logger.child("init")
        logger.info("Session Pool Initializer started.")

        # socket init
        # TODO: テストする, configから読み取る
        # Job Manager のInit実装を汎用化して切り出すべきかも

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind("/tmp/session_pool.sock")
        server.listen(5)

        self.engine = create_engine(engine_url, echo=False)

        logger.info("Session Pool Initializer finished.")

        self.init_flag = True

        self.run(server=server)

    def run(self, server: socket.socket):
        logger = sp_logger
        logger.info("Session Pool started.")

        while True:
            logger.info("Waiting connection...")
            conn, addr = server.accept()
            logger.info(f"Connected from {addr}")
            # TODO: 切り出す
            received = conn.recv(1024).decode()
            logger.debug(f"Received: {received}")
            if received == "session_req":
                logger.debug("Received session request.")
                session = self.Session()
                logger.debug("Created session.")
                conn.sendall(dill.dumps(session))
                logger.debug("Sent session.")
            elif received == "connection_test":
                logger.debug("Received connection test.")
                conn.sendall("ok".encode())
                logger.debug("Sent ok.")
            else:
                logger.error("Received unknown message.")
                conn.sendall("ng".encode()) # 何か返さないとクライアントが困るので
                logger.debug("Sent ng.")

            conn.close()
            logger.info("Connection closed.")
