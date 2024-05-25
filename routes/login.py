from bottle import post, response, template
import utils
from icecream import ic
import bcrypt
import credentials
from utility import data

@post("/login")
def _():
    try:
        user_email = utils.validate_email()
        user_password = utils.validate_password()
        db = utils.db()
        user = data.get_user_by_email(db, user_email)
        if not user:
            raise ValueError("User not found or not verified", 404)
        
        # Kontroller adgangskoden ved hjælp af bcrypt
        #TODO: hvorfor skifter det mellem at fungere med user["user_password"] når der ikke står encode efter det og når der gør? Er det kun med de "første" gemte kodeord?
        if not bcrypt.checkpw(user_password.encode(), user["user_password"].encode()):
            raise ValueError("Invalid credentials", 400)
    
        user.pop("user_password") # Do not put the user's password in the cookie
        ic(user)
        try:
            import production
            is_cookie_https = True
        except:
            #TODO:skal alle disse oplysninger om user gemmes?
            is_cookie_https = False        
        response.set_cookie("user", user, secret=credentials.COOKIE_SECRET, httponly=True, secure=is_cookie_https)
        
        frm_login = template("__frm_login")
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
