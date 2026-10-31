"""Week 5: no canary identifier may reach the bridge's logs."""
import logging

import hl7
import pytest

import bridge
from test_redact import CANARIES

GOOD = open("canary.hl7", newline="").read()
CASES = {  # one message per path through process()
    "accepted": GOOD,
    "no-mrn": GOOD.replace("987650^^^GENHOSP^MR", ""),
    "bad-dob": GOOD.replace("19610704", "1961070X"),
    "unknown-authority": GOOD.replace("GENHOSP^MR", "OTHER^MR"),
    "production": GOOD.replace("|T|2.5.1", "|P|2.5.1"),
    "fhir-down": GOOD,
}


@pytest.mark.parametrize("case", CASES)
def test_no_canary_in_logs(case, caplog, monkeypatch, tmp_path):
    caplog.set_level(logging.DEBUG)  # incidents turn debug on
    audit_file = tmp_path / "audit.jsonl"
    monkeypatch.setattr(bridge, "AUDIT", audit_file)
    if case == "fhir-down":  # nothing listens on port 9
        monkeypatch.setattr(bridge, "FHIR", "http://localhost:9/fhir")
    else:
        monkeypatch.setattr(bridge, "upsert", lambda p: (
            201, "http://fhir.example.org/fhir/Patient/1/_history/1"))
    bridge.process(hl7.parse(CASES[case]))
    logged = caplog.text
    if audit_file.exists():  # the audit log is a log too
        logged += audit_file.read_text()
    leaked = [c for c in CANARIES if c in logged]
    if leaked:
        pytest.fail(f"{len(leaked)} canaries in logs, first {leaked[0]}")
