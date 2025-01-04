import os
import uuid
from bottle import request, response
import requests
import re
import settings
from database.models.user import RoleEnum
from utility import regexes
from PIL import Image
from werkzeug.utils import secure_filename
from database.models.base import Session
import secrets
import time
import hashlib


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
    error = "email invalid"
    user_email = request.forms.get("user_email", "").strip()

    # Tjekker, om e-mailen matcher den angivne regex
    if not re.match(regexes.USER_EMAIL_REGEX, user_email):
        raise Exception(error, 400)

    # API-kald til Disify for at tjekke e-mailen
    try:
        response = requests.get(f"https://www.disify.com/api/email/{user_email}")
        if response.status_code != 200:
            raise Exception("API-kald mislykkedes", 500)
        
        # Parsing af API-svaret
        data = response.json()
        if data.get("disposable", False):  # Hvis e-mailen er midlertidig
            raise Exception("E-mailen er en midlertidig adresse og kan ikke bruges.", 400)
    except requests.exceptions.RequestException as e:
        # Hvis der er fejl i API-kaldet, logges fejlen, men tillader ikke brugeren at registrere sig
        print(f"Fejl ved API-kald: {e}")
        raise Exception("Kunne ikke verificere e-mailen. Prøv igen senere.", 500)

    # Hvis e-mailen er valid
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

 
 
# Funktion til at læse en liste over de mest brugte kodeord fra OWASP
def load_common_passwords(file_path="./utility/most-common.txt"):
    try:
        with open(file_path, "r") as file:
            return set(line.strip().lower() for line in file)
    except FileNotFoundError as exc:
        raise Exception("Common passwords file not found") from exc


#Validate (skip_name_validation=True) blive bruget til at validere kodeord ved login hvor der ikke bliver brugt for- og efternavn
def validate_password(skip_name_validation=False, user_first_name=None, user_last_name=None):
    # Læs brugerdata
    user_password = request.forms.get("user_password", "").strip()

    # Fejlbeskeder
    error_length = f"password {regexes.USER_PASSWORD_MIN} to {regexes.USER_PASSWORD_MAX} characters"
    error_simple = "password is too simple"
    
    # Tjek for længde og regex-regler
    if not re.match(regexes.USER_PASSWORD_REGEX, user_password):
        raise Exception(error_length, 400)

    # Tjek om for- eller efternavn indgår i password (case-insensitive) for bedre matching
    if not skip_name_validation and user_first_name and user_last_name:
        if user_first_name.lower() in user_password.lower() or user_last_name.lower() in user_password.lower():
            raise Exception(error_simple, 400)

    # Tjek om password er på listen over mest brugte kodeord fra OWASP
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
    error = f"Stars must be between {regexes.STAR_MIN} and {regexes.STAR_MAX}"
    item_stars = request.forms.get("stars", "").strip()
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
    error = "Image must be a valid image file (jpg, jpeg, png, gif, webp)"
    size_error = "Image file size exceeds the allowed limit (5 MB)"
    format_error = "Image format is not allowed. Only jpg, jpeg, png, gif, and webp are accepted."
    #max_file_size = 5 * 1024 * 1024  # Maksimal filstørrelse i bytes (5 MB)
    max_file_size = settings.MAX_FILE_SIZE
    #allowed_formats = ["JPEG", "PNG", "GIF", "WEBP"]  # Liste over tilladte formater
    allowed_formats=settings.ALLOWED_IMAGE_FORMATS

    file = request.files.get('image')

    # Tjek om filen eksisterer og har et navn
    if file is None or not file.filename.strip():
        raise Exception(error, 400)

    # Tjek filens størrelse
    file.file.seek(0, 2)  # Gå til slutningen af filen for at få dens størrelse
    file_size = file.file.tell()
    if file_size > max_file_size:
        raise Exception(size_error, 400)
    file.file.seek(0)  # Reset filstrømmen til starten efter størrelsestjekket

    # Sikrer, at filnavnet er sikkert
    original_filename = secure_filename(file.filename)

    # Tjek om filnavnet matcher det ønskede mønster
    if not re.match(regexes.ITEM_IMAGE_REGEX, original_filename):
        raise Exception(error, 400)

    # Valider om filens indhold er et billede ved at forsøge at åbne det med Pillow
    try:
        file.file.seek(0)  # Sørg for at starte fra begyndelsen af filstrømmen
        img = Image.open(file.file)
        img.verify()  # Tjekker om det er et gyldigt billede

        # Tjek billedformatet
        if img.format not in allowed_formats:
            raise Exception(format_error, 400)
    except Exception:
        raise Exception(error, 400)

    # Genindlæs billedet for at sikre, at strømmen kan bruges igen
    file.file.seek(0)  # Nulstil strømmen til starten igen for videre brug

    # Tilføj UUID til filnavnet
    file_extension = original_filename.rsplit('.', 1)[-1]  # Hent filens udvidelse
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"  # Generér nyt unikt filnavn

    # Returner det originale filobjekt og det sikre, unikke filnavn
    return file, unique_filename

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

def generate_csrf_token(user_pk=None):
    """Generate a stateless CSRF token containing timestamp and user info"""
    timestamp = int(time.time())
    nonce = secrets.token_hex(8)  # 8 bytes is sufficient for CSRF
    
    # Combine data
    token_parts = [str(timestamp), nonce]
    if user_pk:
        token_parts.append(str(user_pk))
    
    # Create token with signature
    raw_token = ':'.join(token_parts)
    signature = hashlib.sha256(
        f"{raw_token}:{settings.COOKIE_SECRET}".encode()
    ).hexdigest()[:16]  # First 16 chars of signature is enough
    
    return f"{raw_token}:{signature}"

def validate_csrf_token(token, user_pk=None):
    """Validate a stateless CSRF token"""
    try:
        # Split token parts
        parts = token.split(':')
        if len(parts) < 3:  # minimum: timestamp, nonce, signature
            return False
            
        timestamp = int(parts[0])
        nonce = parts[1]
        provided_signature = parts[-1]  # Last part is always signature
        token_user_pk = parts[2] if len(parts) > 3 else None
        
        # Verify timestamp (15 minute expiry)
        if time.time() - timestamp > 900:
            return False
            
        # Verify user if provided
        if user_pk and str(user_pk) != token_user_pk:
            return False
            
        # Rebuild signature
        raw_token = ':'.join(parts[:-1])  # Everything except signature
        expected_signature = hashlib.sha256(
            f"{raw_token}:{settings.COOKIE_SECRET}".encode()
        ).hexdigest()[:16]
        
        return provided_signature == expected_signature
        
    except Exception as ex:
        ic("Token validation failed:", str(ex))
        return False

