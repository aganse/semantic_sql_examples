# Semantic_sql_demos
Semantic SQL demos using PostgreSQL pgvector and review embeddings


### Summary

These demos use the contents of the 
[Seattle AirBnB](https://www.kaggle.com/datasets/airbnb/seattle/data) dataset
which are deposited into a database for further processing and exploration.
(The original Kaggle dataset was contained in csv files, but the 
[Seattle_AirBnB_ETL](https://github.com/mileslucey/Seattle_AirBnB_ETL)
repo had a nice setup to load that into database, albeit written for MySQL.
The version of it in here was updated to work for PostgreSQL instead.)
A language-embeddings model is run on each review comments field to produce
an embedding vector that gets saved to the database.
Then various SQL queries are run on the resulting database contents to
explore and demonstrate semantic search related ideas.


### Usage

  1. Create and enter Python virtual environment
      - `python3.12 -m venv .venv`
      - `source .venv/bin/activate`
      - `pip install -r requirements.txt`

  2. Only needed once: download the models and dataset
      - `python download_model_and_data.py`
      - in the console output from that run, find the long OpenCLIP model path
        string and paste into config.py under CLIP_PATH.

  2. Create database and prep/load Airbnb data into it
      - assuming that you have a PostgreSQL database system running/available
      - you might need to update database connect string in `config.py` to match
        your setup; by default it assumes a `~/.pgpass` file exists containing
        a corresponding line like
        `localhost:5432:seattle_airbnb_db:script_runner:mypasswordhere`.
      - `createdb.sql` is called via `\i /path/to/createdb.sql` in `psql` to
        create the `seattle_airbnb_db` database and its schema.
      - `python etl_data.py` cleans the CSV contents and writes
        listings/hosts/reviews/availability data into the database

  3. (Optional) Document the DB schema
      - `docker-compose.yaml` runs SchemaSpy and writes the generated schema
        docs into `spy_data/`.

  4. Create embeddings
      - `python pipeline.py` runs embedding model on review comments and saves
        in `embeddings_768` table
      - by default the OpenCLIP ViT-L-14 model is used (because it's really fast
        and requires few resources).  after trying that one you can change the
        EMBED_TYPE in config.py from CLIP to E5.  both types can go into that
        embeddings_768 table (they both have length 768 embedding vectors and
        the tags field in that table records which EMBED_TYPE it was), and then
        you can specify the tag desired in database queries later.
      - on my MacBookPro-M2-2022 that OpenCLIP model takes about 43 minutes to
        compute the embeddings for the 84849 reviews, and the E5 model takes
        about 4 hours to do so.

