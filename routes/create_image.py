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


@post("/items/image/<item_pk>")
def _(item_pk): 
    try:
        image_folder = utils.get_image_folder()
        updatet_at=int(time.time())
        
        # Validate and save image
        image, image_filename = utils.validate_image()
        image.save(os.path.join(image_folder, image_filename))
        
        image_pk=uuid.uuid4().hex

        db = utils.db()
        db.execute("""
            INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES (?, ?, ?)
            """, (
            image_pk,                       
            item_pk,
            image_filename,
        ))
        db.commit()

        #q = db.execute("SELECT * FROM items WHERE item_pk=? LIMIT 1", (item_pk,))
        q = db.execute("""
                SELECT items.*, 
                       group_concat(item_images.image_filename) AS images
                FROM items
                LEFT JOIN item_images ON items.item_pk = item_images.item_pk
                WHERE items.item_pk = ?
                GROUP BY items.item_pk
            """, 
            (item_pk,)
        )
        item = q.fetchone()
        item['images'] = item['images'].split(',')
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