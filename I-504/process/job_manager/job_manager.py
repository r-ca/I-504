# Job Manager(本体)

from ...enums.job import *
from ...common.logger import Logger

import pickle
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
import socket

from ...types.job import *

class JobManager:
    def __init__(self):
        self.Session = None
        # Logger
        self.job_m_logger = Logger("JobMgr")

    def run(self, server: socket.socket):
        self.job_m_logger.succ("I-504 Job Manager started.")

        continue_flag = True

        # メインループを別プロセスで実行
        interval_executer_pipe, child_pipe = Pipe() # TODO: 終了処理に組み込む
        Process(target=self.interval_executer, args=(5, child_pipe)).start()

        while continue_flag:
            try:
                # request:JobManagerRequest = self.pipe.recv()
                # self.job_m_logger.debug("Received request.")

                self.job_m_logger.debug("Waiting for connection...")
                client, addr = server.accept()
                self.job_m_logger.debug(f"Connected from {addr}")
                self.job_m_logger.debug("Waiting for request...")
                request:JobManagerRequest = pickle.loads(client.recv(4096))
                #requestが空の場合はbreak
                if not request:
                    self.job_m_logger.debug("Received empty request.")
                    break

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
                self.job_m_logger.error("Type error occured.")
                self.job_m_logger.error(f"Error: {e}")
            # その他のエラー
            except Exception as e:
                self.job_m_logger.error(f"Unknown error occured: {e}")

    def job_register(self, job_id: str, job: Job):
        logger = self.job_m_logger.child("job_register")

        # ログにジョブ情報を出力するかどうか
        # (あまりに長いのでDebugでも出力したくない場合がある)
        enable_job_info: bool = True

        if enable_job_info:
            logger.debug("Job info")
            logger.debug(f"Job ID: {job_id}")
            logger.debug(f"Job name: {job.job_meta.job_name}")
            logger.debug(f"Job description: {job.job_meta.job_desc}")
            logger.debug(f"Job priority: {job.job_meta.priority}")
            logger.debug(f"Job is repeat: {job.job_meta.is_repeat}")
            logger.debug(f"Job can retry: {job.job_meta.can_retry}")
            logger.debug(f"Job retry limit: {job.job_meta.retry_limit}")
            logger.debug(f"Job retry interval: {job.job_meta.retry_interval.interval} {job.job_meta.retry_interval.unit}")
            logger.debug(f"Job interval: {job.job_meta.job_interval.interval} {job.job_meta.job_interval.unit}")
            logger.debug(f"Job has depend job: {job.job_meta.has_depend_job}")
            logger.debug(f"Job depend: {job.job_meta.job_depend.depend_job_id if job.job_meta.has_depend_job else None}")
            logger.debug(f"Job depend require mediator: {job.job_meta.job_depend.require_mediator if job.job_meta.has_depend_job else None}")
            logger.debug(f"Job depend mediator func: {job.job_meta.job_depend.mediator_func if job.job_meta.has_depend_job else None}")
            logger.debug(f"Job func: {pickle.loads(job.job_func)}")
            logger.debug(f"Job args: {job.args}")
            logger.debug(f"Job kwargs: {job.kwargs}")
            logger.debug("Job info end")

        # JobをDBに登録

        session: Session = self.Session()

        session.add(JobModel(
            id=job_id,
            name=job.job_meta.job_name,
            desc=job.job_meta.job_desc,
            priority=job.job_meta.priority.value,
            status=job.job_meta.job_status.value,
            is_repeat=job.job_meta.is_repeat,
            can_retry=job.job_meta.can_retry,
            retry_limit=job.job_meta.retry_limit,
            retry_interval=job.job_meta.retry_interval.interval,
            retry_interval_unit=job.job_meta.retry_interval.unit.value,
            interval=job.job_meta.job_interval.interval,
            unit=job.job_meta.job_interval.unit.value,
            has_depend_job=job.job_meta.has_depend_job,
            depend_job_id=job.job_meta.job_depend.depend_job_id if job.job_meta.has_depend_job else None,
            require_mediator=job.job_meta.job_depend.require_mediator if job.job_meta.has_depend_job else None,
            mediator_func=job.job_meta.job_depend.mediator_func if job.job_meta.has_depend_job else None,
            func=job.job_func, # 関数自体はDBに保存できない？ので
            args=json.dumps(job.args),
            kwargs=json.dumps(job.kwargs),
            # next_run=InternalUtils.calc_next_run_time(job.job_meta.job_interval)
        ))

        # TODO: 切り出す
        # 実行キューに登録
        session.add(QueueModel(
            id=uuid.uuid4().__str__(),
            job_id=job_id,
            status=QueueStatus.SCHEDULED.value,
            next_run=InternalUtils.calc_next_run_time(job.job_meta.job_interval),
            last_run=None,
            retry_count=0
        ))

        try:
            session.commit()
        except Exception as e:
            logger.error(f"Failed to register job: {e}")
            session.rollback()
        else:
            logger.succ(f"Job registered. ID: {job_id}, Name: {job.job_meta.job_name}")

    def queue_db_register(self, queue: QueueModel):
        """キューをデータベースに登録する"""
        logger = self.job_m_logger.child("queue_register")
        logger.debug(f"Registering queue. ID: {queue.id}")
        session: Session = self.Session()
        session.add(queue)
        session.commit()
        logger.succ(f"Queue registered. ID: {queue.id}")
        session.close()

    def job_unregister(self, job_id: str):
        """ジョブの登録解除"""
        logger = self.job_m_logger.child("job_unregister")
        logger.debug(f"Unregistering job. ID: {job_id}")
        session: Session = self.Session()
        session.query(JobModel).filter(JobModel.id == job_id).delete()
        session.commit()
        logger.succ(f"Job unregistered. ID: {job_id}")
        session.close()

    def job_update(self, job_id: str, job: Job):
        pass # TODO
