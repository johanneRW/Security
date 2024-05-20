import os
from bottle import get, template
import utils
from icecream import ic
import json
import variables




@get("/items/page/<page_number>")
def _(page_number):
    try:
        db = utils.db()
        limit = variables.ITEMS_PER_PAGE
        #tjekker hvor mage items der skal vises for at regne ud hvormange sider der skal være i alt
        cursor = db.execute("SELECT COUNT(*) FROM items")
        result = cursor.fetchone()
        total_items = int(result['COUNT(*)'])

        
        total_pages = (total_items + limit - 1) // limit
        next_page = int(page_number) + 1
        
        offset = (int(page_number) - 1) * limit
        # q = db.execute(f"""SELECT * FROM items 
        #                    ORDER BY item_created_at 
        #                    LIMIT {limit} OFFSET {offset}
        #                 """)
        q = db.execute(f"""
            SELECT items.*, 
                   COALESCE(AVG(ratings.stars), 0) as item_stars,
                   group_concat(item_images.image_filename) AS images
            FROM items
            LEFT JOIN ratings ON items.item_pk = ratings.item_pk
            LEFT JOIN item_images ON items.item_pk = item_images.item_pk
            GROUP BY items.item_pk
            ORDER BY items.item_created_at
            LIMIT {limit} OFFSET {offset}
        """)
        items = q.fetchall()
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
        image_folder = utils.get_image_folder()
        for item in items:
            item['images'] = [
                os.path.join(image_folder, img)
                for img in item['images'].split(',')
            ]
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
