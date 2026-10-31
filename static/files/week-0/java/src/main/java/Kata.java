import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.rest.client.api.IClientInterceptor;
import ca.uhn.fhir.rest.client.api.IGenericClient;
import ca.uhn.fhir.rest.client.api.IHttpRequest;
import ca.uhn.fhir.rest.client.api.IHttpResponse;
import org.hl7.fhir.r4.model.Bundle;
import org.hl7.fhir.r4.model.ContactPoint.ContactPointSystem;
import org.hl7.fhir.r4.model.ContactPoint.ContactPointUse;
import org.hl7.fhir.r4.model.OperationOutcome;
import org.hl7.fhir.r4.model.Patient;

import java.util.Map;
import java.util.TreeMap;

/**
 * Week 0 kata: find by MRN, add a mobile, $validate,
 * conditional PUT, prove exactly one write.
 */
public class Kata {
  static final String S = "http://hospital.smarthealthit.org";
  static int status; // HTTP status of the last response

  public static void main(String[] args) {
    String mrn = System.getenv("MRN"), mobile = args[0];
    String byMrn = "Patient?identifier=" + S + "|" + mrn;

    IGenericClient client = FhirContext.forR4()
        .newRestfulGenericClient(System.getenv("FHIR"));
    client.registerInterceptor(new IClientInterceptor() {
      public void interceptRequest(IHttpRequest req) {}
      public void interceptResponse(IHttpResponse res) {
        status = res.getStatus();
      }
    });

    // 1. Search by identifier (never _id: not the MRN)
    Bundle found = client.search().byUrl(byMrn)
        .returnBundle(Bundle.class).execute();
    check(found.getTotal() == 1,
        "expected 1 match, got " + found.getTotal());
    Patient p = (Patient) found.getEntryFirstRep().getResource();
    String id = p.getIdElement().getIdPart();
    int before = Integer.parseInt(p.getMeta().getVersionId());
    log("search   GET  Patient?identifier=S|MRN",
        "1 match, id " + id + ", v" + before);

    // 2. Replace any mobile number with ours
    p.getTelecom().removeIf(t -> t.getUse() == ContactPointUse.MOBILE);
    p.addTelecom().setSystem(ContactPointSystem.PHONE)
        .setUse(ContactPointUse.MOBILE).setValue(mobile);

    // 3. $validate: HTTP 200 says nothing; count severities
    OperationOutcome oo = (OperationOutcome) client.validate()
        .resource(p).execute().getOperationOutcome();
    Map<String, Integer> sev = new TreeMap<>();
    for (var issue : oo.getIssue())
      sev.merge(issue.getSeverity().toCode(), 1, Integer::sum);
    log("validate POST Patient/$validate", sev.toString());
    check(!sev.containsKey("fatal") && !sev.containsKey("error"),
        "invalid");

    // 4. Conditional update on the identifier
    client.update().resource(p).conditionalByUrl(byMrn).execute();
    log("update   PUT  Patient?identifier=S|MRN", "");

    // 5. Read back: still one patient, one version more
    Bundle again = client.search().byUrl(byMrn)
        .returnBundle(Bundle.class).execute();
    Patient q = (Patient) again.getEntryFirstRep().getResource();
    int after = Integer.parseInt(q.getMeta().getVersionId());
    log("re-read  GET  Patient?identifier=S|MRN",
        again.getTotal() + " match, v" + after);
    check(again.getTotal() == 1, "duplicate patient");
    check(after == before + 1,
        "expected v" + (before + 1) + ", got v" + after);

    // 6. History holds every version: none lost, none extra
    Bundle hist = client.history().onInstance("Patient/" + id)
        .returnBundle(Bundle.class).execute();
    log("history  GET  Patient/" + id + "/_history",
        hist.getTotal() + " versions");
    check(hist.getTotal() == after, "history has " + hist.getTotal());

    System.out.println(
        "PASS java: v" + before + " -> v" + after + ", one patient");
  }

  static void log(String call, String note) {
    String line = String.format("%-40s %d  %s", call, status, note);
    System.out.println(line.stripTrailing());
  }

  static void check(boolean ok, String why) {
    if (ok) return;
    System.out.println("FAIL java: " + why);
    System.exit(1);
  }
}
