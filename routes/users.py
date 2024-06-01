import time
from bottle import  get, post, put, request,response,  template
from utility import utils
from icecream import ic
import bcrypt 
from utility import email
import credentials
from utility import data


@get("/users")
def _():
    try:
        is_logged = False
        user=""
        try:    
            utils.validate_user_logged()
            user = request.get_cookie("user", secret=credentials.COOKIE_SECRET)
            is_logged = True
        except:
            pass
        if  utils.validate_user_logged():
            db = utils.db()
            users = data.get_all_users(db)
            return template("users", users=users,is_logged=is_logged, user=user)
        else: 
           pass
    except Exception as ex:
        ic(ex)
        return "system under maintainance"         
    finally:
        pass


@post("/toggle_user_block/<user_pk>")
def toggle_user_block(user_pk):
   
    try:
        current_blocked_status=int(request.forms.get("user_blocked"))
        if current_blocked_status == 0:
            new_blocked_status=1
            button_name="Unblock"
            email_subject = 'User is blocked'
            email_template = "email_blocked_user"
        else:
            new_blocked_status=0
            button_name="Block"
            email_subject = 'User is unblocked'
            email_template = "email_ublocked_user"
          
        updated_at = int(time.time())
        
        db = utils.db()
        data.toggle_block_user(db, new_blocked_status, updated_at, user_pk)
        
        
        user_info = data.get_user_name_and_email(db,user_pk)
        ic(user_info)
        ic(email_subject)
        ic(email_template)
        
        user_first_name=user_info[0]['user_first_name']
        user_email=user_info[0]['user_email']
        ic(user_first_name)
        ic(user_email)


        template_vars = {"user_first_name": user_first_name}
        #email.send_email( user_email, subject, template_name, **template_vars)
        email.send_email(credentials.DEFAULT_EMAIL, email_subject, email_template, **template_vars)


        return f"""
            <template mix-target="#user_block_{user_pk}" mix-replace>
                <form id="user_block_{user_pk}">
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
        return f"<p>Error: {str(ex)}</p>"
    finally:
        if db:
            db.close()


@put("/users/<user_pk>")
def _(user_pk):
    try:
        user = request.get_cookie("user", secret= credentials.COOKIE_SECRET)
        if user:
            first_name = utils.validate_user_first_name()
            last_name = utils.validate_user_last_name()
            username=utils.validate_user_username()
            email=utils.validate_email()
            updated_at = int(time.time())
            db = utils.db()
            data.update_user(db,username,first_name,last_name,email,user_pk)
            
            user = data.get_user(db, user_pk)
            if not user: raise Exception("user not found", 400)
            user.pop("user_password") # Do not put the user's password in the cookie
            ic(user)
            try:
                import production
                is_cookie_https = True
            except:
            #TODO:skal alle disse oplysninger om user gemmes?
                is_cookie_https = False        
            response.set_cookie("user", user, secret=credentials.COOKIE_SECRET, httponly=True, secure=is_cookie_https, path="/")

            html = template("_user.html", user=user,is_logged=True)
            return f"""
            <template mix-target="[id='{user_pk}']" mix-replace>
            {html}
            </template>
            """
        else: return "You are not logged in. Access denied."
    except Exception as ex:
        ic(ex)
        if "user_first_name" in str(ex):
            return f"""
            <template mix-target="#message">
                {ex.args[1]}
            </template>
            """            
    finally:
        pass


#Dette er en put da det gentlig ikke omhandler en sletning som sådan, men en soft-delet der er en opdatering af databasen. 
#@delete("/users/<user_pk>")
# Update: nu er det en PUT, fordi mixhtml ikke laver client-side validering på "mix-delete"
@put("/users/<user_pk>/delete")
def _(user_pk):
    user_password = utils.validate_password()
    try:
        user = request.get_cookie("user", secret= credentials.COOKIE_SECRET)
        if user:
            # Fetch user's password so we can validate it
            db = utils.db()
            db_user = data.get_user_password(db, user_pk)   
            if not bcrypt.checkpw(user_password.encode(), db_user["user_password"].encode()):
                raise ValueError("Invalid credentials", 400)
            
            deleted_at = int(time.time())
            #user_pk=user['user_pk']
            ic(user_pk)
            db = utils.db()
            data.delete_user(db,deleted_at,user_pk)
      
        user_first_name=user['user_first_name']   
        user_email=user['user_email'] 
        ic(user_first_name)
        ic(user_email)
             
        subject = "Profile deleted"
        template_name = "email_delete_profile"
        template_vars = {"user_first_name": user_first_name}
        #email.send_email( user_email, subject, template_name, **template_vars)
        email.send_email(credentials.DEFAULT_EMAIL, subject, template_name, **template_vars)
        

        response.delete_cookie("user", path='/')
        return f"""
        <template mix-redirect="/"></template>
        """


    except Exception as ex:
        ic(ex)
    finally:
        if "db" in locals(): db.close()


