--DROP SEQUENCE IF EXISTS traveler_id_sequence;
--CREATE SEQUENCE traveler_id_sequence start 1 increment 1;

DROP TABLE IF EXISTS traveler; 
CREATE TABLE traveler (
    id  SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    password VARCHAR(1025) NOT NULL,
    city_id INT,
    city VARCHAR(255),
    address VARCHAR(1025),
    phone VARCHAR(50),
    email VARCHAR(255) NOT NULL UNIQUE,
    bio TEXT,
    profile_picture bytea,
    credit_card_info VARCHAR(255),
    date_joined DATE,
    last_login DATE,
    is_admin boolean,
    is_active boolean,
    is_staff boolean,
    is_superuser boolean
);

--ALTER SEQUENCE traveler_id_sequence OWNED BY traveler.id;

DROP TABLE IF EXISTS friend;
CREATE TABLE friend (
    traveller_id INT not null,
    friend_id INT not null,
    date_of_friendship DATE CHECK(date_of_friendship > '2021-03-08')
);

DROP TABLE IF EXISTS favorites;
CREATE TABLE favorites (
    traveller_id INT not null,
    dest_id INT not null
);


DROP TABLE IF EXISTS destination;
CREATE TABLE destination (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(255) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    country_code VARCHAR(3) NOT NULL,
    destination_picture bytea,
    website_link VARCHAR(255)
);


DROP TABLE IF EXISTS attractions;
CREATE TABLE attractions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(2500) NOT NULL,
    zipcode VARCHAR(255),   
    phone VARCHAR(255),      
    website VARCHAR(255),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

-- INDEX -- Searching by name is the most common way to search in our app
CREATE INDEX dest_index ON destination(city_name);
CREATE INDEX att_index ON attractions(name);


-- VIEWS --
CREATE VIEW favorite_rank AS SELECT city_name, COUNT(city_name) AS c FROM (destination INNER JOIN favorites ON id = dest_id) GROUP BY city_name ORDER BY c DESC; 
CREATE VIEW museum_attractions AS SELECT * FROM attractions WHERE name LIKE '%museum%';
CREATE VIEW drinker_attractions AS SELECT * FROM attractions WHERE (name LIKE '%brewery%') OR (name LIKE '%distillery%') OR (name LIKE '%bar%') OR (name LIKE '%pub%');
CREATE VIEW nature_attractions AS SELECT * FROM attractions WHERE (name LIKE '%park%') OR (name LIKE '%trail%') OR (name LIKE '%slope%') OR (name LIKE '%mountain%') ;
CREATE VIEW sports_attractions AS SELECT * FROM attractions WHERE (name LIKE '%ballpark%') OR (name LIKE '%stadium%') OR (name LIKE '%sports%');
CREATE VIEW art_attractions AS SELECT * FROM attractions WHERE (name LIKE '%sculpture%') OR (name LIKE '%art%') OR (name LIKE '%exhibit%');
CREATE VIEW entertain_attractions AS SELECT * FROM attractions WHERE (name LIKE '%arcade%') OR (name LIKE '%laser tag%') OR (name LIKE '%Go Kart%');

-- CONSTRAINTS -- used in schemas above
-- PROCEDURES -- 
-- Deletes Friends and favorites when a user is deleted
CREATE OR REPLACE FUNCTION cleanFriendsFavs () RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN 
    DELETE FROM favorites WHERE OLD.id = traveller_id;
    DELETE FROM friend WHERE (traveller_id = OLD.id) OR (friend_id= OLD.id);
    RETURN NULL;
END;$$;

CREATE OR REPLACE PROCEDURE 

-- TRIGGERS -- 
CREATE TRIGGER cleanDB
    AFTER DELETE
    ON traveler
    FOR EACH ROW EXECUTE PROCEDURE cleanFriendsFavs();

-- PREPARED STATEMENTS --
-- Used in views because it can only be used per connection

-- Advanced Funtions Used:
-- 1.) Index
-- 2.) Views
-- 3.) Constraints
-- 4.) Triggers
-- 5.) Stored Procedures
-- 6.) Prepared Statements