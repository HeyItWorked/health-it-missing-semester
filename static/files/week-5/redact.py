"""Week 5: redact a PID segment before it leaves the hospital."""
import hashlib
import hmac
import os
import sys

import hl7

KEEP = {1, 3, 7, 8}  # set ID, MRN, birth date, sex
# blocklist: the fields we thought of (don't do this)
DROP = {2, 4, 5, 6, 9, 11, 13, 14, 18, 19}


def pseudonym(mrn):
    """Keyed hash (HMAC-SHA-256): same MRN, same pseudonym."""
    key = os.environ["PSEUDONYM_KEY"].encode()  # never in git
    return hmac.new(key, mrn.encode(), hashlib.sha256).hexdigest()[:16]


def allowlist(msg):
    for n in range(1, len(msg.segment("PID"))):
        if n not in KEEP:
            msg[f"PID.F{n}"] = ""
    mrn = str(msg["PID.F3.R1.C1"])
    msg["PID.F3.R1.C1"] = pseudonym(mrn)  # salted SHA-256
    msg["PID.F7"] = str(msg["PID.F7"])[:4]  # birth year
    return msg


def blocklist(msg):
    for n in DROP:
        msg[f"PID.F{n}"] = ""
    mrn = str(msg["PID.F3.R1.C1"])
    msg["PID.F3.R1.C1"] = pseudonym(mrn)
    msg["PID.F7"] = str(msg["PID.F7"])[:4]
    return msg


if __name__ == "__main__":
    how, path = sys.argv[1:3]
    msg = hl7.parse(open(path, newline="").read())
    print(globals()[how](msg).segment("PID"))
