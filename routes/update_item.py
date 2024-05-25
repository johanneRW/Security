import time
from bottle import delete, get, post, put, request,response, static_file, template
import utils
from icecream import ic
import uuid
import bcrypt 
import variables
import credentials
import os
import time
import uuid
from werkzeug.utils import secure_filename
import utils
import credentials
from utility import data


@put("/items/<item_pk>")
def _(item_pk): 
    try:
        
        item_name = utils.validate_item_name()
        item_lat = utils.validate_item_lat()
        item_lon = utils.validate_item_lon()
        item_price_per_night = utils.validate_item_price_per_night()
     


        db = utils.db()
        data.update_item(db,item_name,item_lat,item_lon,item_price_per_night,item_pk )
        item = data.get_item(db, item_pk)
        
        html = template("_item_detail.html", item=item)
        return f"""
        <template mix-target="frm_item_{item_pk}" mix-replace>
        {html}
        </template>
        """
       
    except Exception as ex:
        ic(ex)
        raise
        return f"""
        <template mix-target="#message">
            {ex.args[1]}
        </template>
        """            
    finally:
        pass