"""Write a synthetic day of ADT traffic (TEST feed) to day.hl7.

One message per line; segments end in \\r as HL7 requires.
Usage: python3 day.py [patients] > day.hl7
"""
import random
import sys

FAMILY = ["NGUYEN", "SMITH", "TREMBLAY", "GARCIA", "PATEL",
          "ROY", "BROWN", "LI", "MARTIN", "WILSON"]
GIVEN = ["ALEX", "SAM", "JORDAN", "TAYLOR", "RILEY", "CASEY"]
# A08 reuses the A01 structure; A03 has its own
STRUCT = {"A01": "ADT_A01", "A08": "ADT_A01", "A03": "ADT_A03"}


def msg(n, t, event, mrn, name, dob, sex, cls):
    return "\r".join([
        f"MSH|^~\\&|REGADT|GENHOSP|BRIDGE|LAB|{t}||"
        f"ADT^{event}^{STRUCT[event]}|DAY{n:05d}|T|2.5.1",
        f"EVN|{event}|{t}",
        f"PID|1||{mrn}^^^GENHOSP^MR||{name}||{dob}|{sex}",
        f"PV1|1|{cls}|4W^{400 + n % 30}^A",
    ]) + "\r"


def day(patients, seed=6):
    rng = random.Random(seed)  # same file every run
    events = []
    for i in range(patients):
        mrn = 300001 + i
        name = f"{rng.choice(FAMILY)}^{rng.choice(GIVEN)}"
        dob = f"{rng.randint(1940, 2020)}{rng.randint(1, 12):02d}" \
              f"{rng.randint(1, 28):02d}"
        sex = rng.choice("FM")
        start = rng.randint(0, 20 * 60)
        events.append((start, "A01", mrn, name, dob, sex, "I"))
        if rng.random() < 0.5:  # demographics corrected
            name = f"{name.split('^')[0]}^{rng.choice(GIVEN)}"
            events.append((start + 30, "A08", mrn, name, dob, sex, "I"))
        if rng.random() < 0.6:
            events.append((start + 180, "A03", mrn, name, dob, sex, "I"))
    events.sort()
    for n, (m, event, *rest) in enumerate(events, 1):
        t = f"20261030{m // 60:02d}{m % 60:02d}00"
        yield msg(n, t, event, *rest)


if __name__ == "__main__":
    for m in day(int(sys.argv[1]) if len(sys.argv) > 1 else 100):
        print(m)
