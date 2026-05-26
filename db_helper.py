import numpy as np
import pandas as pd
from sqlalchemy import create_engine


def fetch_embedding_chunks(engine, embed_type, chunk_size=5000):
    query = """SELECT id, review_id, embedding, tag
                FROM embeddings_768
                WHERE tag->>'embed_type' = :embed_type
                  AND NOT (tag ? 'sem_axis')
                ORDER BY 1"""
    yield from pd.read_sql(
        query,
        engine,
        chunksize=chunk_size,
        params={"embed_type": embed_type}
    )


def fetch_review_chunks(engine, chunk_size=5000):
    query = "SELECT review_id, comments FROM property_reviews ORDER BY 1"
    yield from pd.read_sql(
        query,
        engine,
        chunksize=chunk_size
    )


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
        df.to_sql(
            name=table_name,
            con=conn,
            if_exists="append",
            index=False,
            chunksize=2000
        )


def to_pgvector(v: np.ndarray) -> str:
    # pgvector accepts string literal like '[0.1, 0.2, ...]'
    return "[" + ",".join(f"{x:.6f}" for x in v.tolist()) + "]"
