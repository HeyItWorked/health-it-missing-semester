# Rules for AI coding tools in this repo

This repo moves patient data. These rules apply to every AI tool
and every person using one.

## Data
- Use approved tools only (see the team wiki). No personal accounts.
- Synthetic data only: Synthea output, the canary messages in this
  repo, or hand-made samples with example.org identifier systems.
- Never paste logs, tickets, screenshots, crash dumps or database
  rows into a prompt, even "just one line". Describe the problem.
- Do not open or read files under `data/`, `exports/` or `*.log`.

## Code
- Never log message bodies, names, birth dates, MRNs, health card
  numbers or addresses. Log MSH-10 control IDs and resource ids.
- Redaction is allowlist-only: name the fields you keep.
- Pseudonyms use HMAC with `PSEUDONYM_KEY` from the environment.
  Never hard-code the key, print it, or commit it.
- Any change to logging, redaction or error handling must keep
  `pytest test_redact.py test_canary_logs.py` passing.

## If you see PHI
Stop. Do not copy it anywhere, including into the prompt.
Tell the privacy contact, then follow the incident runbook.
