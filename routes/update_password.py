from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put 
import utils
from icecream import ic
import bcrypt
import json
import credentials
import time
import variables


@put("/reset_password/<key>")
def _(key):
   #TODO: tilføj try/except og tilføj fejl besked

   # password_reset_key     TEXT,
   # password_reset_at       INTEGER,
   # password_user_pk    TEXT,

   try:
       
        db = utils.db()
        time_now = int(time.time())

      
        q = db.execute("SELECT * FROM password_reset WHERE password_reset_key = ?", (key,))
        reset_info = q.fetchone()

        
        if reset_info is None:
            return "Invalid reset key."

        reset_time = reset_info['password_reset_at']
        user_pk = reset_info['password_user_pk']

       
        if time_now - reset_time > 900:
            return "Reset link has expired."

        
        user_password = utils.validate_password().encode()
        hashed_password = bcrypt.hashpw(user_password, bcrypt.gensalt())

     
        db.execute("UPDATE users SET user_password = ? WHERE user_pk = ?", (hashed_password, user_pk))
        db.commit()

        return "Password changed successfully."

   except Exception as ex:
        return f"Error: {str(ex)}"

   finally:
        if db:
            db.close()
