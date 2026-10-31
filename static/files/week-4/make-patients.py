"""Week 4: write the Patient the week 3 bridge would store, per message.

Usage: python3 make-patients.py adt*.hl7   -> out/<name>.json
Messages the bridge rejects (AE/AR) are reported and skipped.
"""
import json
import pathlib
import sys

import hl7

import bridge  # week 3's bridge.py, next to this file

out = pathlib.Path("out")
out.mkdir(exist_ok=True)
for name in sys.argv[1:]:
    msg = hl7.parse(open(name, newline="").read())
    try:
        patient = bridge.to_patient(msg)
    except bridge.Reject as r:
        print(f"{name}: rejected {r.code} {r.why}")
        continue
    target = out / (pathlib.Path(name).stem + ".json")
    target.write_text(json.dumps(patient, indent=2) + "\n")
    print(f"{name}: wrote {target}")
