from enum import Enum

class JobReqType(Enum):
    """ジョブマネージャーのリクエストの種類"""
    CONTROL = "control"
    REGISTER = "register"
    UNREGISTER = "unregister"
    UPDATE = "update"
    DEBUG = "debug" #デバッグ用

class JobManagerControlCommand(Enum):
    """ジョブマネージャーをコントロールするコマンドの一覧"""
    STOP = "stop"
    TEST = "test" # 分岐テストコマンド
