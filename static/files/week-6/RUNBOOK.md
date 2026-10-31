# Runbook: ADT to FHIR lab stack

Commands below were run on 31 Oct 2026 (see the week 6 page),
except where a heading says "not run".
Run commands from the repo root. Lab credentials only.

    export OIE=https://localhost:8443/api
    export CH=6e0d3c1a-7b2f-4c55-9e1a-0a5d2f3b6c01

## Start
    docker compose up -d --wait --wait-timeout 120   # < 1 min, images local
    curl -K oie.curl -H 'Content-Type: application/xml' \
      --data-binary @channels/adt-to-bridge.xml $OIE/channels
    curl -K oie.curl -X POST $OIE/channels/$CH/_deploy   # 204
Check: `.../status` says STARTED; send `adt.hl7` to port 6661, expect AA.

## Stop
    docker compose down
Warning: HAPI keeps its data inside the container. `down` deletes
every Patient. Production servers use an external database.

## Health check (cron every minute)
    ./oncall.sh $CH     # exit 2 = page someone
Pages on queue depth > 3 or error rate > 5%, not on single errors.

## Change (in an agreed change window)
1. Edit `channels/adt-to-bridge.xml`, open a pull request; the
   reviewer reads the diff and the interface spec together.
2. Deploy: PUT the file with `?override=true`, then `_deploy`.
3. Export the channel back into `channels/` and commit it (the
   server bumps `<revision>`).
4. Send `adt.hl7`; expect AA. If not, roll back.

## Roll back
    git revert --no-edit <change-commit>
    # then step 2 of Change, and check status + one AA
Rollback is just another deploy. Rehearse it before the window.

## Bridge or FHIR server down
- With queue-on-failure deployed (tested): OIE answers the sender
  with an empty MLLP frame (no ACK), keeps the message and retries
  every 10 s. Watch `queued` in `oncall.sh`.
- With the channel as committed (no queue): not run in week 6;
  expect no AA, so the sender keeps the message and retries.
- FHIR server down: the bridge sends no ACK (tested in week 3).
- Fix the bridge or HAPI, then confirm `queued=0` and one AA.

## Replay a day
    python3 day.py > day.hl7           # or the sender's archive
    mllp_send --loose -f day.hl7 -p 6661 localhost | grep -c 'MSA|AA'
Safe because every write is a conditional PUT on the MRN. Replay
in the original order; patients with A08 updates briefly rewind
to their A01 state and are restored by the replayed A08.

## Downtime (planned; people procedure, not run in the lab)
1. Tell registration and the units, with start and end times.
2. Units switch to the downtime procedure (paper or read-only).
3. After the window: check `queued=0`, send a test message,
   tell everyone the interface is back, reconcile any paper
   registrations through the normal registration screens.
