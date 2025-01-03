from decimal import Decimal

from .models.item import Item, ItemImage
from .models.item_logs import ItemBlockedLog, ItemUpdatedLog, ItemVisibilityLog 
from .models.user import User
from .models.user_logs import PasswordResetLog, UserBlockedLog, UserUpdatedLog, UserVerificationRequest,UserVerificationCompleted,UserDeletedLog
from .models.ratings import Rating
from .models.bookings import Booking

from .events.user_events import insert_user_blocked_listener, update_user_listener
from .events.item_events import insert_item_blocked_listener, update_item_listener, insert_item_visibility_listener

from sqlalchemy.orm import Session

from .queryManagers import ItemQueryManager, UserQueryManager



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



def create_user(
    db: Session,
    user_pk: str,
    user_username: str,
    user_first_name: str,
    user_last_name: str,
    user_email: str,
    hashed_password: str,
    user_created_at: int,
    user_verification_key: str
):
    from models.user import RoleEnum  # Importer RoleEnum, hvis det ikke allerede er gjort

    # Sæt rollen til 'user' som standard
    default_role = RoleEnum.USER

    # Opret en ny brugerinstans
    new_user = User(
        user_pk=user_pk,
        user_username=user_username,
        user_first_name=user_first_name,
        user_last_name=user_last_name,
        user_email=user_email,
        user_password=hashed_password,
        user_role=default_role,  # Brug standardrollen
        user_created_at=user_created_at
    )

    # Opret en ny user_verification_request
    verification_request = UserVerificationRequest(
        user_pk=user_pk,
        user_verification_key=user_verification_key
    )

    # Tilføj til session og commit
    db.add(new_user)
    db.add(verification_request)
    db.commit()

    # Opdater objekterne, hvis nødvendigt
    db.refresh(new_user)
    db.refresh(verification_request)

    return new_user, verification_request





def create_password_reset(db: Session, password_reset_key: str, password_reset_at: int, user_pk: str):
    # Opret en ny instans af PasswordResetLog
    password_reset = PasswordResetLog(
        password_reset_key=password_reset_key,
        password_reset_at=password_reset_at,
        user_pk=user_pk
    )

    # Tilføj til session og commit
    db.add(password_reset)
    db.commit()
    db.refresh(password_reset)  # Opdater objektet, hvis nødvendigt
    return password_reset



def object_as_dict(obj):
    return {column.key: getattr(obj, column.key) for column in obj.__table__.columns}


def get_reset_info(db: Session, key: str):
    # Join PasswordResetLog med User
    reset_info = (
        db.query(PasswordResetLog, User)
        .join(User, User.user_pk == PasswordResetLog.user_pk)
        .filter(PasswordResetLog.password_reset_key == key)
        .first()
    )

    if reset_info:
        reset_log, user = reset_info  # Split resultatet i PasswordResetLog og User

        # Kombinér dataene i én dictionary
        return {
            "reset_log": {
                "user_pk": reset_log.user_pk,
                "password_reset_key": reset_log.password_reset_key,
                "password_reset_at": reset_log.password_reset_at,
            },
            "user": {
                "user_first_name": user.user_first_name,
                "user_last_name": user.user_last_name,
            },
        }

    return None




def get_item(db: Session, item_pk: str):
    from sqlalchemy import func
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
    from sqlalchemy import func
    
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
    from sqlalchemy import func
    # Get the latest blocked status subquery
    latest_blocked_log = (
        db.query(ItemBlockedLog.item_blocked_value)
        .filter(ItemBlockedLog.item_pk == Item.item_pk)
        .order_by(ItemBlockedLog.item_blocked_updated_at.desc())
        .limit(1)
        .correlate(Item)
    )

    # Udfør forespørgslen med aggregering og pagination
    query = (
        db.query(
            Item,  # Hent alle kolonner fra Item-modellen
            func.coalesce(func.avg(Rating.stars), 0).label("item_stars"),  # Beregn gennemsnit af stjerner
            func.group_concat(ItemImage.image_filename.distinct()).label("images"),  # Aggreger billeder
            func.coalesce(latest_blocked_log.as_scalar(), 0).label("item_is_blocked")  # Get blocked status
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
    for item, stars, images, is_blocked in results:
        # Convert SQLAlchemy model to dict
        # item_dict = {
        #     "item_pk": item.item_pk,
        #     "item_name": item.item_name,
        #     "item_lat": float(item.item_lat),  # Convert to float for JSON
        #     "item_lon": float(item.item_lon),  # Convert to float for JSON
        #     "item_price_per_night": float(item.item_price_per_night),
        #     "item_created_at": item.item_created_at,
        #     "item_owned_by": item.item_owned_by,
        #     "item_stars": float(stars),
        #     "images": images.split(",") if images else [],
        #     "item_is_blocked": is_blocked  # Add blocked status to the dictionary
        # }
        # Konverter billeder til en liste
        images_list = [f"/images/{img}" for img in images.split(",")] if images else []
        # Lav en dictionary for hvert item
        item_dict = item.__dict__.copy()
        # Fjern "_sa_instance_state", som ikke kan konverteres til JSON
        del item_dict["_sa_instance_state"]
        item_dict.update({
            "item_stars": float(stars.quantize(Decimal("1.0"))),
            "images": images_list
        })
        items.append(item_dict)
    return items




def get_all_users(db: Session):
    users = UserQueryManager.get_users_with_status(db)
    return users


def get_user_by_email(db, user_email):
    # Brug UserQueryManager til at hente brugeren med de nødvendige filtre
    users = UserQueryManager.get_users_with_status(
        session=db,
        email=user_email,
        is_verified=True,
        is_deleted=False
    )

    # Returnér den første bruger, hvis en findes
    return users[0] if users else None



def get_user_name_and_email(db: Session, user_pk: str):
    # Udfør forespørgslen
    user = (
        db.query(User.user_first_name, User.user_email)
        .filter(User.user_pk == user_pk)
        .first()
    )

    # Returnér som dictionary, hvis bruger findes
    if user:
        return {
            "user_first_name": user.user_first_name,
            "user_email": user.user_email,
        }
    return None


def get_user(db, user_pk):
    # Brug UserQueryManager med direkte filtrering
    users = UserQueryManager.get_users_with_status(
        session=db,
        user_pk=user_pk,
        is_verified=None,
        is_deleted=None
    )
    user = users[0] if users else None
    return user



def get_user_password(db: Session, user_pk: str):
    # Forespørg på brugernes adgangskode
    user = (
        db.query(User.user_password)
        .filter(User.user_pk == user_pk)
        .first()
    )

    # Returnér adgangskoden, hvis brugeren findes
    if user:
        return user.user_password
    return None


def get_items_by_user(db: Session, user_pk: str):
    # Forespørg items for den specifikke bruger
    query = ItemQueryManager.get_items_with_status(db).filter(Item.item_owned_by == user_pk)

    # Udfør forespørgslen
    items = query.order_by(Item.item_created_at).all()
     # Formater resultaterne
    formatted_items=ItemQueryManager.format_items(items)

    return formatted_items


def get_user_by_item(db: Session, item_uuid: str):
    # Forespørg brugeren baseret på item_uuid
    user = (
        db.query(
            User.user_first_name,
            User.user_email,
        )
        .join(Item, Item.item_owned_by == User.user_pk)  # Join mellem items og users
        .filter(Item.item_pk == item_uuid)  # Filter baseret på item_uuid
        .first()
    )

    # Returnér som dictionary, hvis bruger findes
    if user:
        return {
            "user_first_name": user.user_first_name,
            "user_email": user.user_email,
        }
    return None



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



def update_user(db: Session, username: str, first_name: str, last_name: str, email: str, user_pk: str):
    # Forespørg for at finde den eksisterende bruger
    user = db.query(User).filter(User.user_pk == user_pk).first()

    # Opdater felterne, hvis brugeren findes
    if user:
        user.user_username = username
        user.user_first_name = first_name
        user.user_last_name = last_name
        user.user_email = email

        # Gem ændringerne i databasen
        db.commit()
        db.refresh(user)  # Opdater objektet med de nyeste værdier
        return user
    else:
        return None  # Returner None, hvis brugeren ikke findes



def update_user_password(db: Session, hashed_password: str, user_pk: str):
    # Forespørg for at finde den eksisterende bruger
    user = db.query(User).filter(User.user_pk == user_pk).first()

    # Opdater adgangskoden, hvis brugeren findes
    if user:
        user.user_password = hashed_password

        # Gem ændringerne i databasen
        db.commit()
        db.refresh(user)  # Opdater objektet med de nyeste værdier
        return user
    else:
        return None  # Returner None, hvis brugeren ikke findes



def update_verification_status(db: Session, user_is_verified_at: int, key: str):
    # Forespørg for at finde user_pk baseret på verificeringsnøglen
    verification_request = (
        db.query(UserVerificationRequest)
        .filter(UserVerificationRequest.user_verification_key == key)
        .first()
    )

    if verification_request:
        user_pk = verification_request.user_pk

        # Opret en ny række i user_verification_completed
        verification_completed = UserVerificationCompleted(
            user_pk=user_pk,
            user_is_verified_at=user_is_verified_at
        )

        # Tilføj til session og gem ændringer
        db.add(verification_completed)
        db.commit()
        db.refresh(verification_completed)  # Opdater objektet med de nyeste værdier

        return verification_completed
    else:
        return None  # Returner None, hvis verificeringsnøglen ikke findes




def delete_user(db: Session, deleted_at: int, user_pk: str):
    # Opret en ny række i user_deleted_log
    deleted_log = UserDeletedLog(
        user_pk=user_pk,
        user_deleted_at=deleted_at
    )

    # Tilføj til session og gem ændringer
    db.add(deleted_log)
    db.commit()
    db.refresh(deleted_log)  # Opdater objektet med de nyeste værdier

    return deleted_log


def update_user_role_to_partner(db: Session, user_pk: str):
    from models.user import RoleEnum  # Sørg for at importere RoleEnum

    # Hent brugeren fra databasen
    user = db.query(User).filter(User.user_pk == user_pk).first()

    if not user:
        raise Exception(f"User with id {user_pk} does not exist")

    # Tjek om brugeren allerede er en partner
    if user.user_role == RoleEnum.PARTNER:
        raise Exception(f"User with id {user_pk} is already a partner")

    # Opdater rollen til partner
    user.user_role = RoleEnum.PARTNER
    db.commit()
    db.refresh(user)  # Opdater brugerobjektet med de nyeste værdier fra databasen

    return user



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


def toggle_block_user(db: Session, new_blocked_status: int, updated_at: int, user_pk: str):
    # Opret en ny række i user_blocked_updated_log
    blocked_log = UserBlockedLog(
        user_pk=user_pk,
        user_blocked_updated_at=updated_at,
        user_blocked_value=new_blocked_status
    )

    # Tilføj til session og gem ændringer
    db.add(blocked_log)
    db.commit()
    db.refresh(blocked_log)  # Opdater objektet med de nyeste værdier

    return blocked_log



def create_booking(
    db: Session, 
    user_pk: str, 
    item_pk: str, 
    booking_created_at: int, 
    booking_number_of_nights: int, 
    booking_price: float
):
    # Opret en ny række i bookings
    booking = Booking(
        user_pk=user_pk,
        item_pk=item_pk,
        booking_created_at=booking_created_at,
        booking_number_of_nights=booking_number_of_nights,
        booking_price=booking_price
    )

    # Tilføj til session og gem ændringer
    db.add(booking)
    db.commit()
    db.refresh(booking)  # Opdater objektet med de nyeste værdier

    return booking