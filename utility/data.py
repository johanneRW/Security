
def create_image(db, image_pk, item_pk, image_filename):
    db.execute("""
            INSERT INTO items_images (image_pk, item_pk, image_filename) VALUES (?, ?, ?)
            """, (
            image_pk,                       
            item_pk,
            image_filename,
        ))
    db.commit()



def create_item(
    db, 
    item_pk, 
    item_name,
    item_lat, 
    item_lon, 
    item_price_per_night, 
    item_created_at, 
    item_owned_by
):
    db.execute("""
        INSERT INTO items (
            item_pk, 
            item_name, 
            item_lat, 
            item_lon, 
            item_price_per_night, 
            item_created_at, 
            item_owned_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        item_pk, 
        item_name,
        item_lat, 
        item_lon, 
        item_price_per_night, 
        item_created_at,
        item_owned_by
    ))
    db.commit()


def create_user(
    db,
    user_pk,
    user_username,
    user_first_name,
    user_last_name,
    user_email,
    hashed_password,
    role_id,
    user_created_at,
    user_verification_key
):
    q = db.execute("""
    INSERT INTO users (
        user_pk,
        user_username,
        user_first_name,
        user_last_name,
        user_email,
        user_password,
        role_id,
        user_created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, 
        (user_pk,
        user_username,
        user_first_name,
        user_last_name,
        user_email,
        hashed_password,
        role_id,
        user_created_at)
    )
    q = db.execute(
        "INSERT INTO user_verification_request (user_pk, user_verification_key) VALUES (?, ?)",
        (user_pk, user_verification_key),
    )
    db.commit()



def create_password_reset(db,password_reset_key,password_reset_at,user_pk):
    q = db.execute("INSERT INTO password_reset_log(password_reset_key,password_reset_at,user_pk) VALUES (?,?,?)",(password_reset_key,password_reset_at,user_pk))
    db.commit()



def get_reset_info(db,key):
    q = db.execute("SELECT * FROM password_reset_log WHERE password_reset_key = ?", (key,))
    reset_info = q.fetchone()
    return reset_info



def get_item(db, item_pk):
    q = db.execute("""
            SELECT items_with_status.*, 
                    group_concat(items_images.image_filename) AS images
            FROM items_with_status
            LEFT JOIN items_images ON items_with_status.item_pk = items_images.item_pk
            WHERE items_with_status.item_pk = ?
            GROUP BY items_with_status.item_pk
        """, 
        (item_pk,)
    )
    item = q.fetchone()
    try:
        item['images'] = item['images'].split(',')
    except AttributeError:
        item['images'] = []
    return item

def get_number_of_items(db):
    cursor = db.execute("SELECT COUNT(*) FROM items")
    result = cursor.fetchone()
    total_items = int(result['COUNT(*)'])
    return total_items


def get_items_limit_offset(db,limit,offset=0):
    q = db.execute(f"""
            SELECT items_with_status.*, 
                   COALESCE(AVG(ratings.stars), 0) as item_stars,
                   group_concat(items_images.image_filename) AS images
            FROM items_with_status
            LEFT JOIN ratings ON items_with_status.item_pk = ratings.item_pk
            LEFT JOIN items_images ON items_with_status.item_pk = items_images.item_pk
            GROUP BY items_with_status.item_pk
            ORDER BY items_with_status.item_created_at
            LIMIT {limit} OFFSET {offset}
        """)
    items = q.fetchall()
    for item in items:
        try:
            item['images'] = [
                "/images/" + img 
                for img in item['images'].split(',')
            ]
        except AttributeError:
            item['images'] = []
    return items



def get_all_users(db):
    q = db.execute("SELECT * FROM user_with_status ORDER BY user_created_at ")
    users = q.fetchall()
    return users


def get_user_by_email(db,user_email):
    q = db.execute(
        "SELECT * FROM user_with_status WHERE user_email = ? AND user_is_verified = 1 AND user_is_deleted= 0 LIMIT 1", 
        (user_email,)
    )
    user = q.fetchone()
    return user

def get_user_name_and_email(db,user_pk):
    q = db.execute("""SELECT
                        user_first_name,
                        user_email
                        FROM 
                        users
                        WHERE 
                        user_pk =?""", (user_pk,))
    user_info = q.fetchall()
    return user_info

def get_user(db, user_pk):
    q = db.execute("SELECT * FROM user_with_status WHERE user_pk=? LIMIT 1", (user_pk,))
    user = q.fetchone()
    return user

def get_user_password(db, user_pk):
    q = db.execute("SELECT user_password FROM users WHERE user_pk = ? LIMIT 1", (user_pk,))
    user = q.fetchone()  
    return user 

def get_items_by_user(db, user_pk):
    q = db.execute("""
                SELECT items_with_status.*, 
                       group_concat(items_images.image_filename) AS images
                FROM items_with_status
                LEFT JOIN items_images ON items_with_status.item_pk = items_images.item_pk
                WHERE items_with_status.item_owned_by = ?
                GROUP BY items_with_status.item_pk
                ORDER BY items_with_status.item_created_at
            """, (user_pk,))
    items = q.fetchall()
    for item in items:
        try:
            item['images'] = item['images'].split(',')
        except AttributeError:
            item['images'] = []
    return items


def get_user_by_item(db, item_uuid):
    q = db.execute("""SELECT
    users.user_first_name,
    users.user_email
    FROM 
    items
    JOIN 
    users
    ON 
    items.item_owned_by = users.user_pk
    WHERE 
    items.item_pk =?""", (item_uuid,))
    user_info = q.fetchall()
    return user_info



def update_image(db, image_filename, item_pk, oldname,):
    db.execute("""
            UPDATE items_images SET image_filename = ?
            WHERE item_pk=? AND image_filename = ?
            """, (
            image_filename,            
            item_pk,
            oldname,
        ))
    db.commit() 



def update_item(db,item_name,
            item_lat,
            item_lon,
            item_price_per_night,
            item_pk ):
    db.execute("""
            UPDATE items SET item_name=?, item_lat=?, item_lon=?, item_price_per_night=?
            WHERE item_pk=?
        """, (
            item_name,
            item_lat,
            item_lon,
            item_price_per_night,
            item_pk
        ))
    db.commit()


def update_user(db,username,first_name,last_name,email,user_pk):
    q = db.execute("""UPDATE users
                        SET user_username =?,  user_first_name=?, 
                           user_last_name=?, 
                        user_email = ?
                           WHERE user_pk=?
                            """
            ,(username,first_name,last_name,email,user_pk))
    db.commit()


def update_user_password(db,hashed_password, user_pk):
    db.execute("UPDATE users SET user_password = ? WHERE user_pk = ?", (hashed_password, user_pk))
    db.commit()


def update_verification_status(db,user_is_verified_at,key):
    q = db.execute(
        "SELECT user_pk FROM user_verification_request WHERE user_verification_key = ?",
        (key,),
    )
    user_pk = q.fetchone()["user_pk"]
    db.execute(
        "INSERT INTO user_verification_completed (user_pk, user_is_verified_at) VALUES (?, ?)",
        (user_pk, user_is_verified_at),
    )
    db.commit()


def delete_user(db,deleted_at,user_pk):
    db.execute(
        "INSERT INTO user_deleted_log (user_pk, user_deleted_at) VALUES (?, ?)",
        (user_pk,deleted_at),
    )
    db.commit()


def delete_item(db, item_pk):
    db.execute("BEGIN")
    db.execute("DELETE FROM ratings WHERE item_pk = ?", (item_pk,))
    db.execute("DELETE FROM item_blocked_log WHERE item_pk = ?", (item_pk,))
    db.execute("DELETE FROM item_updated_log WHERE item_pk = ?", (item_pk,))
    db.execute("DELETE FROM items_images WHERE item_pk=?", (item_pk,))
    db.execute("DELETE FROM bookings WHERE item_pk=?", (item_pk,))
    db.execute("DELETE FROM items WHERE item_pk=?", (item_pk,))
    db.commit()


def toggle_block_item(db,new_blocked_status, updated_at, item_uuid):
    db.execute(
        "INSERT INTO item_blocked_log (item_pk, item_blocked_updated_at, item_blocked_value) VALUES (?, ?, ?)",
        (item_uuid,updated_at,new_blocked_status),
    )
    db.commit()


def toggle_block_user(db, new_blocked_status, updated_at, user_pk):
    db.execute(
        "INSERT INTO user_blocked_updated_log (user_pk, user_blocked_updated_at, user_blocked_value) VALUES (?, ?, ?)",
        (user_pk,updated_at,new_blocked_status),
    )
    db.commit() 
