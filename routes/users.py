import time
from bottle import  get, post, put, request,response,  template
from database.models.user import RoleEnum
from utility import utils
from icecream import ic
import bcrypt 
from utility import email
import settings
from database import data


@get("/users")
def _():
    try:
        is_logged = False
        user = ""
        try:    
            # validate that user is logged in
            utils.validate_user_logged()
            
            # get the user cookie
            user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
            
            if not user:
                ic("No user cookie found")
                raise Exception("User not found")
                
            is_logged = True
            
            # Check if user is admin
            user_role = user.get("user_role")

            # Compare the string value of the role
            if user_role != RoleEnum.ADMIN:
                ic("User is not admin")
                response.status = 403
                return "you are not admin"
            
            # Generate CSRF token after validating admin status    
            csrf_token = utils.generate_csrf_token(user.get("user_pk"))
            
            # Get users list
            db = utils.db()
            users = data.get_all_users(db)
            return template("users", users=users, is_logged=is_logged, user=user, is_admin=True, csrf_token=csrf_token)
            
        except Exception as ex:
            ic("Login error:", str(ex))
            response.status = 403
            return "you are not logged in"
            
    except Exception as ex:
        ic("System error:", str(ex))
        return "system under maintainance"         
    finally:
        if "db" in locals(): db.close()


@post("/toggle_user_block/<user_pk>")
def toggle_user_block(user_pk):
    try:
        
        csrf_token = request.forms.get('csrf_token')
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        
        if not utils.validate_csrf_token(csrf_token, user.get("user_pk")):
            raise ValueError("Invalid CSRF token")

        if user.get("user_role") != RoleEnum.ADMIN:
            response.status = 403
            return "you are not admin"

        current_blocked_status = int(request.forms.get("user_blocked"))
        
        if current_blocked_status == 0:
            new_blocked_status = 1
            button_name = "Unblock"
            email_subject = 'User is blocked'
            email_template = "email_blocked_user"
        else:
            new_blocked_status = 0
            button_name = "Block"
            email_subject = 'User is unblocked'
            email_template = "email_ublocked_user"
            
        updated_at = int(time.time())
        
        db = utils.db()
        data.toggle_block_user(db, new_blocked_status, updated_at, user_pk)
        
        user_info = data.get_user_name_and_email(db, user_pk)
        user_first_name = user_info['user_first_name']
        user_email = user_info['user_email']

        template_vars = {"user_first_name": user_first_name}
        try:
            email.send_email(settings.DEFAULT_EMAIL, email_subject, email_template, **template_vars)
        except Exception as email_ex:
            ic("Email sending failed:", str(email_ex))
            
        return f"""
            <template mix-target="#user_block_{user_pk}" mix-replace>
                <form id="user_block_{user_pk}">
                    <input type="hidden" name="csrf_token" value="{utils.generate_csrf_token(user.get('user_pk'))}">
                    <input type="hidden" name="user_blocked" value="{new_blocked_status}">
                    <button id="user_block_{user_pk}"
                        mix-data="#user_block_{user_pk}"
                        mix-post="/toggle_user_block/{user_pk}"
                        mix-await="Please wait..."
                        mix-default={button_name}
                        class= "toggle"
                    >
                        {button_name}
                    </button>
                </form>
            """
    except Exception as ex:
        ic("Toggle block failed:", str(ex))
        response.status = 400
        return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Blocking or unblocking user failed
            </div>
            </template>
            """    
    finally:
        if "db" in locals(): db.close()


@put("/users/<user_pk>")
def _(user_pk):
    try:
        # Validate user is logged in
        user = utils.validate_user_logged()
            
        # Validate CSRF token
        csrf_token = request.forms.get('csrf_token')
        if not utils.validate_csrf_token(csrf_token, user.get("user_pk")):
            raise ValueError("Invalid CSRF token")
            
        # Validate all input fields
        first_name = utils.validate_user_first_name()
        last_name = utils.validate_user_last_name()
        username = utils.validate_user_username()
        email = utils.validate_email()

        # DB update
        db = utils.db()
        data.update_user(db, username, first_name, last_name, email, user_pk)
        
        # Get updated user data
        updated_user = data.get_user(db, user_pk)
        if not updated_user:
            raise Exception("user not found", 400)
            
        # Update cookie with new user data
        updated_user.pop("user_password")
        response.set_cookie("user", updated_user, secret=settings.COOKIE_SECRET, httponly=True, secure=settings.COOKIE_SECURE, path="/")

        # Generate new CSRF token and return updated template
        csrf_token = utils.generate_csrf_token(updated_user.get("user_pk"))
        html = template("_user.html", user=updated_user, is_logged=True, csrf_token=csrf_token)
        return f"""
        <template mix-target="[id='{user_pk}']" mix-replace>
        {html}
        </template>
        """
    except Exception as ex:
        ic(ex)
        response.status = 400
        return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Error when updating user
            </div>
            </template>
            """    
    finally:
        if "db" in locals(): db.close()



#Dette er en put da det egentlig ikke omhandler en sletning som sådan, men en soft-delete der er en opdatering af databasen. 
@put("/users/<user_pk>/delete")
def _(user_pk):
    try:
        csrf_token = request.forms.get('csrf_token')
        if not utils.validate_csrf_token(csrf_token, user.get("user_pk")):
            raise ValueError("Invalid CSRF token")
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        if user:
            user_password = utils.validate_password()
            # Fetch user's password so we can validate it
            db = utils.db()
            db_user = data.get_user_password(db, user_pk)   
            if not bcrypt.checkpw(user_password.encode(), db_user["user_password"]):
                raise ValueError("Invalid credentials", 400)
            
            # Get user info from DB before deleting it
            user_info = data.get_user(db, user_pk)
            
            # Delete user
            deleted_at = int(time.time())
            data.delete_user(db, deleted_at, user_pk)

            # Send email
            user_first_name = user_info['user_first_name']   
            user_email = user_info['user_email']                 
            subject = "Profile deleted"
            template_name = "email_delete_profile"
            template_vars = {"user_first_name": user_first_name}
            #email.send_email( user_email, subject, template_name, **template_vars)
            email.send_email(settings.DEFAULT_EMAIL, subject, template_name, **template_vars)
            

            response.delete_cookie("user", path='/')
            return f"""
            <template mix-redirect="/"></template>
            """
        else:
            response.status = 403
            return "you must be logged in"
    except Exception as ex:
        ic(ex)
        return """
        <template mix-target="#toast">
        <div mix-ttl="3000" class="error">
            Delete failed
        </div>
        </template>
        """
    finally:
        if "db" in locals(): db.close()


