import json
import time

import numpy as np
from sqlalchemy import create_engine

import db_helper
import embedding_helper
from config import DB_URL, EMBED_TYPE


chunknum = 0
engine = create_engine(DB_URL)
embedding_helper.initialize_embedding_model(EMBED_TYPE)

for reviews_df in db_helper.fetch_review_chunks(engine, chunk_size=500):

    starttime = time.time()
    rows = []
    chunknum += 1

    texts = reviews_df["comments"].tolist()

    # embeddings are length-768 numerical vectors
    embeddings = embedding_helper.compute_embeddings(texts, EMBED_TYPE)

    for review_id, embedding in zip(reviews_df["review_id"], embeddings):
        rows.append({
            "review_id": review_id,
            "embedding": db_helper.to_pgvector(embedding),
            "tag": json.dumps({
                "embed_type": EMBED_TYPE,
            })
        })

    with engine.begin() as conn:
        db_helper.insert_embeddings(conn, rows)

    endtime = time.time()
    print(f"finished processing chunk {chunknum}; processing/insert time {(endtime - starttime):.3f} seconds")

    # just for testing, to stop after first few chunks...
    # if chunknum == 3:
    #     break
