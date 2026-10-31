# Interface spec: GENHOSP ADT to FHIR Patient (TEST)

Version 1.0 · Owner: integration team · Status: lab

## Summary
Registration (REGADT at GENHOSP) sends ADT over MLLP to OIE
channel "ADT to bridge". OIE forwards each message unchanged to
the bridge, which upserts one FHIR Patient per MRN in HAPI and
answers. OIE returns the bridge's ACK to the sender.

## Connection
| Item | Value |
|------|-------|
| Transport | MLLP over TCP (0x0B ... 0x1C 0x0D) |
| Inbound | OIE TCP Listener, port 6661 |
| Outbound | bridge:2575 (MLLP), then HAPI `PUT /fhir/Patient?identifier=` |
| Network | lab: localhost only. Production: VPN or TLS tunnel between named hosts |
| HL7 version | 2.5.1 (MSH-12) |
| Processing ID | `T` only on this feed (MSH-11). `P` gets AR |
| ACK mode | original mode; one message at a time, in order |

## Trigger events
| Event | Structure | What we do |
|-------|-----------|------------|
| A01 admit | ADT_A01 | upsert Patient from PID |
| A08 update | ADT_A01 | upsert Patient from PID |
| A03 discharge | ADT_A03 | upsert Patient from PID (visit not stored) |
| A40 merge | ADT_A39 | not on this feed. Open item: the bridge does not check MSH-9 yet, so an A40 would update the PID patient and ignore MRG |

PV1 and Z-segments are accepted and ignored.

## Field mappings (PID to FHIR Patient)
| HL7 v2 | FHIR | Rule |
|--------|------|------|
| PID-3.1 | identifier.value | required, else AE 101 |
| PID-3.4 | identifier.system | `GENHOSP` -> `https://genhosp.example.org/mrn`; other -> AE 103 |
| PID-5.1 | name.family | |
| PID-5.2 | name.given[0] | omitted if empty |
| PID-7 | birthDate | YYYY, YYYYMM or YYYYMMDD; else AE 102 |
| PID-8 | gender | F/M/O/U -> female/male/other/unknown; else unknown |
| (fixed) | active | true |

## ACK rules
| Situation | ACK | ERR |
|-----------|-----|-----|
| Patient written (HTTP 200 or 201) | AA | |
| MSH-11 is not `T` | AR | MSH^1^11, 202 |
| PID-3 missing | AE | PID^1^3, 101 |
| Unknown assigning authority | AE | PID^1^3, 103 |
| Bad birth date | AE | PID^1^7, 102 |
| MRN already on several patients (HTTP 412) | AE | PID^1^3, 205 |
| Other HTTP 4xx | AE | PID, 207 |
| FHIR server down or 5xx | none: connection closed, sender retries | |

AA is sent only after the FHIR write has committed.

## Duplicates and replay
Writes are conditional PUTs keyed on PID-3 (system + value), so
a resend or a replayed day never creates a second Patient.
MSH-10 is used to match ACKs and trace messages only.

## Monitoring
Page on-call when the bridge destination's queue holds more than
3 messages, or more than 5% of received messages errored
(`oncall.sh`). Single AE/AR go to the daily error review.
