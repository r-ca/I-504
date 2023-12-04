from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from ..common.logger import Logger

import socket
import pickle
import dill
import queue
import uuid
import time

def init(engine_url: str):
    engine = create_engine(url=engine_url, echo=False)
    Session = sessionmaker(bind=engine)

    db_manager = DbManager()

    db_manager.run(engine=engine, session=Session)

# データベースアクセスキューの型(ここにあったほうがインポートで便利なので)
class DbQueue:
    def __init__(self, require_result: bool, priority: int, session: Session):
        self.id = uuid.uuid4().__str__()
        self.require_result = require_result
        self.priority = priority
        self.session = session

    id: str
    require_result: bool # このフラグが立っていたら実行結果を返却する
    priority: int
    session: Session
    client: socket.socket

class DbManager:
    """データベースアクセスをとりまとめるマネージャー"""
    def __init__(self):
        self.engine_url = None
        self.Session = None

        self.queue = queue.PriorityQueue()

    def run(self, engine: create_engine, session: sessionmaker):
        """run"""
        continue_flag = True

        self.engine = engine
        self.Session = session

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind("/tmp/db_access_manager.sock")
        server.listen(5)

        while continue_flag:
            conn, addr = server.accept()
            with self.Session() as session:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    else:
                        db_queue: DbQueue = dill.loads(data)
                        if db_queue.require_result: # 結果が必要な場合はクライアントをキューに追加
                            db_queue.client = conn
                        else:
                            conn.close() # 結果が不要な場合はクライアントを閉じる
                        self.queue.put(db_queue)

    def execute(self):
        """execute"""
        logger = Logger("db_manager-execute")
        logger.info("Starting execute loop...")
        continue_flag = True

        self.Session = sessionmaker(bind=self.engine)

        # debug
        waiting_log = False # ログが多すぎるので

        while continue_flag:
            queue: DbQueue = self.queue.get()
            logger.debug(f"Got queue: {queue}")
            session = self.Session()
            result = session.execute(queue.session)
            logger.debug(f"Executed session: {queue.session}")
            if queue.require_result:
                logger.debug("this queue requires result.")
                logger.debug("sending result...")
                try: # Closeされていたりして失敗するかもしれないので
                    queue.client.send(dill.dumps(result))
                    queue.client.close()
                except Exception as e:
                    logger.error(f"Failed to send result: {e}")
            session.close()
            logger.debug("Closed session.")
            self.queue.task_done()
            logger.debug("Task done.")

            # キューが空の場合は0.5秒待機(負荷軽減)
            if self.queue.empty():
                if waiting_log:
                    logger.debug("Queue is empty. Waiting for 0.5 sec...")
                time.sleep(0.5)
