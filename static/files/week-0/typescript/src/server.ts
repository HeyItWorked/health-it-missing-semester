// Week 0 kata: find by MRN, add a mobile, $validate,
// conditional PUT, prove exactly one write.
// fhirclient's Node build works per request: the kata is a route.
import express from "express";
import { smart } from "fhirclient/node";
import type { Bundle, OperationOutcome, Patient } from "fhir/r4";

const S = "http://hospital.smarthealthit.org";
const FHIR = process.env.FHIR!;
const MRN = process.env.MRN!;
const byMrn = `Patient?identifier=${S}|${MRN}`;

const app = express();

app.get("/kata/:mobile", async (req, res) => {
  const client = smart(req, res).client(FHIR);
  const out: string[] = [];
  let status = 0;

  async function call<T>(method: string, url: string, body?: object) {
    const r = await client.request<{ body: T; response: Response }>({
      url, method, includeResponse: true,
      headers: { "content-type": "application/fhir+json" },
      body: body && JSON.stringify(body),
    });
    status = r.response.status;
    return r.body;
  }
  const log = (call: string, note = "") =>
    out.push(`${call.padEnd(40)} ${status}  ${note}`.trimEnd());
  const check = (ok: boolean, why: string) => {
    if (!ok) throw new Error(why);
  };

  try {
    // 1. Search by identifier (never _id: not the MRN)
    const found = await call<Bundle<Patient>>("GET", byMrn);
    check(found.total === 1, `expected 1 match, got ${found.total}`);
    const p = found.entry![0].resource!;
    const before = Number(p.meta!.versionId);
    log("search   GET  Patient?identifier=S|MRN",
      `1 match, id ${p.id}, v${before}`);

    // 2. Replace any mobile number with ours
    p.telecom = (p.telecom ?? []).filter((t) => t.use !== "mobile");
    p.telecom.push(
      { system: "phone", use: "mobile", value: req.params.mobile });

    // 3. $validate: HTTP 200 says nothing; count severities
    const oo = await call<OperationOutcome>(
      "POST", "Patient/$validate", p);
    const sev: Record<string, number> = {};
    for (const i of oo.issue) sev[i.severity] = (sev[i.severity] ?? 0) + 1;
    const counts = Object.keys(sev).sort()
      .map((k) => `${k}=${sev[k]}`);
    log("validate POST Patient/$validate", `{${counts.join(", ")}}`);
    check(!sev.fatal && !sev.error, "invalid");

    // 4. Conditional update on the identifier
    await call("PUT", byMrn, p);
    log("update   PUT  Patient?identifier=S|MRN");

    // 5. Read back: still one patient, one version more
    const again = await call<Bundle<Patient>>("GET", byMrn);
    const after = Number(again.entry![0].resource!.meta!.versionId);
    log("re-read  GET  Patient?identifier=S|MRN",
      `${again.total} match, v${after}`);
    check(again.total === 1, "duplicate patient");
    check(after === before + 1, `expected v${before + 1}, got v${after}`);

    // 6. History holds every version: none lost, none extra
    const hist = await call<Bundle>("GET", `Patient/${p.id}/_history`);
    log(`history  GET  Patient/${p.id}/_history`,
      `${hist.total} versions`);
    check(hist.total === after, `history has ${hist.total}`);

    out.push(`PASS typescript: v${before} -> v${after}, one patient`);
    res.type("text").send(out.join("\n") + "\n");
  } catch (e) {
    out.push(`FAIL typescript: ${(e as Error).message}`);
    res.status(500).type("text").send(out.join("\n") + "\n");
  }
});

app.listen(3000, () =>
  console.log("kata on http://localhost:3000/kata/:mobile"));
