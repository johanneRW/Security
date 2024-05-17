import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put, delete
import utils
from icecream import ic
import bcrypt
import json
import credentials
import time
import variables
from send_email import send_email



#Dette kunne være en put når det gentlig ikke omhandler en sletning som sådan, men en soft-delet der er en opdatering af databasen. 
@delete("/items/<item_pk>")
def _(item_pk):
    try:
       
        user = request.get_cookie("user", secret= credentials.COOKIE_SECRET)
        if user:
           
            db = utils.db()
            q = db.execute("""DELETE FROM items WHERE item_pk=?
                            """,(item_pk,))

        db.commit()
       
             
       
      
        return f"""
        <template mix-target="#frm_item_{item_pk}" mix-replace>
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

    