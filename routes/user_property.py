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



@get("/user_property")
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

        if  utils.validate_user_logged():
            user_pk=user['user_pk']
            ic(user_pk)
            #x.disable_cache()
            db = utils.db()
            items =data.get_items_by_user(db, user_pk)
            ic(items)
            return template("user_property", items=items,is_logged=is_logged, user=user)
        else: 
           pass
    except Exception as ex:
        raise
        ic(ex)
        return "system under maintainance"         
    finally:
        pass