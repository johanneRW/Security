from bottle import  get, post, delete, request, template, put, response 
from utility import utils
from utility import variables
from utility import email
from utility import data
from icecream import ic
import json
import credentials
import time
import uuid


@get("/items/page/<page_number>")
def _(page_number):
    try:
        csrf_token = utils.get_csrf_token()
        db = utils.db()
        limit = variables.ITEMS_PER_PAGE
        #tjekker hvor mage items der skal vises for at regne ud hvormange sider der skal være i alt
        total_items = data.get_number_of_items(db)

        total_pages = (total_items + limit - 1) // limit
        next_page = int(page_number) + 1
        offset = (int(page_number) - 1) * limit
  
        items = data.get_items_limit_offset(db,limit,offset)
        ic(items)

        is_logged = False
        is_admin = False
        try:
            utils.validate_user_logged()
            user = request.get_cookie("user", secret=credentials.COOKIE_SECRET)
            is_logged = True
            is_admin = user.get("role_id") == 1
        except:
            pass
        
        #hvis det er sidste side skal der ikke være en "more" button
        is_last_page = int(page_number) >= total_pages

        html = ""
        for item in items:
            html += template("_item", item=item, is_logged=is_logged, is_admin=is_admin, csrf_token=csrf_token)
        btn_more = template("__btn_more", page_number=next_page)
        if is_last_page: 
            btn_more = ""
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
        if "db" in locals(): db.close()



@get("/items/user")
def _():
    try:
        is_logged = False
        user=""
        try:
            utils.validate_user_logged()
            user = request.get_cookie("user", secret=credentials.COOKIE_SECRET)
            is_logged = True
        except:
            response.status = 403
            return "you are not logged in"
        else:
            user_pk=user['user_pk']
            ic(user_pk)
            db = utils.db()
            items =data.get_items_by_user(db, user_pk)
            ic(items)
            csrf_token = utils.get_csrf_token()
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
        csrf_token = utils.validate_csrf_token()
        utils.validate_user_logged()
        user = request.get_cookie("user", secret=credentials.COOKIE_SECRET)

        item_pk=uuid.uuid4().hex
        item_name=utils.validate_item_name()
        item_lat=utils.validate_item_lat()
        item_lon=utils.validate_item_lon()
        item_price_per_night=utils.validate_item_price_per_night()
        item_created_at=int(time.time())
        item_owned_by=user['user_pk']
        
        db = utils.db()
        data.create_item(db, item_pk, item_name, item_lat, item_lon, 
                        item_price_per_night, item_created_at, item_owned_by)
        
        item = data.get_item(db, item_pk)
       
        
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
        utils.validate_csrf_token()
        utils.validate_user_logged()

        item_name = utils.validate_item_name()
        item_lat = utils.validate_item_lat()
        item_lon = utils.validate_item_lon()
        item_price_per_night = utils.validate_item_price_per_night()
     
        db = utils.db()
        data.update_item(db,item_name,item_lat,item_lon,item_price_per_night,item_pk )
        item = data.get_item(db, item_pk)
        
        csrf_token = utils.get_csrf_token()
        html = template("_item_detail.html", item=item, csrf_token=csrf_token)
        return f"""
        <template mix-target="frm_item_{item_pk}" mix-replace>
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
        utils.validate_csrf_token()
        utils.validate_user_logged()
        db = utils.db()
        data.delete_item(db,item_pk)
        return f"""
            <template mix-target="#item_{item_pk}" mix-replace>
            </template>
            """
    except Exception as ex:
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
        utils.validate_csrf_token()
        utils.validate_user_logged()

        current_blocked_status=int(request.forms.get("item_blocked"))
        if current_blocked_status == 0:
            new_blocked_status=1
            button_name="Unblock"
            email_subject = 'Property is blocked'
            email_template = "email_blocked_item"
        else:
            new_blocked_status=0
            button_name="Block"
            email_subject = 'Property is unblocked'
            email_template = "email_ublocked_item"
          

        db = utils.db()
        updated_at = int(time.time())
        data.toggle_block_item(db,new_blocked_status, updated_at, item_uuid)
        
        
        user_info = data.get_user_by_item(db,item_uuid)
        ic(user_info)
        ic(email_subject)
        ic(email_template)
        
        user_first_name=user_info[0]['user_first_name']
        user_email=user_info[0]['user_email']
        ic(user_first_name)
        ic(user_email)

        template_vars = {"user_first_name": user_first_name}
        #email.send_email( user_email, subject, template_name, **template_vars)
        email.send_email(credentials.DEFAULT_EMAIL, email_subject, email_template, **template_vars)

        return f"""
            <template mix-target="#item_{item_uuid}" mix-replace>
                <form id="item_{item_uuid}">
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
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Error blocking or unblocking item
            </div>
            </template>
            """   
    finally:
        if "db" in locals(): db.close()