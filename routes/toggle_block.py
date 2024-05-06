from bottle import post, request
import x
from icecream import ic
import time


@post("/toggle_item_block/<item_uuid>")
def toggle_item_block(item_uuid):
    try:
       
        current_blocked_status=int(request.forms.get("item_blocked"))
        if current_blocked_status == 0:
            new_blocked_status=1
            button_name="Unblock"
        else:
            new_blocked_status=0
            button_name="Block"
          

        db = x.db()
        updated_at = int(time.time())
        db.execute("UPDATE items SET item_is_blocked = ?, item_blocked_updated_at = ? WHERE item_pk = ?", (new_blocked_status, updated_at, item_uuid))
        db.commit() 

        return f"""
            <template mix-target="#item_{item_uuid}" mix-replace>
                <form id="item_{item_uuid}">
            <input type="hidden" name="item_blocked" value="{new_blocked_status}">
            <button id="item_{item_uuid}"
                    mix-data="#item_{item_uuid}"
                    mix-post="/toggle_item_block/{item_uuid}"
            >
                {button_name}
            </button>
        </form>
            """
    except Exception as ex:
        return f"<p>Error: {str(ex)}</p>"
    finally:
        if db:
            db.close()