from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ItemBlockedLog(Base):
    __tablename__ = 'item_blocked_log'
    item_pk = Column(String(36), ForeignKey('items.item_pk'), primary_key=True)
    item_blocked_updated_at = Column(Integer, primary_key=True)
    item_blocked_value = Column(Integer, nullable=False)

    item = relationship("Item", back_populates="blocked_logs")

class ItemUpdatedLog(Base):
    __tablename__ = 'item_updated_log'
    item_pk = Column(String(36), ForeignKey('items.item_pk'), primary_key=True)
    item_updated_at = Column(Integer, primary_key=True)

    item = relationship("Item", back_populates="updated_logs")

