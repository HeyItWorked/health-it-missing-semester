"""Week 5: no canary identifier may survive redaction."""
import glob

import hl7
import pytest

import redact

CANARIES = ["987650", "ZZCANARY", "TWEETY", "ZZMAIDEN", "19610704",
            "CANARY LANE", "555-0142", "A5550142", "999-55-0142",
            "D5550142", "9990001425"]


@pytest.mark.parametrize("path", sorted(glob.glob("canary*.hl7")))
@pytest.mark.parametrize("how", ["allowlist", "blocklist"])
def test_no_canary_survives(how, path, monkeypatch):
    monkeypatch.setenv("PSEUDONYM_KEY", "test-key-not-a-secret")
    msg = hl7.parse(open(path, newline="").read())
    out = str(getattr(redact, how)(msg))
    leaked = [c for c in CANARIES if c in out]
    if leaked:
        pytest.fail(f"{path}: {leaked} survived {how}")
