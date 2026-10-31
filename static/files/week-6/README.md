# ADT to FHIR: an HL7 v2 interface you can run in 10 minutes

Registration systems announce admissions in HL7 v2. This repo
receives those ADT messages through Open Integration Engine,
keeps exactly one FHIR Patient per medical record number in a
HAPI FHIR server, and only acknowledges a message once the
patient is stored. All data is synthetic.

    sender --MLLP:6661--> OIE --MLLP:2575--> bridge --PUT--> HAPI FHIR

## Run it
Needs Docker with Compose v2, curl, jq, Python 3 with `hl7`
(`pip install hl7==0.4.5`, for `mllp_send`).

    git clone <this repo> && cd <this repo>
    docker compose up -d --wait
    export OIE=https://localhost:8443/api
    export CH=6e0d3c1a-7b2f-4c55-9e1a-0a5d2f3b6c01
    curl -K oie.curl -H 'Content-Type: application/xml' \
      --data-binary @channels/adt-to-bridge.xml $OIE/channels
    curl -K oie.curl -X POST $OIE/channels/$CH/_deploy
    mllp_send --loose -f adt.hl7 -p 6661 localhost | tr '\r' '\n'

Expect `MSA|AA|MSG00001`. Then try `adt-prod.hl7` (AR: this is a
TEST feed) and the replay test in RUNBOOK.md.

## What to look at
- `bridge.py`: the mapping, the ACK rules, AA only after the write.
- `channels/adt-to-bridge.xml`: the OIE channel, exported from the
  engine; every change to it is a reviewed diff.
- `interface-spec.md`: triggers, segments, field mappings, ACKs.
- `RUNBOOK.md`: start, stop, replay, roll back, downtime.
- `oncall.sh`: pages on queue depth and error rate.

## Tested
- Replaying a synthetic day (`day.py`, 100 patients) twice leaves
  the same patients with the same `snapshot.sh` fingerprint.
- A PROD message on the TEST feed gets AR and writes nothing.
- With the bridge stopped, OIE queues and `oncall.sh` pages; the
  queue drains when it is back.

## Limits
Lab only: default admin password, self-signed certificate, no TLS
on MLLP, HAPI data lost on `docker compose down`. No A40 merges.
