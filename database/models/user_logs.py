from sqlalchemy import Boolean, Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class UserBlockedLog(Base):
    __tablename__ = 'user_blocked_updated_log'

    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    user_blocked_updated_at = Column(Integer, primary_key=True)
    user_blocked_value = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="blocked_logs")


class UserUpdatedLog(Base):
    __tablename__ = 'user_updated_log'

    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    user_updated_at = Column(Integer, primary_key=True)

    user = relationship("User", back_populates="updated_logs")


class UserVerificationRequest(Base):
    __tablename__ = 'user_verification_request'

    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    user_verification_key = Column(String(255), primary_key=True)  # Tilføjet som del af primærnøglen

    user = relationship("User", back_populates="verification_request")

class UserVerificationCompleted(Base):
    __tablename__ = 'user_verification_completed'

    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    user_is_verified_at = Column(Integer, primary_key=True)

    user = relationship("User", back_populates="verification_completed")


class PasswordResetLog(Base):
    __tablename__ = 'password_reset_log'

    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    password_reset_key = Column(String(255), nullable=False)
    password_reset_at = Column(Integer, nullable=False)

    # Definer en unik constraint på kombinationen af kolonner
    __table_args__ = (
        UniqueConstraint('user_pk', 'password_reset_key', 'password_reset_at', name='uix_user_key_time'),
    )

    user = relationship("User", back_populates="password_reset_logs")

class UserDeletedLog(Base):
    __tablename__ = 'user_deleted_log'

    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    user_deleted_at = Column(Integer, primary_key=True)

    user = relationship("User", back_populates="deleted_logs")