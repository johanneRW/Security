from bottle import default_app, get, post, request, run, static_file, template, hook, response, abort
from database.models.user import RoleEnum
from utility import utils
from icecream import ic
import settings
from database import data
import git
import secrets
from database.models.base import Base, engine

ic("Loading routes...")

import routes.signup
import routes.login
import routes.profile
import routes.users
import routes.reset_password
import routes.items
import routes.images
import routes.bookings

ic("Routes loaded successfully")

@hook('before_request')
def setup_security():
    # Generate nonce for CSP
    request.nonce = secrets.token_hex(16)
    ic("Nonce generated:", request.nonce)
    
    # Generate CSRF token if not exists
    if not request.get_cookie("csrf_token", secret=settings.COOKIE_SECRET):
        response.set_cookie("csrf_token", secrets.token_hex(32), secret=settings.COOKIE_SECRET, httponly=True)
    
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
@get("/")
def _():
    try:
        # Opret en SQLAlchemy-session
        db = utils.db()

        # Hent items med limit og offset
        items = data.get_items_limit_offset(db, settings.ITEMS_PER_PAGE)
        
        # Handle JSON format request
        if request.query.get("format") == "json":
            response.content_type = 'application/json'
            return {"status": "success", "items": items}

        # Handle HTML request
        is_logged = False
        is_admin = False
        user = ""
        csrf_token = utils.get_csrf_token()
        try:    
            utils.validate_user_logged()
            user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
            is_logged = True
            is_admin = user.get("user_role").value == RoleEnum.ADMIN.value
        except Exception:
            pass

        return template(
            "index.html",
            items=items,
            mapbox_token=settings.MAPBOX_TOKEN,
            is_logged=is_logged,
            user=user,
            is_admin=is_admin,
            nonce=request.nonce,
            request=request,
            csrf_token=csrf_token
        )
    except Exception as ex:
        ic(ex)
        if request.query.get("format") == "json":
            response.status = 400
            response.content_type = 'application/json'
            return {"status": "error", "message": str(ex)}
        return {"error": str(ex)}
    finally:
        if "db" in locals():
            db.close()

##############################
if settings.PRODUCTION:
    application = default_app()
else:
    # Udskriv alle tabeller i metadata
    print("Tabeller der oprettes:")
    for table_name in Base.metadata.tables.keys():
        print(f"- {table_name}")
    
    Base.metadata.create_all(engine)
    print("Database and models initialized successfully.")

    run(host="0.0.0.0", port=81, debug=True, reloader=True, interval=0)











