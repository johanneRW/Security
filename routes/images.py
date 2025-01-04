from bottle import post, put, template, response, request
from utility import utils
from icecream import ic
import uuid
import os
import time
import uuid
from utility import utils
import settings
from database.data import item_data


@post("/items/image/<item_pk>")
def _(item_pk): 
    try:
        # Get token and validate with user_pk
        csrf_token = request.forms.get('csrf_token')
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        if not utils.validate_csrf_token(csrf_token, user.get("user_pk")):
            raise ValueError("Invalid CSRF token")
            
        image_folder = utils.get_image_folder()
        
        # Validate and save image
        image, image_filename = utils.validate_image()
        image_path = os.path.join(image_folder, image_filename)
        image.save(image_path)

        
        image_pk=uuid.uuid4().hex

        db = utils.db()
        item_data.create_image(db, image_pk, item_pk, image_filename)
        item = item_data.get_item(db, item_pk)

        # Generate new token for response
        csrf_token = utils.generate_csrf_token(user.get("user_pk"))

        html = template("_item_detail.html", item=item, csrf_token=csrf_token)
        return f"""
        <template mix-target="#item_{item_pk}" mix-replace mix-function="closeModal">
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
        # Get token and validate with user_pk
        csrf_token = request.forms.get('csrf_token')
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        if not utils.validate_csrf_token(csrf_token, user.get("user_pk")):
            raise ValueError("Invalid CSRF token")
            
        image_folder = utils.get_image_folder()
        
        oldname = utils.validate_oldname()

        # Validate and save image
        image, image_filename = utils.validate_image()
        image.save(os.path.join(image_folder, image_filename))
        
        db = utils.db()
        item_data.update_image(db, image_filename, item_pk, oldname,)

        item = item_data.get_item(db, item_pk)
        
        # Generate new token for response
        csrf_token = utils.generate_csrf_token(user.get("user_pk"))
        html = template("_item_detail.html", item=item, csrf_token=csrf_token)
        return f"""
        <template mix-target="#item_{item_pk}" mix-replace mix-function="closeModal">
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