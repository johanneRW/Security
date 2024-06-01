from bottle import  get,  response,  template, request
from utility import utils
from icecream import ic
import credentials




@get("/profile")
#ikke sikker på om denne skal være der
#TODO:ændre til at lave om i brugeren, hvordan sørger man for at databasen bliver opdateret, sanmtiding med cookien? og skal den det?
def _():
    try:
        utils.no_cache()
        utils.validate_user_logged()
        db = utils.db()
        user = request.get_cookie("user", secret=credentials.COOKIE_SECRET)
        return template("profile.html", is_logged=True,  user=user)
    except Exception as ex:
        ic(ex)
        response.status = 303 
        response.set_header('Location', '/login')
        return
    finally:
        if "db" in locals(): db.close()



