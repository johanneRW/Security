from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Rating(Base):
    __tablename__ = 'ratings'
    item_pk = Column(String(36), ForeignKey('items.item_pk'), primary_key=True)
    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    stars = Column(Integer, nullable=False)
    rating_created_at = Column(Integer, nullable=False)

    item = relationship("Item", back_populates="ratings")
    user = relationship("User", back_populates="ratings")