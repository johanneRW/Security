import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put 
import utils
from icecream import ic
import bcrypt
import json
import credentials
import time
import variables
from send_email import send_email
import os
import time
import uuid
from werkzeug.utils import secure_filename
import utils
import credentials




@post("/items")
def _():
    try:
#     item_pk                         TEXT,
#     item_name                       TEXT,
#     item_splash_image               TEXT,
#     item_lat                        TEXT,
#     item_lon                        TEXT,
#     item_price_per_night            REAL,
#     item_created_at                 INTEGER,
#     item_updated_at                 INTEGER,
#     item_is_blocked                 INTEGER,
#     item_blocked_updated_at         INTEGER,
#     item_owned_by                   TEXT,
        user = request.get_cookie("user", secret= credentials.COOKIE_SECRET)

        item_pk=uuid.uuid4().hex
        item_name=utils.validate_item_name()
        item_splash_image=utils.validate_item_splash_image()
        item_lat=utils.validate_item_lat()
        item_lon=utils.validate_item_lon()
        item_price_per_night=utils.validate_item_price_per_night()
        item_created_at=int(time.time())
        item_updated_at=None
        item_is_blocked=0
        item_blocked_updated_at=None
        item_owned_by=user['user_pk']


        ic(item_owned_by)

        
        db = utils.db()
        new_item=db.execute("""
            INSERT INTO items (
                item_pk, 
                item_name, 
                item_splash_image, 
                item_lat, 
                item_lon, 
                item_price_per_night, 
                item_created_at, 
                item_updated_at, 
                item_is_blocked, 
                item_blocked_updated_at, 
                item_owned_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_pk, 
            item_name, 
            item_splash_image, 
            item_lat, 
            item_lon, 
            item_price_per_night, 
            item_created_at, 
            item_updated_at,
            item_is_blocked, 
            item_blocked_updated_at, 
            item_owned_by
        ))
        db.commit()


        q=db.execute("SELECT * FROM items WHERE item_pk = ?", (item_pk,))
        item = q.fetchone()
        ic(item)

        
        html = template("_item_detail.html", item=item)
        html_create=template("create_item")
        return f"""
        <template mix-target="#items" mix-bottom>
        {html}
        </template>
         <template mix-target="#new_item" mix-replace>
        {html_create}
        </template>
        """
       
    except Exception as ex:
        ic(ex)
        return f"""
        <template mix-target="#message">
            {ex.args[1]}
        </template>
        """            
    finally:
        if "db" in locals(): db.close()
