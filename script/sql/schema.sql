DROP TYPE IF EXISTS gender;
CREATE TYPE gender AS ENUM ('male', 'female', 'other');

--DROP SEQUENCE IF EXISTS traveler_id_sequence;
--CREATE SEQUENCE traveler_id_sequence start 1 increment 1;

DROP TABLE IF EXISTS traveler; 
CREATE TABLE traveler (
    id  SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    -- password VARCHAR(1025) NOT NULL,
    address VARCHAR(1025),
    phone VARCHAR(50),
    email VARCHAR(255) NOT NULL,
    -- birth_date DATE CHECK(birth_date > '1900-01-01'),
    bio TEXT,
    -- user_gender gender NOT NULL,
    profile_picture bytea,
    --location VARCHAR(255),
    credit_card_info VARCHAR(255),
    email_confirmation boolean
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

