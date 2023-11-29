from .source.twitter import *

class IDBConfig:
    def getConfig(self) -> dict:
        pass

class DBSettings:
    def __init__(self, db_type:str, db_config:IDBConfig):
        self.db_type = db_type
        self.db_config = db_config

    def getDBSettings(self) -> dict:
        return {
            "db_type": self.db_type,
            "db_config": self.db_config
        }
    
class SqliteConfig(IDBConfig):
    def __init__(self, db_name:str):
        self.db_name = db_name

    def getConfig(self) -> dict:
        return {
            "db_name": self.db_name
        }

class CoreConfig: # システムのConfig
    def __init__(self, db_settings: DBSettings ,tw_cookie: TwCookie):
        self.db_settings: DBSettings = db_settings
        self.tw_cookie: TwCookie = tw_cookie
