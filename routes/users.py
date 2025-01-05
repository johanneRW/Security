import time
from bottle import  get, post, put, request,response,  template
from database.models.user import RoleEnum
from utility import utils
from icecream import ic
import bcrypt 
from utility import email
import settings
from database.data import user_data


@get("/users")
def _():
    try:
        is_logged = False
        user = ""
        try:    
            # validate that user is logged in
            user = utils.validate_user_logged()
        except:
            response.status = 403
            return "you are not logged in"
        else:
            is_logged = True
            #if user.get("role_id") == 1:  
            if user.get("user_role") == RoleEnum.ADMIN.value:
                # Generate CSRF token after validating admin status    
                csrf_token = utils.generate_csrf_token(user.get("user_pk"))
                db = utils.db()
                users = user_data.get_all_users(db)
                return template("users", users=users, is_logged=is_logged, user=user, is_admin=True, csrf_token=csrf_token)
            else:
                response.status = 403
                return "you are not admin"
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

        #if user.get("role_id") != 1:
        if user.get("user_role") != RoleEnum.ADMIN.value:
            response.status = 403
            return "you are not admin"

        current_blocked_status=True if request.forms.get("user_blocked") == "True" else False
        if current_blocked_status == False:
            new_blocked_status=True
            button_name="Unblock"
            email_subject = 'User is blocked'
            email_template = "email_blocked_user"
        else:
            new_blocked_status=False
            button_name="Block"
            email_subject = 'User is unblocked'
            email_template = "email_ublocked_user"
          
        updated_at = int(time.time())
        
        db = utils.db()
        user_data.toggle_block_user(db, new_blocked_status, updated_at, user_pk)
        
        
        user_info = user_data.get_user_name_and_email(db,user_pk)
        ic(user_info)
        ic(email_subject)
        ic(email_template)
        
        user_first_name=user_info['user_first_name']
        user_email=user_info['user_email']
        ic(user_first_name)
        ic(user_email)
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
        user_data.update_user(db, username, first_name, last_name, email, user_pk)
        
        # Get updated user data
        updated_user = user_data.get_user(db, user_pk)
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
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        csrf_token = request.forms.get('csrf_token')
        if not utils.validate_csrf_token(csrf_token, user.get("user_pk")):
            raise ValueError("Invalid CSRF token")
        
        if user:
            user_password = utils.validate_password()
            # Fetch user's password so we can validate it
            db = utils.db()
            db_user_password = user_data.get_user_password(db, user_pk)   
            if not bcrypt.checkpw(user_password.encode(), db_user_password.encode()):
                raise ValueError("Invalid credentials", 400)
            
            # Get user info from DB before deleting it
            user_info = user_data.get_user(db, user_pk)
            
            # Delete user
            deleted_at = int(time.time())
            user_data.delete_user(db, deleted_at, user_pk)

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

@put("/users/<user_pk>/promote_to_partner")
def promote_to_partner(user_pk):
    try:
        # Valider, at brugeren er logget ind
        logged_user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        
        if not logged_user:
            response.status = 403
            return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                You must be logged in to promote your role.
            </div>
            </template>
            """

        # Tjek om brugeren forsøger at ændre sin egen rolle
        if logged_user["user_pk"] != user_pk:
            response.status = 403
            return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                You can only promote your own role.
            </div>
            </template>
            """
        
        # Valider CSRF token    
        utils.validate_csrf_token(logged_user["user_pk"])

        # Valider brugerens adgangskode
        user_password = utils.validate_password()
        db = utils.db()
        db_user_password = user_data.get_user_password(db, user_pk)
        if not bcrypt.checkpw(user_password.encode(), db_user_password.encode()):
            response.status = 400
            return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Invalid credentials. Promotion failed.
            </div>
            </template>
            """

        # Hent brugerens nuværende rolle
        user_info = user_data.get_user(db, user_pk)
        if not user_info:
            response.status = 404
            return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                User not found.
            </div>
            </template>
            """

        # Tjek om brugeren allerede er en partner
        if user_info["user_role"] == RoleEnum.PARTNER.value:
            return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                You are already a partner.
            </div>
            </template>
            """

        # Opdater brugerens rolle til partner
        updated_user = user_data.update_user_role_to_partner(db, user_pk)
        
        # Opdater brugerens cookie
        updated_cookie = {
            "user_pk": updated_user.user_pk,
            "user_role": RoleEnum.PARTNER.value,
            "user_email": updated_user.user_email,
            "user_first_name": updated_user.user_first_name
        }
        response.set_cookie("user", updated_cookie, secret=settings.COOKIE_SECRET, httponly=True, secure=settings.COOKIE_SECURE, path="/")

        # Send email til brugeren om ændringen
        user_first_name = updated_user.user_first_name
        user_email = updated_user.user_email
        subject = "You are now a Partner on Home-Away"
        template_name = "email_promote_to_partner"
        template_vars = {"user_first_name": user_first_name}
        email.send_email(settings.DEFAULT_EMAIL, subject, template_name, **template_vars)

        # Returnér succesbesked
        return """
        <template mix-target="#toast">
        <div mix-ttl="3000" class="ok">
            Congratulations! Your role has been updated to Partner.
        </div>
        </template>
        """
    except Exception as ex:
        ic(ex)
        response.status = 400
        return f"""
        <template mix-target="#toast">
        <div mix-ttl="3000" class="error">
            Error promoting role: {str(ex)}
        </div>
        </template>
        """
    finally:
        if "db" in locals():
            db.close()


