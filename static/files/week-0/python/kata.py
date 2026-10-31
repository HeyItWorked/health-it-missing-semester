"""Week 0 kata: find by MRN, add a mobile, $validate,
conditional PUT, prove exactly one write."""
import os
import sys
from collections import Counter

from fhirclient import client
from fhirclient.models.contactpoint import ContactPoint
from fhirclient.models.operationoutcome import (
    OperationOutcome)
from fhirclient.models.patient import Patient

S = "http://hospital.smarthealthit.org"
mrn, mobile = os.environ["MRN"], sys.argv[1]
by_mrn = f"Patient?identifier={S}|{mrn}"

smart = client.FHIRClient(settings={
    "app_id": "kata", "api_base": os.environ["FHIR"]})
server = smart.server
status = None


def remember(res, *args, **kwargs):
    global status
    status = res.status_code


# fhirclient hides HTTP; a requests hook shows us each status
server.session.hooks["response"].append(remember)


def log(call, note=""):
    print(f"{call:<40} {status}  {note}".rstrip())


def check(ok, why):
    if not ok:
        sys.exit(f"FAIL python: {why}")


def search():
    return Patient.where(
        {"identifier": f"{S}|{mrn}"}).perform(server)


# 1. Search by identifier (never _id: server id is not the MRN)
found = search()
check(found.total == 1, f"expected 1 match, got {found.total}")
p = found.entry[0].resource
before = int(p.meta.versionId)
log("search   GET  Patient?identifier=S|MRN",
    f"1 match, id {p.id}, v{before}")

# 2. Replace any mobile number with ours
p.telecom = [t for t in p.telecom or [] if t.use != "mobile"]
p.telecom.append(ContactPoint(
    {"system": "phone", "use": "mobile", "value": mobile}))

# 3. $validate: HTTP 200 says nothing; count the severities
res = server.post_json("Patient/$validate", p.as_json())
oo = OperationOutcome(res.json())
sev = Counter(i.severity for i in oo.issue)
log("validate POST Patient/$validate",
    "{" + ", ".join(f"{k}={n}" for k, n in sorted(sev.items()))
    + "}")
check(not {"fatal", "error"} & sev.keys(), "invalid")

# 4. Conditional update on the identifier (no helper for it)
server.put_json(by_mrn, p.as_json())
log("update   PUT  Patient?identifier=S|MRN")

# 5. Read back: still one patient, one version more
again = search()
after = int(again.entry[0].resource.meta.versionId)
log("re-read  GET  Patient?identifier=S|MRN",
    f"{again.total} match, v{after}")
check(again.total == 1, "duplicate patient")
check(after == before + 1, f"expected v{before + 1}, got v{after}")

# 6. History holds every version: none lost, none extra
hist = server.request_json(f"Patient/{p.id}/_history")
log(f"history  GET  Patient/{p.id}/_history",
    f"{hist['total']} versions")
check(hist["total"] == after, f"history has {hist['total']}")

print(f"PASS python: v{before} -> v{after}, one patient")
