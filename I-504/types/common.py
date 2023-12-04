from .source.twitter import *
import abc

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

class CoreConfigTargets:
    def __init__(self, enabled:bool, conf_path:str):
        self.enabled = enabled
        self.conf_path = conf_path


class CoreConfig: # システムのConfig
    def __init__(self, db_settings: DBSettings, source_list: dict, dest_list: dict):
        self.db_settings = db_settings
        self.source_list = source_list
        self.dest_list = dest_list


