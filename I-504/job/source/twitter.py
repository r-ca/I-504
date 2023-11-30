
# TODO: ファイルの場所とか考えなおす


class TwitterUpdateJob:
    def __init__(self, tw_cookie: TwCookie, update_limit: int, target_user_id: str):
        self.tw_cookie = tw_cookie
        self.update_limit = update_limit
        self.target_user_id = target_user_id

    def execute(self):
        self.scraper = Scraper(cookies={ "ct0": self.tw_cookie.ct0, "auth_token": self.tw_cookie.auth_token })
        
    def get_tweets(self) -> list:
        return self.scraper.get_tweets(self.target_user_id, self.update_limit)
