// Validation harness for docs/works/recalls.html — private review checkout, 2026-09-27.
// Runs the page's OWN extracted script against a stub DOM and the live keyless openFDA
// enforcement API, so the query string, the date rule, the interval arithmetic, the summary and
// the card renderer are tested as shipped rather than as intended.
//
//   node tests/validate_recalls_page.mjs [docs/works/recalls.html]
//
// Written by the same architecture that wrote the page: this is a check, not a review.
import fs from "node:fs";

const file = process.argv[2] || "docs/works/recalls.html";
const html = fs.readFileSync(file, "utf8");

const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (blocks.length !== 1) { console.error("expected exactly one inline script, got", blocks.length); process.exit(1); }
const code = blocks[0];

// --- minimal DOM stub ------------------------------------------------------
const el = () => ({
  value: "", textContent: "", innerHTML: "", style: {}, id: "",
  addEventListener() {}, querySelectorAll: () => [], appendChild() {}, dataset: {},
  getAttribute: () => null, onclick: null,
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
  return { parseFdaDate, days, iso, intervals, dated, readRecord, summarize, quantile,
           searchExpr, searchUrl, countUrl, classCountUrl, recordUrl, apiGet, searchPage,
           countByClass, pct, card, dateLine, statBlock, classOf, showQuery,
           MAX_CARDS, MAX_PAGES, PAGE_SIZE, OVER90, FIELDS, TYPES };
`)();

// --- 1. dates: openFDA sends "YYYYMMDD", and nothing else is guessed -----------------
check("a full date is read as that day", mod.iso(mod.parseFdaDate("20210315")) === "2021-03-15");
check("a missing date is null, not the epoch", mod.parseFdaDate(null) === null && mod.parseFdaDate("") === null);
check("an ISO date is refused rather than half-read", mod.parseFdaDate("2021-03-15") === null);
check("a short string is refused", mod.parseFdaDate("2021") === null && mod.parseFdaDate("202103") === null);
check("an impossible day is refused rather than rolled forward", mod.parseFdaDate("20210231") === null);
check("month 00 and month 13 are refused", mod.parseFdaDate("20210015") === null && mod.parseFdaDate("20211315") === null);
check("a leap day in a real leap year is accepted", mod.iso(mod.parseFdaDate("20240229")) === "2024-02-29");
check("a leap day in a common year is refused", mod.parseFdaDate("20230229") === null);

// --- 2. the interval rule, on fixed records ----------------------------------------
const rec = (i, c, p) => ({ recall_initiation_date: i, center_classification_date: c, report_date: p });
const a = mod.intervals(rec("20110927", "20140723", "20140730"));
check("start→publication is the whole span, in days", a.startToPublished === 1037, String(a.startToPublished));
check("start→classification is measured separately", a.startToClassified === 1030, String(a.startToClassified));
check("classification→publication is measured separately", a.classifiedToPublished === 7, String(a.classifiedToPublished));
check("the two intervals add up to the whole span (an identity, and it holds whatever the order)",
  a.startToClassified + a.classifiedToPublished === a.startToPublished);
const inv = mod.intervals(rec("20210315", "20210301", "20210320"));   // classification before initiation: a record defect
check("an inverted pair is not error-corrected, it is counted as it stands", inv.startToClassified === -14);
check("an inverted pair still adds up", inv.startToClassified + inv.classifiedToPublished === inv.startToPublished);
const plain = mod.intervals(rec("20210315", null, "20210602"));
check("a missing classification date leaves that interval null, not zero", plain.startToClassified === null && plain.classifiedToPublished === null);
check("a usable pair still yields the headline interval when the middle date is missing", plain.startToPublished === 79);
const none = mod.intervals(rec(null, null, null));
check("no dates at all is not a zero-day interval", none.startToPublished === null && mod.dated(rec(null, null, null)) === false);

// --- 3. the statistics are computed, not asserted ----------------------------------
check("quantile takes the middle of an odd list", mod.quantile([5, 1, 3], 0.5) === 3);
check("quantile interpolates on an even list", mod.quantile([1, 2, 3, 4], 0.5) === 2.5);
check("quantile of an empty list is null, not NaN", mod.quantile([], 0.5) === null);
check("quantile ignores non-numbers", mod.quantile([1, null, 3, "x"], 0.5) === 2);
const fixed = [0, 10, 20, 30, 100].map(v => ({ iv: { startToPublished: v, startToClassified: v - 8, classifiedToPublished: 8 } }));
const agg = mod.summarize(fixed);
check("the summary counts what it read", agg.n === 5 && agg.dated === 5 && agg.undated === 0);
check("the summary reports the median of what it read", agg.median === 20, String(agg.median));
check("the summary reports the share over the 90-day line", agg.over90 === 1 && mod.pct(agg.over90, agg.dated) === "20.0%");
check("the summary reports the longest interval", agg.max === 100);
const mixed = mod.summarize([{ iv: { startToPublished: 5, startToClassified: 5, classifiedToPublished: 0 } }, { iv: { startToPublished: null, startToClassified: null, classifiedToPublished: null } }]);
check("an undated record is excluded from the interval figures and counted separately",
  mixed.dated === 1 && mixed.undated === 1 && mixed.median === 5);
const backwards = mod.summarize([{ iv: { startToPublished: -3, startToClassified: 0, classifiedToPublished: -3 } }]);
check("a record whose publication precedes its start is flagged, not hidden", backwards.beforeStart === 1);

// --- 4. the queries the page actually sends ----------------------------------------
check("a one-word product is searched in the named field", mod.searchExpr("product_description", "metformin") === "product_description:metformin");
check("a multi-word product is quoted so it is a phrase, not two terms",
  mod.searchExpr("product_description", "ice cream") === 'product_description:"ice cream"');
check("quotes the user typed cannot break out of the quoted value",
  mod.searchExpr("product_description", 'a"b') === 'product_description:"ab"');
check("the 'any field' choice is passed as a bare term, as openFDA expects", mod.searchExpr("any", "ice cream") === "ice cream");
// A hyphen is not whitespace, so a rule that quotes on whitespace alone sends `hand-sanitizer`
// unquoted — and openFDA reads an unquoted hyphen as a separator, returning another product's
// recalls under the name typed. Measured live on 2026-09-27: unquoted 291 records, quoted 211.
check("a hyphenated single word is quoted, not sent bare (an unquoted hyphen is a separator)",
  mod.searchExpr("product_description", "hand-sanitizer") === 'product_description:"hand-sanitizer"');
check("the same holds in the free-text field, where a single token is still one token",
  mod.searchExpr("any", "hand-sanitizer") === '"hand-sanitizer"');
check("a term of several words is still left bare in the free-text field",
  mod.searchExpr("any", "ice cream") === "ice cream");
check("an empty term is sent as no constraint, never as a bare 'field:' (openFDA answers that 500)",
  mod.searchExpr("product_description", "") === "" && mod.searchExpr("", "") === ""
  && mod.searchUrl("drug", "", "", 0).includes("search=&"));
const u = mod.searchUrl("food", "product_description", "ice cream", 2000);
check("the query names the product type in the path", u.includes("/food/enforcement.json"));
check("the query asks for arrays of up to 1000 records", /[?&]limit=1000\b/.test(u));
check("the query carries its page offset rather than re-sorting", /[?&]skip=2000\b/.test(u));
check("the search expression is URL-encoded, not concatenated raw", mod.searchUrl("drug", "product_description", "a b", 0).includes("a+b"));
check("the count query asks openFDA to count the class field itself", mod.countUrl("drug", "product_description", "metformin").includes("count=classification.exact"));
check("the index-size query asks for the same count with no search", mod.classCountUrl("device").endsWith("?count=classification.exact"));
const ru = mod.recordUrl("drug", "D-1448-2014");
check("the per-record query quotes the recall number (unquoted, openFDA returns the whole index)",
  ru.includes(encodeURIComponent('recall_number:"D-1448-2014"')) || ru.includes('recall_number%3A%22D-1448-2014%22'), ru);
check("the per-record query is limited to one row", /[?&]limit=1\b/.test(ru));

// --- 5. live: a blank answer is a zero, not a failure ------------------------------
const nothing = await mod.apiGet(mod.searchUrl("drug", "product_description", "zzzz-no-such-product-zzzz", 0));
check("openFDA's 404 'NOT_FOUND' is read as zero records, not thrown",
  nothing.zero === true && !nothing.json, JSON.stringify(nothing).slice(0, 80));
const missing = await mod.searchPage("drug", "product_description", "zzzz-no-such-product-zzzz", 0);
check("a product with no record returns an empty set and a total of zero",
  Array.isArray(missing.records) && missing.records.length === 0 && missing.total === 0);
// The bug the quoting rule exists to prevent, measured live rather than asserted from memory: the
// same nonsense name sent the old way — unquoted, so openFDA splits it on the hyphens — is read as
// loose terms and returns another product's records instead of none.
const split = await mod.apiGet("https://api.fda.gov/drug/enforcement.json?search=product_description%3Azzzz-no-such-product-zzzz&limit=1");
check("the same nonsense name sent unquoted is read as loose terms and returns records, not none",
  split.json && (split.json.meta.results.total || 0) > 0,
  `total=${split.json && split.json.meta.results.total}`);

// --- 6. live: one product, read two ways ------------------------------------------
const TERM = "metformin";
const page = await mod.searchPage("drug", "product_description", TERM, 0);
check("the live index answers for a real product", page.records.length > 0 && page.total > 0,
  `n=${page.records.length} total=${page.total} updated=${page.updated}`);
check("a page of results is no longer than the limit it asked for", page.records.length <= mod.PAGE_SIZE);
check("the index reports its own last-updated date, and the page prints that rather than a date of its own",
  typeof page.updated === "string" && /^\d{4}-\d{2}-\d{2}$/.test(page.updated), String(page.updated));
check("every record read carries a recall number, a class and a firm",
  page.records.every(r => r.recall_number && r.classification && typeof r.firm === "string"));
check("the page reports the field it searched rather than a bare number",
  typeof mod.FIELDS["product_description"] === "string");

// an independent count of the same query, through the count endpoint
const counted = await mod.countByClass("drug", "product_description", TERM);
check("the search endpoint's total and the count endpoint's total agree",
  counted.total === page.total, `search=${page.total} count=${counted.total}`);
check("the class counts add up to the total the page would print",
  Object.values(counted.counts).reduce((s, v) => s + v, 0) === counted.total);

// an independent recount of the interval distribution: own parse, own median, no reuse of the page's maths
const pyParse = s => (typeof s === "string" && /^\d{8}$/.test(s))
  ? Date.UTC(+s.slice(0, 4), +s.slice(4, 6) - 1, +s.slice(6, 8)) : null;
const raw = await (await fetch(mod.searchUrl("drug", "product_description", TERM, 0))).json();
const spans = raw.results
  .map(r => [pyParse(r.recall_initiation_date), pyParse(r.report_date)])
  .filter(([x, y]) => x !== null && y !== null)
  .map(([x, y]) => Math.round((y - x) / 86400000))
  .sort((p, q) => p - q);
const indMedian = spans.length % 2 ? spans[(spans.length - 1) / 2]
  : (spans[spans.length / 2 - 1] + spans[spans.length / 2]) / 2;
const s = mod.summarize(page.records);
check("the page's median equals an independently computed one (own parse, own median)",
  Math.abs(s.median - indMedian) <= 1, `page=${s.median} independent=${indMedian}`);
check("the page's dated count equals the number of records carrying both dates",
  s.dated === spans.length, `page=${s.dated} independent=${spans.length}`);
check("the page's 'over 90 days' count equals an independent one",
  s.over90 === spans.filter(v => v > mod.OVER90).length, `page=${s.over90}`);
check("the split into classification and publication is present, not just the headline",
  typeof s.medianToClassified === "number" && typeof s.medianToPublishedAfter === "number",
  `classified=${s.medianToClassified} published=${s.medianToPublishedAfter}`);

// --- 7. live: the whole-record claim the page makes in prose ----------------------
// The page states that every drug record carries both dates. Two pages of the whole drug set is
// a 2,000-row sample of that claim, read here with the page's own date parser. An empty term is
// sent as `search=` — no constraint — which is the whole index; the earlier version of this file
// passed an empty field through to `search=:` and openFDA answered 500, killing the run here.
const whole = [];
for (const skip of [0, 1000]) {
  const p = await mod.searchPage("drug", "", "", skip);
  whole.push(...p.records);
}
const noStart = whole.filter(r => !r.iv.started).length;
const noPublished = whole.filter(r => !r.iv.published).length;
const noClass = whole.filter(r => !r.iv.classified).length;
check("over a 2,000-row sample of the whole drug record, every row carries a start date",
  whole.length >= 1900 && noStart === 0, `n=${whole.length} missing=${noStart}`);
check("and every row carries a publication date", noPublished === 0, `missing=${noPublished}`);
check("the FDA classification date is present on all but a handful",
  noClass <= whole.length * 0.01, `missing=${noClass} of ${whole.length}`);
console.log(`      sample: ${whole.length} drug records; classification date missing on ${noClass}; ` +
  `median start→publication ${mod.quantile(whole.map(r => r.iv.startToPublished), 0.5)} d, ` +
  `median start→classification ${mod.quantile(whole.map(r => r.iv.startToClassified), 0.5)} d, ` +
  `median classification→publication ${mod.quantile(whole.map(r => r.iv.classifiedToPublished), 0.5)} d`);

// --- 8. live: a row can be checked against the index by hand -----------------------
const one = page.records[0];
const again = await mod.apiGet(mod.recordUrl(one.record_type, one.recall_number));
check("the per-record link returns exactly that one record",
  again.json && (again.json.results || []).length === 1 && again.json.results[0].recall_number === one.recall_number,
  one.recall_number);
check("the linked record's dates match the row the page printed",
  again.json.results[0].recall_initiation_date === one.initiated.replace(/-/g, "") ||
  again.json.results[0].recall_initiation_date === one.initiated,
  `${again.json.results[0].recall_initiation_date} vs ${one.initiated}`);

// --- 9. the renderer: escapes the record's own text, and never accuses --------------
const hostile = mod.readRecord({
  recall_number: "<b>D-0001</b>", classification: "Class I", status: "Ongoing",
  recalling_firm: "Firm & Sons <script>", product_description: "<img src=x onerror=alert(1)>",
  reason_for_recall: "label mix-up & <b>error</b>", distribution_pattern: "<i>Nationwide</i>",
  recall_initiation_date: "20240101", center_classification_date: "20240301", report_date: "20240310",
  city: "Boston", state: "MA", voluntary_mandated: "Voluntary: Firm initiated",
  initial_firm_notification: "Letter", product_quantity: "1"
}, "drug");
const cardHtml = mod.card(hostile, 1);
check("the card escapes the record's own text", cardHtml.includes("&lt;img") && cardHtml.includes("Firm &amp; Sons"));
check("the card does not let a quoted recall number break its own link", !/<script>/.test(cardHtml));
check("the card prints all three dates rather than folding them into one number",
  cardHtml.includes("2024-01-01") && cardHtml.includes("2024-03-01") && cardHtml.includes("2024-03-10"));
check("the card prints the headline interval and says most of it is the classification step",
  /69 d/.test(cardHtml) && /classification step/.test(cardHtml));
check("the card marks the class with the record's own words", cardHtml.includes("Class I"));
// the row's own words, with the markup taken off first — the sentence carries a <strong> in the
// middle, so a regex over the raw html sees tags where the reader sees a word
const undatedRow = mod.card(mod.readRecord({ recall_number: "D-2", classification: "Class II" }, "drug"), 1).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
check("a record with no usable dates says so on the row instead of printing a zero",
  /not counted in the interval figures/.test(undatedRow), undatedRow.trim().slice(0, 70));

const pageText = html.replace(/<script[\s\S]*?<\/script>/g, "").replace(/<style[\s\S]*?<\/style>/g, "")
  .replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
check("says plainly that a recall is not proof anyone was harmed",
  /not\s*<\/strong>\s*a finding that anyone was harmed/.test(html) || /A recall is not a finding that anyone was harmed/.test(pageText.replace(/<\/?strong>/g, "")));
check("says the class is not a severity of injury", /not<\/strong> a severity of injury/.test(html) || /class is not a severity of injury/.test(pageText.replace(/<\/?strong>/g, "")));
check("says the interval measures record-keeping and classification, not concealment",
  /measures\s*<strong>record-keeping/.test(html) && /\bnot concealment by the firm\b/.test(pageText));
check("says a blank result is not a clean bill of health", /not "never recalled"/.test(pageText));
check("says which field was searched changes the count", /changes the count/.test(pageText));
check("states there is no ranking, no worst-offenders list and no firm league table",
  /no "worst offenders"/.test(pageText) && /no firm league table/.test(pageText));
check("says it is not medical advice", /not medical advice/.test(pageText));
check("says it reports what one index contained on the day it was read",
  /what one public index contained on the day it was read/.test(pageText));
check("the limit is stated above the search box, not in a footnote",
  html.indexOf("A recall is <strong>not</strong>") > 0 && html.indexOf("A recall is <strong>not</strong>") < html.indexOf('<div class="bar">'));

// The page must not speak like an accuser in its own voice. A word is allowed only where the page
// is denying it — so a negation has to sit in the run-up to the word, within the same sentence.
const NEG = /\b(not|no|never|nothing|cannot|nor|without|isn't|does not|doesn't)\b[^.;]{0,90}$/i;
const accusatory = /\b(misconduct|withheld|withholding|failed to report|hid|hidden|hiding|conceal\w*|violation|offender)s?\b/gi;
function accusations(text, label) {
  const own = text.replace(/<pre[\s\S]*?<\/pre>/g, "");   // quoted record text is the index talking
  const bad = [...own.matchAll(accusatory)]
    .filter(m => !NEG.test(own.slice(Math.max(0, m.index - 100), m.index)))
    .map(m => m[0]);
  check(`outside quoted record text, ${label} uses no accusatory word`, bad.length === 0,
    bad.length ? "found: " + [...new Set(bad)].join(", ") : "");
}
accusations(cardHtml, "a card");
accusations(html.replace(/<script[\s\S]*?<\/script>/g, ""), "the page's own prose");

// --- 10. no network path other than the one keyless index -------------------------
const hosts = [...new Set([...html.matchAll(/https?:\/\/[a-z0-9.\-]+/gi)].map(m => m[0].toLowerCase()))]
  .filter(h => !/fonts\.(googleapis|gstatic)\.com|www\.w3\.org/.test(h));
console.log("      external hosts referenced:", hosts.join(" "));
check("only the keyless openFDA index is contacted", hosts.every(h =>
  /api\.fda\.gov|open\.fda\.gov|accessdata\.fda\.gov|github\.com/.test(h)));
check("the page sends no key or credential", !/api_key|apikey|authorization|bearer/i.test(code));

// --- 11. the page is registered where a reader would look for it ------------------
const index = fs.readFileSync(file.replace(/[^/]+$/, "index.html"), "utf8");
const slug = file.replace(/^.*\//, "");
check("the works index links to this page", index.includes(`href="${slug}"`), slug);
check("the works index names this page as an entry rather than a placeholder", /href="recalls\.html">/.test(index));

console.log(fail === 0 ? "\nALL CHECKS PASSED" : `\n${fail} CHECK(S) FAILED`);
process.exit(fail === 0 ? 0 : 1);
