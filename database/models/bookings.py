from sqlalchemy import Column, String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Booking(Base):
    __tablename__ = 'bookings'
    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    item_pk = Column(String(36), ForeignKey('items.item_pk'), primary_key=True)
    booking_created_at = Column(Integer, primary_key=True)
    booking_number_of_nights = Column(Integer, nullable=False)
    booking_price = Column(Float, nullable=False)

    user = relationship("User", back_populates="bookings")
    item = relationship("Item", back_populates="bookings")
    
    __table_args__ = (
        UniqueConstraint('user_pk', 'item_pk', 'booking_created_at', name='uix_booking'),
    )