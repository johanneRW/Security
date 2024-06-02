-- Hashed passsword is: $2b$12$V/cXqWN/M2vTnYUcXMB9oODcNBX/QorJekmaDkq1Z7aeD3I5ZAjfu


DROP TABLE IF EXISTS roles;
--skal muligvis sættes anderledes op
CREATE TABLE roles(
    role_id INTEGER UNIQUE,
    role_name TEXT UNIQUE,
    PRIMARY KEY(role_id)
) WITHOUT ROWID;

INSERT INTO roles VALUES (1,'admin'), (2,'partner'), (3,'user');

DROP TABLE IF EXISTS users;
CREATE TABLE users(
    user_pk                 TEXT,
    user_username           TEXT,
    user_first_name               TEXT,
    user_last_name          TEXT,
    user_email              TEXT UNIQUE,
    user_password           TEXT,
    role_id                 INTEGER,
    user_created_at         INTEGER,
    user_updated_at         INTEGER,
    user_verification_key   TEXT UNIQUE,
    user_is_verified        INTEGER,
    user_is_verified_at     INTEGER,
    user_is_blocked         INTEGER,
    user_blocked_updated_at         INTEGER,
    user_is_deleted         INTEGER,
    user_deleted_at         INTEGER,
    FOREIGN KEY(role_id) REFERENCES roles(role_id),
    PRIMARY KEY(user_pk)
) WITHOUT ROWID;


--admin-user
INSERT INTO users VALUES(
    "d11854217ecc42b2bb17367fe33dc8f4",
    "johndoe",
    "John",
    "Doe",
    "admin@company.com",
    "$2b$12$V/cXqWN/M2vTnYUcXMB9oODcNBX/QorJekmaDkq1Z7aeD3I5ZAjfu",
    (SELECT role_id FROM roles WHERE role_name = 'admin'),
    1712674758,
    0,
    1,
    1,
    1,
    0,
    NULL,
    0,
    NULL
);

--partner-user
INSERT INTO users VALUES(
    "d11854217ecc42b2bb17367fe33dc8f5",
    "janedoe",
    "Jane",
    "Doe",
    "partner@partner.com",
    "$2b$12$V/cXqWN/M2vTnYUcXMB9oODcNBX/QorJekmaDkq1Z7aeD3I5ZAjfu",
    (SELECT role_id FROM roles WHERE role_name = 'partner'),
    1712674758,
    0,
    2,
    1,
    1,
    0,
    NULL,
    0,
    NULL
);
--user_user
INSERT INTO users VALUES(
    "d11854217ecc42b2bb17367fe33dc8f6",
    "useruser",
    "Just",
    "Auser",
    "user@user.com",
    "$2b$12$V/cXqWN/M2vTnYUcXMB9oODcNBX/QorJekmaDkq1Z7aeD3I5ZAjfu",
    (SELECT role_id FROM roles WHERE role_name = 'user'),
    1712674758,
    0,
    3,
    1,
    1,
    0,
    NULL,
    0,
    NULL
);




-- CREATE TABLE items(
--     item_pk                         TEXT,
--     item_name                       TEXT,
--     item_splash_image               TEXT,
--     item_lat                        TEXT,
--     item_lon                        TEXT,
--     item_stars                      REAL,
--     item_price_per_night            REAL,
--     item_created_at                 INTEGER,
--     item_updated_at                 INTEGER,
--     item_is_blocked                 INTEGER,
--     item_blocked_updated_at         INTEGER,
--     item_owned_by                   TEXT,
--     PRIMARY KEY(item_pk)
-- ) WITHOUT ROWID;
DROP TABLE IF EXISTS items;
CREATE TABLE items(
    item_pk                         TEXT,
    item_name                       TEXT,
    item_lat                        TEXT,
    item_lon                        TEXT,
    item_price_per_night            REAL,
    item_created_at                 INTEGER,
    item_updated_at                 INTEGER,
    item_is_blocked                 INTEGER,
    item_blocked_updated_at         INTEGER,
    item_owned_by                   TEXT,
    PRIMARY KEY(item_pk),
    FOREIGN KEY(item_owned_by) REFERENCES users(user_pk)
) WITHOUT ROWID;

DROP TABLE IF EXISTS ratings;
CREATE TABLE ratings(
    item_pk                         TEXT,
    user_pk                         TEXT,
    stars                           INTEGER,
    rating_created_at               INTEGER,
    PRIMARY KEY(item_pk, user_pk),
    FOREIGN KEY(item_pk) REFERENCES items(item_pk),
    FOREIGN KEY(user_pk) REFERENCES users(user_pk)
) WITHOUT ROWID;

-- INSERT INTO items VALUES
-- ("5dbce622fa2b4f22a6f6957d07ff4951", "Christiansborg Palace", "5dbce622fa2b4f22a6f6957d07ff4951.webp", 55.6761, 12.5770, 5, 2541, 1, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
-- ("5dbce622fa2b4f22a6f6957d07ff4952", "Tivoli Gardens", "5dbce622fa2b4f22a6f6957d07ff4952.webp", 55.6736, 12.5681, 4.97, 985, 2, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
-- ("5dbce622fa2b4f22a6f6957d07ff4953", "Nyhavn", "5dbce622fa2b4f22a6f6957d07ff4953.webp", 55.6794, 12.5918, 3.45, 429, 3, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
-- ("5dbce622fa2b4f22a6f6957d07ff4954", "The Little Mermaid statue", "5dbce622fa2b4f22a6f6957d07ff4954.webp", 55.6929, 12.5998, 4, 862, 4, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
-- ("5dbce622fa2b4f22a6f6957d07ff4955", "Amalienborg Palace", "5dbce622fa2b4f22a6f6957d07ff4955.webp", 55.6846, 12.5949, 2.67, 1200, 5, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f4"),
-- ("5dbce622fa2b4f22a6f6957d07ff4956", "Copenhagen Opera House", "5dbce622fa2b4f22a6f6957d07ff4956.webp",  55.6796, 12.6021, 4.57, 1965, 6, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
-- ("5dbce622fa2b4f22a6f6957d07ff4957", "Rosenborg Castle", "5dbce622fa2b4f22a6f6957d07ff4957.webp", 55.6867, 12.5734, 4, 1700, 7, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
-- ("5dbce622fa2b4f22a6f6957d07ff4958", "The National Museum of Denmark", "5dbce622fa2b4f22a6f6957d07ff4958.webp", 55.6772, 12.5784, 5, 2100, 8, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
-- ("5dbce622fa2b4f22a6f6957d07ff4959", "Church of Our Saviour", "5dbce622fa2b4f22a6f6957d07ff4959.webp", 55.6732, 12.5986, 4.3, 985, 9, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
-- ("5dbce622fa2b4f22a6f6957d07ff4910", "Round Tower", "5dbce622fa2b4f22a6f6957d07ff4910.webp",  55.6813, 12.5759, 4.8, 1200, 10, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f4");

INSERT INTO items VALUES
("5dbce622fa2b4f22a6f6957d07ff4951", "Christiansborg Palace", 55.6761, 12.5770, 2541, 1, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
("5dbce622fa2b4f22a6f6957d07ff4952", "Tivoli Gardens", 55.6736, 12.5681,  985, 2, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
("5dbce622fa2b4f22a6f6957d07ff4953", "Nyhavn", 55.6794, 12.5918,  429, 3, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
("5dbce622fa2b4f22a6f6957d07ff4954", "The Little Mermaid statue", 55.6929, 12.5998,  862, 4, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
("5dbce622fa2b4f22a6f6957d07ff4955", "Amalienborg Palace", 55.6846, 12.5949,  1200, 5, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f4"),
("5dbce622fa2b4f22a6f6957d07ff4956", "Copenhagen Opera House",  55.6796, 12.6021,  1965, 6, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
("5dbce622fa2b4f22a6f6957d07ff4957", "Rosenborg Castle", 55.6867, 12.5734,  1700, 7, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
("5dbce622fa2b4f22a6f6957d07ff4958", "The National Museum of Denmark", 55.6772, 12.5784,  2100, 8, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
("5dbce622fa2b4f22a6f6957d07ff4959", "Church of Our Saviour", 55.6732, 12.5986,  985, 9, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f5"),
("5dbce622fa2b4f22a6f6957d07ff4910", "Round Tower",  55.6813, 12.5759,  1200, 10, 0,0,0,"d11854217ecc42b2bb17367fe33dc8f4");

INSERT INTO ratings VALUES
("5dbce622fa2b4f22a6f6957d07ff4951","d11854217ecc42b2bb17367fe33dc8f4", 5,1 ),
("5dbce622fa2b4f22a6f6957d07ff4952","d11854217ecc42b2bb17367fe33dc8f4", 4.97,2),
("5dbce622fa2b4f22a6f6957d07ff4953","d11854217ecc42b2bb17367fe33dc8f4", 3.45,3),
("5dbce622fa2b4f22a6f6957d07ff4954","d11854217ecc42b2bb17367fe33dc8f4",  4,4),
("5dbce622fa2b4f22a6f6957d07ff4955","d11854217ecc42b2bb17367fe33dc8f4", 2.67,5),
("5dbce622fa2b4f22a6f6957d07ff4956", "d11854217ecc42b2bb17367fe33dc8f4", 4.57,6),
("5dbce622fa2b4f22a6f6957d07ff4957","d11854217ecc42b2bb17367fe33dc8f4",  4,7),
("5dbce622fa2b4f22a6f6957d07ff4958","d11854217ecc42b2bb17367fe33dc8f4", 5,8),
("5dbce622fa2b4f22a6f6957d07ff4959","d11854217ecc42b2bb17367fe33dc8f4", 4.3,9),
("5dbce622fa2b4f22a6f6957d07ff4910","d11854217ecc42b2bb17367fe33dc8f4", 4.8,10);





DROP TABLE IF EXISTS password_reset;

CREATE TABLE password_reset(
password_reset_key     TEXT,
password_reset_at       INTEGER,
password_user_pk    TEXT,
PRIMARY KEY(password_reset_key )
)WITHOUT ROWID;


DROP TABLE IF EXISTS item_images;
CREATE TABLE item_images (
    image_pk TEXT ,
    item_pk TEXT,
    image_filename TEXT,
    PRIMARY KEY(image_pk),
    FOREIGN KEY (item_pk) REFERENCES items (item_pk)
)WITHOUT ROWID;

INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('b8e3b2e6b0794d229b19bb9b95761e0d', '5dbce622fa2b4f22a6f6957d07ff4951', '5dbce622fa2b4f22a6f6957d07ff4951.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('0b2b3c5b5c0a4bbca46da4d3c3f9b41e', '5dbce622fa2b4f22a6f6957d07ff4951', '5dbce622fa2b4f22a6f6957d07ff4952.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('528d7f7a5d7e4d44a71b4a3b08a2f71f', '5dbce622fa2b4f22a6f6957d07ff4951', '5dbce622fa2b4f22a6f6957d07ff4953.webp');

INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('27d77f9b3d6242a9b8b4b0b5c87f7f57', '5dbce622fa2b4f22a6f6957d07ff4952', '5dbce622fa2b4f22a6f6957d07ff4952.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('b2a8d9b1b1c64b5e8f3b8b7f7e9a8f88', '5dbce622fa2b4f22a6f6957d07ff4952', '5dbce622fa2b4f22a6f6957d07ff4953.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('6c3f2f4e4a1a4a9e8b3b8d7f7e8a6a67', '5dbce622fa2b4f22a6f6957d07ff4952', '5dbce622fa2b4f22a6f6957d07ff4954.webp');

INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('2d3b8f9b2f2a4a4b8d3a8a7b7e9a8f89', '5dbce622fa2b4f22a6f6957d07ff4953', '5dbce622fa2b4f22a6f6957d07ff4953.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('f7e7a5d2d2a8b8f5c5b5d4f4b3a8e9e9', '5dbce622fa2b4f22a6f6957d07ff4953', '5dbce622fa2b4f22a6f6957d07ff4954.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('1f9a8b7c3c2b1a1e8d3b8f7f7e9a8a9a', '5dbce622fa2b4f22a6f6957d07ff4953', '5dbce622fa2b4f22a6f6957d07ff4955.webp');

INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('d7b8c3f2a9e8d5a4b4a5f5e7c7b9d8e8', '5dbce622fa2b4f22a6f6957d07ff4954', '5dbce622fa2b4f22a6f6957d07ff4954.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('8c3b3a7b9b4b4b5b8a6f7f5e7c6d6a6a', '5dbce622fa2b4f22a6f6957d07ff4954', '5dbce622fa2b4f22a6f6957d07ff4955.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('3b9a8b7c2c3b4a1b8d7b8f7f7e9a8b8a', '5dbce622fa2b4f22a6f6957d07ff4954', '5dbce622fa2b4f22a6f6957d07ff4956.webp');

INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('2a9b3b7c2c4a5a1e8d3b8f7f7e9a8c8a', '5dbce622fa2b4f22a6f6957d07ff4955', '5dbce622fa2b4f22a6f6957d07ff4955.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('5a7b8b7c1c3a4a1f8b3b8f7f7e9a8d8a', '5dbce622fa2b4f22a6f6957d07ff4955', '5dbce622fa2b4f22a6f6957d07ff4956.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('9a8b3c7b1c2a3a4e8d3b8f7f7e9a8b9a', '5dbce622fa2b4f22a6f6957d07ff4955', '5dbce622fa2b4f22a6f6957d07ff4957.webp');

INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('4a8b9c7a1b2a3c4a8d3b8f7f7e9a8c8a', '5dbce622fa2b4f22a6f6957d07ff4956', '5dbce622fa2b4f22a6f6957d07ff4956.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('7a8b1c7a2b3a4a1e8d3b8f7f7e9a8d8a', '5dbce622fa2b4f22a6f6957d07ff4956', '5dbce622fa2b4f22a6f6957d07ff4957.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('2b8c3b7c4a5a1a8e8d3b8f7f7e9a8c8a', '5dbce622fa2b4f22a6f6957d07ff4956', '5dbce622fa2b4f22a6f6957d07ff4958.webp');

INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('1a8b3c7a4c2a5a8e8d3b8f7f7e9a8b8a', '5dbce622fa2b4f22a6f6957d07ff4957', '5dbce622fa2b4f22a6f6957d07ff4957.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('6a8b1c2a4a3a5e8d3b8f7f7e9a8c8a8a', '5dbce622fa2b4f22a6f6957d07ff4957', '5dbce622fa2b4f22a6f6957d07ff4958.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('9a8b2c4a1b3a3a8e8d3b8f7f7e9a8b8a', '5dbce622fa2b4f22a6f6957d07ff4957', '5dbce622fa2b4f22a6f6957d07ff4959.webp');

INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('3a8b1c2a4b3a5a8e8d3b8f7f7e9a8c8a', '5dbce622fa2b4f22a6f6957d07ff4958', '5dbce622fa2b4f22a6f6957d07ff4958.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('7a8b2c3a1a4a5e8d3b8f7f7e9a8c8a8a', '5dbce622fa2b4f22a6f6957d07ff4958', '5dbce622fa2b4f22a6f6957d07ff4959.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('4a8b1c3a2a5a3e8d3b8f7f7e9a8b8a8a', '5dbce622fa2b4f22a6f6957d07ff4958', '5dbce622fa2b4f22a6f6957d07ff4910.webp');

INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('9a8b2c1a3b4a5a8e8d3b8f7f7e9a8c8a', '5dbce622fa2b4f22a6f6957d07ff4959', '5dbce622fa2b4f22a6f6957d07ff4959.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('2a8b1c3a4b5a1e8d3b8f7f7e9a8c8a8a', '5dbce622fa2b4f22a6f6957d07ff4959', '5dbce622fa2b4f22a6f6957d07ff4910.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('1a8b2c3a4a5a3e8d3b8f7f7e9a8b8a8a', '5dbce622fa2b4f22a6f6957d07ff4959', '5dbce622fa2b4f22a6f6957d07ff4951.webp');

INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('8a8b1c2a3b4a5a8e8d3b8f7f7e9a8c8a', '5dbce622fa2b4f22a6f6957d07ff4910', '5dbce622fa2b4f22a6f6957d07ff4910.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('3a8b1c2a4a5a5e8d3b8f7f7e9a8c8a8a', '5dbce622fa2b4f22a6f6957d07ff4910', '5dbce622fa2b4f22a6f6957d07ff4951.webp');
INSERT INTO item_images (image_pk, item_pk, image_filename) VALUES ('6a8b2c3a4b5a1e8d3b8f7f7e9a8b8a8a', '5dbce622fa2b4f22a6f6957d07ff4910', '5dbce622fa2b4f22a6f6957d07ff4952.webp');



-- (page_number - 1) * items_per_page
-- (1 - 1) * 3 = 10 1 2
-- (2 - 1) * 3 = 3 4 5
-- (3 - 1) * 3 = 6 7 8


-- Page 4
-- 0 3 6 9
SELECT * FROM items 
ORDER BY item_created_at
LIMIT 9,3;


-- offset = (currentPage - 1) * itemsPerPage
-- page 1 = 1 2 3+
-- page 2 = 4 5 6
-- page 3 = 7 8 9
-- page 4 = 10
SELECT * FROM items 
ORDER BY item_created_at
LIMIT 3 OFFSET 9;

SELECT * FROM items WHERE item_pk = '5dbce622fa2b4f22a6f6957d07ff4910';

UPDATE items 
SET item_is_blocked = 1, item_blocked_updated_at = 2 
WHERE item_pk = '5dbce622fa2b4f22a6f6957d07ff4910';

SELECT * FROM items;

UPDATE users
SET user_username ='updateuserName',  user_first_name='updateName', user_last_name='updateLastName', 
 user_email = 'updateEmail',  user_updated_at=67 WHERE user_pk='d11854217ecc42b2bb17367fe33dc8f6';         
             

UPDATE users
SET user_is_verified = 1,
    user_is_verified_at = 2222
WHERE user_verification_key = '18c0312bf32345aea8c4cb6b980ba958';

DELETE FROM users WHERE user_pk='a749ea0f2dac49f286c7377443d7148d';

SELECT users.user_username, users.user_email 
FROM items JOIN users ON items.item_owned_by = users.user_pk
WHERE items.item_pk = 'd11854217ecc42b2bb17367fe33dc8f5';


SELECT user_pk FROM users WHERE user_email= 'user@user.com';


SELECT * FROM users WHERE user_email = 'user@user.com' AND user_is_verified = 1 AND user_is_deleted= 0 LIMIT 1;

UPDATE users SET user_is_deleted=0, user_deleted_at=NULL WHERE user_pk='d11854217ecc42b2bb17367fe33dc8f6';

SELECT * FROM items  WHERE item_owned_by='d11854217ecc42b2bb17367fe33dc8f5' ORDER BY item_created_at;

SELECT items.*, 
            COALESCE(AVG(ratings.stars), 0) as item_stars
            FROM items
            LEFT JOIN ratings ON items.item_pk = ratings.item_pk
            GROUP BY items.item_pk
            ORDER BY items.item_created_at;


SELECT image_filename FROM item_images WHERE item_pk = '5dbce622fa2b4f22a6f6957d07ff4951';

SELECT items.*, 
    group_concat(item_images.image_filename) AS images
    FROM items
    LEFT JOIN item_images ON items.item_pk = item_images.item_pk
    WHERE items.item_owned_by = 'd11854217ecc42b2bb17367fe33dc8f5'
    GROUP BY items.item_pk
    ORDER BY items.item_created_at;

SELECT items.*, 
            group_concat(item_images.image_filename) AS images
    FROM items
    LEFT JOIN item_images ON items.item_pk = item_images.item_pk
    WHERE items.item_owned_by = 'd11854217ecc42b2bb17367fe33dc8f5'
      --AND items.item_pk = '5dbce622fa2b4f22a6f6957d07ff4952'
    GROUP BY items.item_pk
    ORDER BY items.item_created_at;               