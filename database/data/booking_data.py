from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_ , func
from ..models.item import Item 
from ..models.ratings import Rating
from ..models.bookings import Booking
from sqlalchemy.orm import Session
from ..events.user_events import insert_user_blocked_listener, update_user_listener
from ..events.item_events import insert_item_blocked_listener, update_item_listener, insert_item_visibility_listener



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



def get_user_bookings_with_ratings_and_owner(db: Session, user_pk: str):
    # Forespørgsel til at hente bookinger, ratings og ejeren af ejendommen
    results = (
        db.query(
            Booking.item_pk,
            Booking.booking_created_at,
            Booking.booking_number_of_nights,
            Booking.booking_price,
            Item.item_name,
            Item.item_owned_by,  # Tilføj ejeren af ejendommen
            func.coalesce(
                Rating.stars, 0  # Hvis ingen rating er tilgængelig, returner 0
            ).label("user_rating")
        )
        .join(Item, Booking.item_pk == Item.item_pk)  # Join med Item-tabellen
        .outerjoin(
            Rating,
            (Rating.item_pk == Booking.item_pk) & (Rating.user_pk == Booking.user_pk)
        )  # Join med Rating-tabellen for brugerens rating for ejendommen
        .filter(Booking.user_pk == user_pk)  # Filtrér for den specifikke bruger
        .order_by(Booking.booking_created_at.desc())  # Sortér efter booking-tidspunkt (nyeste først)
        .all()
    )

    # Konverter resultater til liste af dictionaries
    bookings_with_ratings = []
    for result in results:
        # Konverter booking_created_at til datoformat (dd-mm-yyyy)
        booking_date = datetime.utcfromtimestamp(result.booking_created_at).strftime('%d-%m-%Y')

        bookings_with_ratings.append({
            "item_pk": result.item_pk,
            "item_name": result.item_name,
            "booking_created_at": booking_date,  # Bruger læsevenligt datoformat
            "booking_number_of_nights": result.booking_number_of_nights,
            "booking_price": result.booking_price,
            "user_rating": result.user_rating,  # Rating givet af brugeren
            "item_owner": result.item_owned_by  # Tilføj ejerens ID
        })

    return bookings_with_ratings




def rate_item(db: Session, user_pk: str, item_pk: str, stars: int):
    """
    Tildeler stjerner til en ejendom, hvis bookingen er afsluttet, og brugeren ikke ejer ejendommen.
    Returns:
        dict: Succes- eller fejlinformation.
    """
    try:
        # Tjek om ejendommen tilhører brugeren (brugeren må ikke rate sin egen ejendom)
        item = db.query(Item).filter(Item.item_pk == item_pk).first()
        if not item:
            return {"error": "Item not found"}
        if item.item_owned_by == user_pk:
            return {"error": "You cannot rate your own property"}

        # Find booking for ejendommen og brugeren
        now = int(datetime.utcnow().timestamp())
        booking = (
            db.query(Booking)
            .filter(
                and_(
                    Booking.user_pk == user_pk,
                    Booking.item_pk == item_pk,
                
                )
            )
            .first()
        )

        if not booking:
            return {"error": "No completed booking found for this property"}

        # Tildel eller opdater stjerner
        existing_rating = (
            db.query(Rating)
            .filter(and_(Rating.user_pk == user_pk, Rating.item_pk == item_pk))
            .first()
        )

        if existing_rating:
            # Opdater eksisterende rating
            existing_rating.stars = stars
            existing_rating.rating_created_at = now
            db.commit()
            db.refresh(existing_rating)
            return {"success": "Rating updated successfully", "rating": stars}
        else:
            # Opret en ny rating
            new_rating = Rating(
                user_pk=user_pk,
                item_pk=item_pk,
                stars=stars,
                rating_created_at=now
            )
            db.add(new_rating)
            db.commit()
            db.refresh(new_rating)
            return {"success": "Rating created successfully", "rating": stars}

    except IntegrityError as e:
        db.rollback()
        return {"error": "Database error occurred", "details": str(e)}
    except Exception as ex:
        db.rollback()
        return {"error": "An error occurred", "details": str(ex)}
    
    

def get_booking_by_user_and_item_with_ratings(db: Session, user_pk: str, item_pk: str):
    try:
        # Forespørg for at hente booking med ratings og ejeroplysninger
        result = (
            db.query(
                Booking.item_pk,
                Booking.booking_created_at,
                Booking.booking_number_of_nights,
                Booking.booking_price,
                Item.item_name,
                Item.item_owned_by.label("item_owner"),  # Ejerens ID
                func.coalesce(Rating.stars, 0).label("user_rating")  # Brugerens rating (hvis den findes)
            )
            .join(Item, Booking.item_pk == Item.item_pk)  # Join med Item-tabellen
            .outerjoin(
                Rating,
                (Rating.item_pk == Booking.item_pk) & (Rating.user_pk == Booking.user_pk)
            )  # Join med Rating-tabellen for brugerens rating
            .filter(Booking.user_pk == user_pk, Booking.item_pk == item_pk)  # Filtrér efter user_pk og item_pk
            .first()
        )

        # Returnér som et dictionary, hvis booking findes
        if result:
            # Konverter booking_created_at til datoformat (dd-mm-yyyy)
            booking_date = datetime.utcfromtimestamp(result.booking_created_at).strftime('%d-%m-%Y')

            return {
                "item_pk": result.item_pk,
                "item_name": result.item_name,
                "booking_created_at": booking_date,  # Bruger læsevenligt datoformat
                "booking_number_of_nights": result.booking_number_of_nights,
                "booking_price": result.booking_price,
                "user_rating": result.user_rating,  # Rating givet af brugeren
                "item_owner": result.item_owner  # Ejerens ID
            }

        # Hvis ingen booking findes, returnér None
        return None

    except Exception as ex:
        print(f"Error fetching booking: {ex}")
