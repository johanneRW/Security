#TODO: importer allfabetisk
from bottle import default_app, get, post, request, response, run, static_file, template, put 
from utility import utils
from icecream import ic
import bcrypt
import json
import credentials
import time
from utility import variables
from utility import data
import git

##############################
@get("/app.css")
def _():
    return static_file("app.css", ".")


##############################
@get("/<file_name>.js")
def _(file_name):
    return static_file("./js/" + file_name+".js", ".")


##############################
@get("/images/<item_image>")
def _(item_image):
    return static_file(item_image, "images")


@post('/secret_url_for_git_hook')
def get_update():
    repo = git.Repo('./home_away')
    origin = repo.remotes.origin
    repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
    origin.pull()
    return ""
    

##############################
import routes.signup
import routes.login
import routes.profile
import routes.users
import routes.reset_password
import routes.items
import routes.images


##############################
@get("/")
def _():
    try:
        db = utils.db()
        items = data.get_items_limit_offset(db, variables.ITEMS_PER_PAGE)
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
            return {"items": items}

        return template("index.html", items=items, mapbox_token=credentials.MAPBOX_TOKEN, 
                        is_logged=is_logged,user=user)
    except Exception as ex:
        raise
        ic(ex)
        return ex
    finally:
        if "db" in locals(): db.close()


##############################
try:
    import production
    application = default_app()
except:
    run(host="0.0.0.0", port=81, debug=True, reloader=True, interval=0)








