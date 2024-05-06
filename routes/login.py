
from bottle import post, response, template
import x
from icecream import ic
import bcrypt
import credentials

@post("/login")
def _():
    try:
        user_email = x.validate_email()
        user_password = x.validate_password()
        db = x.db()
        # q = users_db.execute(
            # "SELECT * from Users WHERE user_email=? AND user_is_verified = 1",
            # (user_email,)
        # ) TODO:skift til at tjekke email verification, evt besked ny fejl-besked hvis den ikke er
        q = db.execute("SELECT * FROM users WHERE user_email = ? LIMIT 1", (user_email,))
        user = q.fetchone()
        if not user: raise Exception("user not found", 400)
        if not bcrypt.checkpw(user_password.encode(), user["user_password"].encode()): raise Exception("Invalid credentials", 400)
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
        <template mix-redirect="/profile">
        </template>
        """
    except Exception as ex:
        try:
            response.status = ex.args[1]
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
