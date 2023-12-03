from fastapi import APIRouter

import os
import pickle
import json

router = APIRouter()

# デバッグとか実験とかで使うエンドポイント郡

@router.get("/job_queue_conf/")
async def meta():
    """メタ情報の取得"""
    # 環境変数にpickleされたJobQueueの設定があるのでそれを返す
    return json.loads(os.environ["I504_SOCKET_CONF"])

@router.post("/add_debug_job/")
async def add_debug_job():
    """デバッグ用ジョブの登録"""
    pass
