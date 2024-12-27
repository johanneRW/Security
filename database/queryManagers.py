from sqlalchemy import exists, func, desc
from sqlalchemy.orm import aliased

from database.models import Item, ItemBlockedLog, User, UserBlockedLog, UserDeletedLog, UserVerificationCompleted

class UserQueryManager:
    @staticmethod
    def get_users_with_status(session):
        # Subquery: Check if the user is verified
        subquery_verified = (
            session.query(UserVerificationCompleted.user_pk)
            .filter(UserVerificationCompleted.user_pk == User.user_pk)
            .exists()
        )

        # Subquery: Check if the user is deleted
        subquery_deleted = (
            session.query(UserDeletedLog.user_pk)
            .filter(UserDeletedLog.user_pk == User.user_pk)
            .exists()
        )

        # Subquery: Get the latest blocked value for the user
        latest_blocked_log = (
            session.query(UserBlockedLog.user_blocked_value)
            .filter(UserBlockedLog.user_pk == User.user_pk)
            .order_by(desc(UserBlockedLog.user_blocked_updated_at))
            .limit(1)
        ).correlate(User)  # Correlate to main query

        # Main query: Select users with their status
        query = (
            session.query(
                User.user_pk,
                User.user_username,
                User.user_email,
                func.coalesce(subquery_verified, 0).label("user_is_verified"),
                func.coalesce(subquery_deleted, 0).label("user_is_deleted"),
                func.coalesce(latest_blocked_log.as_scalar(), 0).label("user_is_blocked"),
            )
        )
        return query.all()





class ItemQueryManager:
    @staticmethod
    def get_items_with_status(session):
        # Subquery: Get the latest blocked value for the item
        latest_blocked_log = (
            session.query(ItemBlockedLog.item_blocked_value)
            .filter(ItemBlockedLog.item_pk == Item.item_pk)
            .order_by(desc(ItemBlockedLog.item_blocked_updated_at))
            .limit(1)
        ).correlate(Item)

        # Main query: Select items with their status
        query = (
            session.query(
                Item.item_pk,
                Item.item_name,
                Item.item_lat,
                Item.item_lon,
                Item.item_price_per_night,
                Item.item_created_at,
                Item.item_owned_by,
                func.coalesce(latest_blocked_log.as_scalar(), 0).label("item_is_blocked"),
            )
        )
        return query.all()
