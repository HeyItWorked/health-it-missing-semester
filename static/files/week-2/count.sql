-- Observation rows, and the ones with no category
SELECT count(*),
       count(*) FILTER (WHERE category IS NULL) AS no_category
  FROM observations;
SELECT code, description, count(*) FROM observations
 WHERE category IS NULL GROUP BY 1, 2;
