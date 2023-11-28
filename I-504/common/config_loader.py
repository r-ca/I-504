from ..types import *
from ..interface.system import *
import json

class DummyConfigLoader(IConfigLoader):
    def load(self) -> CoreConfig:
        return CoreConfig(
            tw_cookie=TwCookie(
                ct0="ct0",
                auth_token="auth_token"
            )
        )
    
class JsonConfigLoader(IConfigLoader):
    def __init__(self, path:str):
        self.path = path

    def load(self) -> CoreConfig:
        cookie_json = open(self.path, "r")
        config = json.load(cookie_json)
        return CoreConfig(
            tw_cookie=TwCookie(
                ct0=config["ct0"],
                auth_token=config["auth_token"]
            )
        )
