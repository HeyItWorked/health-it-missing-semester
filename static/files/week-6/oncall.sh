#!/usr/bin/env bash
# Page a human on queue depth or error rate, not on every error.
# Usage: ./oncall.sh <channel-id>   (cron it every minute)
set -euo pipefail
OIE=${OIE:-https://localhost:8443/api}
MAX_QUEUED=${MAX_QUEUED:-3}     # messages waiting downstream
MAX_ERR_PCT=${MAX_ERR_PCT:-5}   # errors per 100 received

stats=$(curl -sfk -u admin:admin -H 'X-Requested-With: OpenAPI' \
  -H 'Accept: application/json' "$OIE/channels/$1/statistics")
read -r rcv err q < <(jq -r '.channelStatistics |
  "\(.received) \(.error) \(.queued)"' <<<"$stats")
pct=$(( rcv ? 100 * err / rcv : 0 ))
echo "received=$rcv error=$err (${pct}%) queued=$q"
if (( q > MAX_QUEUED || pct > MAX_ERR_PCT )); then
  echo "PAGE: interface needs a human"; exit 2
fi
echo "OK"
