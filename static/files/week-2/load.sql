-- Load a Synthea CSV export (mounted at /csv) into PostgreSQL.
-- Run: docker exec -i pg psql -U postgres -v ON_ERROR_STOP=1 < load.sql
-- Only the columns this lecture uses are typed; the rest stay text.

DROP TABLE IF EXISTS patients, encounters, observations,
  conditions, medications, immunizations;

CREATE TABLE patients (
  id uuid PRIMARY KEY, birthdate date, deathdate date,
  ssn text, drivers text, passport text, prefix text,
  first text, middle text, last text, suffix text, maiden text,
  marital text, race text, ethnicity text, gender text,
  birthplace text, address text, city text, state text,
  county text, fips text, zip text, lat numeric, lon numeric,
  healthcare_expenses numeric, healthcare_coverage numeric,
  income numeric);

CREATE TABLE encounters (
  id uuid PRIMARY KEY, start timestamptz, stop timestamptz,
  patient uuid, organization uuid, provider uuid, payer uuid,
  encounterclass text, code text, description text,
  base_encounter_cost numeric, total_claim_cost numeric,
  payer_coverage numeric, reasoncode text,
  reasondescription text);

-- VALUE is text: one column holds numbers and coded answers.
CREATE TABLE observations (
  date timestamptz, patient uuid, encounter uuid,
  category text, code text, description text,
  value text, units text, type text);

CREATE TABLE conditions (
  start date, stop date, patient uuid, encounter uuid,
  system text, code text, description text);

CREATE TABLE medications (
  start timestamptz, stop timestamptz, patient uuid,
  payer uuid, encounter uuid, code text, description text,
  base_cost numeric, payer_coverage numeric, dispenses int,
  totalcost numeric, reasoncode text, reasondescription text);

CREATE TABLE immunizations (
  date timestamptz, patient uuid, encounter uuid,
  code text, description text, base_cost numeric);

\copy patients FROM '/csv/patients.csv' CSV HEADER
\copy encounters FROM '/csv/encounters.csv' CSV HEADER
\copy observations FROM '/csv/observations.csv' CSV HEADER
\copy conditions FROM '/csv/conditions.csv' CSV HEADER
\copy medications FROM '/csv/medications.csv' CSV HEADER
\copy immunizations FROM '/csv/immunizations.csv' CSV HEADER

-- Cast once, at load time, and only the rows that are numbers.
ALTER TABLE observations ADD COLUMN num numeric;
UPDATE observations SET num = value::numeric
 WHERE type = 'numeric';
