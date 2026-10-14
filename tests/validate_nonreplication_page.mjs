// Validation harness for docs/works/nonreplication.html — private review checkout, 2026-10-03.
// Runs the page's OWN extracted script against a stub DOM and the two live keyless APIs, so the
// query strings, the p-value parser, the per-study reducer and the aggregation are tested as shipped.
//
//   node tests/validate_nonreplication_page.mjs [docs/works/nonreplication.html]
import fs from "node:fs";

const file = process.argv[2] || "docs/works/nonreplication.html";
const html = fs.readFileSync(file, "utf8");

const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (blocks.length !== 1) { console.error("expected exactly one inline script, got", blocks.length); process.exit(1); }
const code = blocks[0];

// --- minimal DOM stub ------------------------------------------------------
const el = () => ({
  value: "", textContent: "", innerHTML: "", style: {}, id: "", disabled: false,
  addEventListener() {}, querySelectorAll: () => [], appendChild() {}, dataset: {}, getAttribute: () => null,
});
const store = new Map();
globalThis.document = {
  getElementById: id => store.get(id) || (store.set(id, el()), store.get(id)),
  createElement: () => el(),
  querySelectorAll: () => [],
};
globalThis.location = { search: "" };
globalThis.window = {};

let fail = 0;
const check = (name, cond, extra = "") => {
  console.log((cond ? "PASS  " : "FAIL  ") + name + (extra ? "  " + extra : ""));
  if (!cond) fail++;
};

const mod = new Function(code + `
  return { parseP, classifyP, epmcQuery, epmcUrl, ctgovUrl, summarizeStudy, aggregateStudies,
           REPL_PHRASES, NULL_PHRASES, ALL_PHRASES, TRIAL_PAGE, MAX_LIST };
`)();

// --- 1. the p-value parser. The registry prints "=0.7158" for some rows and a bare
//        "0.488" for others; a parser that assumes a bare number drops the prefixed rows.
check('parseP("=0.7158") reads the leading = as the page measured', (() => { const p = mod.parseP("=0.7158"); return p && p.op === "=" && Math.abs(p.num - 0.7158) < 1e-9; })());
check('parseP("0.488") reads a bare number', (() => { const p = mod.parseP("0.488"); return p && p.num === 0.488; })());
check('parseP("<0.0001") keeps the inequality rather than dropping it', (() => { const p = mod.parseP("<0.0001"); return p && p.op === "<" && p.num === 0.0001; })());
check('parseP(">0.999") keeps the inequality', (() => { const p = mod.parseP(">0.999"); return p && p.op === ">"; })());
check("an empty or missing p-value is null, not zero", mod.parseP("") === null && mod.parseP(null) === null && mod.parseP(undefined) === null);
check('free text is refused rather than coerced', mod.parseP("not reported") === null && mod.parseP("NA") === null);

// --- 2. the classifier: reached / didnot / indeterminate. 0.05 is the conventional line
check("a p-value below 0.05 is 'reached'", mod.classifyP(mod.parseP("0.04")) === "reached");
check("exactly 0.05 is 'didnot' — the conventional line is p<0.05, not p<=0.05", mod.classifyP(mod.parseP("0.05")) === "didnot");
check("above 0.05 is 'didnot'", mod.classifyP(mod.parseP("0.71")) === "didnot");
check('"<0.001" is reached (the whole interval is below the line)', mod.classifyP(mod.parseP("<0.001")) === "reached");
check('">0.05" is didnot', mod.classifyP(mod.parseP(">0.05")) === "didnot");
check("no p-value is its own bucket, not a 'reached'", mod.classifyP(null) === "none");

// --- 3. one study: only PRIMARY outcomes count, and a missing p-value is counted, not dropped
const study = {
  protocolSection: { identificationModule: { nctId: "NCT00000001", briefTitle: "A trial" } },
  resultsSection: { outcomeMeasuresModule: { outcomeMeasures: [
    { type: "PRIMARY", title: "p1", analyses: [{ pValue: "=0.7158" }] },
    { type: "PRIMARY", title: "p2", analyses: [{ pValue: "0.03" }] },
    { type: "PRIMARY", title: "p3", analyses: [] },                        // printed no p-value
    { type: "SECONDARY", title: "s1", analyses: [{ pValue: "0.9" }] },     // not primary: ignored
  ] } }
};
const r = mod.summarizeStudy(study);
check("only PRIMARY outcomes are read (secondary is ignored)", r.primary === 3, "primary=" + r.primary);
check("a primary outcome with no p-value is counted in 'none', not dropped", r.none === 1, "none=" + r.none);
check("the printed p-values split into reached/didnot correctly", r.reached === 1 && r.didnot === 1, "reached=" + r.reached + " didnot=" + r.didnot);
check("withP + none equals the primary count (no silent loss)", r.withP + r.none === r.primary);
check("the study id is carried through for the card", r.nct === "NCT00000001");

const agg = mod.aggregateStudies([r, mod.summarizeStudy({ resultsSection: { outcomeMeasuresModule: { outcomeMeasures: [] } } })]);
check("aggregate counts studies, not outcomes, for the study total", agg.studies === 2);
check("aggregate flags a study with a non-significant primary outcome", agg.studiesWithNonSignificant === 1, "n=" + agg.studiesWithNonSignificant);
check("aggregate preserves the parts (primary = withP + none)", agg.withP + agg.none === agg.primary);

// --- 4. the query strings the page actually sends
check("phrases are a title phrase, not title-or-abstract", mod.epmcQuery("failure to replicate", "") === 'TITLE:"failure to replicate"');
check("a topic is ANDed inside parentheses", mod.epmcQuery("failure to replicate", "depression") === 'TITLE:"failure to replicate" AND (depression)');
check("a double quote in the phrase cannot break the query", mod.epmcQuery('a"b', "") === 'TITLE:"ab"');
const eu = mod.epmcUrl(mod.epmcQuery("failed to replicate", "chronic fatigue"), 8, true);
check("the literature request asks for JSON and a page size", eu.includes("format=json") && eu.includes("pageSize=8"));
check("the title-list request asks for core records (author/journal/year)", eu.includes("resultType=core"));
check("the count request does NOT ask for core (cheap counts)", !mod.epmcUrl(mod.epmcQuery("null results", "x"), 1, false).includes("resultType=core"));

const cu = mod.ctgovUrl("pancreatic cancer");
check("the trial request filters to studies with posted results", /HasResults/.test(decodeURIComponent(cu)));
check("the trial request asks for the total", cu.includes("countTotal=true"));
check("the trial request asks for the results section AND the id", /ResultsSection/.test(decodeURIComponent(cu)) && /NCTId/.test(decodeURIComponent(cu)));
check("the trial request is bounded to one page", decodeURIComponent(cu).includes("pageSize=" + mod.TRIAL_PAGE));

// --- 5. the two phrase families are kept apart and never overlapped
const overlap = mod.REPL_PHRASES.filter(p => mod.NULL_PHRASES.includes(p));
check("no phrase appears in both families (they could be summed by accident)", overlap.length === 0, overlap.join(","));
check("the replication family is the four claim-making phrases", mod.REPL_PHRASES.length === 4 && mod.ALL_PHRASES.length === mod.REPL_PHRASES.length + mod.NULL_PHRASES.length);

// --- 6. live: the two records answer, in the shape the page parses ------------------
console.log("\n--- live checks (public, keyless APIs) ---");
try {
  const tj = await (await fetch(mod.ctgovUrl("pancreatic cancer"))).json();
  const studies = (tj.studies || []).map(mod.summarizeStudy);
  const la = mod.aggregateStudies(studies);
  check("ClinicalTrials.gov answers with studies", studies.length > 0, "n=" + studies.length);
  check("the registry returns a total count for the condition", typeof tj.totalCount === "number" && tj.totalCount > 0, "total=" + tj.totalCount);
  check("every study read preserves primary = withP + none", studies.every(s => s.withP + s.none === s.primary));
  console.log("       live sample: " + la.studies + " studies, " + la.primary + " primary outcomes, " +
              la.withP + " with a p-value (" + la.none + " without), " + la.didnot + " did not reach, " +
              la.reached + " reached, " + la.indeterminate + " indeterminate");
} catch (e) {
  check("ClinicalTrials.gov reachable from this harness", false, String(e && e.message || e));
}
try {
  const eu = mod.epmcUrl(mod.epmcQuery("failure to replicate", "depression"), 1, false);
  const ej = await (await fetch(eu)).json();
  check("Europe PMC answers a title-scoped query", typeof ej.hitCount === "number", "hitCount=" + ej.hitCount);
  check("a known replication phrase with a real topic returns works", ej.hitCount > 0, "depression=" + ej.hitCount);
  const zu = mod.epmcUrl(mod.epmcQuery("failure to replicate", "nutrition"), 1, false);
  const zj = await (await fetch(zu)).json();
  console.log("       coverage gradient (recorded in the queue file): failure-to-replicate titles — depression=" +
              ej.hitCount + ", nutrition=" + zj.hitCount);
} catch (e) {
  check("Europe PMC reachable from this harness", false, String(e && e.message || e));
}

console.log("");
if (fail) { console.log(fail + " FAILED"); process.exit(1); }
console.log("validate_nonreplication_page: ALL CHECKS PASSED");
