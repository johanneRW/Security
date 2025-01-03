from sqlalchemy.orm import Session
from ..models.item import Item 
from ..models.user import User, RoleEnum
from ..models.user_logs import PasswordResetLog, UserBlockedLog, UserUpdatedLog, UserVerificationRequest,UserVerificationCompleted,UserDeletedLog
from ..queryManagers import  UserQueryManager
from ..events.user_events import insert_user_blocked_listener, update_user_listener
from ..events.item_events import insert_item_blocked_listener, update_item_listener, insert_item_visibility_listener



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
        email=None,
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


