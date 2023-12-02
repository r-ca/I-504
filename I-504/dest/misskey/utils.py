import requests
from ...common.logger import Logger
from sqlalchemy.orm import sessionmaker
from ...db_model.dest.misskey import *

mk_utils_logger = Logger("misskey-utils")
class MisskeyUtils:
    def placeholder():
        pass

    def update_user(engine, user_unique_id:str):
        logger = mk_utils_logger.child("update_user")
        Session = sessionmaker(bind=engine)
        session = Session()

        # ユーザーの取得
        user = session.query(DestMisskeyAccounts).filter(DestMisskeyAccounts.unique_id == user_unique_id).first()

        if user is None:
            logger.error("User not found")
            return

