
import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put 
import utils
from icecream import ic
import bcrypt
import json
import credentials
import time
import variables
from send_email import send_email
from utility import data


@post("/request_reset_password")
def _():
    try:


        user_email = utils.validate_email()
            
        db = utils.db()
        user_info = data.get_user_by_email(db,user_email)
        ic(user_info)
        user_pk=user_info['user_pk']
        user_first_name=user_info['user_first_name']
        ic(user_first_name)
        ic(user_pk)

        #TODO:denne skal måske ikke sende en fejl?
        if not user_info:
            raise ValueError("User not found or not verified", 404)
        
        password_reset_key =uuid.uuid4().hex
        password_reset_at=int(time.time())
        
        data.create_password_reset(db,password_reset_key,password_reset_at,user_pk)


        subject = "Reset password"
        template_name = "email_reset_password"
        template_vars = {"user_first_name": user_first_name, "password_reset_key": password_reset_key}
        #send_email( user_email, subject, template_name, **template_vars)
        send_email(credentials.DEFAULT_EMAIL, subject, template_name, **template_vars)

        
        return """
        <template mix-target="#message">
            <div id="message">
                email sendt
            </div>        
        </template>
        """
    except Exception as ex:
        print(ex)
        if "user_email invalid" in str(ex):
            return """
            <template mix-target="#message">
            <div id="message">
                Email invalid
            </div>
            </template>    
            """
    finally:
        if "db" in locals(): db.close()
