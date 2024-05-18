import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put, delete
import utils
from icecream import ic
import bcrypt
import json
import credentials
import time
import variables
from send_email import send_email



#Dette kunne være en put når det gentlig ikke omhandler en sletning som sådan, men en soft-delet der er en opdatering af databasen. 
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
            q = db.execute("SELECT user_password FROM users WHERE user_pk = ? LIMIT 1", (user_pk,))
            db_user = q.fetchone()   
            if not bcrypt.checkpw(user_password.encode(), db_user["user_password"].encode()):
                raise ValueError("Invalid credentials", 400)
            
            deleted_at = int(time.time())
            #user_pk=user['user_pk']
            ic(user_pk)
            db = utils.db()
            q = db.execute("""UPDATE users
                        SET
                           user_is_deleted=1,
                           user_deleted_at=?
                           WHERE user_pk=?
                            """
            ,(deleted_at,user_pk,))




        db.commit()
        user_first_name=user['user_first_name']   
        user_email=user['user_email'] 
        ic(user_first_name)
        ic(user_email)
             
        subject = "Profile deleted"
        template_name = "email_delete_profile"
        template_vars = {"user_first_name": user_first_name}
        #send_email( user_email, subject, template_name, **template_vars)
        send_email(credentials.DEFAULT_EMAIL, subject, template_name, **template_vars)
        



        response.delete_cookie("user", path='/')

        
        return f"""
        <template mix-redirect="/"></template>
        """


    except Exception as ex:
        ic(ex)
       
    finally:
        if "db" in locals(): db.close()

    