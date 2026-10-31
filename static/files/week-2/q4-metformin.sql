-- Q4: patients with type 2 diabetes on metformin today.
-- Matching on display text catches prediabetes too:
SELECT code, description, count(DISTINCT patient)
  FROM conditions WHERE description ILIKE '%diabetes%'
 GROUP BY 1, 2 ORDER BY 3 DESC;
SELECT count(DISTINCT patient) AS by_text FROM conditions
 WHERE description ILIKE '%diabetes%';
-- Matching on the code (SNOMED CT 44054006), then joining
-- metformin (RxNorm 860975) with no STOP date
SELECT count(DISTINCT c.patient) AS diabetics,
       count(DISTINCT m.patient) AS on_metformin,
       count(m.patient) AS rows_joined
  FROM conditions c
  LEFT JOIN medications m
    ON m.patient = c.patient AND m.code = '860975'
   AND m.stop IS NULL
 WHERE c.code = '44054006' AND c.stop IS NULL;
-- Rows are prescriptions, not patients
SELECT count(*) AS prescriptions, count(DISTINCT patient)
  FROM medications WHERE code = '860975';
