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


@post("/password_reset")
def _():
   try:
      user_email = utils.validate_email()
      db = utils.db()
      
      q = db.execute("SELECT * FROM users WHERE user_email = ? AND user_is_verified = 1 LIMIT 1", (user_email,))
      user = q.fetchone()
      if not user:
         raise ValueError("User not found or not verified", 404)
      
      # Kontroller adgangskoden ved hjælp af bcrypt
     


         message = MIMEMultipart()
         message["To"] = credentials.DEFAULT_EMAIL
         message["From"] = credentials.DEFAULT_EMAIL
         message["Subject"] = 'Testing my email'


         email_body = template("email_welcome",user_verification_key=user_verification_key, user_first_name=user_first_name)
         messageText = MIMEText(email_body, 'html')
         message.attach(messageText)


         email = credentials.DEFAULT_EMAIL
         password = credentials.EMAIL_PASSWORD


         server = smtplib.SMTP('smtp.gmail.com:587')
         server.ehlo('Gmail')
         server.starttls()
         server.login(email,password)
         from_email = credentials.DEFAULT_EMAIL
         to_email  = credentials.DEFAULT_EMAIL
         server.sendmail(from_email,to_email,message.as_string())
         server.quit()
      
   except Exception as ex:
      print(ex)
   finally:
      pass