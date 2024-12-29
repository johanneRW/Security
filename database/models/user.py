from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.orm import relationship
from .base import Base
from enum import Enum as PyEnum
import uuid
from datetime import datetime

# Definer roller som en Python Enum
class RoleEnum(PyEnum):
    ADMIN = "admin"
    PARTNER = "partner"
    USER = "user"

class User(Base):
    __tablename__ = 'users'
    user_pk = Column(String(36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()))
    user_username = Column(String(30), nullable=True)  # Tilføjet længde
    user_first_name = Column(String(30), nullable=True)  # Tilføjet længde
    user_last_name = Column(String(30), nullable=True)  # Tilføjet længde
    user_email = Column(String(100), unique=True, nullable=False)  # Tilføjet længde
    user_password = Column(String(60), nullable=False)  # Tilføjet længde
    user_role = Column(Enum(RoleEnum, name="role_enum"), nullable=False)  # Enum bruges direkte
    user_created_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)

    verification_request = relationship("UserVerificationRequest", back_populates="user", uselist=False)
    verification_completed = relationship("UserVerificationCompleted", back_populates="user", uselist=False)
    password_reset_logs = relationship("PasswordResetLog", back_populates="user")
    blocked_logs = relationship("UserBlockedLog", back_populates="user")
    deleted_logs = relationship("UserDeletedLog", back_populates="user")
    updated_logs = relationship("UserUpdatedLog", back_populates="user")
    items = relationship("Item", back_populates="owner")
    ratings = relationship("Rating", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
