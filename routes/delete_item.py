import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put, delete
import utility.utils as utils
from icecream import ic
import bcrypt
import json
import credentials
import time
import variables
from utility import data





@delete("/items/<item_pk>")
def _(item_pk):
    try:
       
        user = request.get_cookie("user", secret= credentials.COOKIE_SECRET)
        if user:
           
            db = utils.db()
            data.delete_item(db,item_pk)
       
               

        return f"""
        <template mix-target="#item_{item_pk}" mix-replace>
        </template>
        """
       
    except Exception as ex:
        ic(ex)
        return f"""
        <template mix-target="#message">
            {ex.args[1]}
        </template>
        """            
    finally:
        pass

    