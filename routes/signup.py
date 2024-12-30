import uuid
from bottle import get, post, request, template, put, response
from utility import utils
from icecream import ic
import bcrypt
import credentials
import time
from utility import email
from utility import data


@get("/signup")
def _():
    try:
        # For GET requests, just get the token from the cookie
        csrf_token = utils.get_csrf_token()
        return template("signup", csrf_token=csrf_token)
    except Exception as ex:
        ic(ex)
        return str(ex)


@post("/signup")
def _():
    try:
        # Validate CSRF token and use it in the response
        csrf_token = utils.validate_csrf_token()

        user_pk = uuid.uuid4().hex
        user_username = utils.validate_user_username()
        user_first_name = utils.validate_user_first_name()
        user_last_name = utils.validate_user_last_name()
        user_email = utils.validate_email()
        user_password = utils.validate_password().encode()
        hashed_password = bcrypt.hashpw(user_password, bcrypt.gensalt())
        role_id = request.forms.get("role_type", "")
        user_created_at = int(time.time())
        user_verification_key = uuid.uuid4().hex

        db = utils.db()
        data.create_user(db, user_pk,
                    user_username,
                    user_first_name,
                    user_last_name,
                    user_email,
                    hashed_password,
                    role_id,
                    user_created_at,  
                    user_verification_key)

        subject = 'Welcome to Home-Away'
        template_name = "email_welcome"
        template_vars = {
            "user_first_name": user_first_name, 
            "user_verification_key": user_verification_key,
            "host_name": utils.get_host_name(),
        }
        email.send_email(credentials.DEFAULT_EMAIL, subject, template_name, **template_vars)

        html = template("__frm_signup.html", csrf_token=csrf_token)
        
        return f"""
            <template mix-target="#toast">
            <div mix-ttl="3000" class="ok">
                   User created and email sent
            </div>
            </template>
        <template mix-target="#frm_signup" mix-replace">
        {html}
        </template>
        """    

    except Exception as ex:
        ic(ex)
        if "users.user_email" in str(ex):
            return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Email not available
            </div>
            </template>
            """    

        if "user_email invalid" in str(ex):
            return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Email invalid
            </div>
            </template>
            """    
       
    finally:
        if "db" in locals(): db.close()


@get("/verify/<key>")
def _(key):
    # For GET requests, just get the token from the cookie
    csrf_token = request.get_cookie("csrf_token", secret=credentials.COOKIE_SECRET)
    return template("verify_key", key=key, csrf_token=csrf_token)


@put("/verify/<key>")
def _(key):
    try:
        # Validate CSRF token for PUT request
        utils.validate_csrf_token()
        
        db = utils.db()
        user_is_verified_at = int(time.time())
        data.update_verification_status(db, user_is_verified_at, key)

        return """<template mix-target="#toast">
                <div mix-ttl="3000" class="ok">
                    Account verified
                </div>
                </template>
                """
    except Exception:
        response.status = 404
        return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Verification key not found
            </div>
            </template>
            """    
    finally:
        if "db" in locals(): db.close()

