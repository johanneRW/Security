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


@put("/items/<item_pk>")
def _(item_pk): 
    try:
        
        item_name = utils.validate_item_name()
        #item_splash_image = utils.validate_item_splash_image()
        item_lat = utils.validate_item_lat()
        item_lon = utils.validate_item_lon()
        item_price_per_night = utils.validate_item_price_per_night()
        updatet_at=int(time.time())



        image_folder = utils.get_image_folder()

        # Validate and save splash image
        splash_image, splash_image_filename = utils.validate_splash_image()
        splash_image.save(os.path.join(image_folder, splash_image_filename))

        # Validate and save additional images
        additional_images = utils.validate_additional_images()
        additional_image_filenames = []
        for file, filename in additional_images:
            file.save(os.path.join(image_folder, filename))
            additional_image_filenames.append(filename)

        
        db = utils.db()
        db.execute("""
            UPDATE items SET item_name=?, item_splash_image=?, item_lat=?, item_lon=?, item_price_per_night=?, item_updated_at=?
            WHERE item_pk=?
        """, (
            item_name,
            splash_image_filename,
            item_lat,
            item_lon,
            item_price_per_night,
            updatet_at,
            item_pk
        ))
        db.commit()

        for filename in additional_image_filenames:
            image_pk = uuid.uuid4().hex
            db.execute("""
                INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES (?, ?, ?)
            """, (image_pk, item_pk, filename))
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
        raise
        return f"""
        <template mix-target="#message">
            {ex.args[1]}
        </template>
        """            
    finally:
        pass