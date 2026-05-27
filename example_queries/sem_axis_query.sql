-- Given an embedding type (CLIP or E5) and the absval of a semantic axis
-- whose seed values (words/phrases with embeddings) have been already entered
-- into the database by compute_semaxis_embeddings.py, find the 10 review
-- comments that are farthest in each direction along that semantic axis.

WITH config AS (
  SELECT
    17 AS abssemaxis  -- absval of semaxis for seed embeddings in db
    'CLIP' AS embed_type,  -- 'CLIP' or 'E5'
),

-- Pull all semantic-axis seed embeddings for the selected axis
axis_seed_embeddings AS (
  SELECT
    e.id,
    e.embedding,
    (e.tag->>'semaxis')::int AS semaxis,
    e.tag->>'wordphrase' AS wordphrase
  FROM embeddings_768 e
  CROSS JOIN config c
  WHERE e.review_id IS NULL
    AND e.tag->>'embed_type' = c.embed_type
    AND ABS((e.tag->>'semaxis')::int) = c.abssemaxis
),

-- Average together all positive and all negative pole embeddings in sem axis
axis_poles AS (
  SELECT
    AVG(embedding) FILTER (WHERE semaxis > 0) AS pos_embedding,
    AVG(embedding) FILTER (WHERE semaxis < 0) AS neg_embedding
  FROM axis_seed_embeddings
),

-- Build semantic axis vector (with optional normalization) as diff between
-- the avgs of pos and neg pole embeddings
axis_vector AS (
  SELECT
    pos_embedding,
    neg_embedding,
    (pos_embedding - neg_embedding) AS axis_embedding

    -- If your pgvector version supports vector_norm():
    -- (alas no for mine but for directional comparisons it's ok)
    -- (pos_embedding - neg_embedding)
    --   / vector_norm(pos_embedding - neg_embedding)
    --   AS axis_unit_embedding

  FROM axis_poles
),

-- Project all review embeddings onto semantic axis; then axis_value is
-- the scalar projection on that sem axis.
scored_reviews AS (
  SELECT
    e.id AS embed_id,
    pr.review_id,
    regexp_replace(
      pr.comments,
      '(\d+) days before arrival',
      '[X] days before arrival',
      'g'
    ) AS comment,

    e.tag->>'embed_type' AS etype,

    -- dot product:
    -- pgvector <#> returns NEGATIVE inner product,
    -- so must negate it to get actual dot product
    -1 * (e.embedding <#> av.axis_embedding) AS axis_value

  FROM embeddings_768 e
  CROSS JOIN axis_vector av
  JOIN property_reviews pr
    ON pr.review_id = e.review_id
  CROSS JOIN config c
  WHERE e.review_id IS NOT NULL
    AND e.tag->>'embed_type' = c.embed_type
)

(
  -- Get 10 most positive (re semantic axis) comments
  SELECT
    length(comment) as comment_len,
    substring(comment for 90) AS comment,
    etype,
    ROUND(MAX(axis_value)::numeric, 4) AS axis_value,
    COUNT(*) AS count,
    MAX(review_id) AS last_review_id,
    MAX(embed_id) AS last_embed_id
  FROM scored_reviews
  GROUP BY comment, etype
  ORDER BY axis_value DESC
  LIMIT 10
)
UNION ALL
(SELECT NULL, '...', '...', NULL, NULL, NULL, NULL)
UNION ALL
(
  -- Get 10 most negative (re semantic axis) comments
  SELECT
    length(comment) as comment_len,
    substring(comment for 90) AS comment,
    etype,
    ROUND(MIN(axis_value)::numeric, 4) AS axis_value,
    COUNT(*) AS count,
    MAX(review_id) AS last_review_id,
    MAX(embed_id) AS last_embed_id
  FROM scored_reviews
  GROUP BY comment, etype
  ORDER BY axis_value
  LIMIT 10
);
