# Types
import abc

class TwCookie:
    def __init__(self, ct0:str, auth_token:str):
        self.ct0 = ct0
        self.auth_token = auth_token

    def getTwCookie(self) -> dict:
        return {
            "ct0": self.ct0,
            "auth_token": self.auth_token
        }

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

class MisskeyVisibility:
    public = "public"
    home = "home"
    followers = "followers"
    specified = "specified"
    private = "private"

class MetaData(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        pass
    
class PostData:
    def __init__(self, origin:str, content:str):
        self.origin = origin
        self.content = content

class IPostData(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, post_data:PostData, meta_data:MetaData):
        post_data:PostData = post_data
        meta_data:MetaData = meta_data



class MisskeyMetaData(MetaData):
    def __init__(self, visibility:MisskeyVisibility, instance_address:str, token:str):
        self.visibility: MisskeyVisibility = visibility
        self.instance_address: str = instance_address
        self.token: str = token

class MisskeyPostData(IPostData):
    def __init__(self, post_data:PostData, meta_data:MisskeyMetaData):
        self.post_data:PostData = post_data
        self.meta_data:MisskeyMetaData = meta_data
