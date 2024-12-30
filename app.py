from bottle import default_app, get, post, request, run, static_file, template, hook, response, abort
from utility import utils
from icecream import ic
import credentials
from utility import variables
from utility import data
import git
import secrets



##### CSRF Protection #####
@hook('before_request')
def setup_security():
    # Generate nonce for CSP
    request.nonce = secrets.token_hex(16)
    
    # Generate CSRF token if not exists
    if not request.get_cookie("csrf_token", secret=credentials.COOKIE_SECRET):
        response.set_cookie("csrf_token", secrets.token_hex(32), secret=credentials.COOKIE_SECRET, httponly=True)
    
    # CSRF validation for unsafe methods
    if request.method in ('POST', 'PUT', 'DELETE'):
        # Skip CSRF for API endpoints if needed
        if request.path.startswith('/api/'): 
            return
            
        ic("CSRF Validation Starting")
        ic("Request Method:", request.method)
        ic("Request Path:", request.path)
        
        try:
            utils.validate_csrf_token()
            ic("CSRF Validation Successful!")
        except Exception as ex:
            ic("CSRF Validation Failed:", str(ex))
            abort(403, str(ex))

##### Content Security Policy (CSP) #####

@hook('after_request')
def add_security_headers():
    response.headers['Content-Security-Policy'] = f"\
        default-src 'self'; \
        script-src 'self' https://api.mapbox.com 'nonce-{request.nonce}'; \
        style-src 'self' https://api.mapbox.com 'nonce-{request.nonce}'; \
        worker-src blob:; \
        img-src 'self' data: https://*.mapbox.com; \
        connect-src 'self' https://api.mapbox.com https://events.mapbox.com; \
        frame-ancestors 'none'; \
        form-action 'self'; \
        base-uri 'self';"

##############################

@get("/css/<file_name>.css")
def _(file_name):
    return static_file("./css/" + file_name+".css", ".")


##############################
@get("/js/<file_name>.js")
def _(file_name):
    return static_file("./js/" + file_name+".js", ".")


##############################
@get("/images/<item_image>")
def _(item_image):
    return static_file(item_image, "images")

##############################
@get("/favicon.ico")
def _():
    return static_file("favicon.ico", ".")


@post('/secret_url_for_git_hook')
def get_update():
    repo = git.Repo('./home_away')
    origin = repo.remotes.origin
    repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
    repo.head.reset(index=True, working_tree=True)
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
import routes.bookings

import routes.arango


##############################
@get("/")
def _():
    try:
        db = utils.db()
        items = data.get_items_limit_offset(db, variables.ITEMS_PER_PAGE)
        ic(items)

        is_logged = False
        is_admin = False
        user=""
        csrf_token = utils.get_csrf_token()
        try:    
            utils.validate_user_logged()
            user = request.get_cookie("user", secret=credentials.COOKIE_SECRET)
            is_logged = True
            is_admin = user.get("role_id") == 1
        except:
            pass

        format = request.query.get('format')
        if format == "json":
            return {"items": items}

        return template("index.html", items=items, mapbox_token=credentials.MAPBOX_TOKEN, 
                        is_logged=is_logged,user=user,is_admin=is_admin, request=request, csrf_token=csrf_token)
    except Exception as ex:
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











