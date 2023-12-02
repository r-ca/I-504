class TwitterAuthCookie:
    def __init__(self, ct0:str, auth_token:str):
        self.ct0 = ct0
        self.auth_token = auth_token

class TwitterSourceConfig:
    auth_cookie: TwitterAuthCookie = None # 認証クッキー
    update_limit = None # 取得するツイートの数

    def __init__(self, auth_cookie:TwitterAuthCookie, update_limit:int):
        self.auth_cookie = auth_cookie
        self.update_limit = update_limit

class TweetData: # ツイートデータ（のうち保持するもの）
    entry_id = None # ツイートのEntryId
    created_at = None # ツイートの作成日時
    full_text = None # ツイートの本文
    user_rest_id = None # ツイートしたユーザーのRestId

    def __init__(self, entry_id:str, created_at:str, full_text:str, user_rest_id:str):
        self.entry_id = entry_id
        self.created_at = created_at # TODO: とんでもない形式だったのでパーサー書いてDatetimeにする
        self.full_text = full_text
        self.user_rest_id = user_rest_id


