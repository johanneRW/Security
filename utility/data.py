import os
import utils

def create_image(db, image_pk, item_pk, image_filename):
    db.execute("""
            INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES (?, ?, ?)
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
    item_updated_at,
    item_is_blocked, 
    item_blocked_updated_at, 
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
            item_updated_at, 
            item_is_blocked, 
            item_blocked_updated_at, 
            item_owned_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item_pk, 
        item_name,
        item_lat, 
        item_lon, 
        item_price_per_night, 
        item_created_at, 
        item_updated_at,
        item_is_blocked, 
        item_blocked_updated_at, 
        item_owned_by
    ))
    db.commit()

def create_user(db,user_pk,
    user_username,
    user_first_name,
    user_last_name,
    user_email,
    hashed_password,
    role_id,
    user_created_at,
    user_updated_at,  
    user_verification_key,
    user_is_verified,
    user_is_verified_at,
    user_is_blocked):
    q = db.execute("""
INSERT INTO users (
    user_pk,
    user_username,
    user_first_name,
    user_last_name,
    user_email,
    user_password,
    role_id,
    user_created_at,
    user_updated_at,
    user_verification_key,
    user_is_verified,
    user_is_verified_at,
    user_is_blocked
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", 
    (user_pk,
    user_username,
    user_first_name,
    user_last_name,
    user_email,
    hashed_password,
    role_id,
    user_created_at,
    user_updated_at,  
    user_verification_key,
    user_is_verified,
    user_is_verified_at,
    user_is_blocked))
    db.commit()


def create_password_reset(db,password_reset_key,password_reset_at,user_pk):
    q = db.execute("INSERT INTO password_reset(password_reset_key,password_reset_at,password_user_pk) VALUES (?,?,?)",(password_reset_key,password_reset_at,user_pk))
    db.commit()

def get_reset_info(db,key):
    q = db.execute("SELECT * FROM password_reset WHERE password_reset_key = ?", (key,))
    reset_info = q.fetchone()
    return reset_info


def get_item(db, item_pk):
    q = db.execute("""
            SELECT items.*, 
                    group_concat(item_images.image_filename) AS images
            FROM items
            LEFT JOIN item_images ON items.item_pk = item_images.item_pk
            WHERE items.item_pk = ?
            GROUP BY items.item_pk
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


def get_items_limit_offset(db,limit,offset):
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
    image_folder = utils.get_image_folder()
    for item in items:
        try:
            item['images'] = [
                os.path.join(image_folder, img)
                for img in item['images'].split(',')
            ]
        except AttributeError:
            item['images'] = []
    return items

def get_item_limit(db, limit):
    q = db.execute("""
            SELECT items.*, 
                   COALESCE(AVG(ratings.stars), 0) AS item_stars,
                   group_concat(item_images.image_filename) AS images
            FROM items
            LEFT JOIN ratings ON items.item_pk = ratings.item_pk
            LEFT JOIN item_images ON items.item_pk = item_images.item_pk
            GROUP BY items.item_pk
            ORDER BY items.item_created_at
            LIMIT ?
        """, (limit,))
    items = q.fetchall()
    return items

def get_users(db, limit):
    q = db.execute("SELECT * FROM users ORDER BY user_created_at LIMIT 0, ?", (limit,))
    users = q.fetchall()
    return users

def get_user_by_email(db,user_email):
    q = db.execute("SELECT * FROM users WHERE user_email = ? AND user_is_verified = 1 AND user_is_deleted= 0 LIMIT 1", (user_email,))
    user = q.fetchone()
    return user

# def get_user_by_email(db, user_email):
#     q = db.execute("SELECT user_pk, user_first_name  FROM users WHERE user_email=? LIMIT 1", (user_email,))
#     user_info = q.fetchone()
#     return user_info


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
    q = db.execute("SELECT * FROM users WHERE user_pk=? LIMIT 1", (user_pk,))
    user = q.fetchone()
    return user

def get_user_password(db, user_pk):
    q = db.execute("SELECT user_password FROM users WHERE user_pk = ? LIMIT 1", (user_pk,))
    user = q.fetchone()  
    return user 

def get_items_by_user(db, user_pk):
    q = db.execute("""
                SELECT items.*, 
                       group_concat(item_images.image_filename) AS images
                FROM items
                LEFT JOIN item_images ON items.item_pk = item_images.item_pk
                WHERE items.item_owned_by = ?
                GROUP BY items.item_pk
                ORDER BY items.item_created_at
            """, (user_pk,))
    results = q.fetchall()
    return results



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
            UPDATE item_images SET image_filename = ?
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
            updatet_at,
            item_pk ):
    db.execute("""
            UPDATE items SET item_name=?, item_lat=?, item_lon=?, item_price_per_night=?, item_updated_at=?
            WHERE item_pk=?
        """, (
            item_name,
            item_lat,
            item_lon,
            item_price_per_night,
            updatet_at,
            item_pk
        ))
    db.commit()

def update_user(db,username,first_name,last_name,email,updated_at,user_pk):
    q = db.execute("""UPDATE users
                        SET user_username =?,  user_first_name=?, 
                           user_last_name=?, 
                        user_email = ?,  
                           user_updated_at=?
                           WHERE user_pk=?
                            """
            ,(username,first_name,last_name,email,updated_at,user_pk))
    db.commit()




def update_user_password(db,hashed_password, user_pk):
    db.execute("UPDATE users SET user_password = ? WHERE user_pk = ?", (hashed_password, user_pk))
    db.commit()

def update_verification_status(db,user_is_verified_at,key):
    q = db.execute(
        "UPDATE users SET user_is_verified = 1, user_is_verified_at=? WHERE user_verification_key = ?", 
        (user_is_verified_at,key)
    )
    db.commit()



def delete_user(db,deleted_at,user_pk):
    q = db.execute("""UPDATE users
                        SET
                        user_is_deleted=1,
                        user_deleted_at=?
                        WHERE user_pk=?
                        """
            ,(deleted_at,user_pk,))
    db.commit()



def delete_item(db, item_pk):
    db.execute("BEGIN")
    db.execute("DELETE FROM ratings WHERE item_pk = ?", (item_pk,))
    db.execute("""DELETE FROM items WHERE item_pk=?
                    """,(item_pk,))
    db.execute("""DELETE FROM item_images WHERE item_pk=?
                    """,(item_pk,))
    db.commit()


def toggle_block_item(db,new_blocked_status, updated_at, item_uuid):
    db.execute("UPDATE items SET item_is_blocked = ?, item_blocked_updated_at = ? WHERE item_pk = ?", (new_blocked_status, updated_at, item_uuid))
    db.commit()

def toggle_block_user(db, new_blocked_status, updated_at, user_pk):
    db.execute("UPDATE users SET user_is_blocked = ?, user_blocked_updated_at = ? WHERE user_pk = ?", (new_blocked_status, updated_at, user_pk))
    db.commit() 

