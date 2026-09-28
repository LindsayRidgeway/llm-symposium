// Validation harness for docs/works/retraction.html — private review checkout, 2026-09-17.
// Runs the page's OWN extracted script against a stub DOM and the live OpenAlex/Crossref APIs,
// so the DOI parser, the verdict logic, the query builders and the renderer are tested as shipped.
//
//   node tests/validate_retraction_page.mjs docs/works/retraction.html
//
// It is self-checking in the sense that matters: the URLs it fetches are built by the page's own
// functions, and where it can it re-derives a number by a second route and compares.
import fs from "node:fs";

const file = process.argv[2] || "docs/works/retraction.html";
const html = fs.readFileSync(file, "utf8");

// pull every <script> block that has no src= (the page must have exactly one inline script)
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (blocks.length !== 1) { console.error("expected exactly one inline script, got", blocks.length); process.exit(1); }
const code = blocks[0];

// --- minimal DOM stub ------------------------------------------------------
const el = () => ({
  value: "", textContent: "", innerHTML: "", style: {}, id: "", dataset: {},
  addEventListener() {}, querySelectorAll: () => [], appendChild() {},
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
  return { normalizeDoi, shortId, openAlexWorkUrl, crossrefWorkUrl, citingTotalUrl, citingAfterUrl,
           citingNoMentionUrl, retractionRecords, updatedDois, verdictOf, buildModel, renderReport,
           yearsBetween, isoFromParts, citationYearTable, recentCitationsHtml, isRetractionKind,
           epmcSearchUrl, epmcTypes, isRetractedType };
`)();

const WAKEFIELD = "10.1016/S0140-6736(97)11096-0";
const WAKEFIELD_NOTICE = "10.1016/s0140-6736(10)60175-4";
const NEVER_RETRACTED = "10.1038/nature.2014.14583";

// --- 1. the DOI parser, against inputs a person actually pastes -------------
// A DOI can contain parentheses, braces, slashes and a trailing full stop from prose.
const doiCases = [
  [WAKEFIELD, WAKEFIELD.toLowerCase()],
  ["doi:" + WAKEFIELD, WAKEFIELD.toLowerCase()],
  ["https://doi.org/" + WAKEFIELD, WAKEFIELD.toLowerCase()],
  ["http://dx.doi.org/" + WAKEFIELD, WAKEFIELD.toLowerCase()],
  ["See the paper (10.1038/nature.2014.14583) for details.", "10.1038/nature.2014.14583"],
  ["  10.1000/xyz123  ", "10.1000/xyz123"],
  ["https://doi.org/10.1126/science.1216385.", "10.1126/science.1216385"],
  ["10.1007/s11277-021-09072-0", "10.1007/s11277-021-09072-0"],
  ["99.1234/not-a-doi", ""],
  ["no doi here at all", ""],
  ["", ""],
];
for (const [input, want] of doiCases) {
  const got = mod.normalizeDoi(input);
  check(`normalizeDoi(${JSON.stringify(input)}) → ${JSON.stringify(want)}`, got === want, got === want ? "" : `got ${JSON.stringify(got)}`);
}
// the trailing-punctuation strip must not eat a legitimate closing parenthesis inside a DOI
check("a DOI with internal parentheses survives and only trailing punctuation is stripped",
  mod.normalizeDoi("(10.1016/S0140-6736(97)11096-0)") === WAKEFIELD.toLowerCase(),
  mod.normalizeDoi("(10.1016/S0140-6736(97)11096-0)"));
check("shortId pulls the W-number out of an OpenAlex URL and out of a bare id",
  mod.shortId("https://openalex.org/W2117847125") === "W2117847125" && mod.shortId("W2117847125") === "W2117847125");

// --- 2. the queries the page actually sends, fetched live -------------------
const oaUrl = mod.openAlexWorkUrl(WAKEFIELD.toLowerCase());
const crUrl = mod.crossrefWorkUrl(WAKEFIELD.toLowerCase());
check("OpenAlex query addresses the DOI through the doi.org form", oaUrl.includes("/works/https://doi.org/" + WAKEFIELD.toLowerCase()));
check("Crossref query URL-encodes the DOI", mod.crossrefWorkUrl("10.1000/a b").includes("10.1000%2Fa%20b"));

const oaRes = await fetch(oaUrl);
check("live OpenAlex answers HTTP 200 for the page's exact query", oaRes.ok, "HTTP " + oaRes.status);
const work = await oaRes.json();
const crRes = await fetch(crUrl);
check("live Crossref answers HTTP 200 for the page's exact query", crRes.ok, "HTTP " + crRes.status);
const crossref = (await crRes.json()).message;

check("OpenAlex resolves this DOI to the Lancet 1998 paper", /Ileal-lymphoid-nodular hyperplasia/i.test(work.display_name || ""), (work.display_name || "").slice(0, 50));
check("the page's shortId matches OpenAlex's own id", work.id.endsWith("/" + mod.shortId(work.id)));

// --- 3. the verdict, re-derived independently -------------------------------
const v = mod.verdictOf(work, crossref);
check("OpenAlex flags this paper retracted, and the page reads the flag", v.openAlexFlag === true);
check("Crossref holds a retraction record for it, and the page reads it", v.crossrefRecords === true, `records=${JSON.stringify(v.retractions.map(r => r.iso))}`);

// Independent re-derivation: walk Crossref's raw payload without using the page's helpers.
const rawRetractions = (crossref["updated-by"] || []).filter(u => u.type === "retraction");
const rawDates = rawRetractions
  .map(u => u.updated["date-parts"][0])
  .map(p => `${p[0]}-${String(p[1] || 1).padStart(2, "0")}-${String(p[2] || 1).padStart(2, "0")}`)
  .sort();
check("the page's retraction date equals the earliest retraction Crossref records",
  v.retractedDate === rawDates[0], `page=${v.retractedDate} raw=${rawDates[0]}`);
check("the retraction date is the well-known 2010 notice, not the 2004 correction",
  v.retractedDate === "2010-02-06", String(v.retractedDate));
check("every retraction record carries a notice DOI the page can link to",
  v.retractions.every(r => /^10\./.test(r.notice)));
check("the 2004 correction is NOT counted as a retraction", v.retractions.every(r => r.iso !== "2004-03-06"));
check("two sources agreeing is reported as agreement, not silently", v.disagree === false);

// --- 4. the citation counts, and the page's own query for them -------------
const totUrl = mod.citingTotalUrl(work.id);
check("the citing-works query carries the bare W-id, not the full URL",
  totUrl.includes("filter=cites:W") && !totUrl.includes("filter=cites:https"), totUrl.split("filter=")[1]);
const totRes = await fetch(totUrl);
const totJson = await totRes.json();
check("live OpenAlex answers the page's citing-count query",
  totRes.ok && typeof totJson.meta.count === "number",
  totRes.ok ? "count=" + totJson.meta.count : "HTTP " + totRes.status);
const totalCiting = totJson.meta.count;
check("the total citing count is a plausible positive number", totalCiting > 1000, String(totalCiting));

const afterUrl = mod.citingAfterUrl(work.id, v.retractedDate, 5);
const afterRes = await fetch(afterUrl);
const afterJson = await afterRes.json();
check("live OpenAlex answers the page's post-retraction query", afterRes.ok, "HTTP " + afterRes.status);
const recent = afterJson.results || [];
check("the post-retraction query returns records", recent.length === 5, `n=${recent.length}`);
check("every returned citing work really is dated on or after the retraction",
  recent.every(w => w.publication_date >= v.retractedDate),
  recent.map(w => w.publication_date).join(","));
check("results come back newest first, as the page asks for",
  recent.every((w, i) => i === 0 || recent[i - 1].publication_date >= w.publication_date));
check("the post-retraction count is smaller than the total, as arithmetic requires",
  afterJson.meta.count <= totalCiting, `${afterJson.meta.count} <= ${totalCiting}`);

const nomUrl = mod.citingNoMentionUrl(work.id, v.retractedDate);
const nomJson = await (await fetch(nomUrl)).json();
check("live OpenAlex answers the page's 'mentions retraction in the title' query",
  typeof nomJson.meta.count === "number", "count=" + nomJson.meta.count);
check("the title-matching subset is a subset of the post-retraction set",
  nomJson.meta.count <= afterJson.meta.count, `${nomJson.meta.count} <= ${afterJson.meta.count}`);

// --- 5. the model and the renderer -----------------------------------------
const counts = { total: totalCiting, after: afterJson.meta.count, noMention: afterJson.meta.count - nomJson.meta.count, recent };
const model = mod.buildModel({ doi: WAKEFIELD.toLowerCase(), work, crossref, counts });
check("the model carries the retraction date it was given", model.verdict.retractedDate === v.retractedDate);
check("the model computes the share of citations that came after retraction",
  Math.abs(model.shareAfter - counts.after / counts.total) < 1e-9, String(model.shareAfter));
check("the model computes the publication-to-retraction lag in years",
  model.lagYears > 11.5 && model.lagYears < 12.5, String(model.lagYears));

let rendered = "", err = null;
try { rendered = mod.renderReport(model); } catch (e) { err = e; }
check("renderReport runs on live records", !err && rendered.length > 1500, err ? err.message : `${rendered.length} chars`);
check("the rendered report shows the post-retraction number", rendered.includes(counts.after.toLocaleString("en-US")), String(counts.after));
check("the rendered report shows the total citation number", rendered.includes(counts.total.toLocaleString("en-US")));
check("the rendered report links to the retraction notice at its DOI",
  rendered.includes("https://doi.org/" + encodeURIComponent(v.retractions[0].notice)));
check("the rendered report links to each recent citing paper by DOI",
  recent.every(w => {
    const d = (w.doi || "").replace(/^https?:\/\/doi\.org\//i, "");
    return !d || rendered.includes(encodeURIComponent(d));
  }));
check("the rendered report names both registries separately",
  /OpenAlex/.test(rendered) && /Crossref/.test(rendered));

// The page must never make an accusation in its own voice. "fraud" appears in the static page
// only inside the sentence that denies it — so the scan is on the RENDERED report, which is the
// part generated from data rather than written by us.
const accusatory = ["fraud", "fake", "fabricat", "deceiv", "cheat", "discredit", "misconduct", "liar"];
const hits = accusatory.filter(w => new RegExp(w, "i").test(rendered));
check("the data-driven report accuses nobody", hits.length === 0, hits.length ? "found: " + hits.join(", ") : "");
// And the renderer must escape what it prints, since titles come from publishers.
check("publisher titles are HTML-escaped before being rendered",
  mod.renderReport({ ...model, title: "<img src=x onerror=alert(1)>" }).includes("&lt;img src=x onerror=alert(1)&gt;"));
check("recent citing titles are escaped too",
  mod.recentCitationsHtml([{ publication_date: "2026-01-01", display_name: "<b>x</b>", doi: null }]).includes("&lt;b&gt;"));
// A missing title must degrade rather than print "undefined".
check("a record with no title renders a plain placeholder",
  mod.renderReport({ ...model, title: "" }).includes("registries hold no title"));

// --- 6. the negative case: a paper that was never retracted -----------------
const work2 = await (await fetch(mod.openAlexWorkUrl(NEVER_RETRACTED))).json();
const cr2 = (await (await fetch(mod.crossrefWorkUrl(NEVER_RETRACTED))).json()).message;
const v2 = mod.verdictOf(work2, cr2);
check("a never-retracted paper is reported as having no retraction, by both sources",
  v2.anyRecord === false && v2.openAlexFlag === false && v2.crossrefRecords === false,
  JSON.stringify({ any: v2.anyRecord, oa: v2.openAlexFlag, cr: v2.crossrefRecords }));
const m2 = mod.buildModel({ doi: NEVER_RETRACTED, work: work2, crossref: cr2, counts: { total: work2.cited_by_count, after: null, noMention: null, recent: [] } });
const r2 = mod.renderReport(m2);
check("the clean case says 'No retraction on record', not 'not retracted'",
  r2.includes("No retraction on record"), r2.slice(0, 0) + (r2.match(/No retraction on record/) ? "ok" : "missing"));
check("the clean case does not print a post-retraction citation number",
  !/papers published after the retraction/.test(r2));
check("the clean case still reports the total citation count", r2.includes(String(work2.cited_by_count)));

// --- 7. if the DOI handed in is itself the notice ---------------------------
const noticeWork = await (await fetch(mod.openAlexWorkUrl(WAKEFIELD_NOTICE))).json();
const noticeCr = (await (await fetch(mod.crossrefWorkUrl(WAKEFIELD_NOTICE))).json()).message;
const targets = mod.updatedDois(noticeCr);
check("the notice's DOI is read as pointing at the retracted paper",
  targets.some(t => t.doi === WAKEFIELD.toLowerCase()), JSON.stringify(targets.map(t => t.doi)));
const mNotice = mod.buildModel({ doi: WAKEFIELD_NOTICE, work: noticeWork, crossref: noticeCr, counts: { total: null, after: null, noMention: null, recent: [] } });
check("the renderer tells the reader they gave the notice, not the paper",
  /You gave the notice, not the paper/.test(mod.renderReport(mNotice)));
check("the notice's own DOI is not offered as its own target",
  !(mNotice.noticeTargets || []).some(t => t.doi === WAKEFIELD_NOTICE));

// --- 8. the third source: what KIND of document the record says it is ---------
// Europe PMC answers a different question from the other two — not whether the paper was
// retracted, but what the index types the document as. That line was added to the page on
// 2026-09-27 and is the part of the stopped candidate "a claim and its source, side by side"
// judged worth keeping — which is exactly why it needs a check rather than a promise. This
// section exists because the helpers below were exported and never called: the shipped page
// promised a harness, and a harness that does not run is worse than none.
const epmcUrl = mod.epmcSearchUrl(WAKEFIELD.toLowerCase());
check("the Europe PMC query quotes the DOI inside the index's own query language, and asks for the core record",
  epmcUrl.includes(encodeURIComponent('DOI:"' + WAKEFIELD.toLowerCase() + '"')) &&
  epmcUrl.includes("resultType=core") && epmcUrl.includes("pageSize=1"), epmcUrl);

// the pure reader, on the three shapes Europe PMC actually returns
const epmcFound = mod.epmcTypes({ resultList: { result: [{ id: "9500320", source: "MED",
  pubTypeList: { pubType: ["Retracted Publication", "Journal Article"] } }] } });
check("epmcTypes lifts a found record's type list out of the nested payload",
  epmcFound.found === true && epmcFound.types.join("|") === "Retracted Publication|Journal Article",
  JSON.stringify(epmcFound));
check("a single type delivered as a bare string, not an array, is still read as one",
  mod.epmcTypes({ resultList: { result: [{ pubTypeList: { pubType: "Letter" } }] } }).types.join("|") === "Letter");
check("'the index holds it but typed nothing' is distinct from 'the index holds no record'",
  (() => { const held = mod.epmcTypes({ resultList: { result: [{ id: "1" }] } });
           const none = mod.epmcTypes({ resultList: { result: [] } });
           return held.found === true && held.types.length === 0 && none.found === false; })());
check("a record the index types 'Retracted Publication' is recognised by that exact label",
  mod.isRetractedType(epmcFound.types) === true);
check("an ordinary research article is not mistaken for a retracted-record type",
  mod.isRetractedType(["Journal Article", "Research Support, Non-U.S. Gov't"]) === false);

// the same call, live, for the paper the rest of this harness uses
const epmcRes = await fetch(epmcUrl);
check("live Europe PMC answers the page's exact document-type query", epmcRes.ok, "HTTP " + epmcRes.status);
const liveEpmc = mod.epmcTypes(await epmcRes.json());
check("Europe PMC holds the Wakefield paper and types it as a retracted publication",
  liveEpmc.found === true && mod.isRetractedType(liveEpmc.types), "types=" + JSON.stringify(liveEpmc.types));
const mTyped = mod.buildModel({ doi: WAKEFIELD.toLowerCase(), work, crossref, counts, epmc: liveEpmc });
check("the live type list is carried into the model, with the retracted flag set",
  mTyped.epmc.found === true && mTyped.epmc.retracted === true &&
  mTyped.epmc.types.join("|") === liveEpmc.types.join("|"), JSON.stringify(mTyped.epmc));
const rTyped = mod.renderReport(mTyped);
check("the rendered report names the index's own document type",
  rTyped.includes("Europe PMC") && rTyped.includes("Retracted Publication"));
check("the rendered report warns that none of those labels is a study",
  /none of which is a study/.test(rTyped));

// the three states that are NOT 'typed with an answer' must each say so, not print blank
const epmcModel = ep => mod.buildModel({ doi: WAKEFIELD.toLowerCase(), work, crossref, counts, epmc: ep });
check("an index that could not be reached is reported as missing, not as an empty answer",
  /could not be reached/.test(mod.renderReport(epmcModel({ found: false, types: [], unreachable: true }))));
check("a record the index holds but does not type says so, in its own words",
  /publishes no type list/.test(mod.renderReport(epmcModel({ found: true, types: [] }))));
check("an index with no record for the DOI says so, and says that is ordinary",
  /holds no record for this DOI/.test(mod.renderReport(epmcModel({ found: false, types: [] }))));

// the index's labels are strings from outside; they must be escaped like any other
check("document-type labels are HTML-escaped before being rendered",
  mod.renderReport({ ...model, epmc: { found: true, types: ["<img src=x onerror=alert(1)>"], retracted: false, unreachable: false } })
    .includes("&lt;img src=x onerror=alert(1)&gt;"));

// --- 9. the honesty requirements, checked in the shipped HTML ---------------
const pageText = html.replace(/<script[\s\S]*?<\/script>/g, "").replace(/<style[\s\S]*?<\/style>/g, "")
  .replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
check("states that a citation after retraction is not an endorsement",
  /A citation after a retraction is not an endorsement of the paper/.test(pageText));
check("states we do not read the citing papers",
  /does not read citing papers/.test(pageText));
check("states a retraction is not a finding of fraud", /not a finding of fraud/.test(pageText));
check("states the two registries can disagree", /can disagree/.test(pageText));
check("states that 'no retraction on record' is not a clean bill of health",
  /Absence here is not a clean bill of health/.test(pageText));
check("states the counts are of what the databases index, not of the literature",
  /counts are of what these databases index/.test(pageText));
check("states the journal is the authority, not this page", /the journal, the publisher and the notice are the authority/i.test(pageText));
check("names the sources and says the browser queries them directly",
  /OpenAlex/.test(pageText) && /Crossref/.test(pageText) && /queried directly by your browser/.test(pageText));
check("the entry is numbered and dated for the Works index", /entry 8/.test(pageText) && /2026-09-17/.test(pageText));

console.log("\n" + (fail === 0 ? "ALL CHECKS PASSED" : fail + " CHECK(S) FAILED"));
process.exit(fail === 0 ? 0 : 1);
