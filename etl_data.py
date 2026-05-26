"""This script was adapted from the ipynb file
https://github.com/mileslucey/Seattle_AirBnB_ETL/blob/master/etl_analysis.ipynb
(thank you!)
"""

import os

import pandas as pd

from db_helper import insert_table
from config import DB_URL

# This should match the path output in download_models_and_data.py
dataset_dir = "~/.cache/kagglehub/datasets/airbnb/seattle/versions/2"


## Creating the "Listings" dataframe and cleaning it
print("Creating/cleaning listings df...")

# Store CSV to DataFrame
listing_host_csv = os.path.join(dataset_dir, "listings.csv")
print("listing_host_csv", listing_host_csv)
listing_host_df = pd.read_csv(listing_host_csv,encoding="utf8")

# change column "name" to something that SQL doesn't already recognize
listing_host_df = listing_host_df.rename(index=str,columns={"name":"listing_name"})
listing_host_df.head()

# Create new data with select columns for the AirBnB listings
listing_df = listing_host_df[["id","listing_name","street","neighbourhood_cleansed","neighbourhood_group_cleansed","city","state","zipcode","latitude","longitude","is_location_exact","property_type","room_type","accommodates","bathrooms","bedrooms","beds","bed_type","square_feet","price","weekly_price","monthly_price","security_deposit","cleaning_fee","guests_included","extra_people","minimum_nights","maximum_nights","has_availability","availability_30","availability_60","availability_90","availability_365","number_of_reviews","first_review","last_review","review_scores_rating","review_scores_accuracy","review_scores_cleanliness","review_scores_checkin","review_scores_communication","review_scores_location","review_scores_value","requires_license","instant_bookable","cancellation_policy","require_guest_profile_picture","require_guest_phone_verification","reviews_per_month","host_id"]].copy()
# convert dates to datetime
listing_df["first_review"]=pd.to_datetime(listing_df["first_review"])
listing_df["last_review"]=pd.to_datetime(listing_df["last_review"])
# convert boolean columns to boolean
bool_map = {"t": True, "f": False}
listing_bool_cols = [
    "is_location_exact",
    "has_availability",
    "requires_license",
    "instant_bookable",
    "require_guest_profile_picture",
    "require_guest_phone_verification",
]
for col in listing_bool_cols:
    listing_df[col] = listing_df[col].map(bool_map).astype("boolean")
# convert all the currency columns to numeric values instead of strings
# define the currency columns
currency_cols=["price","weekly_price","monthly_price","security_deposit","cleaning_fee","extra_people"]
# remove dollar sign and commas
for col in currency_cols:
    cleaned = listing_df[col].astype("string").str.replace(r"[$,]", "", regex=True)
    listing_df[col] = pd.to_numeric(cleaned, errors="coerce")


## Creating the "Hosts" dataframe and cleaning it (2751 rows × 12 columns)
print("Creating/cleaning hosts df...")

# Create new data with select columns for the AirBnB hosts
host_df = listing_host_df[["host_id","host_name","host_since","host_location","host_response_time","host_response_rate","host_acceptance_rate","host_is_superhost","host_neighbourhood","host_listings_count","host_has_profile_pic","host_identity_verified"]].copy()
# delete duplicates
host_df = host_df.drop_duplicates(keep="first")
# convert dates to datetime format
host_df["host_since"]=pd.to_datetime(host_df["host_since"])
# convert boolean columns to boolean
host_bool_cols = ["host_is_superhost", "host_has_profile_pic", "host_identity_verified"]
for col in host_bool_cols:
    host_df[col] = host_df[col].map(bool_map).astype("boolean")
# converting the percentage columns from strings to percentages
# remove the percentage symbols from the columns with percentages
for col in ["host_response_rate", "host_acceptance_rate"]:
    cleaned = host_df[col].astype("string").str.replace(r"[$,%]", "", regex=True)
    host_df[col] = pd.to_numeric(cleaned, errors="coerce")


## Creating the "Availability" dataframe and cleaning it
print("Creating/cleaning availability df...")

# Store CSV to DataFrame
availability_file = os.path.join(dataset_dir, "calendar.csv")
availability_df = pd.read_csv(availability_file,encoding="utf8")
# change column "date" to something that SQL doesn't already recognize
availability_df = availability_df.rename(index=str,columns={"date":"available_date"})
# convert column to datetime
availability_df["available_date"]=pd.to_datetime(availability_df["available_date"])
# convert boolean columns to boolean
availability_df["available"] = availability_df["available"].map(bool_map).astype("boolean")
# remove dollar sign
cleaned_price = availability_df["price"].astype("string").str.replace(r"[$,]", "", regex=True)
# convert the price column to numeric values instead of strings
availability_df["price"] = pd.to_numeric(cleaned_price, errors="coerce")


## Creating the "Reviews" dataframe and cleaning it
print("Creating/cleaning reviews df...")

# Store CSV to DataFrame
reviews_file = os.path.join(dataset_dir, "reviews.csv")
reviews_df = pd.read_csv(reviews_file,encoding="utf8")
# change column "date/id" to something that SQL doesn't already recognize
reviews_df = reviews_df.rename(index=str,columns={"date":"review_date"})
reviews_df = reviews_df.rename(columns={"id":"review_id"})
# Create new data with select columns for the AirBnB listings
reviews_df = reviews_df[['review_id', "listing_id", "review_date", "reviewer_id", "reviewer_name", "comments"]].copy()
# convert dates to datetime
reviews_df["review_date"] = pd.to_datetime(reviews_df["review_date"])
# trim newlines and "exterior" whitespace from comments (not in original ipynb)
reviews_df["comments"] = (
    reviews_df["comments"]
        .astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
)
# convert any np.nan to "" in the comments (not in original ipynb)
reviews_df["comments"] = reviews_df["comments"].fillna("").astype(str).tolist()


## Load dataframes into database (a bit different from original ipynb)
print("Adding df's to database...")
insert_table(host_df, "airbnb_hosts", DB_URL)
insert_table(listing_df, "listings", DB_URL)
insert_table(availability_df, "property_availability", DB_URL)
insert_table(reviews_df, "property_reviews", DB_URL)
