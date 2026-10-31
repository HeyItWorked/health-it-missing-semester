#!/usr/bin/env bash
# What the FHIR server says about patients: how many, how many
# versions, and a fingerprint of identity fields (not ids/versions).
# Same fingerprint before and after a replay = nothing changed.
# shortcut: reads one page (_count=500); page through
# Bundle.link "next" for bigger servers.
set -euo pipefail
FHIR=${FHIR:-http://localhost:8080/fhir}
# no-cache: HAPI otherwise reuses recent search results
get() { curl -sf -H 'Cache-Control: no-cache' "$FHIR/$1"; }
all=$(get 'Patient?_count=500' | jq -c '[.entry[]?.resource |
  [.identifier[0].value, .name, .gender, .birthDate]] | sort')
versions=$(get 'Patient/_history?_summary=count' | jq .total)
echo "$(jq length <<<"$all") patients, $versions versions," \
  "sha256 $(sha256sum <<<"$all" | cut -c1-16)"
