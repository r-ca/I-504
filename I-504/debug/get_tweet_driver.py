from ..source.twitter.actions import TwitterActions
from ..source.twitter.utils import TwitterUtils
from ..common.config.source.tw_loader import TwitterSourceConfigLoader
from ..common.config.dest.mk_loader import *
from ..types.source.twitter import *
from ..types.dest.misskey import *
from ..common.logger import Logger
from ..dest.misskey.actions import MisskeyActions

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..common.db_utils import DbUtils

from ..db_model.base import Base

logger = Logger("debug_logger")
def get_tweets():
    ## Debug params
    user_rest_id = "1267154527750258689"
    tw_config_path = "./I-504/config/source/twitter.yml"

    tw_config = TwitterSourceConfigLoader(path=tw_config_path).load()

    # Db init
    engine = create_engine("sqlite:///./db.sqlite3", echo=True)
    # Session = sessionmaker(bind=engine)
    # session = Session()
    Base.metadata.create_all(engine)

    # Get tweets
    twitterActions = TwitterActions()
    tweets = twitterActions.get_tweets(tw_cookie=tw_config.auth_cookie, update_limit=tw_config.update_limit, target_user_rest_id=user_rest_id)

    # Add tweets to db
    parsed_new_tweets = twitterActions.check_new_tweet(engine=engine, tweet_data=tweets)

    if len(parsed_new_tweets) == 0:
        logger.info("No new tweets.")
        return
    else:
        logger.info("New tweets found.")

        logger.info("New tweets:")

        misskeyConfig = MisskeyConfigLoader(path="./I-504/config/dest/misskey.yml").load()
        
        misskeyActions = MisskeyActions()

        for tweet in parsed_new_tweets:
            logger.info(tweet.entry_id)
            logger.info(tweet.user_rest_id)
            logger.info(tweet.created_at)
            logger.info(tweet.full_text)

            # DBのアイテム更新 / 投稿テスト
            for tweet in parsed_new_tweets:
                TwitterUtils.insert_new_item(engine=engine, tweet_data=tweet)

                MisskeyPostReqData = {
                    "post_body": tweet.full_text,
                    "meta_data": MisskeyMetaData(
                        instance_address=misskeyConfig["target_instance"],
                        token=misskeyConfig["token"],
                        visibility=misskeyConfig["default_visibility"]
                    )
                }

                misskeyActions.post(MisskeyPostReqData)
