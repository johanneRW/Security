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
  password_reset_key TEXT,
  password_reset_at INTEGER,
  PRIMARY KEY(user_pk),
  CONSTRAINT user_pk_user_pk FOREIGN KEY (user_pk) REFERENCES users (user_pk)
) WITHOUT ROWID;


DROP TABLE IF EXISTS user_blocked_updated_log;
CREATE TABLE user_blocked_updated_log(
  user_pk TEXT ,
  user_blocked_updated_at INTEGER ,
  user_blocked_value INTEGER ,
  PRIMARY KEY(user_pk),
  CONSTRAINT user_pk_user_pk FOREIGN KEY (user_pk) REFERENCES users (user_pk)
) WITHOUT ROWID;

DROP TABLE IF EXISTS user_deleted_log;
CREATE TABLE user_deleted_log(
  user_pk TEXT ,
  user_deleted_at INTEGER,
  PRIMARY KEY(user_pk),
  CONSTRAINT user_pk_user_pk FOREIGN KEY (user_pk) REFERENCES users (user_pk)
) WITHOUT ROWID;

DROP TABLE IF EXISTS user_updated_log;
CREATE TABLE user_updated_log(
  user_pk TEXT ,
  user_updated_at INTEGER,
  PRIMARY KEY(user_pk),
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
  CONSTRAINT users_items
    FOREIGN KEY (item_owned_by) REFERENCES users (user_pk)
) WITHOUT ROWID;


DROP TABLE IF EXISTS item_blocked_log;
CREATE TABLE item_blocked_log(
  item_pk TEXT,
  item_blocked_updated_at INTEGER,
  item_blocked_value INTEGER,
  PRIMARY KEY(item_pk),
  CONSTRAINT item_pk_item_pk FOREIGN KEY (item_pk) REFERENCES items (item_pk)
) WITHOUT ROWID;

DROP TABLE IF EXISTS item_images;
CREATE TABLE item_images(
  image_pk TEXT UNIQUE,
  item_pk TEXT,
  image_filename TEXT,
  PRIMARY KEY(image_pk),
  CONSTRAINT items_item_images
    FOREIGN KEY (item_pk) REFERENCES items (item_pk) ON DELETE No action
      ON UPDATE No action
) WITHOUT ROWID;

 
DROP TABLE IF EXISTS item_updated_log;
CREATE TABLE item_updated_log(
  item_pk TEXT ,
  item_updated_at INTEGER,
  PRIMARY KEY(item_pk),
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
    FOREIGN KEY (user_pk) REFERENCES users (user_pk) ON DELETE No action
      ON UPDATE No action,
  CONSTRAINT items_ratings
    FOREIGN KEY (item_pk) REFERENCES items (item_pk) ON DELETE No action
      ON UPDATE No action
) WITHOUT ROWID;

 
DROP TABLE IF EXISTS bookings;
CREATE TABLE bookings(
  user_pk TEXT NOT NULL,
  item_pk TEXT NOT NULL,
  booking_created_at INTEGER NOT NULL,
  booking_number_of_nights INTEGER,
  booking_price REAL,
  PRIMARY KEY(item_pk, user_pk, booking_created_at),
  CONSTRAINT user_pk_user_pk FOREIGN KEY (user_pk) REFERENCES users (user_pk),
  CONSTRAINT item_pk_item_pk FOREIGN KEY (item_pk) REFERENCES items (item_pk)
) WITHOUT ROWID;


