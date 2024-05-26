import os
from bottle import get, template
from utility import utils
from icecream import ic
import json
from utility import variables
from utility import data




@get("/items/page/<page_number>")
def _(page_number):
    try:
        db = utils.db()
        limit = variables.ITEMS_PER_PAGE
        #tjekker hvor mage items der skal vises for at regne ud hvormange sider der skal være i alt
        total_items = data.get_number_of_items(db)

        total_pages = (total_items + limit - 1) // limit
        next_page = int(page_number) + 1
        offset = (int(page_number) - 1) * limit
  
        items = data.get_items_limit_offset(db,limit,offset)
        ic(items)

        is_logged = False
        try:
            utils.validate_user_logged()
            is_logged = True
        except:
            pass
#hvis det er sidste side skal der ikke være  være en "more" button
        is_last_page = int(page_number) >= total_pages

        html = ""
        for item in items:
            html += template("_item", item=item, is_logged=is_logged)
        btn_more = template("__btn_more", page_number=next_page)
        if is_last_page: 
            btn_more = ""
        return f"""
        <template mix-target="#items" mix-bottom>
            {html}
        </template>
        <template mix-target="#more" mix-replace>
            {btn_more}
        </template>
        <template mix-function="addPropertiesToMap">{json.dumps(items)}</template>
        """
    except Exception as ex:
        ic(ex)
        raise
        return "ups..."
    finally:
        if "db" in locals(): db.close()
