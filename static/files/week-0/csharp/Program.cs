// Week 0 kata: find by MRN, add a mobile, $validate,
// conditional PUT, prove exactly one write.
using Hl7.Fhir.Model;
using Hl7.Fhir.Rest;
using Severity = Hl7.Fhir.Model.OperationOutcome.IssueSeverity;

const string S = "http://hospital.smarthealthit.org";
var mrn = Environment.GetEnvironmentVariable("MRN");
var mobile = args[0];
var byMrn = new SearchParams().Where($"identifier={S}|{mrn}");

using var client =
    new FhirClient(Environment.GetEnvironmentVariable("FHIR"));

// LastResult is the response line of the last call
void Log(string call, string note) => Console.WriteLine(
    $"{call,-40} {client.LastResult?.Status}  {note}".TrimEnd());

void Check(bool ok, string why)
{
    if (ok) return;
    Console.WriteLine($"FAIL csharp: {why}");
    Environment.Exit(1);
}

// 1. Search by identifier (never _id: not the MRN)
var found = await client.SearchAsync<Patient>(byMrn);
Check(found.Total == 1, $"expected 1 match, got {found.Total}");
var p = (Patient)found.Entry[0].Resource;
var before = int.Parse(p.Meta.VersionId);
Log("search   GET  Patient?identifier=S|MRN",
    $"1 match, id {p.Id}, v{before}");

// 2. Replace any mobile number with ours
p.Telecom.RemoveAll(t => t.Use == ContactPoint.ContactPointUse.Mobile);
p.Telecom.Add(new ContactPoint(ContactPoint.ContactPointSystem.Phone,
    ContactPoint.ContactPointUse.Mobile, mobile));

// 3. $validate: HTTP 200 says nothing; count severities
var oo = await client.ValidateResourceAsync(p);
var sev = oo.Issue.GroupBy(i => i.Severity.ToString().ToLower())
    .OrderBy(g => g.Key).Select(g => $"{g.Key}={g.Count()}");
Log("validate POST Patient/$validate",
    "{" + string.Join(", ", sev) + "}");
Check(!oo.Issue.Any(i =>
    i.Severity is Severity.Fatal or Severity.Error), "invalid");

// 4. Conditional update on the identifier
await client.ConditionalUpdateAsync(p, byMrn);
Log("update   PUT  Patient?identifier=S|MRN", "");

// 5. Read back: still one patient, one version more
var again = await client.SearchAsync<Patient>(byMrn);
var after = int.Parse(again.Entry[0].Resource.Meta.VersionId);
Log("re-read  GET  Patient?identifier=S|MRN",
    $"{again.Total} match, v{after}");
Check(again.Total == 1, "duplicate patient");
Check(after == before + 1, $"expected v{before + 1}, got v{after}");

// 6. History holds every version: none lost, none extra
var hist = await client.HistoryAsync($"Patient/{p.Id}");
Log($"history  GET  Patient/{p.Id}/_history",
    $"{hist.Total} versions");
Check(hist.Total == after, $"history has {hist.Total}");

Console.WriteLine($"PASS csharp: v{before} -> v{after}, one patient");
