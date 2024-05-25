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
from utility import data




@post("/items")
def _():
    try:
        user = request.get_cookie("user", secret= credentials.COOKIE_SECRET)

        item_pk=uuid.uuid4().hex
        item_name=utils.validate_item_name()
        item_lat=utils.validate_item_lat()
        item_lon=utils.validate_item_lon()
        item_price_per_night=utils.validate_item_price_per_night()
        item_created_at=int(time.time())
        item_owned_by=user['user_pk']


        ic(item_owned_by)

        
        db = utils.db()
        
        data.create_item(
            db, 
            item_pk, 
            item_name,
            item_lat, 
            item_lon, 
            item_price_per_night, 
            item_created_at, 
            item_owned_by
        )
        
        item = data.get_item(db, item_pk)
        ic(item)

        
        html = template("_item_detail.html", item=item)
       
        return f"""
        <template mix-target="frm_item_{item_pk}" mix-bottom mix-function="updateModalEvents">
        {html}
        </template>
        <template mix-target="#items" mix-bottom mix-function="updateModalEvents">
        {html}
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
