from bottle import post, request, response, template
from utility import utils
from icecream import ic
import credentials
import time
from utility import data

@post("/bookings/<item_pk>")
def _(item_pk):
    try:
        
        user = request.get_cookie("user", secret= credentials.COOKIE_SECRET)
        if user:

            user_pk=user['user_pk']
            db = utils.db()
            item=data.get_item(db,item_pk)
            item_price=item['item_price_per_night']
            number_of_nights=utils.validate_number_of_nights()
            booking_price=float(item_price)*int(number_of_nights)
            booking_created_at= int(time.time())
            data.create_booking(db, user_pk ,item_pk, booking_created_at , number_of_nights ,booking_price)
        
            btn_book = template("__btn_book", item=item)
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

    except Exception as ex:
        raise
        ic(ex)
        response.status = 303 
        response.set_header('Location', '/login')
        return
    finally:
        if "db" in locals(): db.close()