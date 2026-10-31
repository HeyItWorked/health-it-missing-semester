# Q3 over the FHIR export. Systolic BP usually lives inside a
# blood pressure panel (LOINC 85354-9) as a component.
inputs | .entry[].resource
| select(.resourceType == "Observation"
         and .effectiveDateTime >= "2025-10-31") as $obs
| (.component // [.])[]
| select(any(.code.coding[];
    .system == "http://loinc.org" and .code == "8480-6"))
| select(.valueQuantity.value >= 140)
| [$obs.effectiveDateTime[:10], $obs.subject.reference[9:17],
   $obs.code.coding[0].code, .valueQuantity.value,
   .valueQuantity.unit]
| @tsv
