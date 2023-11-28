# Types
class TwCookie:
    def __init__(self, ct0:str, auth_token:str):
        self.ct0 = ct0
        self.auth_token = auth_token

    def getTwCookie(self) -> dict:
        return {
            "ct0": self.ct0,
            "auth_token": self.auth_token
        }

class CoreConfig: # システムのConfig
    def __init__(self, tw_cookie: TwCookie, hoge:str):
        self.tw_cookie: TwCookie = tw_cookie
