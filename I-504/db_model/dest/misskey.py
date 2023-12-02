from ..base import Base
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean

class DestMisskeyAccounts(Base):

    __tablename__ = 'dest_misskey_accounts'

    unique_id = Column(String(36), primary_key=True) # UUID
    user_id = Column(String(64))
    instance = Column(String(64))
    token = Column(String(64))
    username = Column(String(64))
    name = Column(String(64))
    description = Column(String(4096))
    avatar_url = Column(String(1024))
    banner_url = Column(String(1024))
    is_single_use = Column(Boolean) # 1つのソースと固定で紐付けられているかどうか
    linked_source_id = Column(String(36), ForeignKey('source_list_junction.overall_id')) # 1つのソースと固定で紐付けられている場合のソースのID
    is_active = Column(Boolean) # アカウントが有効かどうか

class DestMisskeyNotes(Base):

    __tablename__ = 'dest_misskey_notes'

    note_id = Column(String(36), primary_key=True) # UUID
    item_id = Column(String(36), ForeignKey('dest_misskey_accounts.unique_id'), primary_key=True) # UUID
    created_at = Column(DateTime)
    source_id = Column(String(36), ForeignKey('source_list_junction.overall_id')) # UUID
    source_item_id = Column(String(36)) # 転送元アイテムID


