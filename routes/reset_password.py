
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

@get("/reset_password/<key>")
def _(key):
    return template("update_password",key=key)


@get("/request_reset_password")
def _():
    return template("request_reset_password")


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
        template_vars = {
            "user_first_name": user_first_name, 
            "password_reset_key": password_reset_key,
            "host_name": utils.get_host_name(),
        }
        #email.send_email( user_email, subject, template_name, **template_vars)
        email.send_email(credentials.DEFAULT_EMAIL, subject, template_name, **template_vars)

        
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


@put("/reset_password/<key>")
def _(key):
   #TODO: tilføj try/except og tilføj fejl besked

   try:
       
        db = utils.db()
        time_now = int(time.time())

        reset_info = data.get_reset_info(db,key)

        
        if reset_info is None:
            return "Invalid reset key."

        reset_time = reset_info['password_reset_at']
        user_pk = reset_info['user_pk']

       
        if time_now - reset_time > 900:
            return "Reset link has expired."

        
        user_password = utils.validate_password().encode()
        hashed_password = bcrypt.hashpw(user_password, bcrypt.gensalt())

        data.update_user_password(db,hashed_password, user_pk)

        return "Password changed successfully."

   except Exception as ex:
        raise
        return f"Error: {str(ex)}"

   finally:
        if db:
            db.close()
