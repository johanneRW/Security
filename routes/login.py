from bottle import get, post, response, template
from utility import utils
from icecream import ic
import bcrypt
import credentials
from utility import data

##############################
@get("/login")
def _():
    utils.no_cache()
    try:
        # For GET requests, just get the token from the cookie
        csrf_token = utils.get_csrf_token()
        return template("login", csrf_token=csrf_token)
    except Exception as ex:
        print(ex)
        return str(ex)


@post("/login")
def _():
    try:
        # Validate CSRF token and use it in the response
        csrf_token = utils.validate_csrf_token()
        
        user_email = utils.validate_email()
        user_password = utils.validate_password()
        db = utils.db()
        user = data.get_user_by_email(db, user_email)
        ic(user)
        
        if not user:
            raise ValueError("User not found or not verified", 404)
        
        if not bcrypt.checkpw(user_password.encode(), user["user_password"]):
            raise ValueError("Invalid credentials", 400)
    
        user.pop("user_password") # Do not put the user's password in the cookie
        ic(user)
        
        try:
            import production
            is_cookie_https = True
        except:
            is_cookie_https = False        
        response.set_cookie("user", user, secret=credentials.COOKIE_SECRET, httponly=True, secure=is_cookie_https)
        
        frm_login = template("__frm_login", csrf_token=csrf_token)
        return f"""
        <template mix-target="frm_login" mix-replace>
            {frm_login}
        </template>
        <template mix-redirect="/">
        </template>
        """
    except Exception as ex:
        try:
            response.status = ex.args[1] if len(ex.args) > 1 else 400
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                    {ex.args[0]}
                </div>
            </template>
            """
        except Exception as ex:
            ic(ex)
            response.status = 500
            return f"""
            <template mix-target="#toast">
                <div mix-ttl="3000" class="error">
                   System under maintainance
                </div>
            </template>
            """
    finally:
        if "db" in locals(): db.close()

##############################

@get("/logout")
def _():
    response.add_header("Cache-Control", "no-cache, no-store, must-revalidate")
    response.add_header("Pragma", "no-cache")
    response.add_header("Expires", 0)  
    response.delete_cookie("user")
    response.delete_cookie("csrf_token")
    response.status = 303
    response.set_header('Location', '/login')
    return