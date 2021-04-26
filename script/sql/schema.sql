--DROP SEQUENCE IF EXISTS traveler_id_sequence;
--CREATE SEQUENCE traveler_id_sequence start 1 increment 1;

DROP TABLE IF EXISTS traveler; 
CREATE TABLE traveler (
    id  SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    password VARCHAR(1025) NOT NULL,
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

