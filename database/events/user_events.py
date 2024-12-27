from sqlalchemy import event
from datetime import datetime

from ..models.user import User
from ..models.user_logs import UserBlockedLog, UserUpdatedLog

# Event listener for AFTER INSERT on users
@event.listens_for(User, "after_insert")
def insert_user_blocked_listener(mapper, connection, target):
    blocked_log = {
        "user_pk": target.user_pk,
        "user_blocked_updated_at": int(datetime.utcnow().timestamp()),
        "user_blocked_value": 0
    }
    connection.execute(UserBlockedLog.__table__.insert().values(**blocked_log))
    print(f"User blocked log created for user: {target.user_pk}")

# Event listener for AFTER UPDATE on users
@event.listens_for(User, "after_update")
def update_user_listener(mapper, connection, target):
    updated_log = {
        "user_pk": target.user_pk,
        "user_updated_at": int(datetime.utcnow().timestamp())
    }
    connection.execute(UserUpdatedLog.__table__.insert().values(**updated_log))
    print(f"User updated log created for user: {target.user_pk}")