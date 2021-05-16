--DROP SEQUENCE IF EXISTS traveler_id_sequence;
--CREATE SEQUENCE traveler_id_sequence start 1 increment 1;

DROP TABLE IF EXISTS traveler; 
CREATE TABLE traveler (
    id  SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    password VARCHAR(1025) NOT NULL,
    zip_code VARCHAR(5),
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

DROP TABLE IF EXISTS visits;
CREATE TABLE visits (
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

DROP TABLE IF EXISTS zipcodes;
CREATE TABLE zipcodes (
    id SERIAL PRIMARY KEY,
    zip_code VARCHAR(5) NOT NULL,
    city_name VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    timezone INT NOT NULL,
    daylight_savings INT NOT NULL,
    country_code VARCHAR(3) NOT NULL
);

INSERT INTO destination(id, city_name, latitude, longitude,country_code) VALUES (56450, 'Page', 36.9147,-111.4558 , 'USA');


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
CREATE OR REPLACE  VIEW favorite_rank AS SELECT city_name, COUNT(city_name) AS c FROM (destination INNER JOIN favorites ON id = dest_id) GROUP BY city_name ORDER BY c DESC; 
CREATE OR REPLACE  VIEW museum_attractions AS SELECT * FROM attractions WHERE name LIKE '%museum%';
CREATE OR REPLACE  VIEW drinker_attractions AS SELECT * FROM attractions WHERE (name LIKE '%brewery%') OR (name LIKE '%distillery%') OR (name LIKE '%bar%') OR (name LIKE '%pub%');
CREATE OR REPLACE  VIEW nature_attractions AS SELECT * FROM attractions WHERE (name LIKE '%park%') OR (name LIKE '%trail%') OR (name LIKE '%slope%') OR (name LIKE '%mountain%') ;
CREATE OR REPLACE  VIEW sports_attractions AS SELECT * FROM attractions WHERE (name LIKE '%ballpark%') OR (name LIKE '%stadium%') OR (name LIKE '%sports%');
CREATE OR REPLACE  VIEW art_attractions AS SELECT * FROM attractions WHERE (name LIKE '%sculpture%') OR (name LIKE '%art%') OR (name LIKE '%exhibit%') OR (name LIKE '%gallery%');
CREATE OR REPLACE  VIEW entertain_attractions AS SELECT * FROM attractions WHERE (name LIKE '%Arcade%') OR (name LIKE '%Laser%') OR (name LIKE '%Go Kart%') OR (name LIKE '%Cinema%');

--CREATE OR REPLACE  VIEW destination_w_states AS SELECT d.id, d.city_name, d.latitude, d.longitude, d.country_code, z.state FROM zipcodes z, destination d WHERE (ABS(d.latitude - z.latitude) < 0.1) AND (ABS(d.longitude - z.longitude)<0.1);
--CREATE TABLE destination_states AS SELECT distinct on(id) id,  city_name,  latitude,  longitude,  country_code,  state,  count(*) FROM destination_w_states GROUP BY id, city_name, latitude, longitude, country_code, state HAVING count(*) >1;
CREATE OR REPLACE VIEW destination_zipcodes AS SELECT d.id, d.city_name, z.state, z.zip_code FROM zipcodes z, destination d WHERE (d.city_name = z.city_name) AND distance(d.latitude, d.longitude, z.latitude, z.longitude) < 10 ORDER BY id ASC;
CREATE OR REPLACE VIEW destination_states_zip AS SELECT d.id, d.city_name, d.latitude, d.longitude, d.country_code, z.zip_code, z.state FROM zipcodes z, destination d WHERE (d.city_name = z.city_name) AND distance(d.latitude, d.longitude, z.latitude, z.longitude) < 20 ORDER BY id ASC;
CREATE OR REPLACE VIEW destination_states_d AS SELECT distinct on(id) id, city_name, latitude, longitude, state FROM destination_states_zip;

CREATE OR REPLACE VIEW traveler_zipcodes AS SELECT  t.id, t.first_name, t.last_name, z.zip_code, z.latitude, z.longitude FROM (traveler t INNER JOIN zipcodes z ON t.zip_code = z.zip_code); 
CREATE OR REPLACE VIEW visit_destination AS SELECT v.traveller_id, v.dest_id, d.city_name, d.latitude, d.longitude FROM (visits v INNER JOIN destination d ON v.dest_id = d.id);
CREATE OR REPLACE VIEW traveler_zipcodes_visits AS SELECT tz.id, tz.first_name, tz.last_name, tz.zip_code, distance(tz.latitude, tz.longitude, vd.latitude, vd.longitude) as distance_traveled FROM (traveler_zipcodes tz INNER JOIN visit_destination vd ON tz.id = vd.traveller_id); 
CREATE OR REPLACE VIEW traveler_distance_traveled AS SELECT id, first_name, last_name, SUM(distance_traveled) as total_distance_traveled FROM traveler_zipcodes_visits GROUP BY id, first_name, last_name ORDER BY total_distance_traveled DESC;

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

CREATE OR REPLACE FUNCTION distance(lat1 FLOAT, lon1 FLOAT, lat2 FLOAT, lon2 FLOAT) RETURNS FLOAT AS $$
DECLARE                                                   
    x float = 69.1 * (lat2 - lat1);                           
    y float = 69.1 * (lon2 - lon1) * cos(lat1 / 57.3);        
BEGIN                                                     
    RETURN sqrt(x * x + y * y);                               
END  
$$ LANGUAGE plpgsql;

-- TRIGGERS -- 
CREATE TRIGGER cleanDB
    AFTER DELETE
    ON traveler
    FOR EACH ROW EXECUTE PROCEDURE cleanFriendsFavs();

-- PREPARED STATEMENTS --
-- Used in views because it can only be used per connection

-- Advanced Techniques Used:
-- 1.) Index
-- 2.) Views
-- 3.) Constraints
-- 4.) Triggers
-- 5.) Stored Procedures
-- 6.) Prepared Statements


-- Advanced Functions Here -- 
