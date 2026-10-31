# Every resource in a Synthea bundle that points at one
# encounter, sorted by its own clinical time.
# Usage: jq -r --arg enc ENCOUNTER_ID -f timeline.jq BUNDLE
# Prints: time  count  Resource.field  what (+N more kinds)

# The field that says when this resource happened.
def when:
  [ ["effectiveDateTime", .effectiveDateTime],
    ["performedPeriod.start", .performedPeriod.start],
    ["authoredOn", .authoredOn],
    ["date", .date],
    ["created", .created] ]
  | map(select(.[1] != null)) | first;

def what:
  (.code.text // .code.coding[0].display
   // .medicationCodeableConcept.text
   // .category[0].coding[0].code // .type.coding[0].code
   // "")
  | sub(" \\([a-z/ ]+\\)$"; "");

def rows:
  if .resourceType == "Encounter" then
    [.period.start, "Encounter.period.start", .class.code],
    [.period.end, "Encounter.period.end", .status]
  else
    when as $w | [$w[1], .resourceType + "." + $w[0], what]
  end;

("urn:uuid:" + $enc) as $ref
| [ .entry[].resource
    # Provenance lists every resource in the bundle; skip it.
    | select(.resourceType != "Provenance")
    | select(.id == $enc or (tostring | contains($ref)))
    | rows ]
| group_by(.[0][0:16] + .[1])
| sort_by(.[0][0])
| .[]
| (map(.[2]) | unique) as $w
| "\(.[0][0][11:16])  \(length)  \(.[0][1])  \($w[0][0:22])"
  + (if ($w | length) > 1 then " +\($w | length - 1)" else "" end)
