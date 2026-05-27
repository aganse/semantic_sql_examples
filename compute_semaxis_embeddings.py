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
    ["beautiful",         1],
    ["ugly",             -1],
    ["nice smelling",     2],
    ["stinky",           -2],
    ["trustworthy",       3],
    ["sketchy",          -3],
    ["fast",              4],
    ["slow",             -4],
    ["easy",              5],
    ["confusing",        -5],
    ["safe",              6],
    ["unsafe",           -6],
    ["quiet",             7],
    ["noisy",            -7],
    ["clean",             8],
    ["dirty",            -8],
    ["Beautiful: The venue felt gorgeous, elegant, and visually stunning, with charming decor, attractive details, and a warm aesthetic that made the entire experience feel refined and delightful.",  11],
    ["Ugly: The place looked unattractive, grimy, and visually unpleasant, with awkward design choices, harsh lighting, and a run-down appearance that felt depressing and uninviting.",    -11],
    ["Nice smelling: The room had a fresh, pleasant aroma with clean scents, subtle fragrance, and a crisp atmosphere that felt inviting, comfortable, and remarkably well maintained.",     12],
    ["Stinky: The building smelled foul, musty, and unpleasant, with lingering odors, stale air, and a sour scent that made the environment feel dirty and uncomfortable.",                 -12],
    ["Trustworthy: The staff seemed reliable, honest, and dependable throughout the visit, creating a credible and reassuring experience that felt transparent and sincere.",                13],
    ["Sketchy: The atmosphere felt suspicious, unreliable, and somewhat shady, with strange interactions and unsettling behavior that made the entire experience feel questionable.",       -13],
    ["Fast: The service was quick, efficient, and impressively rapid, with minimal delays and smooth interactions that made the whole experience feel streamlined and responsive.",          14],
    ["Slow: Everything moved at a sluggish, delayed, and inefficient pace, with long waits and frustrating interruptions that made the experience feel tedious and exhausting.",            -14],
    ["Easy: The process was simple, intuitive, and straightforward, with clear instructions and effortless navigation that made everything feel convenient and user friendly.",              15],
    ["Confusing: The experience felt disorganized, unclear, and difficult to follow, with inconsistent directions and complicated steps that made everything frustrating and bewildering.", -15],
    ["Safe: The property felt protected, stable, and well monitored, with strong safety measures and a dependable environment that inspired confidence and peace of mind.",                  16],
    ["Unsafe: The location felt vulnerable, poorly protected, and unstable, with weak safeguards and an uneasy atmosphere that made me feel uncomfortable and exposed.",                    -16],
    ["Quiet: The surroundings were peaceful, calm, and remarkably silent, creating a relaxing atmosphere with minimal noise and a tranquil, undisturbed environment.",                       17],
    ["Noisy: The environment was loud, chaotic, and constantly disruptive, filled with overwhelming sounds and nonstop commotion that made it difficult to relax or focus.",                -17],
    ["Clean: The space appeared spotless, tidy, and exceptionally well maintained, with hygienic surfaces and an organized environment that felt fresh and comfortable.",                    18],
    ["Dirty: The environment felt dirty, neglected, and poorly maintained, with visible messes, grimy surfaces, and unhygienic conditions that made the visit unpleasant.",                 -18],
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
