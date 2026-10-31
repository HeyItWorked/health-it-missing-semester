-- Q2: ED visits per month since January 2024
SELECT to_char(start, 'YYYY-MM') AS month,
       count(*) AS visits, count(DISTINCT patient) AS patients
  FROM encounters
 WHERE encounterclass = 'emergency' AND start >= '2024-01-01'
 GROUP BY 1 ORDER BY 1;
-- October 2024 by day: UTC, then Boston time
SELECT start::date AS utc_day,
       (start AT TIME ZONE 'America/New_York')::date AS local_day
  FROM encounters
 WHERE encounterclass = 'emergency'
   AND start BETWEEN '2024-10-01' AND '2024-11-01';
