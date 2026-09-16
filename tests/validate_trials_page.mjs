// Validation harness for docs/works/trials.html — private review checkout, 2026-09-15.
// Runs the page's OWN extracted script against a stub DOM and the live registry,
// so the query string, the distance maths and the card renderer are tested as shipped.
import fs from "node:fs";

const file = process.argv[2];
const html = fs.readFileSync(file, "utf8");

// pull every <script> block that has no src=
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (blocks.length !== 1) { console.error("expected exactly one inline script, got", blocks.length); process.exit(1); }
const code = blocks[0];

// --- minimal DOM stub ------------------------------------------------------
const el = () => ({
  value: "", textContent: "", innerHTML: "", style: {}, id: "",
  addEventListener() {}, querySelectorAll: () => [], appendChild() {}, dataset: {},
});
const store = new Map();
globalThis.document = {
  getElementById: id => store.get(id) || (store.set(id, el()), store.get(id)),
  createElement: () => el(),
  querySelectorAll: () => [],
};
globalThis.location = { search: "" };

let fail = 0;
const check = (name, cond, extra = "") => {
  console.log((cond ? "PASS  " : "FAIL  ") + name + (extra ? "  " + extra : ""));
  if (!cond) fail++;
};

const mod = new Function(code + `
  return { haversineKm, apiUrl, phaseText, agesText, sitesWithDistance, renderStudy,
           fmtKm, placeLabel, FIELDS, setPlace: p => { PLACE = p; } };
`)();

// --- 1. distance maths, against an independent hand calculation ------------
const boston = { lat: 42.35843, lon: -71.05977 };
const birmingham = { lat: 33.52066, lon: -86.80249 };
const km = mod.haversineKm(boston.lat, boston.lon, birmingham.lat, birmingham.lon);
// 1690 km, confirmed independently by the spherical law of cosines in Python before this
// expectation was written — the first version of this line said 1606 and the test, not the page, was wrong.
check("haversine Boston→Birmingham AL ≈ 1690 km (tolerance 5)", Math.abs(km - 1690) < 5, `got ${km.toFixed(1)}`);
check("haversine is 0 for the same point", mod.haversineKm(1, 2, 1, 2) === 0);
check("haversine is symmetric", Math.abs(mod.haversineKm(10, 20, -30, -40) - mod.haversineKm(-30, -40, 10, 20)) < 1e-9);

// --- 2. the query the page actually sends ----------------------------------
const url = mod.apiUrl("pancreatic cancer", "Boston");
check("query carries filter.overallStatus=RECRUITING", url.includes("filter.overallStatus=RECRUITING"));
check("query carries countTotal=true", url.includes("countTotal=true"));
check("query requests LocationGeoPoint (the distance field)", url.includes("LocationGeoPoint"));
check("place is URL-encoded, not concatenated raw", mod.apiUrl("a b", "New York, NY").includes("New+York%2C+NY"));

const res = await fetch(url);
check("live registry answers HTTP 200 for the page's exact query", res.ok, "HTTP " + res.status);
const j = await res.json();
const studies = j.studies || [];
check("live registry returns studies", studies.length > 0, `n=${studies.length} of totalCount=${j.totalCount}`);
check("totalCount is present, so the page can say '50 of N'", typeof j.totalCount === "number", String(j.totalCount));
check("every returned study is RECRUITING as asked",
  studies.every(s => s.protocolSection.statusModule.overallStatus === "RECRUITING"));

// --- 3. distance ordering, on real records ---------------------------------
mod.setPlace({ label: "Boston, Massachusetts, United States", ...boston });
const withKm = studies.map(s => {
  const locs = (s.protocolSection.contactsLocationsModule || {}).locations || [];
  const w = mod.sitesWithDistance(locs, boston);
  return { id: s.protocolSection.identificationModule.nctId, km: w.length ? w[0].km : Infinity,
           geo: locs.filter(l => l.geoPoint).length, locs: locs.length };
});
const placed = withKm.filter(x => Number.isFinite(x.km));
check("at least one study resolved to a distance", placed.length > 0, `${placed.length}/${withKm.length}`);
check("a Boston search puts a Boston site first", placed.length > 0 && placed[0].km < 60,
  placed.length ? `${placed[0].id} at ${placed[0].km.toFixed(1)} km` : "n/a");
check("distances are non-negative and finite", placed.every(x => x.km >= 0));
// The first version of this asserted that out-of-place sites appear in the results. They do not:
// the registry's location filter returns studies that each have at least one site in the place.
// What is true, and why the page must show the nearest sites rather than the whole list, is that
// those same studies list dozens of sites worldwide.
const allSites = studies.flatMap(s => ((s.protocolSection.contactsLocationsModule || {}).locations || [])
  .filter(l => l.geoPoint).map(l => mod.haversineKm(boston.lat, boston.lon, l.geoPoint.lat, l.geoPoint.lon)));
check("returned studies list sites far outside the searched place (why nearest-first is needed)",
  allSites.length > 0 && Math.max(...allSites) > 1000,
  `${allSites.length} sites with coordinates, farthest ${Math.round(Math.max(...allSites))} km`);

// --- 4. the renderer runs on real records and quotes rather than rewrites --
let rendered = "", err = null;
try { rendered = studies.map((s, i) => mod.renderStudy(s, i + 1)).join(""); } catch (e) { err = e; }
check("renderStudy runs over every live study", !err && rendered.length > 2000, err ? err.message : `${rendered.length} chars`);
check("cards link to the registry page for the same NCT id",
  studies.every(s => rendered.includes("clinicaltrials.gov/study/" + s.protocolSection.identificationModule.nctId)));
check("eligibility text is shown verbatim (not summarised)",
  studies.some(s => {
    const e = (s.protocolSection.eligibilityModule || {}).eligibilityCriteria;
    if (!e) return true;
    const probe = e.trim().slice(0, 60);
    return rendered.includes(probe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"));
  }));
// Our voice vs. theirs. The words below are legitimate inside quoted registry text — a sponsor
// summary saying its own drug is being tested for effectiveness is the sponsor talking, and
// eligibility text is full of "highly effective method of contraception". What must never happen
// is this page saying it in its own voice, so the test strips every quoted block first.
const quoted = rendered
  .replace(/<pre[^>]*class="quote"[^>]*>[\s\S]*?<\/pre>/g, "")
  .replace(/<p class="quote"[^>]*>[\s\S]*?<\/p>/g, "")
  .replace(/<pre[^>]*>[\s\S]*?<\/pre>/g, "");
const stray = [...quoted.matchAll(/\b(effective|promising|best chance|breakthrough)\b/gi)].map(m => m[0]);
check("outside quoted registry text, the page makes no efficacy claim", stray.length === 0,
  stray.length ? "found: " + [...new Set(stray)].join(", ") : "");
check("quoted registry text is actually present and marked as quoted",
  /<p class="quote"|<pre class="quote"/.test(rendered));

// The honesty requirements the queue file set for this page, checked in the shipped HTML.
const pageText = html.replace(/<script[\s\S]*?<\/script>/g, "").replace(/<style[\s\S]*?<\/style>/g, "")
  .replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
check("states eligibility is decided by the study team, never by a page",
  /Eligibility is decided by the study team/.test(pageText));
check("states it does not recommend or rank by promise",
  /does not recommend a study, rank one above another/.test(pageText) && /not a ranking of promise/.test(pageText));
check("states it is not medical advice", /not medical advice/.test(pageText));
check("says a listed study is not evidence its treatment works",
  /not evidence that its treatment works/.test(pageText));
check("says ordering is distance and nothing else", /The order is distance, and nothing else/.test(pageText));
check("escaping is applied to registry text", mod.renderStudy({
  protocolSection: { identificationModule: { nctId: "NCT1", briefTitle: "<img src=x onerror=alert(1)>" } }
}, 1).includes("&lt;img"));

// --- 5. age / phase wording, including the missing cases -------------------
check("phase: single", mod.phaseText({ designModule: { phases: ["PHASE2"] } }) === "phase 2");
check("phase: missing on an observational study", mod.phaseText({ designModule: { phases: [], studyType: "OBSERVATIONAL" } }) === "observational");
check("phase: missing and not observational", mod.phaseText({ designModule: {} }) === "phase not stated");
check("ages: open-ended", mod.agesText({ minimumAge: "18 Years" }) === "18 Years and older");
check("ages: banded", mod.agesText({ minimumAge: "18 Years", maximumAge: "65 Years" }) === "18 Years to 65 Years");
check("ages: absent is stated, not guessed", mod.agesText({}) === "ages not stated");

// --- 6. the page has no network path other than the two keyless APIs -------
const hosts = [...html.matchAll(/https?:\/\/[a-z0-9.\-]+/gi)].map(m => m[0].toLowerCase());
const external = [...new Set(hosts.filter(h => !/fonts\.(googleapis|gstatic)\.com|www\.w3\.org/.test(h)))];
console.log("      external hosts referenced:", external.join(" "));
check("only keyless public APIs are contacted", external.every(h =>
  /clinicaltrials\.gov|open-meteo\.com|github\.com|w3\.org/.test(h)));

console.log(fail === 0 ? "\nALL CHECKS PASSED" : `\n${fail} CHECK(S) FAILED`);
process.exit(fail === 0 ? 0 : 1);
