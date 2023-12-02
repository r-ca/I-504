from ...common.logger import Logger
from ...types.source.twitter import *
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import uuid
from ...common.db_utils import DbUtils
from ...db_model.source.twitter import *

twp_logger = Logger("twitter/parser")
class TwitterUtils:
    def parse_tweets(tweets) -> list[TweetData]:
        logger = twp_logger.child("parse_tweets")
        resp: list[TweetData] = []

        entries = tweets[0]["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"][2]["entries"]
        logger.debug("entities: " + len(entries).__str__())

        for entry in entries:
            # logger.debug("entity: " + entity["entryId"])
            if entry["entryId"].startswith("tweet"): # ツイートだけを抽出
                logger.debug("tweet: " + entry["entryId"])
                entry_id = entry["entryId"]

                # tweet = entity["content"]["itemContent"]["tweet_results"]["result"]["legacy"] # ツイートに関する情報だけを抽

                tweet_body = ""
                tweet = {}
                user_results = {}

                # RTと通常ツイートで構成が違うっぽい？
                try:
                    tweet = entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"]
                except KeyError:
                    # 少なくともRTはこっち？
                    try:
                        tweet = entry["content"]["itemContent"]["tweet_results"]["result"]["tweet"]["legacy"]
                    except KeyError as e:
                        logger.error("Tweet structure is not supported.")
                        logger.error(e)
                        continue
                    else:
                        tweet_body = tweet["full_text"] #TODO なぜかここに全文が入ってないことがあるのでなんとかする
                else:
                    tweet_body = tweet["full_text"] #TODO なぜかここに全文が入ってないことがあるのでなんとかする

                try:
                    user_results = entry["content"]["itemContent"]["tweet_results"]["result"]["core"]["user_results"]["result"]
                except KeyError:
                    # TODO: エラーの定義をして、それをraiseする
                    logger.error("User structure is not supported.")
                    continue
                else:
                    user_rest_id = user_results["rest_id"]
                    if user_rest_id is None:
                        logger.error("User structure is not supported.")
                        user_rest_id = "unknown"
                        continue

                
                logger.debug("\t" + tweet["full_text"])

                datetime = TwitterUtils.parse_datetime(tweet["created_at"])
                # TweetDataの組み立て
                tweet_data = TweetData(entry_id=entry_id, created_at=datetime, full_text=tweet["full_text"], user_rest_id=user_rest_id)
                resp.append(tweet_data)

        return resp

    def parse_datetime(datetime_str:str) -> datetime:
        """ツイートの作成日時をパースする
        "Fri May 28 07:00:00 +0000 2021"→datetime型"""
        return datetime.strptime(datetime_str, "%a %b %d %H:%M:%S %z %Y")

    # def parse_user_result(user_result) -> str:
    #     """tweetsのレスポンスに含まれるuser_resultからユーザーのRestIdを取得する"""
    #     try:
    #         return user_result["data"]["user"]["result"]["rest_id"]
    #     except KeyError:
    #         # TODO: エラーの定義をして、それをraiseする
    #         return None

    def insert_new_source_user(engine, user_rest_id):
        Session = sessionmaker(bind=engine)
        session = Session()

        # idの作成
        id = str(uuid.uuid4())

        session.add(TwitterUsers(unique_id=id, user_rest_id=user_rest_id))
        session.commit()
        session.close()

        DbUtils(engine).add_source_to_junction("twitter", id) # ジャンクションテーブルに登録

    def insert_new_item(engine, tweet_data:TweetData):
        Session = sessionmaker(bind=engine)
        session = Session()

        session.add(TwitterTweets(entry_id=tweet_data.entry_id, created_at=tweet_data.created_at, full_text=tweet_data.full_text, user_rest_id=tweet_data.user_rest_id))
        session.commit()
        session.close()



