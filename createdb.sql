-- Populate tables in this database with the contents of the csv datafiles.
-- Then this database will be used in lieu of the files for analysis/modeling work.

CREATE DATABASE seattle_airbnb_db;
\c seattle_airbnb_db;

CREATE EXTENSION IF NOT EXISTS vector;

-- Drop tables (order matters due to FK constraints)
DROP TABLE IF EXISTS property_availability CASCADE;
DROP TABLE IF EXISTS property_reviews CASCADE;
DROP TABLE IF EXISTS listings CASCADE;
DROP TABLE IF EXISTS airbnb_hosts CASCADE;

-- Hosts table
CREATE TABLE airbnb_hosts(
    host_id INTEGER PRIMARY KEY,
    host_name VARCHAR(150),
    host_since DATE,
    host_location VARCHAR(150),
    host_response_time VARCHAR(200),
    host_response_rate INTEGER,
    host_acceptance_rate INTEGER,
    host_is_superhost BOOLEAN,
    host_neighbourhood VARCHAR(100),
    host_listings_count INTEGER,
    host_has_profile_pic BOOLEAN,
    host_identity_verified BOOLEAN
);

-- Listings table
CREATE TABLE listings(
    id INTEGER PRIMARY KEY,
    listing_name VARCHAR(100),
    street VARCHAR(300),
    neighbourhood_cleansed VARCHAR(150),
    neighbourhood_group_cleansed VARCHAR(150),
    city VARCHAR(150),
    state VARCHAR(5),
    zipcode VARCHAR(20),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    is_location_exact BOOLEAN,
    property_type VARCHAR(150),
    room_type VARCHAR(150),
    accommodates INTEGER,
    bathrooms INTEGER,
    bedrooms INTEGER,
    beds INTEGER,
    bed_type VARCHAR(200),
    square_feet INTEGER,
    price NUMERIC,
    weekly_price NUMERIC,
    monthly_price NUMERIC,
    security_deposit NUMERIC,
    cleaning_fee NUMERIC,
    guests_included INTEGER,
    extra_people NUMERIC,
    minimum_nights INTEGER,
    maximum_nights INTEGER,
    has_availability BOOLEAN,
    availability_30 INTEGER,
    availability_60 INTEGER,
    availability_90 INTEGER,
    availability_365 INTEGER,
    calendar_updated DATE,
    number_of_reviews INTEGER,
    first_review DATE,
    last_review DATE,
    review_scores_rating INTEGER,
    review_scores_accuracy INTEGER,
    review_scores_cleanliness INTEGER,
    review_scores_checkin INTEGER,
    review_scores_communication INTEGER,
    review_scores_location INTEGER,
    review_scores_value INTEGER,
    requires_license BOOLEAN,
    instant_bookable BOOLEAN,
    cancellation_policy VARCHAR(200),
    require_guest_profile_picture BOOLEAN,
    require_guest_phone_verification BOOLEAN,
    reviews_per_month NUMERIC,
    host_id INTEGER,
    CONSTRAINT fk_host
        FOREIGN KEY(host_id)
        REFERENCES airbnb_hosts(host_id)
        ON DELETE CASCADE
);

-- Property availability table
CREATE TABLE property_availability(
    id SERIAL PRIMARY KEY,  -- replaces AUTO_INCREMENT
    listing_id INTEGER,
    available_date DATE,
    available BOOLEAN,
    price NUMERIC,
    CONSTRAINT fk_listing_availability
        FOREIGN KEY(listing_id)
        REFERENCES listings(id)
        ON DELETE CASCADE
);

-- Property reviews table
CREATE TABLE property_reviews(
    review_id INTEGER PRIMARY KEY,
    listing_id INTEGER,
    review_date DATE,
    reviewer_id INTEGER,
    reviewer_name VARCHAR(100),
    comments TEXT,  -- replaces MEDIUMTEXT
    CONSTRAINT fk_listing_reviews
        FOREIGN KEY(listing_id)
        REFERENCES listings(id)
        ON DELETE CASCADE
);

CREATE TABLE embeddings_768(
    id BIGSERIAL PRIMARY KEY,  -- autoincrements
    entry_time TIMESTAMP DEFAULT current_timestamp,
    review_id INTEGER,
    embedding vector(768),
    tag TEXT,
    CONSTRAINT fk_review
        FOREIGN KEY(review_id)
        REFERENCES property_reviews(review_id)
        ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_embeddings_768_hnsw
ON embeddings_768
USING hnsw (embedding vector_cosine_ops);

GRANT SELECT, INSERT, UPDATE ON airbnb_hosts TO script_runner;
GRANT SELECT, INSERT, UPDATE ON listings TO script_runner;
GRANT SELECT, INSERT, UPDATE ON property_availability TO script_runner;
GRANT SELECT, INSERT, UPDATE ON property_reviews TO script_runner;

GRANT USAGE ON SCHEMA public TO script_runner;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO script_runner;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO script_runner; -- existing tables 
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO script_runner; -- for future tables
