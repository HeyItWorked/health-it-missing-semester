// Week 4: SMART on FHIR EHR launch, server side (fhirclient 3)
import express from "express";
import session from "express-session";
import { smart } from "fhirclient/node";

type Qty = { value: number; unit: string };
type Obs = { effectiveDateTime: string; code: { text: string };
             valueQuantity?: Qty; component?: { valueQuantity: Qty }[] };
type Bundle = { entry?: { resource: Obs }[] };

const PORT = Number(process.env.PORT ?? 9000);
const app = express();
// fhirclient keeps PKCE verifier, state and token in the session
app.use(session({ secret: "dev-only", resave: false,
                  saveUninitialized: false }));

// The EHR opens /launch?iss=<FHIR base>&launch=<opaque>
app.get("/launch", (req, res, next) => {
  smart(req, res).authorize({
    clientId: "labs-app",
    scope: "launch openid fhirUser patient/Observation.rs",
    redirectUri: "/app",
  }).catch(next);
});

function show(o: Obs): string {
  const q = (v: Qty) => `${Number(v.value.toFixed(1))} ${v.unit}`;
  const value = o.valueQuantity ? q(o.valueQuantity)
    : (o.component ?? []).map((c) => q(c.valueQuantity)).join(" / ");
  return `${o.effectiveDateTime.slice(0, 10)}  ${o.code.text}: ${value}`;
}

// The authorization server redirects back here with ?code=&state=
app.get("/app", async (req, res, next) => {
  try {
    const client = await smart(req, res).ready();
    const lines = [`patient ${client.patient.id}`,
                   `scope ${client.state.tokenResponse?.scope}`];
    for (const cat of ["laboratory", "vital-signs"]) {
      const bundle = await client.request<Bundle>(
        `Observation?patient=${client.patient.id}` +
        `&category=${cat}&_sort=-date&_count=4`);
      lines.push(`-- ${cat}`,
                 ...(bundle.entry ?? []).map((e) => show(e.resource)));
    }
    res.type("text/plain").send(lines.join("\n") + "\n");
  } catch (e) {
    next(e);
  }
});

app.listen(PORT, () => console.log(`labs-app on :${PORT}`));
