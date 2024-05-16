
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


@post("/request_reset_password")
def _():
    try:

# password_reset_key     TEXT,
# password_reset_at       INTEGER,
# password_user_pk    TEXT,

        user_email = utils.validate_email()
            
        db = utils.db()
        q = db.execute("SELECT user_pk, user_first_name  FROM users WHERE user_email=? LIMIT 1", (user_email,))
        user_info = q.fetchone()
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
        
        q = db.execute("INSERT INTO password_reset(password_reset_key,password_reset_at,password_user_pk) VALUES (?,?,?)",(password_reset_key,password_reset_at,user_pk))
        db.commit()


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
