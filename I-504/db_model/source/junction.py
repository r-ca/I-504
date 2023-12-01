from ..base import Base
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean

class SourcesJunction(Base):

    __tablename__ = 'source_list_junction'

    overall_id = Column(String(36), primary_key=True) # UUID
    type = Column(String(64)) # ソースの種類
    id = Column(String(36)) # ソースのID
