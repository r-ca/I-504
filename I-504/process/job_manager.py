from ..common.logger import Logger
from multiprocessing import Pipe
from multiprocessing.connection import Connection
from ..types.job import *

class JobManager:
    def __init__(self, pipe:Connection):
        self.pipe:Connection = pipe

        # Logger
        self.job_m_logger = Logger("JobMgr")

    def run(self):
        self.job_m_logger.succ("I-504 Job Manager started.")

        continue_flag = True

        while continue_flag:
            try:
                request:JobManagerRequest = self.pipe.recv()
                self.job_m_logger.debug("Received request.")
                # リクエストごとに分岐
                # コントロールリクエスト
                if request.job_req_type == JobReqType.CONTROL:
                    if request.job_req_body.command == JobManagerControlCommand.STOP:
                        self.job_m_logger.info("Received stop command.")
                        continue_flag = False
                    elif request.job_req_body.command == JobManagerControlCommand.TEST:
                        self.job_m_logger.info("Test command received.")
                        self.job_m_logger.info("IPC test succeeded.")
            # 型一致エラー
            except TypeError as e:
                self.job_m_logger.error("Received request is not JobManagerRequest type.")
                self.job_m_logger.error(f"Error: {e}")
            # その他のエラー
            except Exception as e:
                self.job_m_logger.error(f"Unknown error occured: {e}")
