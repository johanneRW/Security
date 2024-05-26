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


@post("/toggle_user_block/<user_pk>")
def toggle_user_block(user_pk):
   
    try:
        current_blocked_status=int(request.forms.get("user_blocked"))
        if current_blocked_status == 0:
            new_blocked_status=1
            button_name="Unblock"
            email_subject = 'User is blocked'
            email_template = "email_blocked_user"
        else:
            new_blocked_status=0
            button_name="Block"
            email_subject = 'User is unblocked'
            email_template = "email_ublocked_user"
          
        updated_at = int(time.time())
        
        db = utils.db()
        data.toggle_block_user(db, new_blocked_status, updated_at, user_pk)
        
        
        user_info = data.get_user_name_and_email(db,user_pk)
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
            <template mix-target="#user_block_{user_pk}" mix-replace>
                <form id="user_block_{user_pk}">
            <input type="hidden" name="user_blocked" value="{new_blocked_status}">
            <button id="user_block_{user_pk}"
                    mix-data="#user_block_{user_pk}"
                    mix-post="/toggle_user_block/{user_pk}"
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