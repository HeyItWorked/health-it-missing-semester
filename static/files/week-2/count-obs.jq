# Run with jq -s over one Observation per line.
# Why FHIR has fewer Observations than observations.csv
{resources: length,
 with_components: map(select(.component)) | length,
 rows_if_flattened:
   map(if .component then (.component | length) else 1 end)
   | add,
 panels: map(select(.component) | .code.coding[0].code)
   | group_by(.) | map({(.[0]): length}) | add}
