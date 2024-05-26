import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put 
import utility.utils as utils
from icecream import ic
import bcrypt
import json
import credentials
import time
import variables
from utility import data



@get("/users")
def _():
    try:
        is_logged = False
        user=""
        try:    
            utils.validate_user_logged()
            user = request.get_cookie("user", secret=credentials.COOKIE_SECRET)
            is_logged = True
        except:
            pass
#TODO: der skal ikke være et dobbelt tjek her af logged
        #user = request.get_cookie("user", secret= x.cokie_secret)
        if  utils.validate_user_logged():
            #x.disable_cache()
            db = utils.db()
            users = data.get_all_users(db)
            return template("users", users=users,is_logged=is_logged, user=user)
        else: 
           pass
    except Exception as ex:
        ic(ex)
        return "system under maintainance"         
    finally:
        pass