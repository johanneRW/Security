import time
from bottle import delete, get, post, put, request,response, static_file, template
import utils
from icecream import ic
import uuid
import bcrypt 
import variables
import credentials



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
            q = db.execute("""UPDATE users
                        SET user_username =?,  user_first_name=?, 
                           user_last_name=?, 
                        user_email = ?,  
                           user_updated_at=?
                           WHERE user_pk=?
                            """
            ,(username,first_name,last_name,email,updated_at,user_pk))
            db.commit()
            q = db.execute("SELECT * FROM users WHERE user_pk=? LIMIT 1", (user_pk,))
            user = q.fetchone()
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

            html = template("_user.html", user=user )
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