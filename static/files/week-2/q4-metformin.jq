# Q4 over the FHIR export
def coded($sys; $code):
  any(.coding[]?; .system == $sys and .code == $code);
[inputs | .entry[].resource] as $all
| ($all | map(select(.resourceType == "Condition"
    and (.code | coded("http://snomed.info/sct"; "44054006"))
    and .clinicalStatus.coding[0].code == "active")
    | .subject.reference) | unique) as $dm
| ($all | map(select(.resourceType == "MedicationRequest"
    and (.medicationCodeableConcept | coded(
      "http://www.nlm.nih.gov/research/umls/rxnorm"; "860975"))
    and .status == "active")
    | .subject.reference) | unique) as $met
| {diabetics: ($dm | length),
   on_metformin: ($met | map(select(IN($dm[]))) | length)}
