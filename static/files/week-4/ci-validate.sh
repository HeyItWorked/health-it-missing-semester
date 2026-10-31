#!/bin/sh
# CI gate: validate FHIR Patients against CA Baseline.
# The validator exits non-zero if any file has an error, and
# set -e passes that on, so the CI job fails.
set -e
P=http://hl7.org/fhir/ca/baseline/StructureDefinition
java -jar validator_cli.jar "$@" -version 4.0.1 \
  -ig hl7.fhir.ca.baseline#1.2.0 -profile $P/profile-patient \
  -allow-example-urls true > validation.log 2>&1 || {
  grep -E '^-- |^\*FAILURE|Error @' validation.log
  exit 1
}
grep -E '^-- |^Success' validation.log
