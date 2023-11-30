from ...common.logger import Logger
from ...types.source.twitter import *

twp_logger = Logger("twitter/parser")
class TwitterParser:
    def parse_tweets(tweets) -> list[TweetData]:
        logger = twp_logger.child("parse_tweets")
        
        resp: list[TweetData] = []

        entities = tweets[0]["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"][1]["entries"]
        logger.debug("entities: " + len(entities).__str__())

        for entity in entities:
            # logger.debug("entity: " + entity["entryId"])
            if entity["entryId"].startswith("tweet"): # ツイートだけを抽出
                logger.debug("tweet: " + entity["entryId"])
                entry_id = entity["entryId"]

                tweet = entity["content"]["itemContent"]["tweet_results"]["result"]["legacy"] # ツイートに関する情報だけを抽出
                logger.debug("\t" + tweet["full_text"])
                
                # TweetDataの組み立て
                tweet_data = TweetData(entry_id=entry_id, created_at=tweet["created_at"], full_text=tweet["full_text"], user_rest_id=tweet["id_str"])
                resp.append(tweet_data)

        return resp
