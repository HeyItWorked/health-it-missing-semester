"""Week 5: reverse an unsalted MRN hash by trying every MRN."""
import hashlib
import sys

target = sys.argv[1]
for n in range(1_000_000):  # every 6-digit MRN
    mrn = f"{n:06d}"
    if hashlib.sha256(mrn.encode()).hexdigest().startswith(target):
        print("MRN", mrn)
        break
else:
    print("no match in 1,000,000 candidates")
