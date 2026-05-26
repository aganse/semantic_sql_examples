import ast

import hdbscan
import numpy as np
import pandas as pd
from sklearn.decomposition import IncrementalPCA
from sklearn.preprocessing import normalize
from sqlalchemy import create_engine
import umap

import db_helper
from config import DB_URL, EMBED_TYPE


engine = create_engine(DB_URL)


###########################################################
# Phase 1: stream from Postgres into IncrementalPCA
# (Fit PCA using sequential partial fit - avoids loading all 100k rows at once.)
print("Phase 1...")

BATCH_SIZE = 500
PCA_DIMS = 50  # Good intermediate compression before UMAP

ipca = IncrementalPCA(n_components=PCA_DIMS)

batchnum = 0

for batch_df in db_helper.fetch_embedding_chunks(
    engine,
    EMBED_TYPE,
    chunk_size=BATCH_SIZE
):
    X = np.vstack(batch_df["embedding"].apply(ast.literal_eval).values)
    X = normalize(X)

    ipca.partial_fit(X)

    batchnum += 1

    print("pca-fit batch", batchnum)


###########################################################
# Phase 2: transform all rows through PCA
# (Now that we have that PCA transform fitted, use that on re-pulled data to
# create one global reduced matrix for the UMAP in phase 3.)
print("Phase 2...")

all_ids = []
all_tags = []
all_vectors = []

batchnum = 0

for batch_df in db_helper.fetch_embedding_chunks(
    engine,
    EMBED_TYPE,
    chunk_size=BATCH_SIZE
):

    X = np.vstack(
        batch_df["embedding"].apply(ast.literal_eval).values
    )
    X = normalize(X)

    X_pca = ipca.transform(X)

    all_vectors.append(X_pca)
    all_ids.extend(batch_df["id"].tolist())
    all_tags.extend(batch_df["tag"].tolist())

    batchnum += 1
    print("pca-transformed batch", batchnum)

X_pca_all = np.vstack(all_vectors)

print("~100k x 50 matrix X_pca_all stacked now; actual size:", X_pca_all.shape)

# Now we have 100k × 50 instead of 100k × 768; more likely to fit in memory


###########################################################
# Phase 3: run UMAP globally on the PCA-reduced 100k × 50 matrix
# ("At 100k × 50 this is usually very feasible."  We'll see!)
print("Phase 3...")

# Final dimensionality for clustering
# Try:
#   10  -> tighter/local structure
#   30  -> more global structure preserved
umap_dims = 10

umap_model = umap.UMAP(
    n_components=umap_dims,
    n_neighbors=15,
    min_dist=0.0,
    metric="cosine",
    random_state=42
)

X_umap = umap_model.fit_transform(X_pca_all)
print("UMAP model fitted.")


###########################################################
# Phase 4: run HDBSCAN globally on the UMAP-reduced 100k x 10 matrix
print("Phase 4...")

clusterer = hdbscan.HDBSCAN(
    min_cluster_size=25,  # earlier was 10
    min_samples=10,       # earlier was 5
    metric="euclidean",   # could be "cosine", eg if no dim-red
    prediction_data=True
)

cluster_labels = clusterer.fit_predict(X_umap)
print("cluster_labels fitted/assigned via HDBSCAN.")

print("\n counts per cluster:")
cluster_series = pd.Series(cluster_labels)
print(cluster_series.value_counts().sort_index())


###########################################################
# Phase 5: write cluster labels back to embeddings_768.tag
print("Phase 5...")

with engine.begin() as conn:
    for embed_id, cluster_label in zip(all_ids, cluster_labels):
        db_helper.insert_embedding_tag(
            conn,
            embed_id,
            {"cluster": int(cluster_label)}
        )

print("cluster labels written back to embeddings_768.tag")


# HDBSCAN uses:
#   -1 => noise/outlier
#    0,1,2,... => clusters

# df["cluster"] = cluster_labels
# print(df["cluster"].value_counts().sort_index())
