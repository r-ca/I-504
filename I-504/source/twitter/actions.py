## Twitter actions
from ...types.source.twitter import *
from ...types.common import *
from twitter.scraper import Scraper
from .utils import TwitterUtils
from sqlalchemy.orm import sessionmaker
from ...db_model.source.twitter import *


class TwitterActions:
    def get_tweets(self, tw_cookie: TwitterAuthCookie, update_limit: int, target_user_rest_id: str) -> list[TweetData]:
        # Auth
        scraper = Scraper(cookies={ "ct0": tw_cookie.ct0, "auth_token": tw_cookie.auth_token })

        # Get tweets
        tweets = scraper.tweets([target_user_rest_id], limit=update_limit)

        # Parse tweets
        resp: list[TweetData] = TwitterUtils.parse_tweets(tweets)

        return resp

    def check_new_tweet(self, engine, tweet_data: list[TweetData]):
        # 取得したツイートに対して、DBに存在するかを確認して存在しないものを返す
        Session = sessionmaker(bind=engine)
        session = Session()

        # ユーザーIDが一意か確認する
        # TODO: パース元ユーザーと投稿ユーザーが異なる場合がある？のでDBを修正する？
        first_tweet_rest_id = tweet_data[0].user_rest_id
        for tweet in tweet_data:
            if tweet.user_rest_id != first_tweet_rest_id:
                raise Exception("User rest id is not unique.")

        # created_atで昇順にソートして、最新からtweet_dataの要素数分だけ取得
        tweets = session.query(TwitterTweets).filter(TwitterTweets.user_rest_id == tweet_data[0].user_rest_id).order_by(TwitterTweets.created_at.desc()).limit(len(tweet_data)).all()

        # データベースに存在しないツイートは新規であると判断する
        resp = []
        for tweet in tweet_data:
            tweet_exists = False
            for db_tweet in tweets:
                if tweet.entry_id == db_tweet.entry_id:
                    tweet_exists = True
                    break

            if not tweet_exists:
                resp.append(tweet)

        return resp
    
