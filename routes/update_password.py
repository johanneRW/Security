from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put 
from utility import utils
from icecream import ic
import bcrypt
import json
import credentials
import time
from utility import regexes
from utility import data


@put("/reset_password/<key>")
def _(key):
   #TODO: tilføj try/except og tilføj fejl besked

   try:
       
        db = utils.db()
        time_now = int(time.time())

        reset_info = data.get_reset_info(db,key)

        
        if reset_info is None:
            return "Invalid reset key."

        reset_time = reset_info['password_reset_at']
        user_pk = reset_info['user_pk']

       
        if time_now - reset_time > 900:
            return "Reset link has expired."

        
        user_password = utils.validate_password().encode()
        hashed_password = bcrypt.hashpw(user_password, bcrypt.gensalt())

        data.update_user_password(db,hashed_password, user_pk)

        return "Password changed successfully."

   except Exception as ex:
        raise
        return f"Error: {str(ex)}"

   finally:
        if db:
            db.close()
