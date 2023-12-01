from ..base import Base
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean

class DestinationJunction(Base):

    __tablename__ = 'destination_list_junction'

    overall_id = Column(String(36), primary_key=True) # UUID
    type = Column(String(64)) # ソースの種類
    id = Column(String(36)) # ソースのID
