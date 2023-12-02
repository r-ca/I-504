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

class JobPriority(Enum):
    """ジョブの優先度"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class QueueStatus(Enum):
    """キューのステータス"""
    SCHEDULED = "scheduled" # 登録済み
    WAITING_DEPEND = "waiting_depend" # 依存ジョブ待ち
    RUNNING = "running" # 実行中
    FINISHED = "finished" # 完了
    WAITING_RETRY = "waiting_retry" # リトライ待ち
    FAILED = "failed" # 失敗
    CANCELED = "canceled" # キャンセル済み
    UNKNOWN = "unknown" # 不明

class JobStatus(Enum):
    """ジョブのステータス"""
    ENABLED = "enabled" # 有効
    DISABLED_BY_USER = "disabled_by_user" # 無効(ユーザー起因)

class JobIntervalUnit(Enum):
    """ジョブの実行間隔の単位"""
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
