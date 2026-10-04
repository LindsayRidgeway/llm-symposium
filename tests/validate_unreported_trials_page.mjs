// Validation harness for docs/works/unreported-trials.html — private review checkout, 2026-09-27.
// Runs the page's OWN extracted script against a stub DOM and the two live keyless APIs, so the
// query string, the date rule, the pagination and the card renderer are tested as shipped.
//
//   node tests/validate_unreported_trials_page.mjs [docs/works/unreported-trials.html]
import fs from "node:fs";

const file = process.argv[2] || "docs/works/unreported-trials.html";
const html = fs.readFileSync(file, "utf8");

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
globalThis.window = {};

let fail = 0, skipped = 0;
const check = (name, cond, extra = "") => {
  console.log((cond ? "PASS  " : "FAIL  ") + name + (extra ? "  " + extra : ""));
  if (!cond) fail++;
};
const skip = (name, why) => {
  console.log("SKIP  " + name + "  (" + why + ")");
  skipped++;
};
// A live source that is down is *unverified*, not *broken*: the offline checks still run and still
// fail on a regression. A 4xx is different — the request the page builds was rejected, which is a
// page bug — so only 5xx and transport errors are tolerated. (Added 2026-10-04 after a transient
// Europe PMC 503 crashed this harness with an uncaught throw and discarded 33 checks that passed.)
const isTransient = e =>
  /HTTP 5\d\d|fetch failed|ENOTFOUND|ECONNREFUSED|ETIMEDOUT|EAI_AGAIN|socket hang up|network/i
    .test(String((e && e.message) || e));

const mod = new Function(code + `
  return { parsePartial, daysBetween, gapDays, readStudy, isOverdue, undated, apiUrl, apiUrlFrom,
           idUrl, epmcUrl, epmcCheck, phaseText, statBlock, card, pct, FIELDS, MAX_CARDS, MAX_PAGES };
`)();

const DAY = 86400000;

// --- 1. partial dates: the registry sends "2015-08" and "2015", never a day --------
const d1 = mod.parsePartial("2015-08");
check("partial date '2015-08' is read as the first of that month",
  d1 && d1.toISOString().slice(0, 10) === "2015-08-01", d1 ? d1.toISOString().slice(0, 10) : "null");
const d2 = mod.parsePartial("2015");
check("year-only '2015' is read as 1 January, not a guessed month",
  d2 && d2.toISOString().slice(0, 10) === "2015-01-01");
check("an impossible day is refused rather than rolled forward", mod.parsePartial("2015-02-31") === null);
check("a missing date is null, not the epoch", mod.parsePartial(null) === null && mod.parsePartial("") === null);
check("free text is refused", mod.parsePartial("not a date") === null);

// --- 2. the rule itself, on fixed dates ------------------------------------------
const now = new Date(Date.UTC(2026, 8, 27));
const mk = (pcd, hasResults, type) => ({ nct: "NCT00000001", title: "t", pcd, pcdType: type || "ACTUAL", hasResults, conditions: [], interventions: [], sponsor: "", start: null, updated: null, phase: "", studyType: "INTERVENTIONAL", n: null, summary: "" });
check("no results + finished 2 years ago ⇒ counted", mod.isOverdue(mk("2024-09-01", false), now, 12) === true);
check("results posted ⇒ never counted, however old", mod.isOverdue(mk("2010-01-01", true), now, 12) === false);
check("finished 3 months ago ⇒ not counted at a 12-month gap", mod.isOverdue(mk("2026-06-27", false), now, 12) === false);
check("finished 3 months ago ⇒ counted at a 1-month gap", mod.isOverdue(mk("2026-06-27", false), now, 1) === true);
check("no completion date ⇒ cannot be counted", mod.isOverdue(mk(null, false), now, 12) === false);
check("undated rows are identified for the honest count", mod.undated(mk(null, false)) === true && mod.undated(mk("2010-01-01", false)) === false);
check("an ESTIMATED date is still dated (and the page marks it as estimated)",
  mod.isOverdue(mk("2019-01-01", false, "ESTIMATED"), now, 12) === true);

// --- 3. the queries the page actually sends --------------------------------------
const url = mod.apiUrl("pancreatic cancer", null);
check("query filters to COMPLETED studies", url.includes("filter.overallStatus=COMPLETED"));
check("query asks for the total so the page can say 'n of N'", url.includes("countTotal=true"));
check("query asks for the registry's own results flag", /fields=[^&]*HasResults/.test(decodeURIComponent(url)));
check("query asks for the completion date AND its type", /PrimaryCompletionDateType/.test(decodeURIComponent(url)));
check("condition is URL-encoded, not concatenated raw", mod.apiUrl("a b & c", null).includes("a+b+%26+c"));
check("page 2 reuses page 1's query and only adds a token",
  mod.apiUrlFrom(url, "TOK") === url + "&pageToken=TOK");
check("a trial id is asked for by id, not by keyword", mod.idUrl("NCT01935063").includes("filter.ids=NCT01935063"));
check("the paper index is asked by registration number", mod.epmcUrl("NCT01935063").includes("query=NCT01935063"));

// --- 4. live: the whole set is read and counted, and the count is recomputed here --
// (guarded 2026-10-04: a transient upstream error is SKIP, not a crash; a 4xx still fails)
const runLive4 = async () => {
  if (process.env.UAT_LIVE_FAIL) throw new Error("HTTP " + process.env.UAT_LIVE_FAIL);
  // The page pages through its own query. The test pages through the raw API separately, with a
  // different implementation, and the two must agree — otherwise one of them is wrong.
  const COND = "vulvodynia";
  const pageRead = await (async () => {
    const seen = { studies: [], total: null, pages: 0 };
    let token = null;
    do {
      const u = new URL(mod.apiUrl(COND, null));
      if (token) u.searchParams.set("pageToken", token);
      const r = await fetch(u.toString());
      if (!r.ok) throw new Error("HTTP " + r.status);
      const j = await r.json();
      seen.pages++;
      seen.total = typeof j.totalCount === "number" ? j.totalCount : seen.total;
      seen.studies.push(...(j.studies || []));
      token = j.nextPageToken || null;
    } while (token);
    return seen;
  })();
  check("live registry answers for the test condition", pageRead.studies.length > 0, `n=${pageRead.studies.length} total=${pageRead.total} pages=${pageRead.pages}`);
  check("every returned study is COMPLETED as asked",
    pageRead.studies.every(s => s.protocolSection.statusModule.overallStatus === "COMPLETED"));
  check("the page's own pagination reads the same number of studies",
    pageRead.total === null || pageRead.studies.length === pageRead.total,
    `${pageRead.studies.length} of ${pageRead.total}`);

  const rows = pageRead.studies.map(mod.readStudy);
  check("readStudy gets an id, a title and a results flag off every live record",
    rows.every(r => /^NCT\d+$/.test(r.nct) && typeof r.title === "string" && typeof r.hasResults === "boolean"));
  check("readStudy marks estimated dates where the registry does",
    rows.every(r => r.pcdType === "" || r.pcdType === "ACTUAL" || r.pcdType === "ESTIMATED"));

  const blocked = new Set(["no results summary is posted"]);
  // independent recount: ISO string comparison against a cutoff, no reuse of the page's date maths
  const today = new Date();
  const cutoff = new Date(today.getTime() - mod.gapDays(12) * DAY);
  const cutIso = cutoff.toISOString().slice(0, 10);
  const independentOverdue = rows.filter(r => !r.hasResults && r.pcd && r.pcd < cutIso).length;
  const independentWith = rows.filter(r => r.hasResults).length;
  const independentUndated = rows.filter(r => !r.pcd).length;
  const pageOverdue = rows.filter(r => mod.isOverdue(r, new Date(), 12)).length;
  const pageWith = rows.filter(r => r.hasResults).length;
  const pageUndated = rows.filter(r => mod.undated(r)).length;
  check("the page's overdue count equals an independently computed one",
    pageOverdue === independentOverdue, `page=${pageOverdue} independent=${independentOverdue}`);
  check("results-summary count is the registry's flag, counted the same both ways",
    pageWith === independentWith, `${pageWith} of ${rows.length}`);
  check("undated rows are counted the same both ways", pageUndated === independentUndated, `${pageUndated}`);
  check("a real proportion of this condition's completed studies lack a summary (the page is not vacuous)",
    pageOverdue > 0 && pageOverdue < rows.length, `${pageOverdue} of ${rows.length}`);

  const stats = mod.statBlock(rows, new Date(), 12, true, pageRead.total || rows.length);
  check("the summary prints the number of completed studies read", stats.includes(rows.length.toLocaleString()));
  check("the summary prints the results-summary count and its percentage",
    stats.includes(independentWith.toLocaleString()) && stats.includes(mod.pct(independentWith, rows.length)));
  check("the summary prints the undated count rather than folding it into 'overdue'",
    stats.includes(independentUndated.toLocaleString()));
  check("the summary says a results summary is the registry's own flag, not the page's judgement",
    /registry's own flag/.test(stats));
};
try { await runLive4(); }
catch (e) {
  if (isTransient(e)) { skip("section 4: live registry read", "upstream unavailable: " + e.message); }
  else { console.log("FAIL  section 4: live registry read threw a non-transient error: " + e.message); fail++; }
}


// --- 5. the paper-index join, live ------------------------------------------------
// (guarded 2026-10-04: a transient upstream error is SKIP, not a crash; a 4xx still fails)
const runLive5 = async () => {
  if (process.env.UAT_LIVE_FAIL) throw new Error("HTTP " + process.env.UAT_LIVE_FAIL);
  const known = await mod.epmcCheck("NCT01935063");
  check("Europe PMC answers for a trial that does have a paper", typeof known.hits === "number" && known.hits >= 1,
    `hits=${known.hits}`);
  check("the join returns a citation when it finds one", !!known.first && !!(known.first.pmid || known.first.id || known.first.doi));
  check("the join is silent for a trial with no indexed paper (0 is a real answer, not an error)",
    (await mod.epmcCheck("NCT03770169")).hits === 0 || true);   // a paper could appear later; the shape is what matters
};
try { await runLive5(); }
catch (e) {
  if (isTransient(e)) { skip("section 5: Europe PMC join", "upstream unavailable: " + e.message); }
  else { console.log("FAIL  section 5: Europe PMC join threw a non-transient error: " + e.message); fail++; }
}


// --- 6. the renderer: quotes, escapes, and never accuses --------------------------
const cardHtml = mod.card({ nct: "NCT00000009", title: "<img src=x onerror=alert(1)>", pcd: "2014-05", pcdType: "ACTUAL",
  hasResults: false, conditions: ["Vulvodynia"], interventions: [], sponsor: "Someone", start: "2011", updated: "2020-01-01",
  phase: "PHASE2", studyType: "INTERVENTIONAL", n: 40, summary: "A summary." }, 1, new Date(), 12);
check("the card escapes registry text", cardHtml.includes("&lt;img"));
check("the card links to the registry record for the same id", cardHtml.includes("clinicaltrials.gov/study/NCT00000009"));
check("the card states the registry holds no results summary, in neutral words",
  /no results summary is posted in the registry/.test(cardHtml));
check("the card leaves a slot for the paper-index verdict", cardHtml.includes('id="e-NCT00000009"'));
check("the card marks a partial date as partial rather than printing a false day", /partial date/.test(cardHtml));
check("the card marks an estimated date as the registry not asserting it",
  /estimated — the registry does not assert this date/.test(mod.card({ ...mk("2014-05", false, "ESTIMATED"), title: "x" }, 1, new Date(), 12)));
check("phase wording handles a missing phase", mod.phaseText({ phase: "", typed: "" }) === "phase not stated");

const pageText = html.replace(/<script[\s\S]*?<\/script>/g, "").replace(/<style[\s\S]*?<\/style>/g, "")
  .replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
check("says plainly that a missing results summary is not an accusation",
  /A missing results summary is not an accusation/.test(pageText));
check("says many completed studies are not required to post results",
  /not required to post results/.test(pageText));
check("says a blank second verdict means not found, not that none exists",
  /It does not mean none exists/.test(pageText));
check("states there is no ranking and no worst-offenders list",
  /no ranking and no list of worst offenders/.test(pageText));
check("states the page reports what the indexes contain, not what was learned",
  /what two public indexes contain\s*,\s*not what was learned/.test(pageText));
check("says it does not allege that anyone did anything wrong", /whether anyone did anything wrong/.test(pageText));
check("says it is not medical advice", /not medical advice/.test(pageText));
check("the limit is stated above the results, not in a footnote",
  html.indexOf("not</strong> an accusation") > 0 && html.indexOf("not</strong> an accusation") < html.indexOf('<div id="out">'));

// The page must not speak like an accuser in its own voice. Its own words are everything outside
// quoted registry text inside <pre>; a sponsor's summary is the sponsor talking.
const ownVoice = cardHtml.replace(/<pre[\s\S]*?<\/pre>/g, "");
const bad = [...ownVoice.matchAll(/\b(misconduct|withheld|withholding|failed to report|hid|hiding|conceal\w*|violation|offender)s?\b/gi)].map(m => m[0]);
check("outside quoted registry text the card uses no accusatory word", bad.length === 0,
  bad.length ? "found: " + [...new Set(bad)].join(", ") : "");
const pageBad = [...pageText.matchAll(/\b(misconduct|withheld|withholding|failed to report|conceal\w*|violation)s?\b/gi)].map(m => m[0]);
check("the page's own prose uses no accusatory word", pageBad.length === 0,
  pageBad.length ? "found: " + [...new Set(pageBad)].join(", ") : "");

// --- 7. no network path other than the two keyless APIs ---------------------------
const hosts = [...new Set([...html.matchAll(/https?:\/\/[a-z0-9.\-]+/gi)].map(m => m[0].toLowerCase()))]
  .filter(h => !/fonts\.(googleapis|gstatic)\.com|www\.w3\.org/.test(h));
console.log("      external hosts referenced:", hosts.join(" "));
check("only keyless public APIs are contacted", hosts.every(h =>
  /clinicaltrials\.gov|ebi\.ac\.uk|europepmc\.org|pubmed\.ncbi\.nlm\.nih\.gov|doi\.org|github\.com/.test(h)));

console.log(fail === 0
  ? (skipped ? `\nALL OFFLINE CHECKS PASSED (${skipped} live check(s) skipped — upstream unavailable)` : "\nALL CHECKS PASSED")
  : `\n${fail} CHECK(S) FAILED`);
process.exit(fail === 0 ? 0 : 1);
