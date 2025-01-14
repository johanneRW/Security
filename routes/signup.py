import uuid
from bottle import get, post, template, put, response, request
from utility import utils
from icecream import ic
import bcrypt

import settings
import time
from utility import email
from database.data import user_data


@get("/signup")
def _():
    try:
        csrf_token = utils.generate_csrf_token()
        return template("signup", csrf_token=csrf_token)
    except Exception as ex:
        ic(ex)
        return str(ex)


@post("/signup")
def _():
    try:
        # Get token from form and validate
        csrf_token = request.forms.get('csrf_token')
        if not utils.validate_csrf_token(csrf_token):
            raise ValueError("Invalid CSRF token")
            
        user_pk = uuid.uuid4().hex
        user_username = utils.validate_user_username()
        user_first_name = utils.validate_user_first_name()
        user_last_name = utils.validate_user_last_name()
        user_email = utils.validate_email()
        # Send fornavn og efternavn til validate_password
        user_password = utils.validate_password(
            skip_name_validation=False,
            user_first_name=user_first_name,
            user_last_name=user_last_name
        ).strip()

        # Bekræft, at password og confirm_password matcher
        user_confirm_password = utils.confirm_password()

        # Hash passwordet
        hashed_password = bcrypt.hashpw(user_password.encode(), bcrypt.gensalt())

        #role_id=request.forms.get("role_type", "")
        #role_name=utils.validate_role()
        user_created_at=int(time.time())
        user_verification_key=uuid.uuid4().hex

        db = utils.db()
        user_data.create_user(
            db,
            user_pk,
            user_username,
            user_first_name,
            user_last_name,
            user_email,
            hashed_password,
            #role_id,
            #role_name,
            user_created_at,  
            user_verification_key
        )

        subject = 'Welcome to Home-Away'
        template_name = "email_welcome"
        template_vars = {
            "user_first_name": user_first_name, 
            "user_verification_key": user_verification_key,
            "host_name": utils.get_host_name(),
        }
        #email.send_email( user_email, subject, template_name, **template_vars)
        email.send_email(settings.DEFAULT_EMAIL, subject, template_name, **template_vars)

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
        ic(ex)  # Log fejlen for debugging
        error_message = str(ex)

        if "user_email invalid" in error_message:
            return """
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                    Email invalid
                </div>
            </template>
            """    

        if "too simple" in error_message:
            return """
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                    Password is too simple
                </div>
            </template>
            """    

        if "username" in error_message:
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                    {error_message}
                </div>
            </template>
            """    
            
        if "password and confirm_password" in error_message:
            return """
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                    Password and confirm password do not match.
                </div>
            </template>
            """    

        # Generisk fejlmeddelelse for alle andre undtagelser
        return """
        <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Something went wrong. Please try again.
            </div>
        </template>
        """    

    finally:
        if "db" in locals(): db.close()


@get("/verify/<key>")
def _(key):
    # Generate new stateless token
    csrf_token = utils.generate_csrf_token()
    return template("verify_key", key=key, csrf_token=csrf_token)


@put("/verify/<key>")
def _(key):
    try:
        # Get token from form or headers for SPA requests
        csrf_token = request.forms.get('csrf_token')
        if not csrf_token and request.query.get('spa') == 'yes':
            csrf_token = request.headers.get('X-CSRF-Token')
            
        if not csrf_token:
            raise ValueError("Missing CSRF token")
            
        if not utils.validate_csrf_token(csrf_token):
            raise ValueError("Invalid CSRF token")
        
        db = utils.db()
        user_is_verified_at = int(time.time())
        user_data.update_verification_status(db, user_is_verified_at, key)

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

