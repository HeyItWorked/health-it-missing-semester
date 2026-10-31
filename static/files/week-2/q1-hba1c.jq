# Q1 over the FHIR export: HbA1c above 9%
[inputs | .entry[].resource
 | select(.resourceType == "Observation")
 | select(any(.code.coding[];
     .system == "http://loinc.org" and .code == "4548-4"))
 | select(.valueQuantity.value > 9)]
| {ever: length,
   patients: (map(.subject.reference) | unique | length),
   last_year: (map(select(.effectiveDateTime >= "2025-10-31"))
               | length),
   values: map([.effectiveDateTime, .valueQuantity.value])}
