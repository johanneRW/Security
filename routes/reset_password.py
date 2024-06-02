import uuid
from bottle import  get, post, template, put, response
from utility import utils
from icecream import ic
import bcrypt
import credentials
import time

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
        email.send_email(credentials.DEFAULT_EMAIL, subject, template_name, **template_vars)

        html=template("__frm_send_new_password.html")
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="ok">
                   Email sendt
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
        db = utils.db()
        time_now = int(time.time())

        reset_info = data.get_reset_info(db,key)

        if reset_info is None:
            return"""
             <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                   Invalid reset key.
            </div>
            </template>
            """

        reset_time = reset_info['password_reset_at']
        user_pk = reset_info['user_pk']

        if time_now - reset_time > 900:
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

        html=template("__frm_reset_password.html")

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
        response.status = 500
        return """
        <template mix-target="#toast">
        <div mix-ttl="3000" class="error">
            System under maintenance
        </div>
        </template>
        """

   finally:
        if "db" in locals(): db.close()
