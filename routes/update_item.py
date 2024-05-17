import time
from bottle import delete, get, post, put, request,response, static_file, template
import utils
from icecream import ic
import uuid
import bcrypt 
import variables
import credentials



@put("/items/<item_pk>")
def _(item_pk): 
    try:
        
        item_name = utils.validate_item_name()
        item_splash_image = utils.validate_item_splash_image()
        item_lat = utils.validate_item_lat()
        item_lon = utils.validate_item_lon()
        item_price_per_night = utils.validate_item_price_per_night()
        updatet_at=int(time.time())

        
        db = utils.db()
        db.execute("""
            UPDATE items SET 
                item_name = ?, 
                item_splash_image = ?, 
                item_lat = ?, 
                item_lon = ?,  
                item_price_per_night = ?,
                item_updated_at = ?
            WHERE item_pk = ?
        """, (
            item_name, 
            item_splash_image, 
            item_lat, 
            item_lon,  
            item_price_per_night, 
            updatet_at,  
            item_pk
        ))
        db.commit()

        q = db.execute("SELECT * FROM items WHERE item_pk=? LIMIT 1", (item_pk,))
        item = q.fetchone()

        html = template("_item_detail.html", item=item)
        return f"""
        <template mix-target="frm_item_{item_pk}" mix-replace>
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
        pass