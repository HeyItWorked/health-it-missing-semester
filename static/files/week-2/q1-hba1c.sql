-- Q1: HbA1c (LOINC 4548-4) above 9% in the last year
SELECT count(*) AS results, count(DISTINCT patient) AS patients
  FROM observations
 WHERE code = '4548-4' AND num > 9 AND date >= '2025-10-31';
-- The same question with no time window
SELECT date::date, left(patient::text, 8) AS patient, value
  FROM observations
 WHERE code = '4548-4' AND num > 9;
-- Every type 2 diabetic (SNOMED CT 44054006): latest HbA1c
WITH dm AS (
  SELECT DISTINCT patient FROM conditions
   WHERE code = '44054006'),
ranked AS (
  SELECT patient, date, value, row_number() OVER (
           PARTITION BY patient ORDER BY date DESC) AS n
    FROM observations WHERE code = '4548-4')
SELECT left(dm.patient::text, 8) AS patient,
       r.date::date AS latest, r.value
  FROM dm LEFT JOIN ranked r
    ON r.patient = dm.patient AND r.n = 1
 ORDER BY latest;
