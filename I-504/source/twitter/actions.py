## Twitter actions
from ...types.source.twitter import *
from ...types.common import *
from twitter.scraper import Scraper
from .parser import TwitterParser

class TwitterActions:
    def __init__(self, tw_cookie: TwitterAuthCookie, update_limit: int, target_user_rest_id: str):
        self.tw_cookie = tw_cookie
        self.update_limit = update_limit
        self.target_user_rest_id = target_user_rest_id

    def get_tweets(self) -> list[TweetData]:
        # Auth
        scraper = Scraper(cookies={ "ct0": self.tw_cookie.ct0, "auth_token": self.tw_cookie.auth_token })

        # Get tweets
        tweets = scraper.tweets([self.target_user_rest_id], limit=self.update_limit)

        # Parse tweets
        resp: list[TweetData] = TwitterParser.parse_tweets(tweets)

        return resp

