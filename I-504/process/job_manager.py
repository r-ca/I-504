from ..common.logger import Logger
from multiprocessing import Pipe
from multiprocessing.connection import Connection
from ..types.job import *
import pickle

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

                if request.job_req_type == JobReqType.CONTROL: # Controlリクエスト
                    if request.job_req_body.command == JobManagerControlCommand.STOP:
                        self.job_m_logger.info("Received stop command.")
                        continue_flag = False
                    elif request.job_req_body.command == JobManagerControlCommand.TEST:
                        self.job_m_logger.info("Test command received.")
                        self.job_m_logger.succ("IPC test succeeded.")
                    else:
                        self.job_m_logger.error("Unknown command received.")
                elif request.job_req_type == JobReqType.REGISTER: # Registerリクエスト
                    self.job_m_logger.debug("Register request received.")
                    self.job_register(job_id=request.job_req_body.job_id, job=request.job_req_body.job)
                elif request.job_req_type == JobReqType.UNREGISTER: # Unregisterリクエスト
                    pass #TODO
                elif request.job_req_type == JobReqType.UPDATE: # Updateリクエスト
                    pass #TODO
                elif request.job_req_type == JobReqType.DEBUG:
                    self.job_m_logger.info("Debug request received.")
                    pickle.loads(request.job_req_body.dict["test_target_method"])(is_cat=True)
                else:
                    self.job_m_logger.error("Unknown request received.")
            # 型一致エラー
            except TypeError as e:
                self.job_m_logger.error("Received request is not JobManagerRequest type.")
                self.job_m_logger.error(f"Error: {e}")
            # その他のエラー
            except Exception as e:
                self.job_m_logger.error(f"Unknown error occured: {e}")

    def job_register(self, job_id: str, job: Job):
        # Stub
        logger = self.job_m_logger.child("job_register")
        logger.debug("Job info")
        logger.debug(f"Job ID: {job_id}")
        logger.debug(f"Job name: {job.job_meta.job_name}")
        logger.debug(f"Job description: {job.job_meta.job_desc}")
        logger.debug(f"Job priority: {job.job_meta.priority}")
        logger.debug(f"Job is repeat: {job.job_meta.is_repeat}")
        logger.debug(f"Job interval: {job.job_meta.job_interval.interval} {job.job_meta.job_interval.unit}")
        logger.debug(f"Job has depend job: {job.job_meta.has_depend_job}")
        logger.debug(f"Job depend: {job.job_meta.job_depend.depend_job_id if job.job_meta.has_depend_job else None}")
        logger.debug(f"Job depend require mediator: {job.job_meta.job_depend.require_mediator if job.job_meta.has_depend_job else None}")
        logger.debug(f"Job depend mediator func: {job.job_meta.job_depend.mediator_func if job.job_meta.has_depend_job else None}")
        logger.debug(f"Job func: {pickle.loads(job.job_func)}")
        logger.debug(f"Job args: {job.args}")
        logger.debug(f"Job kwargs: {job.kwargs}")
        logger.debug("Job info end")
