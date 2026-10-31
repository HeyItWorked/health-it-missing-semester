-- Q3: systolic BP (LOINC 8480-6) of 140 mm[Hg] or more
SELECT date::date, left(patient::text, 8) AS patient,
       num, units
  FROM observations
 WHERE code = '8480-6' AND num >= 140 AND date >= '2025-10-31'
 ORDER BY 1;
