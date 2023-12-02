
# TODO: ファイルの場所とか考えなおす
from ...source.twitter.actions import TwitterActions
from ...source.twitter.utils import TwitterUtils
from ...types.source.twitter import *
from ...types.dest.common import *
from ...types.dest.interface import *

class SourceTwitterJob:
    def update_tweets(user_rest_id:str, limit:int, engine, dest_id:str, dest_meta:MetaData, tw_cookie:TwitterAuthCookie):

        tweets = TwitterActions.get_tweets(target_user_rest_id=user_rest_id, update_limit=limit, tw_cookie=tw_cookie)

        new_tweets = TwitterActions.check_new_tweet(engine=engine, tweet_data=tweets)

        # DBのアイテム更新
        for tweet in new_tweets:
            TwitterUtils.insert_new_item(engine=engine, tweet_data=tweet)

        # 通知リクエスト
