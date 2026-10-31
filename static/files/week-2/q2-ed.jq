# Q2 over the FHIR export: ED visits per month
[inputs | .entry[].resource
 | select(.resourceType == "Encounter" and .class.code == "EMER")
 | select(.period.start >= "2024-01-01")
 | {month: .period.start[:7], day: .period.start[:10],
    patient: .subject.reference}]
| group_by(.month)[]
| [.[0].month, length, (map(.patient) | unique | length),
   (map(.day) | join(" "))]
| @tsv
