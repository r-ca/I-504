"""
FastAPIのエントリーポイント
"""
# (一部のOSでは直接インスタンスオブジェクトを引数に含めてプロセスを起動することができないため)
from .app import app
import uvicorn

def run(host, port):
    """サーバー起動
    host: ホスト名
    port: ポート番号"""
    uvicorn.run(app, host=host, port=port)
