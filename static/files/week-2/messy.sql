-- One VALUE column holds numbers and words.
SELECT type, count(*) FROM observations GROUP BY type;
SELECT value, count(*) FROM observations
 WHERE code = '72166-2' GROUP BY value;
-- Compared as text, '99.1' > '126' is true.
SELECT count(*) AS as_text FROM observations
 WHERE code = '2339-0' AND value > '126';
SELECT count(*) AS as_number FROM observations
 WHERE code = '2339-0' AND num > 126;
-- Casting every row fails on the first word.
SELECT count(*) FROM observations
 WHERE value::numeric > 126;
-- Encounters dated after the patient died
SELECT left(p.id::text, 8) AS patient, p.deathdate,
       e.start::date, e.encounterclass, e.description
  FROM patients p JOIN encounters e ON e.patient = p.id
 WHERE e.start::date > p.deathdate;
