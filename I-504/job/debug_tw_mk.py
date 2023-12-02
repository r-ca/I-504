# Debug Job

from ..common.config.source.tw_loader import TwitterSourceConfigLoader
from ..common.config.dest.mk_loader import MisskeyConfigLoader

from ..source.twitter.actions import TwitterActions
from ..source.twitter.utils import TwitterUtils

from ..dest.misskey.actions import MisskeyActions

from ..types.dest.misskey import *
from ..types.source.twitter import *

from ..common.logger import Logger

from sqlalchemy import create_engine

test_job_logger = Logger("test_job1")
def debug_tw_mk():
    ## Debug params
    user_rest_id = "1267154527750258689"
    tw_config_path = "./I-504/config/source/twitter.yml"
    mk_config_path = "./I-504/config/dest/misskey.yml"

    logger = test_job_logger.child("debug_tw_mk")

    tw_config = TwitterSourceConfigLoader(path=tw_config_path).load()
    mk_config = MisskeyConfigLoader(path=mk_config_path).load()

    # Get tweets
    tweets = TwitterActions().get_tweets(tw_cookie=tw_config.auth_cookie, update_limit=tw_config.update_limit, target_user_rest_id=user_rest_id)

    engine = create_engine("sqlite:///./db.sqlite3", echo=True)

    parsed_new_tweets = TwitterActions().check_new_tweet(engine=engine, tweet_data=tweets)

    if len(parsed_new_tweets) == 0:
        logger.info("No new tweets.")
        return
    else:
        logger.info("New tweets found.")
        for tweet in parsed_new_tweets:
            TwitterUtils.insert_new_item(engine=engine, tweet_data=tweet)

            MisskeyPostReqData = {
                "post_body": tweet.full_text,
                "meta_data": MisskeyMetaData(
                    instance_address=mk_config["target_instance"],
                    token=mk_config["token"],
                    visibility=mk_config["default_visibility"]
                )
            }

            MisskeyActions().post(MisskeyPostReqData)
