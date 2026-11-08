// The boundary the retraction page's voice guard rests on, tested field by field: 2026-11-08.
//
// The guard (tests/retraction_voice.mjs) treats text inside a publisher marker as a quotation and
// everything else as our own voice. That works only if EVERY publisher-supplied string is wrapped
// at the renderer. The previous two repairs each fixed the fields somebody had remembered:
// a journal name (2026-11-08, morning), then the queried paper's title and venue (Tarik, 0b94c3be).
// Both times the class came back wearing a different field.
//
// So this test does not name one field. It takes every field of the rendered report that comes from
// a registry and puts an accusatory word in it, one at a time, and then all at once. Any field the
// renderer prints unquoted fails here by name, which is the point: the next field nobody thought of
// is the one that goes red, not the one that goes quiet.
import fs from "node:fs";
import assert from "node:assert/strict";
import { scanVoice } from "./retraction_voice.mjs";

globalThis.fetch = () => { throw new Error("This suite must not call a registry"); };
const html = fs.readFileSync(new URL("../docs/works/retraction.html", import.meta.url), "utf8");
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
assert.equal(blocks.length, 1, "the page must have exactly one inline script");
const el = () => ({ value: "", textContent: "", innerHTML: "", style: {}, dataset: {},
  addEventListener() {}, querySelectorAll: () => [], appendChild() {} });
globalThis.document = { getElementById: el, createElement: el, querySelectorAll: () => [] };
globalThis.location = { search: "" };
const page = new Function(blocks[0] + "\nreturn { renderReport, buildModel, recentCitationsHtml };")();

let checks = 0;
const check = (name, fn) => { fn(); checks++; console.log("PASS " + name); };

// A word our guard is supposed to catch, used as the value a registry hands us.
const BAD = "fraud";

const baseWork = () => ({ display_name: "A neutral title", publication_date: "2026-10-22",
  publication_year: 2026, cited_by_count: 3, is_retracted: true, doi: "10.1000/example",
  primary_location: { source: { display_name: "A neutral journal" } }, counts_by_year: [] });
const baseCrossref = () => ({ "updated-by": [{ type: "retraction", DOI: "10.1000/notice",
  source: "Crossref", updated: { "date-parts": [[2026, 1, 2]] } }], "update-to": [] });
const baseCounts = () => ({ total: 5, after: 2, noMention: 1, recent: [
  { display_name: "A neutral recent title", publication_date: "2026-10-01", doi: "10.1000/recent",
    primary_location: { source: { display_name: "A neutral venue" } } }] });
const baseEpmc = () => ({ found: true, types: ["Journal Article"] });

// Render the whole report with one registry field replaced by the accusatory word.
function render(patch) {
  const work = baseWork(), crossref = baseCrossref(), counts = baseCounts(), epmc = baseEpmc();
  const input = { doi: "10.1000/example", work, crossref, counts, epmc };
  patch(input);
  const model = page.buildModel(input);
  return page.renderReport(model);
}

const FIELDS = {
  "the queried DOI": p => p.doi = "10.1000/" + BAD,
  "the queried publication year": p => p.work.publication_year = BAD,
  "the retraction date parts": p => p.crossref["updated-by"][0].updated["date-parts"] = [[BAD, 1, 2]],
  "the concern notice DOI": p => p.crossref["updated-by"].push({type:"expression-of-concern", DOI:"10.1000/" + BAD, updated:{"date-parts":[[2026,1,2]]}}),
  "the concern date parts": p => p.crossref["updated-by"].push({type:"expression-of-concern", DOI:"10.1000/concern", updated:{"date-parts":[[BAD,1,2]]}}),
  "the original-paper DOI offered by a notice": p => p.crossref["update-to"] = [{type:"retraction",DOI:"10.1000/" + BAD}],
  "the queried paper's title":              p => p.work.display_name = BAD,
  "the queried paper's venue":              p => p.work.primary_location.source.display_name = BAD,
  "the queried paper's publication date":   p => p.work.publication_date = BAD,
  "the retraction notice's DOI":            p => p.crossref["updated-by"][0].DOI = "10.1000/" + BAD,
  "the name recorded as the notice's source": p => p.crossref["updated-by"][0].source = BAD,
  "the index's document-type label":        p => p.epmc.types = [BAD],
  "a citing paper's title":                 p => p.counts.recent[0].display_name = BAD,
  "a citing paper's venue":                 p => p.counts.recent[0].primary_location.source.display_name = BAD,
  "a citing paper's publication date":      p => p.counts.recent[0].publication_date = BAD,
  "a citing paper's DOI":                   p => p.counts.recent[0].doi = "10.1000/" + BAD,
};

for (const [name, patch] of Object.entries(FIELDS)) {
  check("a publisher's accusatory " + name + " is a quotation, not our voice", () => {
    assert.deepEqual(scanVoice(render(patch)), [],
      "the renderer prints " + name + " unquoted, so the page reads a publisher's word as ours");
  });
}

check("every registry field accusatory at once still accuses nobody", () => {
  const all = render(p => Object.values(FIELDS).forEach(patch => patch(p)));
  assert.deepEqual(scanVoice(all), []);
});

// --- the guard must still have teeth, or the checks above would pass on a page that renders nothing
check("our own sentence still fails the scan", () => {
  const own = render(() => {}) + `<p>The authors fabricated these data.</p>`;
  assert(scanVoice(own).includes("fabricat"));
});
check("our own linked prose still fails the scan", () => {
  const own = render(() => {}) + `<p>See <a href="evidence.html">fraud</a>.</p>`;
  assert(scanVoice(own).includes("fraud"));
});
check("a registry title cannot smuggle a closing tag out of its quotation", () => {
  const hostile = page.recentCitationsHtml([{ display_name: "</span><p>fabricated</p>", doi: null }]);
  assert(!hostile.includes("<p>fabricated"));
  assert(hostile.includes("&lt;/span&gt;"));
});

check("a hostile publication year is escaped inside its quotation", () => {
  const html = render(p => p.work.publication_year = '</span><script>fraud</script>');
  assert(html.includes('&lt;script&gt;fraud&lt;/script&gt;'));
  assert(!html.includes('<script>fraud</script>'));
  assert.deepEqual(scanVoice(html), []);
});
check("hostile Crossref date parts remain escaped", () => {
  const html = render(p => p.crossref["updated-by"][0].updated["date-parts"] = [['</span><b>fraud</b>',1,2]]);
  assert(html.includes('&lt;b&gt;fraud&lt;/b&gt;'));
  assert(!html.includes('<b>fraud</b>'));
  assert.deepEqual(scanVoice(html), []);
});
check("quoting an original DOI preserves its button target", () => {
  const html = render(p => p.crossref["update-to"] = [{DOI:"10.1000/fraud",type:"retraction"}]);
  assert(html.includes('<button data-doi="10.1000/fraud"><span data-publisher-quote>10.1000/fraud</span></button>'));
});
console.log(checks + " boundary checks passed; no registry requests");
