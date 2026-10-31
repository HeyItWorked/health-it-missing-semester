"""Week 3 bridge: HL7 v2 ADT over MLLP -> FHIR Patient."""
import asyncio
import datetime
import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request

import hl7
from hl7.mllp import start_hl7_server

FHIR = os.environ.get("FHIR_BASE", "http://localhost:8080/fhir")
# PID-3.4 assigning authority -> FHIR identifier system
SYSTEMS = {"GENHOSP": "https://genhosp.example.org/mrn"}
GENDER = {"F": "female", "M": "male", "O": "other", "U": "unknown"}
log = logging.getLogger("bridge")


class Reject(Exception):
    """Bad message: answer AE/AR with an ERR segment, write nothing."""
    def __init__(self, code, where, why):
        super().__init__(why)
        self.code, self.where, self.why = code, where, why


def birth_date(dtm):
    """HL7 DTM (YYYY[MM[DD[HHMM...]]]) -> FHIR date, same precision."""
    day = dtm[:8]
    fmt = {4: ("%Y", "%Y"), 6: ("%Y%m", "%Y-%m"),
           8: ("%Y%m%d", "%Y-%m-%d")}.get(len(day))
    if not fmt or not day.isdigit():
        raise ValueError(dtm)
    return datetime.datetime.strptime(day, fmt[0]).strftime(fmt[1])


def field(msg, key):
    """Leaf value like "PID.F5.R1.C2"; "" if the sender omitted it."""
    try:
        return msg[key]
    except IndexError:
        return ""


def to_patient(msg):
    if field(msg, "MSH.F11") != "T":  # this is a test listener
        raise Reject("AR", "MSH^1^11",
                     "202^Unsupported processing id^HL70357")
    mrn = field(msg, "PID.F3.R1.C1")
    if not mrn:
        raise Reject("AE", "PID^1^3",
                     "101^Required field missing^HL70357")
    system = SYSTEMS.get(field(msg, "PID.F3.R1.C4"))
    if not system:
        raise Reject("AE", "PID^1^3",
                     "103^Table value not found^HL70357")
    name = {"family": field(msg, "PID.F5.R1.C1")}
    if field(msg, "PID.F5.R1.C2"):
        name["given"] = [field(msg, "PID.F5.R1.C2")]
    patient = {
        "resourceType": "Patient",
        "identifier": [{"system": system, "value": mrn}],
        "active": True,
        "name": [name],
        "gender": GENDER.get(field(msg, "PID.F8"), "unknown"),
    }
    if field(msg, "PID.F7"):
        try:
            patient["birthDate"] = birth_date(field(msg, "PID.F7"))
        except ValueError:
            raise Reject("AE", "PID^1^7",
                         "102^Data type error^HL70357")
    return patient


def upsert(patient):
    """Conditional PUT on the MRN: create the first time, then update"""
    ident = patient["identifier"][0]
    query = urllib.parse.urlencode(
        {"identifier": f"{ident['system']}|{ident['value']}"})
    req = urllib.request.Request(
        f"{FHIR}/Patient?{query}", method="PUT",
        data=json.dumps(patient).encode(),
        headers={"Content-Type": "application/fhir+json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.headers["Content-Location"]
    except urllib.error.HTTPError as e:
        if e.code == 412:  # several patients share this MRN already
            raise Reject("AE", "PID^1^3",
                         "205^Duplicate key identifier^HL70357")
        if e.code < 500:
            raise Reject("AE", "PID",
                         "207^Application internal error^HL70357")
        raise  # 5xx: treat like an outage


def process(msg):
    ctl = field(msg, "MSH.F10")
    try:
        status, location = upsert(to_patient(msg))
    except Reject as e:
        log.warning("%s %s: %s at %s, nothing written",
                    ctl, e.code, e.why, e.where)
        ack = msg.create_ack(e.code)
        return hl7.parse(f"{ack}ERR||{e.where}|{e.why}|E\r")
    except OSError as e:  # FHIR down: no ACK, so it retries
        log.error("%s write failed (%s), no ACK sent",
                  ctl, e)
        return None
    log.info("%s AA after HTTP %s %s", ctl, status, location)
    return msg.create_ack("AA")


async def handle(reader, writer):
    try:
        while not writer.is_closing():
            # one message at a time keeps the feed in order
            ack = process(await reader.readmessage())
            if ack is None:
                break
            writer.writemessage(ack)
            await writer.drain()
    except asyncio.IncompleteReadError:
        pass  # the sender hung up
    finally:
        writer.close()


async def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    async with await start_hl7_server(handle, port=2575) as server:
        log.info("listening for MLLP on port 2575")
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
