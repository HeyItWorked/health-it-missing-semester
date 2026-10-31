"""Week 5: read a patient as a named user; every read is audited."""
import json
import sys
import urllib.request

from bridge import FHIR, audit

user, ref, why = sys.argv[1:4]
with urllib.request.urlopen(f"{FHIR}/{ref}", timeout=10) as resp:
    patient = json.load(resp)
audit(user, "read", ref, why)
name = patient["name"][0]
print(ref, name["family"], name.get("given", [""])[0],
      patient.get("birthDate"))
