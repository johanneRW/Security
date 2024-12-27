import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, ForeignKey, DateTime, PrimaryKeyConstraint, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy import event
from datetime import datetime

# Initialiser SQLAlchemy Base
Base = declarative_base()

# Role-model
class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    role_name = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="role")

# User-model
class User(Base):
    __tablename__ = 'users'
    user_pk = Column(String(36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()))
    user_username = Column(String, nullable=True)
    user_first_name = Column(String, nullable=True)
    user_last_name = Column(String, nullable=True)
    user_email = Column(String, unique=True, nullable=False)
    user_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.role_id'), nullable=True)
    user_created_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    role = relationship("Role", back_populates="users")
    verification_request = relationship("UserVerificationRequest", back_populates="user", uselist=False)
    verification_completed = relationship("UserVerificationCompleted", back_populates="user", uselist=False)
    password_reset_logs = relationship("PasswordResetLog", back_populates="user")
    blocked_logs = relationship("UserBlockedLog", back_populates="user")
    deleted_logs = relationship("UserDeletedLog", back_populates="user")
    updated_logs = relationship("UserUpdatedLog", back_populates="user")
    items = relationship("Item", back_populates="owner")
    ratings = relationship("Rating", back_populates="user")
    bookings = relationship("Booking", back_populates="user")

# UserVerificationRequest-model
class UserVerificationRequest(Base):
    __tablename__ = 'user_verification_request'
    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    user_verification_key = Column(String, nullable=False)
    user = relationship("User", back_populates="verification_request")

# UserVerificationCompleted-model
class UserVerificationCompleted(Base):
    __tablename__ = 'user_verification_completed'
    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    user_is_verified_at = Column(Integer, nullable=False)
    user = relationship("User", back_populates="verification_completed")

# PasswordResetLog-model
class PasswordResetLog(Base):
    __tablename__ = 'password_reset_log'
    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    password_reset_key = Column(String, unique=True, nullable=False)
    password_reset_at = Column(Integer, nullable=False)
    user = relationship("User", back_populates="password_reset_logs")

# UserBlockedLog-model
class UserBlockedLog(Base):
    __tablename__ = 'user_blocked_updated_log'
    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    user_blocked_updated_at = Column(Integer, primary_key=True)
    user_blocked_value = Column(Integer, nullable=False)
    user = relationship("User", back_populates="blocked_logs")

# UserDeletedLog-model
class UserDeletedLog(Base):
    __tablename__ = 'user_deleted_log'
    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    user_deleted_at = Column(Integer, primary_key=True)
    user = relationship("User", back_populates="deleted_logs")

# UserUpdatedLog-model
class UserUpdatedLog(Base):
    __tablename__ = 'user_updated_log'
    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    user_updated_at = Column(Integer, primary_key=True)
    user = relationship("User", back_populates="updated_logs")

# Item-model
class Item(Base):
    __tablename__ = 'items'
    item_pk = Column(String(36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()))
    item_name = Column(String, nullable=False)
    item_lat = Column(String, nullable=True)
    item_lon = Column(String, nullable=True)
    item_price_per_night = Column(Float, nullable=False)
    item_created_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    item_owned_by = Column(String(36), ForeignKey('users.user_pk'), nullable=False)
    owner = relationship("User", back_populates="items")
    blocked_logs = relationship("ItemBlockedLog", back_populates="item")
    images = relationship("ItemImage", back_populates="item")
    updated_logs = relationship("ItemUpdatedLog", back_populates="item")
    ratings = relationship("Rating", back_populates="item")
    bookings = relationship("Booking", back_populates="item")

# ItemBlockedLog-model
class ItemBlockedLog(Base):
    __tablename__ = 'item_blocked_log'
    item_pk = Column(String(36), ForeignKey('items.item_pk'), primary_key=True)
    item_blocked_updated_at = Column(Integer, primary_key=True)
    item_blocked_value = Column(Integer, nullable=False)
    item = relationship("Item", back_populates="blocked_logs")

# ItemImage-model
class ItemImage(Base):
    __tablename__ = 'items_images'
    image_pk = Column(String(36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()))
    item_pk = Column(String(36), ForeignKey('items.item_pk'), nullable=False)
    image_filename = Column(String, nullable=False)
    item = relationship("Item", back_populates="images")

# ItemUpdatedLog-model
class ItemUpdatedLog(Base):
    __tablename__ = 'item_updated_log'
    item_pk = Column(String(36), ForeignKey('items.item_pk'), primary_key=True)
    item_updated_at = Column(Integer, primary_key=True)
    item = relationship("Item", back_populates="updated_logs")

# Rating-model
class Rating(Base):
    __tablename__ = 'ratings'
    item_pk = Column(String(36), ForeignKey('items.item_pk'), primary_key=True)
    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    stars = Column(Integer, nullable=False)
    rating_created_at = Column(Integer, nullable=False)
    item = relationship("Item", back_populates="ratings")
    user = relationship("User", back_populates="ratings")

# Booking-model
class Booking(Base):
    __tablename__ = 'bookings'
    user_pk = Column(String(36), ForeignKey('users.user_pk'), primary_key=True)
    item_pk = Column(String(36), ForeignKey('items.item_pk'), primary_key=True)
    booking_created_at = Column(Integer, primary_key=True)
    booking_number_of_nights = Column(Integer, nullable=False)
    booking_price = Column(Float, nullable=False)
    user = relationship("User", back_populates="bookings")
    item = relationship("Item", back_populates="bookings")

# Databasekonfiguration
DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"  # Skift user, password og dbname

# Initialiser database
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)

print("Database and models with UUID primary keys created successfully.")

# Event listener for AFTER INSERT on users (insert_user_blocked trigger)
@event.listens_for(User, "after_insert")
def insert_user_blocked_listener(mapper, connection, target):
    blocked_log = {
        "user_pk": target.user_pk,
        "user_blocked_updated_at": int(datetime.utcnow().timestamp()),
        "user_blocked_value": 0
    }
    connection.execute(
        UserBlockedLog.__table__.insert().values(**blocked_log)
    )
    print(f"User blocked log created for user: {target.user_pk}")

# Event listener for AFTER UPDATE on users (update_user trigger)
@event.listens_for(User, "after_update")
def update_user_listener(mapper, connection, target):
    updated_log = {
        "user_pk": target.user_pk,
        "user_updated_at": int(datetime.utcnow().timestamp())
    }
    connection.execute(
        UserUpdatedLog.__table__.insert().values(**updated_log)
    )
    print(f"User updated log created for user: {target.user_pk}")

# Event listener for AFTER INSERT on items (insert_item_blocked trigger)
@event.listens_for(Item, "after_insert")
def insert_item_blocked_listener(mapper, connection, target):
    blocked_log = {
        "item_pk": target.item_pk,
        "item_blocked_updated_at": int(datetime.utcnow().timestamp()),
        "item_blocked_value": 0
    }
    connection.execute(
        ItemBlockedLog.__table__.insert().values(**blocked_log)
    )
    print(f"Item blocked log created for item: {target.item_pk}")

# Event listener for AFTER UPDATE on items (update_item trigger)
@event.listens_for(Item, "after_update")
def update_item_listener(mapper, connection, target):
    updated_log = {
        "item_pk": target.item_pk,
        "item_updated_at": int(datetime.utcnow().timestamp())
    }
    connection.execute(
        ItemUpdatedLog.__table__.insert().values(**updated_log)
    )
    print(f"Item updated log created for item: {target.item_pk}")