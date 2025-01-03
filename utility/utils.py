import os
from bottle import request, response
import re
import settings
from database.models.user import RoleEnum
from utility import regexes
from werkzeug.utils import secure_filename
from database.models.base import Session
import secrets


##############################


def db():
    # Returnér en SQLAlchemy-session
    return Session()


##############################
def get_image_folder():
    return settings.IMAGE_FOLDER


##############################

def get_host_name():
    return settings.HOST_NAME



##############################
def no_cache():
    response.add_header("Cache-Control", "no-cache, no-store, must-revalidate")
    response.add_header("Pragma", "no-cache")
    response.add_header("Expires", 0)    


##############################
def validate_user_logged():
    user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
    if user is None: raise Exception("user must login", 400)
    return user


##############################


def validate_user_id():
	error = f"user_id invalid"
	user_id = request.forms.get("user_id", "").strip()      
	if not re.match(regexes.USER_ID_REGEX, user_id): raise Exception(error, 400)
	return user_id


##############################

def validate_email():
    error = f"email invalid"
    user_email = request.forms.get("user_email", "").strip()
    if not re.match(regexes.USER_EMAIL_REGEX, user_email): raise Exception(error, 400)
    return user_email

##############################



def validate_user_username():
    error = f"username {regexes.USER_USERNAME_MIN} to {regexes.USER_USERNAME_MAX} lowercase english letters"
    user_username = request.forms.get("user_username", "").strip()
    if not re.match(regexes.USER_USERNAME_REGEX, user_username): raise Exception(error, 400)
    return user_username

##############################


def validate_user_first_name():
    error = f"name {regexes.USER_FIRST_NAME_MIN} to {regexes.USER_FIRST_NAME_MAX} characters"
    user_first_name = request.forms.get("user_first_name", "").strip()
    if not re.match(regexes.USER_FIRST_NAME_REGEX, user_first_name): raise Exception(error, 400)
    return user_first_name

##############################



def validate_user_last_name():
  error = f"last_name {regexes.USER_LAST_NAME_MIN} to {regexes.USER_LAST_NAME_MAX} characters"
  user_last_name = request.forms.get("user_last_name").strip()
  if not re.match(regexes.USER_LAST_NAME_REGEX, user_last_name): raise Exception(error, 400)
  return user_last_name

##############################


""" def validate_password():
    error = f"password {regexes.USER_PASSWORD_MIN} to {regexes.USER_PASSWORD_MAX} characters"
    user_password = request.forms.get("user_password", "").strip()
    if not re.match(regexes.USER_PASSWORD_REGEX, user_password): raise Exception(error, 400)
    return user_password 
    
 """
 
 
# Funktion til at læse den liste over de mest brugte kodeord
def load_common_passwords(file_path="./utility/10k-most-common.txt"):
    try:
        with open(file_path, "r") as file:
            return set(line.strip().lower() for line in file)
    except FileNotFoundError as exc:
        raise Exception("Common passwords file not found") from exc

# Ny validate_password funktion
def validate_password(skip_name_validation=False):
    # Læs brugerdata
    user_password = request.forms.get("user_password", "").strip()
    user_first_name = request.forms.get("user_first_name", "").strip()
    user_last_name = request.forms.get("user_last_name", "").strip()

    # Fejlbeskeder
    error_length = f"password {regexes.USER_PASSWORD_MIN} to {regexes.USER_PASSWORD_MAX} characters"
    error_simple = "password is too simple"
    
    # Tjek for længde og regex-regler
    if not re.match(regexes.USER_PASSWORD_REGEX, user_password):
        raise Exception(error_length, 400)

    # Tjek om for- eller efternavn indgår i password (case-insensitive)
    if not skip_name_validation:
        if user_first_name.lower() in user_password.lower() or user_last_name.lower() in user_password.lower():
            raise Exception(error_simple, 400)

    # Tjek om password er på listen over mest brugte kodeord
    common_passwords = load_common_passwords()
    if user_password.lower() in common_passwords:
        raise Exception(error_simple, 400)

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
    error = f"Item name must be {regexes.ITEM_NAME_MIN} to {regexes.ITEM_NAME_MAX} characters"
    item_name = request.forms.get("item_name", "").strip()
    if not re.match(regexes.ITEM_NAME_REGEX, item_name):
        raise Exception(error, 400)
    return item_name

##############################

def validate_item_lat():
    error = "Latitude must be a decimal number"
    item_lat = request.forms.get("item_lat", "").strip()
    if not re.match(regexes.ITEM_LATLON_REGEX, item_lat):
        raise Exception(error, 400)
    return item_lat

##############################

def validate_item_lon():
    error = "Longitude must be a decimal number"
    item_lon = request.forms.get("item_lon", "").strip()
    if not re.match(regexes.ITEM_LATLON_REGEX, item_lon):
        raise Exception(error, 400)
    return item_lon

##############################

def validate_item_stars():
    error = f"Stars must be between {regexes.STAR_MIN} and {regexes.STAR_MIN}"
    item_stars = request.forms.get("item_stars", "").strip()
    if not re.match(regexes.ITEM_STARS_REGEX, item_stars):
        raise Exception(error, 400)
    return item_stars

##############################

def validate_item_price_per_night():
    error = "Price per night must be a valid number"
    item_price_per_night = request.forms.get("item_price_per_night", "").strip()
    if not re.match(regexes.ITEM_PRICE_REGEX, item_price_per_night):
        raise Exception(error, 400)
    return item_price_per_night

##############################

def validate_image():
    error = "image must be a valid image filename (jpg, jpeg, png, gif, webp)"
    file = request.files.get('image')
    if file is None or not file.filename.strip():
        raise Exception(error, 400)
    
    filename = secure_filename(file.filename)
    if not re.match(regexes.ITEM_IMAGE_REGEX, filename):
        raise Exception(error, 400)
    
    return file, filename

##############################

def validate_oldname():
    error = "oldname must be a valid image filename (jpg, jpeg, png, gif, webp)"
    oldname = request.forms.get('oldname')
    if oldname is None or not oldname.strip():
        raise Exception(error, 400)
    if not re.match(regexes.ITEM_IMAGE_REGEX, oldname):
        raise Exception(error, 400)
    return oldname

##############################

def validate_number_of_nights():
    error = f"Nights must be between {regexes.NIGHT_MIN} and {regexes.NIGHT_MAX}"
    number_of_nights = request.forms.get("number_of_nights", "").strip()

    try:
        number_of_nights = int(number_of_nights)
    except ValueError:
        raise ValueError(error, 400)
    
    if number_of_nights < regexes.NIGHT_MIN or number_of_nights > regexes.NIGHT_MAX:
        raise ValueError(error, 400)
    
    return number_of_nights

##############################

def validate_role():
    error = f"Role must be one of: {', '.join([role.value for role in RoleEnum])}"
    role_name = request.forms.get("role_type", "").strip()

    # Tjek om role_name er gyldig
    if role_name not in RoleEnum._value2member_map_:
        raise Exception(error, 400)

    # Returner RoleEnum-objektet
    role=RoleEnum(role_name)
    return role.value

##############################

def get_csrf_token():
    """Get CSRF token from cookie, generate new one if not exists"""
    # First check if token exists in cookie
    token = request.get_cookie("csrf_token", secret=settings.COOKIE_SECRET)
    
    # Only generate new token if one doesn't exist
    if not token:
        token = secrets.token_hex(32)
        response.set_cookie("csrf_token", token, secret=settings.COOKIE_SECRET, httponly=True)
    
    return token

##############################

def validate_csrf_token():
    """Validate CSRF token from form matches cookie and return the token"""
    token = request.get_cookie("csrf_token", secret=settings.COOKIE_SECRET)
    if not token:
        raise ValueError("CSRF token not found in cookie")
        
    form_token = request.forms.get('csrf_token')
    if not form_token:
        raise ValueError("Security check failed - missing form token", 403)
        
    if token != form_token:
        raise ValueError("Security check failed - invalid token", 403)
    
    return token

