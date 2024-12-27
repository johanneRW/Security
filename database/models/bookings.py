from sqlalchemy import Column, String, Integer, Float, ForeignKey
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