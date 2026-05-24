import json
import time

import numpy as np
from sqlalchemy import create_engine

import db_helper
import embedding_helper
from config import DB_URL, EMBED_TYPE


def to_pgvector(v: np.ndarray) -> str:
    # pgvector accepts string literal like '[0.1, 0.2, ...]'
    return "[" + ",".join(f"{x:.6f}" for x in v.tolist()) + "]"


engine = create_engine(DB_URL)
chunknum = 0

if EMBED_TYPE == "E5":
    embedding_helper.initialize_e5()
elif EMBED_TYPE == "CLIP":
    embedding_helper.initialize_clip()

for reviews_df in db_helper.fetch_review_chunks(engine, chunk_size=500):

    starttime = time.time()
    rows = []
    chunknum += 1

    texts = reviews_df["comments"].tolist()

    # embeddings are length-768 numerical vectors
    if EMBED_TYPE == "E5":
        embeddings = embedding_helper.compute_e5_embeddings(texts)
    elif EMBED_TYPE == "CLIP":
        embeddings = embedding_helper.compute_clip_embeddings(texts)

    for review_id, embedding in zip(reviews_df["review_id"], embeddings):
        rows.append({
            "review_id": review_id,
            "embedding": to_pgvector(embedding),
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
