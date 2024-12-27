from sqlalchemy import exists, func, desc
from sqlalchemy.orm import aliased

from database.models import Item, ItemBlockedLog, User, UserBlockedLog, UserDeletedLog, UserVerificationCompleted
from database.models.item import ItemImage

class UserQueryManager:
    @staticmethod
    def get_users_with_status(session, email=None, is_verified=None, is_deleted=None):
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
                User.user_first_name,
                User.user_last_name,
                User.user_email,
                User.user_created_at,
                func.coalesce(subquery_verified, 0).label("user_is_verified"),
                func.coalesce(subquery_deleted, 0).label("user_is_deleted"),
                func.coalesce(latest_blocked_log.as_scalar(), 0).label("user_is_blocked"),
            )
        )

        # Tilføj filtre baseret på parametre
        if email:
            query = query.filter(User.user_email == email)
        if is_verified is not None:
            query = query.filter(func.coalesce(subquery_verified, 0) == (1 if is_verified else 0))
        if is_deleted is not None:
            query = query.filter(func.coalesce(subquery_deleted, 0) == (1 if is_deleted else 0))

        # Sortér efter oprettelsestidspunkt
        query = query.order_by(User.user_created_at)

        # Få alle resultater
        results = query.all()

        # Konverter resultater til liste af dictionaries
        users_list = [
            {
                "user_pk": user.user_pk,
                "user_username": user.user_username,
                "user_first_name": user.user_first_name,
                "user_last_name": user.user_last_name,
                "user_email": user.user_email,
                "user_created_at": user.user_created_at,
                "user_is_verified": user.user_is_verified,
                "user_is_deleted": user.user_is_deleted,
                "user_is_blocked": user.user_is_blocked,
            }
            for user in results
        ]

        return users_list






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
                func.group_concat(ItemImage.image_filename.distinct()).label("images"),  # Aggregate images
            )
            .outerjoin(ItemImage, Item.item_pk == ItemImage.item_pk)  # Join images
            .group_by(Item.item_pk)  # Group by item_pk
        )
        return query

    @staticmethod
    def format_items(items):
        # Konverter forespørgselsresultater til liste af dictionaries
        items_list = []
        for item in items:
            item_dict = {
                "item_pk": item.item_pk,
                "item_name": item.item_name,
                "item_lat": item.item_lat,
                "item_lon": item.item_lon,
                "item_price_per_night": item.item_price_per_night,
                "item_created_at": item.item_created_at,
                "item_owned_by": item.item_owned_by,
                "item_is_blocked": item.item_is_blocked,
                "images": item.images.split(",") if item.images else [],  # Convert images to list
            }
            items_list.append(item_dict)
        return items_list
