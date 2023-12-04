import socket
from multiprocessing import Pipe
from multiprocessing.connection import Connection

import dill
from ..common.logger import Logger

process_utils_logger = Logger("process_utils")
class ProcessUtils:
    """Process Utils"""

    def configure_socket(pipe: Connection) -> socket.socket:
        """Configure socket"""
        logger = process_utils_logger.child("configure_socket")
        logger.info("Socket configure started.")
        # connection test
        logger.info("Step1/4: Trying to connect to parent process.")

        # Pipe接続テスト
        wait_flag = True
        while wait_flag:
            try:
                pipe.send("ready")
                logger.info("Sent ready message to parent process.")
                logger.info("Waiting OK message from parent process...")
                received = pipe.recv()
                logger.debug(f"Received: {received}")
                if received == "ok":
                    logger.succ("Pipe IPC connection established.")
                    wait_flag = False
                else:
                    logger.error("IPC test failed.")
                    exit(1)
            except Exception as e:
                logger.error(f"Connection error: {e}")
                exit(1)

        # Socketのconfigを受け取る
        logger.info("Step2/4: Trying to receive socket config from parent process.")
        continue_flag = True

        logger.debug("socket_config_req message send")
        pipe.send("socket_config_req")

        while continue_flag:
            received = dill.loads(pipe.recv())
            logger.debug(f"Received: {received}")
            try:
                # TODO: IPv4, IPv6対応
                server: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                logger.debug(f"Trying to bind socket: {received['socket_path']}")
                server.bind(received["socket_path"])
                server.listen(received["socket_listen"])
                continue_flag = False
            except Exception as e: #TODO: 失敗理由によって分岐
                logger.error(f"Failed to bind socket: {e}")
                pipe.send("bind_failed")
                # もう1度ループ
                continue

        logger.succ("Socket bind succeeded!")
        logger.debug("socket_config_ok message send")
        pipe.send("socket_config_ok")

        # Socket通信のテスト
        logger.info("Step3/4: Socket communication test.")
        logger.debug("Sending socket_test_ready message...")
        pipe.send("socket_test_ready")

        logger.info("Waiting for connection...")
        client, addr = server.accept()
        logger.debug(f"Connected from {addr}")
        received = client.recv(1024).decode("utf-8")
        if received == "ready":
            logger.info("Received ready message.")
            client.sendall("ready".encode("utf-8"))
            logger.info("Sent ready message.")
            received = client.recv(1024).decode("utf-8")
            if received == "ok":
                logger.succ("Socket test succeeded!")
            else:
                logger.error("Socket test failed.")
                exit(1)

        logger.info("Socket communication established!")

        return server
