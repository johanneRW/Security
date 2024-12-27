from sqlalchemy import event
from datetime import datetime
from models.item import Item
from models.item_logs import ItemBlockedLog, ItemUpdatedLog

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