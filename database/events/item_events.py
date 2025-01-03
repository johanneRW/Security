from sqlalchemy import event
from datetime import datetime
from ..models.item import Item, ItemImage
from ..models.item_logs import ItemBlockedLog, ItemUpdatedLog, ItemVisibilityLog
from sqlalchemy.exc import IntegrityError

# Event listener for AFTER INSERT on items
@event.listens_for(Item, "after_insert")
def insert_item_blocked_listener(mapper, connection, target):
    blocked_log = {
        "item_pk": target.item_pk,
        "item_blocked_updated_at": int(datetime.utcnow().timestamp()),
        "item_blocked_value": 0
    }
    connection.execute(ItemBlockedLog.__table__.insert().values(**blocked_log))
    print(f"Item blocked log created for item: {target.item_pk}")

# Event listener for AFTER UPDATE on items
@event.listens_for(Item, "after_update")
def update_item_listener(mapper, connection, target):
    updated_log = {
        "item_pk": target.item_pk,
        "item_updated_at": int(datetime.utcnow().timestamp())
    }
    connection.execute(ItemUpdatedLog.__table__.insert().values(**updated_log))
    print(f"Item updated log created for item: {target.item_pk}")
    
    
# Event listener for AFTER INSERT on items
@event.listens_for(Item, "after_insert")
def insert_item_visibility_listener(mapper, connection, target):
    visibility_log = {
        "item_pk": target.item_pk,
        "item_visibility_updated_at": int(datetime.utcnow().timestamp()),
        "item_visibility_value": target.item_visibility  # Integer-værdi fra Enum
    }
    connection.execute(ItemVisibilityLog.__table__.insert().values(**visibility_log))
    print(f"Item visibility log created for item: {target.item_pk}, visibility: {target.item_visibility}")
    


# Event listener for BEFORE INSERT on ItemImage
@event.listens_for(ItemImage, "before_insert")
def check_image_limit(mapper, connection, target):
    from sqlalchemy.orm import Session
    session = Session(bind=connection)

    # Tæl antal billeder for det givne item_pk
    image_count = session.query(ItemImage).filter(ItemImage.item_pk == target.item_pk).count()

    if image_count >= 10:
        raise IntegrityError(
            "Item image limit exceeded",
            params=None,
            orig=None
        )
