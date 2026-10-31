# Q5 over the FHIR export: convert to mmol/L before comparing
inputs | .entry[].resource
| select(.resourceType == "Observation"
         and .effectiveDateTime >= "2025-10-31")
| select(any(.code.coding[]; .system == "http://loinc.org"
    and (.code == "2339-0" or .code == "2345-7")))
| .valueQuantity as $q
| (if $q.code == "mg/dL" then $q.value / 18.016
   elif $q.code == "mmol/L" then $q.value
   else error("unexpected unit \($q.code)") end) as $mmol
| select($mmol >= 7.0)
| [.effectiveDateTime[:10], .subject.reference[9:17],
   $q.value, ($mmol * 10 | round / 10)]
| @tsv
