import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put 
import utils
from icecream import ic
import bcrypt
import json
import credentials
import time
import variables
from send_email import send_email


#TODO: i et af projekterne er det en api? er der en grund til dette, eller var det for at vise hvad man også kunne gøre, signup skal laves om til en route
#TODO: ændre på mailen der sendes og subject i den
#TODO: se om email-funtionene ikke kan forekles


@post("/signup")
def _():
    try:
    # user_pk                 TEXT,
    # user_username           TEXT,
    # user_first_name               TEXT,
    # user_last_name          TEXT,
    # user_email              TEXT UNIQUE,
    # user_password           TEXT,
    # role_id                 INTEGER,
    # user_created_at         INTEGER,
    # user_updated_at         INTEGER,
    # user_verification_key   TEXT UNIQUE,
    # user_is_verified        INTEGER,
    # user_is_verified_at     INTEGER,
    # user_is_blocked         INTEGER,
    # FOREIGN KEY(role_id) REFERENCES roles(role_id)


        user_pk=uuid.uuid4().hex
        user_username=utils.validate_user_username()
        user_first_name=utils.validate_user_first_name()
        user_last_name=utils.validate_user_last_name()
        user_email=utils.validate_email()
        user_password=utils.validate_password().encode()
        hashed_password = bcrypt.hashpw(user_password, bcrypt.gensalt())
        role_id=request.forms.get("role_type", "")
        user_created_at=int(time.time())
        user_updated_at=None
        user_verification_key=uuid.uuid4().hex
        user_is_verified_at=None
        user_is_verified =0
        user_is_blocked =0

        # user_first_name = request.forms.get("user_first_name", "")
        # user_email=request.forms.get("user_email", "")
        # user_password =  request.forms.get("user_password", "").encode()
        # user_verification_key = uuid.uuid4().hex
        
        # hashed_password = bcrypt.hashpw(user_password)
        
        db = utils.db()
        q = db.execute("""
INSERT INTO users (
    user_pk,
    user_username,
    user_first_name,
    user_last_name,
    user_email,
    user_password,
    role_id,
    user_created_at,
    user_updated_at,
    user_verification_key,
    user_is_verified,
    user_is_verified_at,
    user_is_blocked
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", 
    (user_pk,
    user_username,
    user_first_name,
    user_last_name,
    user_email,
    hashed_password,
    role_id,
    user_created_at,
    user_updated_at,  
    user_verification_key,
    user_is_verified,
    user_is_verified_at,
    user_is_blocked))
        db.commit()

        # message = MIMEMultipart()
        # message["To"] = credentials.DEFAULT_EMAIL
        # message["From"] = credentials.DEFAULT_EMAIL
        # message["Subject"] = 'Welcome to Home-Away'


        # email_body = template("email_welcome",user_verification_key=user_verification_key, user_first_name=user_first_name)
        # messageText = MIMEText(email_body, 'html')
        # message.attach(messageText)


        # email = credentials.DEFAULT_EMAIL
        # password = credentials.EMAIL_PASSWORD


        # server = smtplib.SMTP('smtp.gmail.com:587')
        # server.ehlo('Gmail')
        # server.starttls()
        # server.login(email,password)
        # from_email = credentials.DEFAULT_EMAIL
        # to_email  = credentials.DEFAULT_EMAIL
        # server.sendmail(from_email,to_email,message.as_string())
        # server.quit()

        subject = 'Welcome to Home-Away'
        template_name = "email_welcome"
        template_vars = {"user_first_name": user_first_name, "user_verification_key": user_verification_key}
        #send_email( user_email, subject, template_name, **template_vars)
        send_email(credentials.DEFAULT_EMAIL, subject, template_name, **template_vars)
        
        return """
        <template mix-target="#message">
            <div id="message">
                User created
            </div>        
        </template>
        """
    except Exception as ex:
        print(ex)
        if "users.user_email" in str(ex):
             return """
            <template mix-target="#message">
            <div id="message">
                Email not available
            </div>
            </template>    
            """           

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



