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
        user=""
        try:    
            utils.validate_user_logged()
            user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
            is_logged = True
        except:
            response.status = 403
            return "you are not logged in"
        else:
            #if user.get("role_id") == 1:  
            if user.get("user_role") == RoleEnum.ADMIN.value:          
                db = utils.db()
                users = user_data.get_all_users(db)
                return template("users", users=users,is_logged=is_logged, user=user, is_admin=True)
            else:
                response.status = 403
                return "you are not admin"
    except Exception as ex:
        ic(ex)
        return "system under maintainance"         
    finally:
        if "db" in locals(): db.close()


@post("/toggle_user_block/<user_pk>")
def toggle_user_block(user_pk):
    try:
        utils.validate_user_logged()
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)

        # Check if the user is an admin
        if user.get("user_role") != RoleEnum.ADMIN.value:
            response.status = 403
            return "You are not authorized"

        # Validate admin password from the form
        admin_password = request.forms.get("admin_password", "").strip()
        db = utils.db()
        admin_user = user_data.get_user_password(db, user['user_pk'])  # Fetch the admin's hashed password

        # Check if the provided password matches the admin's password
        if not bcrypt.checkpw(admin_password.encode(), admin_user["user_password"]):
            response.status = 403
            return """
            <template mix-target="#toast">
            <div mix-ttl="3000" class="error">
                Invalid admin password
            </div>
            </template>
            """

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
            email_template = "email_unblocked_user"

        updated_at = int(time.time())

        # Toggle user block status
        user_data.toggle_block_user(db, new_blocked_status, updated_at, user_pk)

        # Fetch user information
        user_info = user_data.get_user_name_and_email(db, user_pk)
        user_first_name = user_info[0]['user_first_name']
        user_email = user_info[0]['user_email']

        # Send email notification
        template_vars = {"user_first_name": user_first_name}
        email.send_email(settings.DEFAULT_EMAIL, email_subject, email_template, **template_vars)

        # Return updated form for frontend
        return f"""
            <template mix-target="#user_block_{user_pk}" mix-replace>
                <form id="user_block_{user_pk}">
                    <input type="hidden" name="user_blocked" value="{new_blocked_status}">
                    <button id="user_block_{user_pk}"
                            mix-data="#user_block_{user_pk}"
                            mix-post="/toggle_user_block/{user_pk}"
                            mix-await="Please wait..."
                            mix-default={button_name}
                            class="toggle">
                        {button_name}
                    </button>
                </form>
            </template>
            """
    except Exception as ex:
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
        user = request.get_cookie("user", secret= settings.COOKIE_SECRET)
        if user:
            first_name = utils.validate_user_first_name()
            last_name = utils.validate_user_last_name()
            username=utils.validate_user_username()
            email=utils.validate_email()

            # DB update
            db = utils.db()
            user = user_data.get_user(db, user_pk)
            if not user: 
                raise Exception("user not found", 400)
            user_data.update_user(db,username,first_name,last_name,email,user_pk)
            
            # Cookie update
            user = user_data.get_user(db, user_pk)
            user.pop("user_password") # Do not put the user's password in the cookie
            ic(user)
            response.set_cookie("user", user, secret=settings.COOKIE_SECRET, httponly=True, secure=settings.COOKIE_SECURE, path="/")

            html = template("_user.html", user=user,is_logged=True)
            return f"""
            <template mix-target="[id='{user_pk}']" mix-replace>
            {html}
            </template>
            """
        else:
            response.status = 403
            return "You are not logged in. Access denied."
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



#Dette er en put da det gentlig ikke omhandler en sletning som sådan, men en soft-delet der er en opdatering af databasen. 
#@delete("/users/<user_pk>")
# Update: nu er det en PUT, fordi mixhtml ikke laver client-side validering på "mix-delete"
@put("/users/<user_pk>/delete")
def _(user_pk):
    try:
        user = request.get_cookie("user", secret= settings.COOKIE_SECRET)
        if user:
            user_password = utils.validate_password()
            # Fetch user's password so we can validate it
            db = utils.db()
            db_user = user_data.get_user_password(db, user_pk)   
            if not bcrypt.checkpw(user_password.encode(), db_user["user_password"]):
                raise ValueError("Invalid credentials", 400)
            
            # Get user info from DB before deleting it
            user_info = user_data.get_user(db, user_pk)
            
            # Delete user
            deleted_at = int(time.time())
            user_data.delete_user(db,deleted_at,user_pk)

            # Send email
            user_first_name=user_info['user_first_name']   
            user_email=user_info['user_email']                 
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

        # Databaseforbindelse
        db = utils.db()

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

