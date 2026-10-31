#!/bin/sh
# Print every resource a FHIR search matches, one JSON per line,
# following Bundle.link "next" until the server stops sending one.
url=$1
while [ -n "$url" ]; do
  page=$(curl -s "$url")
  printf '%s\n' "$page" | jq -c '.entry[]?.resource'
  url=$(printf '%s\n' "$page" |
        jq -r '.link[]? | select(.relation == "next") | .url')
done
