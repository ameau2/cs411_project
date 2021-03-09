CREATE TABLE appVersion (
    version VARCHAR2(255)
);

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
);

CREATE TABLE friend (
    traveller_id INT not null,
    friend_id INT not null
);

CREATE TABLE destination (
    id SERIAL PRIMARY KEY,
    ....



)

* CONSTRAINT
* INDEX/ KEY
* RELATIONSHIP
* ENTITY

