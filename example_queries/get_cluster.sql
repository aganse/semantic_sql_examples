-- Given an embedding type (CLIP or E5) and a valid cluster number generated
-- in the datbaase by cluster.py, retrieve the comments in that cluster.

WITH config AS (
  SELECT
    1 AS cluster_num,  -- cluster number to retrieve
    'CLIP' AS etype  -- 'CLIP' or 'E5'
)

SELECT
  e.id as embed_id,
  r.review_id,
  substring(comments for 80)||'...' AS comments,
  e.tag
FROM config,
  embeddings_768 e JOIN property_reviews r ON e.review_id=r.review_id
WHERE tag->>'embed_type' = config.etype
  AND NOT (tag ? 'semaxis')
  AND (tag->>'cluster')::numeric=config.cluster_num;
