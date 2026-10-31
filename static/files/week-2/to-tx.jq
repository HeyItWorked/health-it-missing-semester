# Patients + HbA1c results from Synthea bundles -> one
# FHIR transaction. Usage: jq -n -f to-tx.jq output/fhir/[A-Z]*.json
{resourceType: "Bundle", type: "transaction", entry: [
  inputs | .entry[].resource
  | select(.resourceType == "Patient" or
      (.resourceType == "Observation" and any(.code.coding[];
        .system == "http://loinc.org" and .code == "4548-4")))
  # urn:uuid references only resolve inside the original bundle
  | del(.encounter)
  | if .subject then .subject.reference |= sub("urn:uuid:"; "Patient/")
    else . end
  | {resource: ., request: {method: "PUT", url: "\(.resourceType)/\(.id)"}}
]}
