import pathlib
# import sys
# sys.path.insert(0, str(pathlib.Path(__file__).parent.resolve())+"/bottle")
from bottle import request, response
import re
import sqlite3
import credentials
import variables
from werkzeug.utils import secure_filename


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
def get_image_folder():
    # Assuming you have a folder named 'images' in the same directory as your script
    image_folder = "/images"
    return str(image_folder)

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

def validate_item_name():
    error = f"Item name must be {variables.ITEM_NAME_MIN} to {variables.ITEM_NAME_MAX} characters"
    item_name = request.forms.get("item_name", "").strip()
    if not re.match(variables.ITEM_NAME_REGEX, item_name):
        raise Exception(error, 400)
    return item_name

# def validate_item_splash_image():
#     error = "Splash image must be a valid image filename (jpg, jpeg, png, gif, webp)"
#     item_splash_image = request.forms.get("item_splash_image", "").strip()
#     if not re.match(variables.ITEM_IMAGE_REGEX, item_splash_image):
#         raise Exception(error, 400)
#     return item_splash_image

def validate_item_lat():
    error = "Latitude must be a decimal number"
    item_lat = request.forms.get("item_lat", "").strip()
    if not re.match(variables.ITEM_LATLON_REGEX, item_lat):
        raise Exception(error, 400)
    return item_lat

def validate_item_lon():
    error = "Longitude must be a decimal number"
    item_lon = request.forms.get("item_lon", "").strip()
    if not re.match(variables.ITEM_LATLON_REGEX, item_lon):
        raise Exception(error, 400)
    return item_lon

def validate_item_stars():
    error = f"Stars must be between {variables.STAR_MIN} and {variables.STAR_MIN}"
    item_stars = request.forms.get("item_stars", "").strip()
    if not re.match(variables.ITEM_STARS_REGEX, item_stars):
        raise Exception(error, 400)
    return item_stars

def validate_item_price_per_night():
    error = "Price per night must be a valid number"
    item_price_per_night = request.forms.get("item_price_per_night", "").strip()
    if not re.match(variables.ITEM_PRICE_REGEX, item_price_per_night):
        raise Exception(error, 400)
    return item_price_per_night


def validate_splash_image():
    error = "Splash image must be a valid image filename (jpg, jpeg, png, gif, webp)"
    file = request.files.get('item_splash_image')
    if file is None or not file.filename.strip():
        raise Exception(error, 400)
    
    filename = secure_filename(file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower()
    if file_extension not in variables.ALLOWED_IMAGE_EXTENSIONS:
        raise Exception(error, 400)
    
    return file, filename

def validate_additional_images():
    error = "Each additional image must be a valid image filename (jpg, jpeg, png, gif, webp)"
    files = request.files.getall('item_images')
    if len(files) < 3:
        raise Exception("At least 3 additional images are required", 400)
    
    validated_files = []
    for file in files:
        if file is None or not file.filename.strip():
            raise Exception(error, 400)
        
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        if file_extension not in variables.ALLOWED_IMAGE_EXTENSIONS:
            raise Exception(error, 400)
        
        validated_files.append((file, filename))
    
    return validated_files













