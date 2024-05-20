# path to bottle main package to replace
# /home/bottlesite/.local/lib/python3.10/site-packages/bottle.py

# import pathlib
# import sys
# sys.path.insert(0, str(pathlib.Path(__file__).parent.resolve())+"/bottle")
#TODO: importer allfabetisk
import uuid
from bottle import default_app, get, post, request, response, run, static_file, template, put 
import utils
from icecream import ic
import bcrypt
import json
import credentials
import time
import variables
import os

##############################
@get("/app.css")
def _():
    return static_file("app.css", ".")


##############################
@get("/<file_name>.js")
def _(file_name):
    return static_file(file_name+".js", ".")


##############################
@get("/test")
def _():
    return [{"name":"one"}]


##############################
@get("/images/<item_image>")
def _(item_image):
    return static_file(item_image, "images")

##############################
import routes.signup
import routes.login
import routes.profile
import routes.get_more_items
import routes.toggle_block_item
import routes.toggle_block_user
import routes.update_user
import routes.get_all_users
import routes.update_password
import routes.request_reset_password
import routes.delete_user
import routes.user_property
import routes.update_item
import routes.delete_item
import routes.create_item
import routes.create_image
import routes.update_image


##############################
@get("/")
def _():
    try:
        db = utils.db()
        # q = db.execute("SELECT * FROM items ORDER BY item_created_at LIMIT 0, ?", (variables.ITEMS_PER_PAGE,))
        q = db.execute("""
            SELECT items.*, 
                   COALESCE(AVG(ratings.stars), 0) AS item_stars,
                   group_concat(item_images.image_filename) AS images
            FROM items
            LEFT JOIN ratings ON items.item_pk = ratings.item_pk
            LEFT JOIN item_images ON items.item_pk = item_images.item_pk
            GROUP BY items.item_pk
            ORDER BY items.item_created_at
            LIMIT ?
        """, (variables.ITEMS_PER_PAGE,))
        items = q.fetchall()
        ic(items)

        image_folder = utils.get_image_folder()
        for item in items:
            ic(item['item_pk'])
            
            item['images'] = [
                os.path.join(image_folder, img)
                for img in item['images'].split(',')
            ]

        ic(items)
        is_logged = False
        user=""
        try:    
            utils.validate_user_logged()
            user = request.get_cookie("user", secret=credentials.COOKIE_SECRET)
            is_logged = True
        except:
            pass

        format = request.query.get('format')
        if format == "json":
            return items

        return template("index.html", items=items, mapbox_token=credentials.MAPBOX_TOKEN, 
                        is_logged=is_logged,user=user)
    except Exception as ex:
        raise
        ic(ex)
        return ex
    finally:
        if "db" in locals(): db.close()


##############################
@get("/login")
def _():
    utils.no_cache()
    return template("login.html")


##############################
@get("/logout")
def _():
    response.delete_cookie("user")
    response.status = 303
    response.set_header('Location', '/login')
    return

#TODO: måske er dele af denne bedre?
# @get("/logout")
# def _():
#     response.add_header("Cache-Control", "no-cache, no-store, must-revalidate")
#     response.add_header("Pragma", "no-cache")
#     response.add_header("Expires", 0)    
#     response.delete_cookie("user")
#     response.status = 303
#     response.set_header("Location", "/")
#     return """
#                 <template mix-repalce mix-redirect="/">

#                 </template>
#                 """

##############################


@get("/verify/<key>")
def _(key):
    return template("verify_key",key=key)



@put("/verify/<key>")
def _(key):
    #TODO: tilføj try/except og tilføj fejl besked
    db = utils.db()
    user_is_verified_at=int(time.time())
    q = db.execute(
        "UPDATE users SET user_is_verified = 1, user_is_verified_at=? WHERE user_verification_key = ?", 
        (user_is_verified_at,key)
    )
    db.commit()

    return "Account verifiyed"


@get("/reset_password/<key>")
def _(key):
    return template("update_password",key=key)


@get("/request_reset_password")
def _():
    return template("request_reset_password")



@get("/signup")
def _():
    return template("signup")

##############################
@get("/api")
def _():
    return utils.test()


##############################
try:
    import production
    application = default_app()
except:
    run(host="0.0.0.0", port=81, debug=True, reloader=True, interval=0)








