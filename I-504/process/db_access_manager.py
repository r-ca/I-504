from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from ..common.logger import Logger

import socket
import pickle
import queue
import uuid
import time

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
    def __init__(self, engine_url: str):
        self.engine_url = engine_url
        self.Session = None

        self.queue = queue.PriorityQueue()

    def init(self):
        self.engine = create_engine(self.engine_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

        self.run()

    def run(self):
        """run"""
        continue_flag = True

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
                        db_queue: DbQueue = pickle.loads(data)
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
                    queue.client.send(pickle.dumps(result))
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
