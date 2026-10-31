"""Week 4: a minimal CDS Hooks service with one patient-view hook.

Run: python3 cds-service.py [port]   (default 3001)
Discovery: GET  /cds-services
Hook call: POST /cds-services/a1c-latest
"""
import json
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

A1C = ("Observation?patient={{context.patientId}}"
       "&code=http://loinc.org|4548-4&_sort=-date&_count=1")
SERVICE = {
    "hook": "patient-view",
    "id": "a1c-latest",
    "title": "Latest HbA1c",
    "description": "Shows the most recent HbA1c, or warns if none.",
    "prefetch": {"a1c": A1C},
}
SOURCE = {"label": "Week 4 demo service (synthetic data)"}


def fetch_a1c(req):
    """Used only when the EHR sent no prefetch: ask its FHIR server."""
    query = A1C.replace("{{context.patientId}}",
                        req["context"]["patientId"])
    http = urllib.request.Request(f"{req['fhirServer']}/{query}")
    token = (req.get("fhirAuthorization") or {}).get("access_token")
    if token:
        http.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(http, timeout=10) as resp:
        return json.load(resp)


def cards(req):
    bundle = req.get("prefetch", {}).get("a1c")
    if bundle is None:
        bundle = fetch_a1c(req)
    entries = bundle.get("entry", [])
    if not entries:
        return [{"summary": "No HbA1c on file", "indicator": "warning",
                 "source": SOURCE}]
    obs = entries[0]["resource"]
    q = obs["valueQuantity"]
    when = obs["effectiveDateTime"][:10]
    return [{"summary": f"Latest HbA1c {q['value']} {q['unit']} ({when})",
             "indicator": "info", "source": SOURCE}]


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/cds-services":
            self.reply(200, {"services": [SERVICE]})
        else:
            self.reply(404, {"error": "not found"})

    def do_POST(self):
        if self.path != f"/cds-services/{SERVICE['id']}":
            return self.reply(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length", 0))
        try:
            req = json.loads(self.rfile.read(length))
            if req.get("hook") != SERVICE["hook"]:
                raise ValueError("wrong hook")
            self.reply(200, {"cards": cards(req)})
        except (ValueError, KeyError) as e:
            self.reply(400, {"error": str(e)})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3001
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
