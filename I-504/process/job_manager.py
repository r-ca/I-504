from ..common.logger import Logger
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from .utils import *
from ..types.job import *
from ..db_model.job_queue import *
import pickle
from datetime import datetime
from datetime import timedelta
from ..common.get_session import get_session
import uuid
import schedule
import time

import socket

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

import json

class JobManager:
    def __init__(self, engine_url: str):
        #self.engine:Engine = create_engine(engine_url, echo=False)
        self.Session = None # initializerで設定するので
        # Logger
        self.job_m_logger = Logger("JobMgr")
        self.init: bool = False

    def init(self, pipe:Connection):
        """init"""
        logger = self.job_m_logger.child("init")
        server: socket.socket = ProcessUtils.configure_socket(pipe=pipe)

        # Try to connect to DB
        logger.info("Trying to get session...")

        session = get_session()

        # Queueのクリア
        logger.info("Clearing queue...")
        count = session.query(QueueModel).count()
        logger.info(f"Found {count} queues.")
        session.query(QueueModel).delete()
        logger.succ("Deleted all queues.")
        session.commit()
        session.close()

        # TODO EnabledなJobをQueueに登録

        self.init = True
        self.run(server=server)

    def run(self, server: socket.socket):
        self.job_m_logger.succ("I-504 Job Manager started.")

        if not self.init:
            self.job_m_logger.error("Job Manager is not initialized.")
            exit(1)

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

    def queue_register_from_job(self, job: JobModel, is_depend: bool = False) -> QueueModel:
        """渡されたジョブからキューを生成する
        is_depend: 依存キューとして登録するかどうか"""
        logger = self.job_m_logger.child("queue_req_job")
        logger.debug(f"Creating queue from job... JobID: {job.id}")

        queue = QueueModel(
            id=uuid.uuid4().__str__(),
            job_id=job.id,
            next_run=InternalUtils.calc_next_run_time(job.job_meta.job_interval),
            last_run=None,
            retry_count=0
        )

        # 自身が依存キューとして登録される場合
        if is_depend:
            queue.status = QueueStatus.WAITING_DEPEND.value
        else:
            queue.status = QueueStatus.SCHEDULED.value

        # 依存ジョブのチェック
        if job.has_depend_job:
            logger.debug("Queue has depend job.")
            # 依存ジョブを取得
            depend_job: JobModel = InternalUtils.get_job(job.depend_job_id)
            # 自身を再帰的に呼び出す
            depend_queue: QueueModel = self.queue_register_from_job(job=depend_job, is_depend=True)
            # 依存キューを登録
            queue.depend_queue_id = depend_queue.id

        return queue

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

    def interval_executer(self, interval: int, pipe: Connection):
        """キューの監視を行う関数を呼び出すプロセス"""
        logger = self.job_m_logger.child("interval_executer")
        logger.debug(f"Interval executer started. Interval: {interval} seconds.")
        schedule.every(interval).seconds.do(self.interval_exec)

        continue_flag = True

        while continue_flag:
            # message = pipe.recv()
            # if message == "stop":
            #     logger.info("Received stop command.")
            #     continue_flag = False
            schedule.run_pending()
            time.sleep(0.5)

    def interval_exec(self):
        """実行するキューを取得して実行(定期実行される関数)"""
        logger = self.job_m_logger.child("interval_exec")
        queues = self.queue_check()

        logger.debug(f"Found {len(queues)} jobs to execute.")

        # TODO: ジョブの優先度によって実行順を変える
        # TODO: ジョブの実行時間上限を設ける
        for queue in queues:
            Process(target=self.queue_executer, args=(queue,)).start()

    def queue_executer(self, queue: QueueModel):
        """キューを実行する"""
        logger = self.job_m_logger.child("queue_executer")
        session = self.Session() # このプロセスでのみ使用するSession
        if queue.status == QueueStatus.SCHEDULED.value:
            logger.info(f"Executing job. Queue ID: {queue.id}")
            # ジョブを取得
            job = InternalUtils.get_job(session, job_id=queue.job_id)
            # ジョブを実行
            # queueのstatusをRUNNINGに更新
            queue.status = QueueStatus.RUNNING.value
            session.add(queue)
            session.commit()
            # TODO: エラーハンドリング
            pickle.loads(job.func)(*json.loads(job.args), **json.loads(job.kwargs))
            # キューのステータスを更新
            InternalUtils.update_queue(session, queue, job, True)

        session.close() # Sessionを閉じる


    def queue_check(self) -> list[JobModel]:
        """実行すべきキューをチェックする"""
        # DB
        session: Session = self.Session()

        # SCHEDULEDとWAITING_RETRYとWAITING_DEPENDのキューを取得
        now = datetime.now()
        jobs = session.query(QueueModel) \
            .filter(QueueModel.next_run <= now) \
            .filter(QueueModel.status.in_([QueueStatus.SCHEDULED.value, QueueStatus.WAITING_RETRY.value, QueueStatus.WAITING_DEPEND.value])) \
            .all()

        session.close()
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

    def update_queue(session: Session, queue: QueueModel, job:JobModel, success: bool):
        """ジョブとキューをチェックして必要であれば更新する"""
        if success:
            if job.is_repeat: # 繰り返し実行するジョブ
                # 次回の実行をスケジュールする
                new_queue = QueueModel(
                    id=uuid.uuid4().__str__(),
                    job_id=job.id,
                    status=QueueStatus.SCHEDULED.value,
                    next_run=InternalUtils.calc_next_run_time(JobInterval(job.interval, JobIntervalUnit(job.unit))),
                    last_run=datetime.now(),
                    retry_count=0
                )
                session.add(new_queue)
            else:
                pass
            # 実行に成功したキューを削除
            session.delete(queue)
            session.commit()
        else:
            # 実行に失敗したキュー
            if job.can_retry:
                # リトライ可能なジョブ
                if queue.retry_count < job.retry_limit:
                    queue.retry_count += 1
                    queue.status = QueueStatus.WAITING_RETRY.value
                    queue.last_run = datetime.now()
                    queue.next_run = InternalUtils.calc_next_run_time(JobInterval(job.retry_interval, JobIntervalUnit(job.retry_interval_unit)))
                else:
                    queue.status = QueueStatus.FAILED.value
                    queue.last_run = datetime.now()
            else:
                queue.status = QueueStatus.FAILED.value
                queue.last_run = datetime.now()

            session.add(queue)
            session.commit()


    def get_job(session: Session, job_id: str):
        """job_idからジョブを取得する"""
        job = session.query(JobModel).filter(JobModel.id == job_id).first()

        return job
