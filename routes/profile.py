from bottle import  get,  response,  template, request
from utility import utils
from icecream import ic
import settings


@get("/profile")
def _():
    try:
        utils.no_cache()
        utils.validate_user_logged()
        user = request.get_cookie("user", secret=settings.COOKIE_SECRET)
        return template("profile.html", is_logged=True,  user=user)
    except Exception as ex:
        ic(ex)
        response.status = 302
        response.set_header('Location', '/login')
        return
    finally:
        pass



