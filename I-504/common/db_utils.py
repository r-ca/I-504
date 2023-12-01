from ..db_model.source.twitter import *
from ..db_model.source.junction import *
from ..db_model.dest.misskey import *
from ..db_model.dest.junction import *
from sqlalchemy.orm import sessionmaker
from ..common.logger import Logger
import uuid

db_utils_logger = Logger("db_utils")
class DbUtils:
    def __init__(self, engine):
        self.engine = engine

    # TODO: typeに型をつける
    def add_source_to_junction(self, type, id): # ソースを追加する
        logger = db_utils_logger.child("add_source_to_junction")
        # セッション作成
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Overall_idの生成
        overall_id = str(uuid.uuid4())
        logger.debug("Generated overall_id: {overall_id}")

        # ソースを追加
        session.add(SourcesJunction(overall_id=overall_id, type=type, id=id))
        session.commit()

        # セッションを閉じる
        session.close()

    