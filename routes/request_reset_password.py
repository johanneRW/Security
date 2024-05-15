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




@post("/request_reset_password")
def _():
    try:


# password_reset_key     TEXT,
# password_reset_at       INTEGER,
# password_user_pk    TEXT,

        user_email = utils.validate_email()
            
        db = utils.db()
        q = db.execute("SELECT user_pk, user_first_name  FROM users WHERE user_email=? LIMIT 1", (user_email,))
        user_info = q.fetchone()
        ic(user_info)
        user_pk=user_info['user_pk']
        user_first_name=user_info['user_first_name']
        ic(user_first_name)
        ic(user_pk)

        #TODO:denne skal måske ikke sende en fejl?
        if not user_info:
            raise ValueError("User not found or not verified", 404)
        
        password_reset_key =uuid.uuid4().hex
        password_reset_at=int(time.time())
        
        q = db.execute("INSERT INTO password_reset(password_reset_key,password_reset_at,password_user_pk) VALUES (?,?,?)",(password_reset_key,password_reset_at,user_pk))
        db.commit()


        message = MIMEMultipart()
        message["To"] = credentials.DEFAULT_EMAIL
        message["From"] = credentials.DEFAULT_EMAIL
        message["Subject"] = 'Reset password'


        email_body = template("email_reset_password",password_reset_key=password_reset_key,user_first_name=user_first_name)
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
        
        return """
        <template mix-target="#message">
            <div id="message">
                email sendt
            </div>        
        </template>
        """
    except Exception as ex:
        print(ex)
        if "user_email invalid" in str(ex):
            return """
            <template mix-target="#message">
            <div id="message">
                Email invalid
            </div>
            </template>    
            """
    finally:
        if "db" in locals(): db.close()
