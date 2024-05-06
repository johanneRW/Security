import pathlib
# import sys
# sys.path.insert(0, str(pathlib.Path(__file__).parent.resolve())+"/bottle")
from bottle import request, response
import re
import sqlite3
import credentials
import variables


##############################
def dict_factory(cursor, row):
    col_names = [col[0] for col in cursor.description]
    return {key: value for key, value in zip(col_names, row)}

##############################

def db():
    db = sqlite3.connect(str(pathlib.Path(__file__).parent.resolve())+"/database/company.db")  
    db.row_factory = dict_factory
    return db


##############################
def no_cache():
    response.add_header("Cache-Control", "no-cache, no-store, must-revalidate")
    response.add_header("Pragma", "no-cache")
    response.add_header("Expires", 0)    


##############################
#TODO: der skal kun være en af disse
def validate_user_logged():
    user = request.get_cookie("user", secret=credentials.COOKIE_SECRET)
    if user is None: raise Exception("user must login", 400)
    return user


##############################
#TODO: der skal kun være en af disse
def validate_logged():
    # Prevent logged pages from caching
    response.add_header("Cache-Control", "no-cache, no-store, must-revalidate")
    response.add_header("Pragma", "no-cache")
    response.add_header("Expires", "0")  
    user_id = request.get_cookie("id", secret = credentials.COOKIE_SECRET)
    if not user_id: raise Exception("***** user not logged *****", 400)
    return user_id


##############################



def validate_user_id():
	error = f"user_id invalid"
	user_id = request.forms.get("user_id", "").strip()      
	if not re.match(variables.USER_ID_REGEX, user_id): raise Exception(error, 400)
	return user_id


##############################

def validate_email():
    error = f"email invalid"
    user_email = request.forms.get("user_email", "").strip()
    if not re.match(variables.USER_EMAIL_REGEX, user_email): raise Exception(error, 400)
    return user_email

##############################



def validate_user_username():
    error = f"username {variables.USER_USERNAME_MIN} to {variables.USER_USERNAME_MAX} lowercase english letters"
    user_username = request.forms.get("user_username", "").strip()
    if not re.match(variables.USER_USERNAME_REGEX, user_username): raise Exception(error, 400)
    return user_username

##############################


def validate_user_first_name():
    error = f"name {variables.USER_FIRST_NAME_MIN} to {variables.USER_FIRST_NAME_MAX} characters"
    user_first_name = request.forms.get("user_first_name", "").strip()
    if not re.match(variables.USER_REGEX, user_first_name): raise Exception(error, 400)
    return user_first_name

##############################



def validate_user_last_name():
  error = f"last_name {variables.USER_LAST_NAME_MIN} to {variables.USER_LAST_NAME_MAX} characters"
  user_last_name = request.forms.get("user_last_name").strip()
  if not re.match(variables.USER_REGEX, user_last_name): raise Exception(error, 400)
  return user_last_name

##############################


def validate_password():
    error = f"password {variables.USER_PASSWORD_MIN} to {variables.USER_PASSWORD_MAX} characters"
    user_password = request.forms.get("user_password", "").strip()
    if not re.match(variables.USER_PASSWORD_REGEX, user_password): raise Exception(error, 400)
    return user_password

##############################

def confirm_password():
  error = f"password and confirm_password do not match"
  user_password = request.forms.get("user_password", "").strip()
  user_confirm_password = request.forms.get("user_confirm_password", "").strip()
  if user_password != user_confirm_password: raise Exception(error, 400)
  return user_confirm_password

##############################


















