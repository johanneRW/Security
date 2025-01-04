from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from ..models.item import Item ,ItemImage
from ..models.item_logs import ItemBlockedLog, ItemUpdatedLog , ItemVisibilityLog 
from ..models.ratings import Rating
from ..models.bookings import Booking
from ..queryManagers import ItemQueryManager
from ..events.user_events import insert_user_blocked_listener, update_user_listener
from ..events.item_events import insert_item_blocked_listener, update_item_listener, insert_item_visibility_listener






def create_image(db: Session, image_pk: str, item_pk: str, image_filename: str):
    # Tæl antallet af billeder for det givne item
    image_count = db.query(ItemImage).filter(ItemImage.item_pk == item_pk).count()

    # Tjek om der allerede er 10 billeder
    if image_count >= 10:
        raise Exception(f"Cannot add more than 10 images for item {item_pk}")

    # Opret en ny instans af ItemImage
    new_image = ItemImage(
        image_pk=image_pk,
        item_pk=item_pk,
        image_filename=image_filename
    )

    # Tilføj til session og commit
    db.add(new_image)
    db.commit()
    db.refresh(new_image)  # Opdater objektet med databasegenererede værdier (hvis nødvendigt)
    return new_image


def create_item(
    db: Session, 
    item_pk: str, 
    item_name: str, 
    item_lat: str, 
    item_lon: str, 
    item_price_per_night: float, 
    item_created_at: int, 
    item_owned_by: str
):
    # Opret en ny instans af Item
    new_item = Item(
        item_pk=item_pk,
        item_name=item_name,
        item_lat=item_lat,
        item_lon=item_lon,
        item_price_per_night=item_price_per_night,
        item_created_at=item_created_at,
        item_owned_by=item_owned_by
    )

    # Tilføj til session og commit
    db.add(new_item)
    db.commit()
    db.refresh(new_item)  # Opdater objektet med databasegenererede værdier (hvis nødvendigt)
    return new_item



def get_item(db: Session, item_pk: str):
    # Udfør venstresammenføjning og gruppering
    result = (
        db.query(
            Item,  # Hent alle kolonner fra Item-modellen
            func.group_concat(ItemImage.image_filename.distinct()).label('images')  # Aggreger billeder
        )
        .outerjoin(ItemImage, Item.item_pk == ItemImage.item_pk)  # Venstresammenføjning med ItemImage
        .filter(Item.item_pk == item_pk)  # Filtrér på det angivne item_pk
        .group_by(Item.item_pk)  # Gruppér på item_pk
        .first()
    )

    if not result:
        return None

    # Pak resultaterne ud
    item, images = result
    images_list = images.split(',') if images else []

    # Tilføj billeder som en liste til objektet
    item_dict = item.__dict__.copy()
    item_dict['images'] = images_list

    return item_dict




def get_number_of_items(db: Session, visibility_filter: str = None):
    
    query = db.query(func.count(Item.item_pk))
    if visibility_filter:
        query = query.filter(Item.item_visibility == visibility_filter)
    return query.scalar()



def get_items_limit_offset(
    db: Session, 
    limit: int, 
    offset: int = 0, 
    visibility_filter: str = None
):
    # Subquery for at finde den nyeste blocked-log for hvert item
    latest_blocked_log = (
        db.query(
            ItemBlockedLog.item_pk,
            func.max(ItemBlockedLog.item_blocked_updated_at).label("latest_blocked")
        )
        .group_by(ItemBlockedLog.item_pk)
        .subquery()
    )

    # Hovedforespørgsel
    query = (
        db.query(
            Item,  # Hent alle kolonner fra Item-modellen
            func.coalesce(func.avg(Rating.stars), 0).label("item_stars"),  # Beregn gennemsnit af stjerner
            func.group_concat(ItemImage.image_filename.distinct()).label("images"),  # Aggreger billeder
            func.coalesce(
                db.query(ItemBlockedLog.item_blocked_value)  # Subquery for blocked_value
                .filter(
                    ItemBlockedLog.item_pk == Item.item_pk,
                    ItemBlockedLog.item_blocked_updated_at == latest_blocked_log.c.latest_blocked
                )
                .as_scalar(), 0
            ).label("item_is_blocked"),  # Hent blocked-status
        )
        .outerjoin(Rating, Item.item_pk == Rating.item_pk)  # Venstresammenføjning med Rating
        .outerjoin(ItemImage, Item.item_pk == ItemImage.item_pk)  # Venstresammenføjning med ItemImage
        .group_by(Item.item_pk)  # Gruppér på item_pk
        .order_by(Item.item_created_at)  # Sortér efter oprettelsestidspunkt
    )

    # Tilføj filtrering baseret på synlighed
    if visibility_filter:
        query = query.filter(Item.item_visibility == visibility_filter)

    # Tilføj limit og offset
    query = query.limit(limit).offset(offset)

    # Hent resultaterne
    results = query.all()

    # Forbered data til returnering
    items = []
    for item, stars, images, blocked in results:
        # Konverter billeder til en liste
        images_list = [f"/images/{img}" for img in images.split(",")] if images else []
        # Lav en dictionary for hvert item
        item_dict = item.__dict__.copy()
        # Fjern "_sa_instance_state", som ikke kan konverteres til JSON
        del item_dict["_sa_instance_state"]
        item_dict.update({
            "item_stars": float(stars),
            "images": images_list,
            "item_visibility": item_dict["item_visibility"].value if item_dict["item_visibility"] else "PRIVATE",
            "item_is_blocked": bool(blocked),
        })
        items.append(item_dict)

    return items

def get_items_by_user(db: Session, user_pk: str):
    # Forespørg items for den specifikke bruger
    query = ItemQueryManager.get_items_with_status(db).filter(Item.item_owned_by == user_pk)

    # Udfør forespørgslen
    items = query.order_by(Item.item_created_at).all()
     # Formater resultaterne
    formatted_items=ItemQueryManager.format_items(items)

    return formatted_items


def update_image(db: Session, image_filename: str, item_pk: str, oldname: str):
    # Forespørg for at finde det eksisterende billede
    image = (
        db.query(ItemImage)
        .filter(ItemImage.item_pk == item_pk, ItemImage.image_filename == oldname)
        .first()
    )

    # Opdater filnavnet, hvis billedet findes
    if image:
        image.image_filename = image_filename
        db.commit()
        db.refresh(image)  # Opdater objektet efter ændringer
        return image
    else:
        return None  # Returner None, hvis billedet ikke findes



def update_item(db: Session, item_name: str, item_lat: str, item_lon: str, item_price_per_night: float, item_pk: str):
    # Forespørg for at finde det eksisterende item
    item = db.query(Item).filter(Item.item_pk == item_pk).first()

    # Opdater felterne, hvis item findes
    if item:
        item.item_name = item_name
        item.item_lat = item_lat
        item.item_lon = item_lon
        item.item_price_per_night = item_price_per_night

        # Gem ændringerne i databasen
        db.commit()
        db.refresh(item)  # Opdater objektet med de nyeste værdier
        return item
    else:
        return None  # Returner None, hvis item ikke findes
    

def delete_item(db: Session, item_pk: str):
    # Sletning af relaterede data i korrekt rækkefølge
    db.query(Rating).filter(Rating.item_pk == item_pk).delete()
    db.query(ItemBlockedLog).filter(ItemBlockedLog.item_pk == item_pk).delete()
    db.query(ItemUpdatedLog).filter(ItemUpdatedLog.item_pk == item_pk).delete()
    db.query(ItemImage).filter(ItemImage.item_pk == item_pk).delete()
    db.query(Booking).filter(Booking.item_pk == item_pk).delete()
    
    # Slet selve itemet
    db.query(Item).filter(Item.item_pk == item_pk).delete()

    # Gem ændringerne i databasen
    db.commit()



def toggle_block_item(db: Session, new_blocked_status: int, updated_at: int, item_uuid: str):
    # Opret en ny række i item_blocked_log
    blocked_log = ItemBlockedLog(
        item_pk=item_uuid,
        item_blocked_updated_at=updated_at,
        item_blocked_value=new_blocked_status
    )

    # Tilføj til session og gem ændringer
    db.add(blocked_log)
    db.commit()
    db.refresh(blocked_log)  # Opdater objektet med de nyeste værdier

    return blocked_log

def toggle_visibility_item(db: Session, new_visibility_status: int, updated_at: int, item_uuid: str):
    # Opret en ny række i item_visibility_log
    visibility_log = ItemVisibilityLog(
        item_pk=item_uuid,
        item_visibility_updated_at=updated_at,
        item_visibility_value=new_visibility_status
    )

    # Tilføj til session og gem ændringer
    db.add(visibility_log)
    db.commit()
    db.refresh(visibility_log)  # Opdater objektet med de nyeste værdier

    return visibility_log

