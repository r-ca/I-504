from fastapi import APIRouter

import os
import pickle
import json

import socket

from ...types.job import *

import uuid

router = APIRouter()

from ...debug.test_stub import ProcessTest

# デバッグとか実験とかで使うエンドポイント郡

@router.get("/job_queue_conf/")
async def meta():
    """メタ情報の取得"""
    # 環境変数にpickleされたJobQueueの設定があるのでそれを返す
    return json.loads(os.environ["I504_SOCKET_CONF"])

@router.post("/add_debug_job/")
async def add_debug_job():
    """デバッグ用ジョブの登録"""
    # 環境変数にpickleされたJobQueueの設定があるのでそれを読み込む
    socket_conf = json.loads(os.environ["I504_SOCKET_CONF"])
    #

    # ソケットを開いてジョブを追加する
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_conf["socket_path"])

    # ジョブの登録
    sock.sendall(pickle.dumps(JobManagerRequest(
        job_req_type=JobReqType.REGISTER,
        job_req_body=JobReqBody_Register(
            job_id=uuid.uuid4().__str__(),
            job=Job(
                job_meta=JobMeta(
                    job_name="test_job",
                    job_desc="テスト",
                    priority=JobPriority.NORMAL,
                    job_status=JobStatus.ENABLED,
                    is_repeat=False,
                    can_retry=True,
                    retry_limit=3,
                    retry_interval=JobInterval(
                        interval=1,
                        unit=JobIntervalUnit.MINUTES
                    ),
                    job_interval=JobInterval(
                        interval=15,
                        unit=JobIntervalUnit.SECONDS
                    ),
                    has_depend_job=False
                ),
                job_func=ProcessTest.stub_cat,
                args=(),
                kwargs={
                    "is_cat": True
                }
            )
        )
    )))
