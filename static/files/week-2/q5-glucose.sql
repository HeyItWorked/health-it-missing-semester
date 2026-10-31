-- Q5: glucose of 7.0 mmol/L or more in the last year.
-- Two LOINC codes; values are mg/dL; 1 mmol/L = 18.016 mg/dL
SELECT code, units, count(*) AS results,
       count(*) FILTER (WHERE num >= 7.0) AS unconverted,
       count(*) FILTER (WHERE num / 18.016 >= 7.0) AS converted
  FROM observations
 WHERE code IN ('2339-0', '2345-7') AND date >= '2025-10-31'
 GROUP BY 1, 2;
SELECT date::date, left(patient::text, 8) AS patient, num,
       round(num / 18.016, 1) AS mmol_l
  FROM observations
 WHERE code IN ('2339-0', '2345-7') AND date >= '2025-10-31'
   AND num / 18.016 >= 7.0;
