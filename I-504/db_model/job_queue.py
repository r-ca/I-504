from .base import Base
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean

class JobModel(Base):

    __tablename__ = '_job'

    id = Column(String(36), primary_key=True) # UUID
    name = Column(String(64)) # ジョブ名
    desc = Column(String(256)) # ジョブの説明
    priority = Column(Integer) # ジョブの優先度
    status = Column(String(16)) # ジョブのステータス
    is_repeat = Column(Boolean) # 繰り返し実行するかどうか
    interval = Column(Integer) # ジョブの実行間隔
    unit = Column(String(64)) # ジョブの実行間隔の単位
    has_depend_job = Column(Boolean) # 依存ジョブを持つかどうか
    depend_job_id = Column(String(36)) # 依存ジョブのID
    require_mediator = Column(Boolean) # 仲介が必要かどうか
    mediator_func = Column(String(256)) # 仲介関数
    func = Column(String(256)) # 実行する関数
    args = Column(String(256)) # 関数に渡す引数
    kwargs = Column(String(256)) # 関数に渡すキーワード引数
    # created_at = Column(DateTime) # 作成日時
    next_run = Column(DateTime) # 次回実行日時
