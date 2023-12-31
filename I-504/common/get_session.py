import socket

from ..common.logger import Logger

from sqlalchemy.orm import sessionmaker, Session

import os
import dill
import json
import pickle

def get_session() -> Session:
    logger = Logger("get_session")
    conf = os.getenv("I504_SESSION_POOL_CONF")
    if conf is None:
        raise Exception("I504_SESSION_POOL_CONF is not set.")
    config = json.loads(conf)

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(config["socket_path"])

    logger.debug("session_req message send")
    client.send("session_req".encode("utf-8"))
    logger.debug("Waiting for response...")
    received = client.recv(4096)
    logger.debug("Received")
    return dill.loads(received)


