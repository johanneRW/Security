from bottle import post, put, template, response
from utility import utils
from icecream import ic
import uuid
import os
import time
import uuid
from utility import utils
from database import data


@post("/items/image/<item_pk>")
def _(item_pk): 
    try:
        image_folder = utils.get_image_folder()
        
        # Validate and save image
        image, image_filename = utils.validate_image()
        image_path = os.path.join(image_folder, image_filename)
        image.save(image_path)

        
        image_pk=uuid.uuid4().hex

        db = utils.db()
        data.create_image(db, image_pk, item_pk, image_filename)

        item = data.get_item(db, item_pk)
        html = template("_item_detail.html", item=item)
        return f"""
        <template mix-target="#frm_item_{item_pk}" mix-replace mix-function="closeModal">
        {html}
        </template>
        """
       
    except Exception as ex:
        ic(ex)
        raise
        response.status = 400 
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Error when saving image
            </div>
            </template>
            """
    finally:
        if "db" in locals(): db.close()


@put("/items/image/<item_pk>")
def _(item_pk): 
    try:
        image_folder = utils.get_image_folder()
        
        oldname = utils.validate_oldname()

        # Validate and save image
        image, image_filename = utils.validate_image()
        image.save(os.path.join(image_folder, image_filename))
        
        db = utils.db()
        data.update_image(db, image_filename, item_pk, oldname,)

        item = data.get_item(db, item_pk)
        
        html = template("_item_detail.html", item=item)
        return f"""
        <template mix-target="#frm_item_{item_pk}" mix-replace mix-function="closeModal">
        {html}
        </template>
        """
       
    except Exception as ex:
        ic(ex)
        response.status = 400 
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Error when updating image
            </div>
            </template>
            """
    finally:
        if "db" in locals(): db.close()