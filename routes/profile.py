
from bottle import  get,  response,  template, request
import utils
from icecream import ic
import variables
import credentials




@get("/profile")
#ikke sikker på om denne skal være der
#TODO:ændre til at lave om i brugeren, hvordan sørger man for at databasen bliver opdateret, sanmtiding med cookien? og skal den det?
def _():
    try:
        utils.no_cache()
        utils.validate_user_logged()
        db = utils.db()
        #q = db.execute("SELECT * FROM items ORDER BY item_created_at LIMIT 0, ?", (variables.ITEMS_PER_PAGE,))
        #items = q.fetchall()
        #ic(items) 
        user = request.get_cookie("user", secret=credentials.COOKIE_SECRET)
        return template("profile.html", is_logged=True,  user=user)
    except Exception as ex:
        raise
        ic(ex)
        response.status = 303 
        response.set_header('Location', '/login')
        return
    finally:
        if "db" in locals(): db.close()



