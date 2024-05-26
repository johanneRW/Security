import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put 
from utility import utils
from icecream import ic
import bcrypt
import json
import credentials
import time
from utility import regexes
from utility import email
from utility import data


@post("/toggle_item_block/<item_uuid>")
def toggle_item_block(item_uuid):
    try:
       
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
            >
                {button_name}
            </button>
        </form>
            """
    except Exception as ex:
        return f"<p>Error: {str(ex)}</p>"
    finally:
        if db:
            db.close()