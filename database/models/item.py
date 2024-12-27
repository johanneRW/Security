from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import uuid
from datetime import datetime

class Item(Base):
    __tablename__ = 'items'
    item_pk = Column(String(36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()))
    item_name = Column(String(255), nullable=False)  # Tilføjet længde
    item_lat = Column(String(100), nullable=True)  # Tilføjet længde
    item_lon = Column(String(100), nullable=True)  # Tilføjet længde
    item_price_per_night = Column(Float, nullable=False)
    item_created_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    item_owned_by = Column(String(36), ForeignKey('users.user_pk'), nullable=False)

    owner = relationship("User", back_populates="items")
    blocked_logs = relationship("ItemBlockedLog", back_populates="item")
    images = relationship("ItemImage", back_populates="item")
    updated_logs = relationship("ItemUpdatedLog", back_populates="item")
    ratings = relationship("Rating", back_populates="item")
    bookings = relationship("Booking", back_populates="item")
    
class ItemImage(Base):
    __tablename__ = 'items_images'
    image_pk = Column(String(36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()))
    item_pk = Column(String(36), ForeignKey('items.item_pk'), nullable=False)
    image_filename = Column(String(255), nullable=False)

    item = relationship("Item", back_populates="images")