-- Given an embedding type (CLIP or E5) and the id of a source embedding (comment)
-- to compare to, find the 5 closest and 5 farthest review comments from that
-- source comment.

WITH config AS (
  SELECT
    98295 AS eid,  -- source comment/embedding to compare to
    'CLIP' AS etype  -- 'CLIP' or 'E5'
),

matches AS (
  -- The "source" comment/embed from config.eid above
  SELECT
    e1.id AS embed_id,
    pr1.review_id AS review_id,
    pr1.comments AS comment,
    1.0 AS similarity,
    e1.tag->>'embed_type' AS etype
  FROM config
  JOIN embeddings_768 e1
      ON e1.id = config.eid
  JOIN property_reviews pr1
    ON pr1.review_id = e1.review_id
  UNION ALL
  -- The rest of the commens/embeds in order of similarity distance
  SELECT
    e2.id AS embed_id,
    pr1.review_id AS review_id,
    regexp_replace(pr1.comments, '(\d+) days before arrival', '[X] days before arrival', 'g'),
    1 - (e1.embedding <=> e2.embedding) AS similarity,
    e2.tag->>'embed_type' AS etype
  FROM config
  JOIN embeddings_768 e1
    ON e1.id = config.eid
  JOIN embeddings_768 e2
    ON e1.id <> e2.id
  JOIN property_reviews pr1
    ON pr1.review_id = e2.review_id
  WHERE e2.tag->>'embed_type'=config.etype
)

(
  -- Get closest 5 comments plus the source comment (6th)
  SELECT
    substring(comment for 80) AS comment,
    etype,
    ROUND(MAX(similarity::numeric),3) AS similarity,
    COUNT(*) AS count,
    MAX(review_id) AS last_review_id,
    MAX(embed_id) AS last_embed_id
  FROM matches
  GROUP BY comment, etype
  ORDER BY similarity DESC
  LIMIT 6
)
UNION ALL
(SELECT '...', '...', NULL, NULL, NULL, NULL)
UNION ALL
(
  -- Get farthest 5 comments
  SELECT
    substring(comment for 80) AS comment,
    etype,
    ROUND(MAX(similarity::numeric),3) AS similarity,
    COUNT(*) AS count,
    MAX(review_id) AS last_review_id,
    MAX(embed_id) AS last_embed_id
  FROM matches
  GROUP BY comment, etype
  ORDER BY similarity
  LIMIT 5
);
