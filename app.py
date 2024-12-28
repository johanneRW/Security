from bottle import default_app, get, post, request, run, static_file, template
from database.models.user import RoleEnum
from utility import utils
from icecream import ic
import settings
from database import data
import git
from database.models.base import Base, engine

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

##############################
@get("/")
def _():
    try:
        # Opret en SQLAlchemy-session
        db = utils.db()

        # Hent items med limit og offset
        items = data.get_items_limit_offset(db, settings.ITEMS_PER_PAGE)
        ic(items)

        # Standardværdier for brugerstatus
        is_logged = False
        is_admin = False
        user = ""

        try:
            # Valider om brugeren er logget ind
            utils.validate_user_logged()
            user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
            is_logged = True
            is_admin = user.get("user_role") == RoleEnum.ADMIN.value
        except Exception:
            pass

        # Håndtér forespørgselsformat
        response_format = request.query.get("format")
        if response_format == "json":
            return {"items": items}

        # Returnér HTML-template
        return template(
            "index.html",
            items=items,
            mapbox_token=settings.MAPBOX_TOKEN,
            is_logged=is_logged,
            user=user,
            is_admin=is_admin,
        )
    except Exception as ex:
        ic(ex)
        return {"error": str(ex)}
    finally:
        # Luk SQLAlchemy-sessionen
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








