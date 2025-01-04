from bottle import get, post, request, response, template
from utility import utils
from icecream import ic
import settings
import time
from database.data import booking_data, item_data

@post("/bookings/<item_pk>")
def _(item_pk):
    try:
        csrf_token = request.forms.get('csrf_token')
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        if not utils.validate_csrf_token(csrf_token, user.get("user_pk")):
            raise ValueError("Invalid CSRF token")
        
        if user:
            user_pk = user['user_pk']
            db = utils.db()
            item = item_data.get_item(db, item_pk)
            item_price = item['item_price_per_night']
            number_of_nights = utils.validate_number_of_nights()
            booking_price = float(item_price) * int(number_of_nights)
            booking_created_at = int(time.time())
            booking_data.create_booking(db, user_pk, item_pk, booking_created_at, number_of_nights, booking_price)
        
            csrf_token = utils.generate_csrf_token(user.get("user_pk"))
            btn_book = template("__btn_book", item=item, csrf_token=csrf_token)
            return f"""
            <template mix-target="#item_booking_{item_pk}" mix-replace>
                {btn_book}
            </template>
            <template mix-target="#toast">
            <div mix-ttl="9000" class="ok">
                    Created booking of {item['item_name']} 
                    for {number_of_nights} nights * {item_price}DKK
                    Total {booking_price} DKK
            </div>
            </template>
            """
        else:
            response.status = 403
            return "you must be logged in"
    except Exception as ex:
        ic(ex)
        response.status = 400 
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Error when creating booking
            </div>
            </template>
            """
    finally:
        if "db" in locals(): db.close()
        


@get("/bookings")
def bookings():
    try:
        csrf_token = utils.get_csrf_token()

        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        if not user:
            response.status = 403
            return "You must be logged in"

        db = utils.db()
        user_pk = user['user_pk']
        bookings = booking_data.get_user_bookings_with_ratings_and_owner(db, user_pk)
        return template("bookings.html", bookings=bookings, is_logged=True, user=user, csrf_token=csrf_token)
    except Exception as ex:
        raise
        ic(ex)
        response.status = 500
        return {"error": "Something went wrong."}
    finally:
        if "db" in locals():
            db.close()


@post("/rate_item/<item_pk>")
def rate_item_endpoint(item_pk):
    try:
        csrf_token = utils.validate_csrf_token()

        # Valider, at brugeren er logget ind
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        if not user:
            response.status = 403
            return "You must be logged in"

        # Få brugerens primærnøgle
        user_pk = user['user_pk']

        # Valider input for stjerner via utils.validate_item_stars()
        stars = int(utils.validate_item_stars())

        # Opret databaseforbindelse
        db = utils.db()

        # Kald funktionen til at rate ejendommen
        result = booking_data.rate_item(db, user_pk, item_pk, stars)
        booking = booking_data.get_booking_by_user_and_item_with_ratings(db, user_pk, item_pk)
        html = template("_booking_details.html", booking=booking, user=user, csrf_token=csrf_token)

        # Håndtér resultatet
        if "error" in result:
            response.status = 400
            return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                {result['error']}
            </div>
            </template>
            """
        else:
            return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="ok">
                {result['success']}
            </div>
            </template>
            
            <template mix-target="#booking_{item_pk}" mix-replace">
            {html}
            </template>
            """

    except Exception as ex:
        raise
        ic(ex)
        response.status = 500
        return """
        <template mix-target="#toast">
        <div mix-ttl="3000" class="error">
            Something went wrong while rating the item.
        </div>
        </template>
        """
    finally:
        if "db" in locals(): db.close()
