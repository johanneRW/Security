import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put, delete
import utils
from icecream import ic
import bcrypt
import json
import credentials
import time
import variables
import send_email




@delete("/users/<user_pk>")
def _(user_pk):
    try:
        user = request.get_cookie("user", secret= credentials.COOKIE_SECRET)
        if user:
            deleted_at = int(time.time())
            db = utils.db()
            q = db.execute("""UPDATE users
                        SET
                        
                           WHERE user_pk=?
                            """
            ,(user_pk,))

            db.commit()
        user_first_name=user['user_first_name']   
        user_email=user['user_email'] 
        ic(user_first_name)
        ic(user_email)
             
        subject = "Profile deleted"
        template_name = "email_profile_deleted"
        template_vars = {"user_first_name": user_first_name}
        #send_email( user_email, subject, template_name, **template_vars)
        send_email(credentials.DEFAULT_EMAIL, subject, template_name, **template_vars)
        

    except Exception as ex:
        ic(ex)
       
    finally:
        pass