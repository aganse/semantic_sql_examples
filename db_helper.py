import pandas as pd
from sqlalchemy import create_engine


def fetch_review_chunks(engine, chunk_size=5000):
    query = "SELECT review_id, comments FROM property_reviews ORDER BY 1"
    yield from pd.read_sql(query, engine, chunksize=chunk_size)


def insert_embeddings(conn, rows):
    df = pd.DataFrame(rows)
    df.to_sql(
        "embeddings_768",
        conn,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )


def insert_table(df: pd.DataFrame, table_name: str, db_url: str):
    engine = create_engine(db_url)
    with engine.begin() as conn:
        df.to_sql(name=table_name, con=engine, if_exists="append", index=False, chunksize=2000)
