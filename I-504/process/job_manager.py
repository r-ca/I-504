from ..common.logger import Logger
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from ..types.job import *
from ..db_model.job_queue import *
import pickle
from datetime import datetime
from datetime import timedelta
import uuid
import schedule
import time

import socket

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

import json



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
