from ..types.common import *
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
        
class YamlConfigLoader(IConfigLoader):
    def __init__(self, path:str):
        self.path = path

    def load(self) -> CoreConfig:
        # 1. Load yaml
        import yaml
        with open(self.path, "r") as yml:
            config = yaml.safe_load(yml)
        # 2. Parse yaml
        if (config["db_settings"]["db_type"] == "sqlite"):
            db_config = SqliteConfig(
                db_name=config["db_settings"]["db_config"]["db_name"]
            )

        if (config["twitter_auth_settings"]["load_from_file"] == True):
            file_path = config["twitter_auth_settings"]["file_path"]
            cookie_json = open(file_path, "r")
            cookie_config = json.load(cookie_json)
            tw_cookie = TwCookie(
                ct0=cookie_config["ct0"],
                auth_token=cookie_config["auth_token"]
            )

        core_config = CoreConfig(
            db_settings=DBSettings(
                db_type=config["db_settings"]["db_type"],
                db_config=db_config
            ),
            tw_cookie=tw_cookie
        )

        return core_config


