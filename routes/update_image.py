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


@put("/items/image/<item_pk>")
def _(item_pk): 
    try:
        image_folder = utils.get_image_folder()
        updatet_at=int(time.time())
        
        oldname = utils.validate_oldname()

        # Validate and save image
        image, image_filename = utils.validate_image()
        image.save(os.path.join(image_folder, image_filename))
        
        db = utils.db()
        data.update_image(db, image_filename, item_pk, oldname,)

        item = data.get_item(db, item_pk)
        
        html = template("_item_detail.html", item=item)
        return f"""
        <template mix-target="frm_item_{item_pk}" mix-replace mix-function="closeModal">
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