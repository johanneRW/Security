import uuid
from bottle import  get, post, template, put, response
from utility import utils
from icecream import ic
import bcrypt
import settings
import time

from utility import email
from database import data

@get("/reset_password/<key>")
def _(key):
    csrf_token = utils.get_csrf_token()
    return template("update_password", key=key, csrf_token=csrf_token)


@get("/request_reset_password")
def _():
    csrf_token = utils.get_csrf_token()
    return template("request_reset_password", csrf_token=csrf_token)


@post("/request_reset_password")
def _():
    try:
        utils.validate_csrf_token()
        user_email = utils.validate_email()
            
        db = utils.db()
        user_info = data.get_user_by_email(db,user_email)
        if not user_info:
            response.status = 404
            return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                   User does not exist, or is not verified
            </div>
            </template>
            """
        
        ic(user_info)
        user_pk=user_info['user_pk']
        user_first_name=user_info['user_first_name']
        ic(user_first_name)
        ic(user_pk)
        
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
        email.send_email(settings.DEFAULT_EMAIL, subject, template_name, **template_vars)

        csrf_token = utils.get_csrf_token()
        html = template("__frm_send_new_password.html", csrf_token=csrf_token)
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="ok">
                   Email sent
            </div>
            </template>
        <template mix-target="#frm_send_password" mix-replace">
        {html}
        </template>
        """
    except Exception as ex:
        ic(ex)
        if "user_email invalid" in str(ex):
            response.status = 400
            return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                   Email invalid
            </div>
            </template>
            """
        else:
            response.status = 500
            return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                   System under maintenance
            </div>
            </template>
            """
    finally:
        if "db" in locals(): db.close()


@put("/reset_password/<key>")
def _(key):
   try:
        utils.validate_csrf_token()
        db = utils.db()
        time_now = int(time.time())

        reset_info = data.get_reset_info(db,key)
        ic("Reset info:", reset_info)  # Debug log

        if reset_info is None:
            response.status = 404
            return"""
             <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                   Invalid reset key.
            </div>
            </template>
            """

        reset_time = reset_info['password_reset_at']
        user_pk = reset_info['user_pk']
        ic("Time now:", time_now)
        ic("Reset time:", reset_time)
        ic("User PK:", user_pk)

        if time_now - reset_time > 900:
            response.status = 400
            return """
             <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                   Reset link has expired.
            </div>
            </template>
            """

        user_password = utils.validate_password().encode()
        hashed_password = bcrypt.hashpw(user_password, bcrypt.gensalt())

        data.update_user_password(db,hashed_password, user_pk)

        csrf_token = utils.get_csrf_token()
        html = template("__frm_reset_password.html", csrf_token=csrf_token, key=key)

        return  f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="ok">
                   Password changed successfully.
            </div>
            </template>
            <template mix-target="#frm_password_reset" mix-replace">
            {html}
            </template>
            """

   except Exception as ex:
        ic("Reset password error:", ex)  # Debug log
        response.status = 500
        return """
        <template mix-target="#toast">
        <div mix-ttl="3000" class="error">
            Password reset failed. Please try again.
        </div>
        </template>
        """

   finally:
        if "db" in locals(): db.close()
