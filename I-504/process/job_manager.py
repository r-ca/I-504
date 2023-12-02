from ..common.logger import Logger
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from ..types.job import *
from ..db_model.job_queue import *
import pickle
from datetime import datetime
from datetime import timedelta
import uuid

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

import json

class JobManager:
    def __init__(self, pipe:Connection, engine:Engine):
        self.pipe:Connection = pipe
        self.engine:Engine = engine


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
                self.job_m_logger.error("Type error occured.")
                self.job_m_logger.error(f"Error: {e}")
            # その他のエラー
            except Exception as e:
                self.job_m_logger.error(f"Unknown error occured: {e}")

    def job_register(self, job_id: str, job: Job):
        logger = self.job_m_logger.child("job_register")

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
        Session = sessionmaker(bind=self.engine)
        session = Session()

        session.add(JobModel(
            id=job_id,
            name=job.job_meta.job_name,
            desc=job.job_meta.job_desc,
            priority=job.job_meta.priority.value,
            status=JobStatus.SCHEDULED.value,
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
            func=job.job_func, # pickle.dumpはDBに保存できない？ので
            args=json.dumps(job.args),
            kwargs=json.dumps(job.kwargs),
            # next_run=InternalUtils.calc_next_run_time(job.job_meta.job_interval)
        ))

        # 実行キューに登録
        session.add(QueueModel(
            id=uuid.uuid4().__str__(),
            job_id=job_id,
            status=JobStatus.SCHEDULED.value,
            next_run=InternalUtils.calc_next_run_time(job.job_meta.job_interval),
            last_run=None,
            retry_count=0
        ))

        try:
            session.commit()
            session.close()
        except Exception as e:
            logger.error(f"Failed to register job: {e}")
            session.rollback()
            session.close()
        else:
            logger.succ(f"Job registered. ID: {job_id}, Name: {job.job_meta.job_name}")

    def job_unregister(self, job_id: str):
        pass # TODO

    def job_update(self, job_id: str, job: Job):
        pass # TODO

    def interval_exec(self):
        """実行するジョブを取得して実行(定期実行される関数)"""
        logger = self.job_m_logger.child("interval_exec")
        queues = self.queue_check()

        # TODO: ジョブの優先度によって実行順を変える
        # TODO: ジョブの実行時間上限を設ける
        for queue in queues:
            Process(target=self.queue_executer, args=(queue,)).start()

    def queue_executer(self, queue: QueueModel):
        """キューを実行する"""
        logger = self.job_m_logger.child("queue_executer")
        if queue.status == JobStatus.SCHEDULED.value:
            logger.info(f"Executing job. Job ID: {queue.job_id}")
            # ジョブを取得
            job = InternalUtils.get_job(queue.job_id)
            # ジョブを実行
            # TODO: エラーハンドリング
            pickle.loads(job.func)(*json.loads(job.args), **json.loads(job.kwargs))
            # キューのステータスを更新
            InternalUtils.update_queue(queue, Job, True)


    def queue_check(self) -> list[JobModel]:
        """実行すべきジョブをチェックする"""
        # DB
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # SCHEDULEDとWAITING_RETRYとWAITING_DEPENDのキューを取得
        now = datetime.now()
        jobs = session.query(QueueModel) \
            .filter(QueueModel.next_run <= now) \
            .filter(QueueModel.status.in_([JobStatus.SCHEDULED.value, JobStatus.WAITING_RETRY.value, JobStatus.WAITING_DEPEND.value])) \
            .all()

        return jobs

        # WAITING_DEPENDの依存ジョブをチェック
        # TODO

class InternalUtils:
    """内部で使用するユーティリティ"""
    def calc_next_run_time(job_interval: JobInterval):
        """次回実行日時を計算する"""
        if job_interval.unit == JobIntervalUnit.SECONDS: # seconds
            return datetime.now() + timedelta(seconds=job_interval.interval)
        elif job_interval.unit == JobIntervalUnit.MINUTES: # minutes
            return datetime.now() + timedelta(minutes=job_interval.interval)
        elif job_interval.unit == JobIntervalUnit.HOURS: # hours
            return datetime.now() + timedelta(hours=job_interval.interval)
        elif job_interval.unit == JobIntervalUnit.DAYS: # days
            return datetime.now() + timedelta(days=job_interval.interval)
        else:
            raise Exception("Unknown interval unit.")

    def update_queue(self, queue: QueueModel, job:JobModel, success: bool):
        """ジョブとキューをチェックして必要であれば更新する"""
        if success:
            if job.is_repeat: # 繰り返し実行するジョブ
                # 次回の実行をスケジュールする
                new_queue = QueueModel(
                    id=uuid.uuid4().__str__(),
                    job_id=job.id,
                    status=JobStatus.SCHEDULED.value,
                    next_run=InternalUtils.calc_next_run_time(JobInterval(job.interval, JobIntervalUnit(job.unit))),
                    last_run=datetime.now(),
                    retry_count=0
                )
                Session = sessionmaker(bind=self.engine)
                session = Session()
                session.add(new_queue)
                session.commit()
                session.close()
            else:
                pass # 繰り返し実行しないジョブ

            # 実行に成功したキューを削除
            Session = sessionmaker(bind=self.engine)
            session = Session()
            session.delete(queue)
            session.commit()
            session.close()
        else:
            # 実行に失敗したキュー
            if job.can_retry:
                # リトライ可能なジョブ
                if queue.retry_count < job.retry_limit:
                    queue.retry_count += 1
                    queue.status = JobStatus.WAITING_RETRY.value
                    queue.last_run = datetime.now()
                    queue.next_run = InternalUtils.calc_next_run_time(JobInterval(job.retry_interval, JobIntervalUnit(job.retry_interval_unit)))
                else:
                    queue.status = JobStatus.FAILED.value
                    queue.last_run = datetime.now()
            else:
                queue.status = JobStatus.FAILED.value
                queue.last_run = datetime.now()

            Session = sessionmaker(bind=self.engine)
            session = Session()
            session.add(queue)
            session.commit()
            session.close()


    def get_job(self, job_id: str):
        """ジョブを取得する"""
        Session = sessionmaker(bind=self.engine)
        session = Session()

        job = session.query(JobModel).filter(JobModel.id == job_id).first()

        return job
