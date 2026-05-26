import json
import time

import pandas as pd
from sqlalchemy import create_engine

import db_helper
import embedding_helper
from config import DB_URL, EMBED_TYPE


engine = create_engine(DB_URL)
embedding_helper.initialize_embedding_model(EMBED_TYPE)

semaxis_rows = [
    ["beautiful",          1],
    ["ugly",              -1],
    ["nice smelling",      2],
    ["stinky",            -2],
    ["trustworthy",        3],
    ["sketchy",           -3],
    ["secure",             4],
    ["insecure",          -4],
    ["fast",               5],
    ["slow",              -5],
    ["easy",               6],
    ["confusing",         -6],
    ["safe",               7],
    ["unsafe",            -7],
    ["quiet",              8],
    ["noisy",             -8],
    ["would return",      10],
    ["would not return", -10],
]

df = pd.DataFrame(semaxis_rows, columns=["wordphrase", "semaxis"])

starttime = time.time()
rows = []

texts = df["wordphrase"].tolist()

# embeddings are length-768 numerical vectors
embeddings = embedding_helper.compute_embeddings(texts, EMBED_TYPE)

for wordphrase, semaxisnum, embedding in zip(
    df["wordphrase"],
    df["semaxis"],
    embeddings
):
    rows.append({
        "review_id": None,
        "embedding": db_helper.to_pgvector(embedding),
        "tag": json.dumps({
            "embed_type": EMBED_TYPE,
            "semaxis": semaxisnum,
            "wordphrase": wordphrase,
        })
    })

with engine.begin() as conn:
    db_helper.insert_embeddings(conn, rows)

endtime = time.time()
print(f"finished processing {len(rows)} semaxis rows; processing/insert time {(endtime - starttime):.3f} seconds")
