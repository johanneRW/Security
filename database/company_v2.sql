DROP TABLE IF EXISTS roles;
CREATE TABLE roles(
    role_id INTEGER UNIQUE,
    role_name TEXT UNIQUE,
    PRIMARY KEY(role_id)
) WITHOUT ROWID;

INSERT INTO roles VALUES (1,'admin'), (2,'partner'), (3,'user');


DROP TABLE IF EXISTS users;
CREATE TABLE users(
  user_pk TEXT UNIQUE,
  user_username TEXT,
  user_first_name TEXT,
  user_last_name TEXT,
  user_email TEXT UNIQUE,
  user_password TEXT,
  role_id INTEGER,
  user_created_at INTEGER,
  PRIMARY KEY(user_pk),
  CONSTRAINT roles_users
    FOREIGN KEY (role_id) REFERENCES roles (role_id)
) WITHOUT ROWID;


DROP TABLE IF EXISTS user_verification_request;
CREATE TABLE user_verification_request(
  user_pk TEXT ,
  user_verification_key TEXT,
  PRIMARY KEY(user_pk),
  CONSTRAINT user_pk_user_pk FOREIGN KEY (user_pk) REFERENCES users (user_pk)
) WITHOUT ROWID;

DROP TABLE IF EXISTS user_verification_completed;
CREATE TABLE user_verification_completed(
  user_pk TEXT,
  user_is_verified_at INTEGER,
  PRIMARY KEY(user_pk),
  CONSTRAINT user_pk_user_pk FOREIGN KEY (user_pk) REFERENCES users (user_pk)
) WITHOUT ROWID;


DROP TABLE IF EXISTS password_reset_log;
CREATE TABLE password_reset_log(
  user_pk TEXT,
  password_reset_key TEXT UNIQUE,
  password_reset_at INTEGER,
  PRIMARY KEY(user_pk,password_reset_key),
  CONSTRAINT user_pk_user_pk FOREIGN KEY (user_pk) REFERENCES users (user_pk)
) WITHOUT ROWID;


DROP TABLE IF EXISTS user_blocked_updated_log;
CREATE TABLE user_blocked_updated_log(
  user_pk TEXT ,
  user_blocked_updated_at INTEGER ,
  user_blocked_value INTEGER ,
  PRIMARY KEY(user_pk,user_blocked_updated_at),
  CONSTRAINT user_pk_user_pk FOREIGN KEY (user_pk) REFERENCES users (user_pk)
) WITHOUT ROWID;

DROP TABLE IF EXISTS user_deleted_log;
CREATE TABLE user_deleted_log(
  user_pk TEXT ,
  user_deleted_at INTEGER,
  PRIMARY KEY(user_pk, user_deleted_at),
  CONSTRAINT user_pk_user_pk FOREIGN KEY (user_pk) REFERENCES users (user_pk)
) WITHOUT ROWID;

DROP TABLE IF EXISTS user_updated_log;
CREATE TABLE user_updated_log(
  user_pk TEXT ,
  user_updated_at INTEGER,
  PRIMARY KEY(user_pk,user_updated_at),
  CONSTRAINT user_pk_user_pk FOREIGN KEY (user_pk) REFERENCES users (user_pk)
) WITHOUT ROWID;


DROP TABLE IF EXISTS items;
CREATE TABLE items(
  item_pk TEXT UNIQUE,
  item_name TEXT,
  item_lat TEXT,
  item_lon TEXT,
  item_price_per_night REAL,
  item_created_at INTEGER,
  item_owned_by TEXT,
  PRIMARY KEY(item_pk),
  CONSTRAINT users_items FOREIGN KEY (item_owned_by) REFERENCES users (user_pk)
) WITHOUT ROWID;


DROP TABLE IF EXISTS item_blocked_log;
CREATE TABLE item_blocked_log(
  item_pk TEXT,
  item_blocked_updated_at INTEGER,
  item_blocked_value INTEGER,
  PRIMARY KEY(item_pk, item_blocked_updated_at),
  CONSTRAINT item_pk_item_pk FOREIGN KEY (item_pk) REFERENCES items (item_pk)
) WITHOUT ROWID;

DROP TABLE IF EXISTS items_images;
CREATE TABLE items_images(
  image_pk TEXT UNIQUE,
  item_pk TEXT,
  image_filename TEXT,
  PRIMARY KEY(image_pk),
  CONSTRAINT items_items_images
    FOREIGN KEY (item_pk) REFERENCES items (item_pk)
) WITHOUT ROWID;

 
DROP TABLE IF EXISTS item_updated_log;
CREATE TABLE item_updated_log(
  item_pk TEXT ,
  item_updated_at INTEGER,
  PRIMARY KEY(item_pk,item_updated_at),
  CONSTRAINT item_pk_item_pk FOREIGN KEY (item_pk) REFERENCES items (item_pk)
) WITHOUT ROWID;

DROP TABLE IF EXISTS ratings;
CREATE TABLE ratings(
  item_pk TEXT,
  user_pk TEXT,
  stars INTEGER,
  rating_created_at INTEGER,
  PRIMARY KEY(item_pk, user_pk),
  CONSTRAINT users_ratings
    FOREIGN KEY (user_pk) REFERENCES users (user_pk), 
  CONSTRAINT items_ratings
    FOREIGN KEY (item_pk) REFERENCES items (item_pk)
) WITHOUT ROWID;

 
DROP TABLE IF EXISTS bookings;
CREATE TABLE bookings(
  user_pk TEXT ,
  item_pk TEXT ,
  booking_created_at INTEGER ,
  booking_number_of_nights INTEGER,
  booking_price REAL,
  PRIMARY KEY(item_pk, user_pk, booking_created_at),
  CONSTRAINT user_pk_user_pk FOREIGN KEY (user_pk) REFERENCES users (user_pk),
  CONSTRAINT item_pk_item_pk FOREIGN KEY (item_pk) REFERENCES items (item_pk)
) WITHOUT ROWID;

-- triggers for users
DROP TRIGGER IF EXISTS insert_user_blocked;
CREATE TRIGGER insert_user_blocked
AFTER INSERT ON users
FOR EACH ROW
BEGIN
  INSERT INTO user_blocked_updated_log (user_pk, user_blocked_updated_at, user_blocked_value)
  VALUES (NEW.user_pk, strftime('%s', 'now'), 0);
END;

DROP TRIGGER IF EXISTS update_user;
CREATE TRIGGER update_user
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
  INSERT INTO user_updated_log (user_pk, user_updated_at)
  VALUES (NEW.user_pk, strftime('%s', 'now'));
END;

-- triggers for items
DROP TRIGGER IF EXISTS insert_item_blocked;
CREATE TRIGGER insert_item_blocked
AFTER INSERT ON items
FOR EACH ROW
BEGIN
  INSERT INTO item_blocked_log (item_pk, item_blocked_updated_at, item_blocked_value)
  VALUES (NEW.item_pk, strftime('%s', 'now'), 0);
END;

DROP TRIGGER IF EXISTS update_item;
CREATE TRIGGER update_item
AFTER UPDATE ON items
FOR EACH ROW
BEGIN
  INSERT INTO item_updated_log (item_pk, item_updated_at)
  VALUES (NEW.item_pk, strftime('%s', 'now'));
END;


-- views
DROP VIEW IF EXISTS user_with_status;
CREATE VIEW user_with_status AS
  SELECT
    users.*,
    COALESCE(
      (SELECT 1 FROM user_verification_completed WHERE user_verification_completed.user_pk = users.user_pk),
      0
    ) AS user_is_verified,
    COALESCE(
      (SELECT 1 FROM user_deleted_log WHERE user_deleted_log.user_pk = users.user_pk),
      0
    ) AS user_is_deleted,
    COALESCE(
      (
        SELECT user_blocked_value FROM user_blocked_updated_log
        WHERE user_blocked_updated_log.user_pk = users.user_pk
        ORDER BY user_blocked_updated_at DESC 
        LIMIT 1
      ),
      0
    ) AS user_is_blocked
  FROM
    users  
;

DROP VIEW IF EXISTS items_with_status;
CREATE VIEW items_with_status AS
  SELECT
    items.*,
    COALESCE(
      (
        SELECT item_blocked_value FROM item_blocked_log 
        WHERE item_blocked_log.item_pk = items.item_pk
        ORDER BY item_blocked_updated_at DESC 
        LIMIT 1
      ),
      0
    ) AS item_is_blocked
  FROM
    items  
;


-- initial data

--admin-user
-- INSERT INTO users VALUES(
--     "d11854217ecc42b2bb17367fe33dc8f4",
--     "johndoe",
--     "John",
--     "Doe",
--     "admin@company.com",
--     "$2b$12$V/cXqWN/M2vTnYUcXMB9oODcNBX/QorJekmaDkq1Z7aeD3I5ZAjfu",
--     (SELECT role_id FROM roles WHERE role_name = 'admin'),
--     1712674758
-- );
-- INSERT INTO user_verification_completed VALUES ("d11854217ecc42b2bb17367fe33dc8f4", 1712674758);

-- --partner-user
-- INSERT INTO users VALUES(
--     "d11854217ecc42b2bb17367fe33dc8f5",
--     "janedoe",
--     "Jane",
--     "Doe",
--     "partner@partner.com",
--     "$2b$12$V/cXqWN/M2vTnYUcXMB9oODcNBX/QorJekmaDkq1Z7aeD3I5ZAjfu",
--     (SELECT role_id FROM roles WHERE role_name = 'partner'),
--     1712674758
-- );
-- INSERT INTO user_verification_completed VALUES ("d11854217ecc42b2bb17367fe33dc8f5", 1712674758);

-- --user_user
-- INSERT INTO users VALUES(
--     "d11854217ecc42b2bb17367fe33dc8f6",
--     "useruser",
--     "Just",
--     "Auser",
--     "user@user.com",
--     "$2b$12$V/cXqWN/M2vTnYUcXMB9oODcNBX/QorJekmaDkq1Z7aeD3I5ZAjfu",
--     (SELECT role_id FROM roles WHERE role_name = 'user'),
--     1712674758
-- );
-- INSERT INTO user_verification_completed VALUES ("d11854217ecc42b2bb17367fe33dc8f6", 1712674758);


UPDATE users SET role_id =1 WHERE user_pk ='340fb8891b954d5ab81c13eec52477fe';

INSERT INTO ratings VALUES 
('1a20f720cec74b72a873ae111a25b347', '13fc34026b674e389fef6eed727db661',3,1717348368),
('3a124a64e43e456490fc699935a83708','13fc34026b674e389fef6eed727db661',4,1717348368),
('42d21968891148aa8572a06960dca0ad','13fc34026b674e389fef6eed727db661',2,1717348368),
('4c6de42726544fec9cab8820c0ce2430','13fc34026b674e389fef6eed727db661',5,1717348368),
('6ec9cd1d0da648b49ce02e369ed6937f','340fb8891b954d5ab81c13eec52477fe',3,1717348368),
('710a1d0761254bf8aaa79e12f3543bcf','340fb8891b954d5ab81c13eec52477fe',1,1717348368),
('8fc121d6bdec467ea3141c5d26d1a526','340fb8891b954d5ab81c13eec52477fe',3,1717348368),
('9a91e5ec95bc47a9a32ad43daab376b4','725df78b0dbf433a8a6a27985b5017ea',4,1717348368),
('1a20f720cec74b72a873ae111a25b347','725df78b0dbf433a8a6a27985b5017ea',3,1717348368),
('3a124a64e43e456490fc699935a83708','725df78b0dbf433a8a6a27985b5017ea',3,1717348368),
('42d21968891148aa8572a06960dca0ad','725df78b0dbf433a8a6a27985b5017ea',2,1717348368),
('4c6de42726544fec9cab8820c0ce2430','91e936b7130d495a90459963a637bd81',5,1717348368),
('6ec9cd1d0da648b49ce02e369ed6937f','91e936b7130d495a90459963a637bd81',3,1717348368),
('710a1d0761254bf8aaa79e12f3543bcf','91e936b7130d495a90459963a637bd81',4,1717348368),
('8fc121d6bdec467ea3141c5d26d1a526','a46f22c43ce542c4995132ea2eb1eb9e',5,1717348368),
('9a91e5ec95bc47a9a32ad43daab376b4', 'a46f22c43ce542c4995132ea2eb1eb9e',3,1717348368);

