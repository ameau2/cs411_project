CREATE TYPE gender AS ENUM ('male', 'female', 'other');

CREATE TABLE traveler (
    id  SERIAL PRIMARY KEY,
    first_name VARCHAR2(255) NOT NULL,
    last_name VARCHAR2(255) NOT NULL,
    password CHKPASS,
    address VARCHAR(1025),
    phone VARCHAR2(50),
    email VARCHAR2(255) NOT NULL,
    birth_date DATE CHECK(birth_date > '1900-01-01'),
    bio TEXT,
    user_gender gender NOT NULL,
    profile_picture bytea,
    location VARCHAR2(255),
    credit_card_info VARCHAR2(255),
    email_confirmation boolean
);

CREATE TABLE friend (
    traveller_id INT not null,
    friend_id INT not null,
    date_of_friendship DATE CHECK(date_of_friendship > '2021-03-08')
);

CREATE TABLE favorites (
    traveller_id INT not null,
    dest_id INT not null
);

CREATE TABLE destination (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR2(255) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    country_code VARCHAR2(3) NOT NULL,
    destination_picture bytea,
    website_link VARCHAR2(255)
);

