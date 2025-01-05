from bottle import (
    get, 
    post, 
    delete, 
    request, 
    template, 
    put, 
    response
)
import uuid
import bcrypt

from database.models.user import RoleEnum
from utility import utils
from utility import email
from icecream import ic
import json
import settings
import time
from utility import email
import time
import uuid
from utility import utils
import settings
from database.data import item_data, user_data


@get("/items/page/<page_number>")
def _(page_number):
    try:
        # Standardværdier for brugerstatus
        is_logged = False
        is_admin = False
        user = None
        try:
            # Valider om brugeren er logget ind
            utils.validate_user_logged()
            user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
            is_logged = True
            is_admin = user.get("user_role") == RoleEnum.ADMIN.value
            csrf_token = utils.generate_csrf_token(user.get("user_pk"))
        except:
            # Generate CSRF token without user_pk for non-logged-in users
            csrf_token = utils.generate_csrf_token()

        db = utils.db()
        limit = settings.ITEMS_PER_PAGE

        # Filtrer antal items baseret på brugertype
        if is_admin:
            # Admins kan se alle items
            total_items = item_data.get_number_of_items(db)
            items = item_data.get_items_limit_offset(db, limit, offset=(int(page_number) - 1) * limit)
        else:
            # Almindelige brugere ser kun "public" items
            total_items = item_data.get_number_of_items(db, visibility_filter="public")
            items = item_data.get_items_limit_offset(db, limit, offset=(int(page_number) - 1) * limit, visibility_filter="public")

        # Beregn antal sider
        total_pages = (total_items + limit - 1) // limit
        next_page = int(page_number) + 1

        # Tjek om det er sidste side
        is_last_page = int(page_number) >= total_pages

        # Generér HTML for items og "More" knap
        html = ""
        for item in items:
            html += template("_item", item=item, is_logged=is_logged, is_admin=is_admin, csrf_token=csrf_token)
        btn_more = template("__btn_more", page_number=next_page, csrf_token=csrf_token)
        if is_last_page: 
            btn_more = ""

        # Returnér HTML og opdatering til kortet
        return f"""
        <template mix-target="#items" mix-bottom>
            {html}
        </template>
        <template mix-target="#more" mix-replace>
            {btn_more}
        </template>
        <template mix-function="addPropertiesToMap">{json.dumps(items)}</template>
        """
    except Exception as ex:
        ic(ex)
        response.status = 400 
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Error getting next properties
            </div>
            </template>
            """
    finally:
        if "db" in locals():
            db.close()





@get("/items/user")
def _():
    try:
        is_logged = False
        user=""
        try:
            utils.validate_user_logged()
            user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
            is_logged = True
        except:
            response.status = 403
            return "you are not logged in"
        else:
            user_pk=user['user_pk']
            ic(user_pk)
            db = utils.db()
            items =item_data.get_items_by_user(db, user_pk)
            ic(items)
            csrf_token = utils.generate_csrf_token(user_pk)
            return template("items_for_user", items=items, is_logged=is_logged, user=user, csrf_token=csrf_token)
    except Exception as ex:
        ic(ex)
        response.status = 500
        return "system under maintainance"
    finally:
        if "db" in locals(): db.close()


@post("/items")
def _():
    try:
        user = utils.validate_user_logged()
        
        # Get token and validate with user_pk
        csrf_token = request.forms.get('csrf_token')
        if not utils.validate_csrf_token(csrf_token, user.get("user_pk")):
            response.status = 403
            return "Invalid CSRF token"
            
        item_pk = uuid.uuid4().hex
        item_name=utils.validate_item_name()
        item_lat=utils.validate_item_lat()
        item_lon=utils.validate_item_lon()
        item_price_per_night=utils.validate_item_price_per_night()
        item_created_at=int(time.time())
        item_owned_by=user['user_pk']
        
        db = utils.db()
        item_data.create_item(db, item_pk, item_name, item_lat, item_lon, 
                        item_price_per_night, item_created_at, item_owned_by)
        
        item = item_data.get_item(db, item_pk)
       
        csrf_token = utils.generate_csrf_token(user.get("user_pk"))
        html = template("_item_detail.html", item=item, csrf_token=csrf_token)
        html_new = template("create_item.html", csrf_token=csrf_token)
       
        return f"""
        <template mix-target="#frm_item_{item_pk}" mix-bottom mix-function="updateModalEvents">
            {html}
        </template>
        <template mix-target="#items-user" mix-bottom mix-function="updateModalEvents">
            {html}
        </template>
        <template mix-target="#frm_new_item" mix-replace">
            {html_new}
        </template>
        """
       
    except Exception as ex:
        ic(ex)
        response.status = 400 
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Error creating property
            </div>
            </template>
            """
    finally:
        if "db" in locals(): db.close()


@put("/items/<item_pk>")
def _(item_pk): 
    try:
        # Validate user is logged in
        utils.validate_user_logged()
        
        # Get token and validate with user_pk
        csrf_token = request.forms.get('csrf_token')
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        if not utils.validate_csrf_token(csrf_token, user.get("user_pk")):
            raise ValueError("Invalid CSRF token")

        item_name = utils.validate_item_name()
        item_lat = utils.validate_item_lat()
        item_lon = utils.validate_item_lon()
        item_price_per_night = utils.validate_item_price_per_night()
     
        db = utils.db()
        item_data.update_item(db, item_name, item_lat,item_lon, item_price_per_night, item_pk)
        item = item_data.get_item(db, item_pk)
        
        csrf_token = utils.generate_csrf_token(user.get("user_pk"))
        html = template("_item_detail.html", item=item, csrf_token=csrf_token)
        return f"""
        <template mix-target="#frm_item_{item_pk}" mix-replace>
        {html}
        </template>
        """
       
    except Exception as ex:
        ic(ex)
        response.status = 400 
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Error updating property
            </div>
            </template>
            """
    finally:
        if "db" in locals(): db.close()



@delete("/items/<item_pk>")
def _(item_pk):
    try:
        # Validate user is logged in
        utils.validate_user_logged()
        
        # Get token and validate with user_pk
        csrf_token = request.forms.get('csrf_token')
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        if not utils.validate_csrf_token(csrf_token, user.get("user_pk")):
            raise ValueError("Invalid CSRF token")

        db = utils.db()
        item_data.delete_item(db,item_pk)
        return f"""
            <template mix-target="#item_{item_pk}" mix-replace>
            </template>
            """
    except Exception as ex:
        raise
        ic(ex)
        response.status = 400 
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Error deleting property
            </div>
            </template>
            """   
    finally:
        if "db" in locals(): db.close()


@post("/toggle_item_block/<item_uuid>")
def toggle_item_block(item_uuid):
    try:
        # Validate user is logged in
        utils.validate_user_logged()
        
        # Get token and validate with user_pk
        csrf_token = request.forms.get('csrf_token')
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        if not utils.validate_csrf_token(csrf_token, user.get("user_pk")):
            raise ValueError("Invalid CSRF token")
        
        # Valider, at brugeren er logget ind
        if not user or user["user_role"] != RoleEnum.ADMIN.value:
            response.status = 403
            return "you are not admin"

        current_blocked_status=True if request.forms.get("item_blocked") == "True" else False
        if current_blocked_status is False:
            new_blocked_status=True
            button_name="Unblock"
            email_subject = 'Property is blocked'
            email_template = "email_blocked_item"
        else:
            new_blocked_status=False
            button_name="Block"
            email_subject = 'Property is unblocked'
            email_template = "email_ublocked_item"
          

        db = utils.db()
        updated_at = int(time.time())
        
        user_info = user_data.get_user_by_item(db, item_uuid)
        if not user_info:
            raise ValueError("User not found for this item")
            
        ic(user_info)
        ic(email_subject)
        ic(email_template)
        
        # Access dictionary values directly
        user_first_name = user_info["user_first_name"]
        user_email = user_info["user_email"]
        ic(user_first_name)
        ic(user_email)
        item_data.toggle_block_item(db, new_blocked_status, updated_at, item_uuid)

        # Send en email til ejeren
        user_info = user_data.get_user_by_item(db, item_uuid)
        user_first_name = user_info[0]['user_first_name']
        user_email = user_info[0]['user_email']
        template_vars = {"user_first_name": user_first_name}
                
        #email.send_email( user_email, subject, template_name, **template_vars)
        email.send_email(settings.DEFAULT_EMAIL, email_subject, email_template, **template_vars)

        return f"""
            <template mix-target="#item_{item_uuid}" mix-replace>
                <form id="item_{item_uuid}">
                    <input type="hidden" name="csrf_token" value="{utils.generate_csrf_token(user.get('user_pk'))}">
                    <input type="hidden" name="item_blocked" value="{new_blocked_status}">
                    <button id="item_{item_uuid}"
                        mix-data="#item_{item_uuid}"
                        mix-post="/toggle_item_block/{item_uuid}"
                        mix-await="Please wait..."
                        mix-default={button_name}
                        class= "toggle"
                    >
                        {button_name}
                    </button>
                </form>
            """
    except Exception as ex:
        ic(ex)
        response.status = 400
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Error blocking or unblocking item
            </div>
            </template>
            """   
    finally:
        if "db" in locals(): db.close()


        

@post("/toggle_item_visibility/<item_uuid>")
def toggle_item_visibility(item_uuid):
    try:
        csrf_token = utils.validate_csrf_token()
        utils.validate_user_logged()

        # Få den aktuelle synlighedsstatus
        current_visibility_status = request.forms.get("item_visibility")  # Forventet at være "public" eller "private"
        
        # Bestem ny synlighedsstatus og relevante variabler
        if current_visibility_status == "public":
            new_visibility_status = "private"
            button_name = "Make Public"
            email_subject = 'Property is now private'
            email_template = "email_visibility_item"
        else:
            new_visibility_status = "public"
            button_name = "Make Private"
            email_subject = 'Property is now public'
            email_template = "email_visibility_item"

        # Databaseopdatering
        db = utils.db()
        updated_at = int(time.time())
        item_data.toggle_visibility_item(db, new_visibility_status, updated_at, item_uuid)
        
        # Hent brugeroplysninger
        user_info = user_data.get_user_by_item(db, item_uuid)
        ic(user_info)
        ic(email_subject)
        ic(email_template)

        user_first_name = user_info['user_first_name']
        user_email = user_info['user_email']
        ic(user_first_name)
        ic(user_email)

        # Send email
        template_vars = {
            "user_first_name": user_first_name,
            "new_visibility_status": new_visibility_status,  # Dynamisk status: "public" eller "private"
        }
        #email.send_email(user_email, email_subject, email_template, **template_vars)
        email.send_email(settings.DEFAULT_EMAIL, email_subject, email_template, **template_vars)

        # Returnér opdateret knap
        return f"""
            <template mix-target="#visibility_item_{item_uuid}" mix-replace>
                <form id="visibility_item_{item_uuid}">
                    <input type="hidden" name="csrf_token" value="{csrf_token}">
                    <input type="hidden" name="item_visibility" value="{new_visibility_status}">
                    <button id="item_{item_uuid}"
                            mix-data="#visibility_item_{item_uuid}"
                            mix-post="/toggle_item_visibility/{item_uuid}"
                            mix-await="Please wait..."
                            mix-default="{button_name}"
                            class="toggle"
                    >
                        {button_name}
                    </button>
                </form>
            </template>
        """
    except Exception as ex:
        raise
        ic(ex)
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Error changing item visibility
            </div>
            </template>
        """   
    finally:
        if "db" in locals(): db.close()

