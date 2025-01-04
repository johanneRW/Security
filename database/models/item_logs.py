from sqlalchemy import Boolean, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy import UniqueConstraint

class ItemBlockedLog(Base):
    __tablename__ = 'item_blocked_log'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Ny primærnøgle
    item_pk = Column(String(36), ForeignKey('items.item_pk'), nullable=False)
    item_blocked_updated_at = Column(Integer, nullable=False)
    item_blocked_value = Column(Boolean, nullable=False)

    __table_args__ = (
        UniqueConstraint('item_pk', 'item_blocked_updated_at', name='uix_item_blocked'),
    )

    item = relationship("Item", back_populates="blocked_logs")


class ItemUpdatedLog(Base):
    __tablename__ = 'item_updated_log'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Ny primærnøgle
    item_pk = Column(String(36), ForeignKey('items.item_pk'), nullable=False)
    item_updated_at = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('item_pk', 'item_updated_at', name='uix_item_updated'),
    )

    item = relationship("Item", back_populates="updated_logs")


class ItemVisibilityLog(Base):
    __tablename__ = 'item_visibility_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_pk = Column(String(36), ForeignKey('items.item_pk'), nullable=False)
    item_visibility_updated_at = Column(Integer, nullable=False)
    item_visibility_value = Column(String(255), nullable=False) 

    __table_args__ = (
        UniqueConstraint('item_pk', 'item_visibility_updated_at', name='uix_item_visibility'),
    )

    item = relationship("Item", back_populates="visibility_logs")
