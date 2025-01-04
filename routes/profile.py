from bottle import get, response, template, request, redirect
from utility import utils
from icecream import ic
import settings


@get("/profile")
def _():
    try:
        utils.no_cache()
        utils.validate_user_logged()
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        if not user:
            redirect("/login")
            
        # Generate new CSRF token with user_pk
        csrf_token = utils.generate_csrf_token(user.get("user_pk"))
        return template("profile.html", is_logged=True, user=user, csrf_token=csrf_token)
    except Exception as ex:
        ic(ex)
        response.status = 302
        response.set_header('Location', '/login')
        return



