// Validation harness for docs/works/air.html — 2026-10-03.
//
// Why this exists. The page tells a reader what is in the air and how it compares to a health
// limit, so two kinds of error matter: printing a guideline number that is not the WHO's, and
// getting the comparison itself wrong (calling polluted air clean, or the reverse). Both are
// checkable with no network:
//
//   1. The WHO guideline values embedded in the page must equal the ones in
//      docs/works/air-quality-sources.json, which carry the date they were checked — so a
//      threshold cannot be edited on the page alone.
//   2. Those JSON values must themselves equal the WHO's published 2021 numbers, hard-coded
//      here, so the sources file is pinned too and not merely self-consistent.
//   3. The page's own comparison functions (timesGuideline / whoVerdict / comparables) are run
//      directly and must give the right answer for each case, including the honest blanks: a
//      missing reading is "unknown", never a zero.
//   4. The demonstration table — the page's central claim that the two indexes disagree — must
//      actually contain a row where they disagree, rather than asserting it in prose.
//
// Same shape as tests/validate_food_safety_page.mjs and tests/validate_ors_calculator.mjs: the
// page's OWN inline script runs against a stub DOM. Offline, so it can run on every landing.
//
// Run: node tests/validate_air_quality_page.mjs
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const html = fs.readFileSync(path.join(root, "docs/works/air.html"), "utf8");
const sources = JSON.parse(fs.readFileSync(path.join(root, "docs/works/air-quality-sources.json"), "utf8"));

let pass = 0, fail = 0;
const ok = (cond, label, extra = "") => {
  if (cond) { pass++; console.log("  ok   " + label); }
  else { fail++; console.log("  FAIL " + label + (extra ? "  [" + extra + "]" : "")); }
};
const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// --- 1. exactly one inline script, and it is the source of every printed number -------------
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
ok(blocks.length === 1, "exactly one inline script", "got " + blocks.length);
const code = blocks[0];
ok(!/<script[^>]*\bsrc=/.test(html), "no external script — the page is self-contained");

// --- 2. run the page's own script against a stub DOM ----------------------------------------
const cache = new Map();
function stubEl(id) {
  if (!cache.has(id)) {
    const children = [];
    const node = {
      id, value: "", textContent: "", innerHTML: "", className: "", style: {}, hidden: false, disabled: false,
      classList: { contains: () => false, add() {}, remove() {} },
      addEventListener() {},
      appendChild(c) { children.push(c); return c; },
      querySelector() { return stubEl(id + "::child"); },
      get children() { return children; },
    };
    cache.set(id, node);
  }
  return cache.get(id);
}
const document = {
  getElementById: (id) => stubEl(id),
  createElement: (tag) => stubEl("created:" + tag + ":" + Math.random()),
  body: { classList: { contains: () => false, add() {}, remove() {} } },
};

let runtime;
try {
  runtime = new Function("document",
    code + "\nreturn { WHO_GUIDELINES, EXAMPLES, EXAMPLES_DATE, GUIDELINE_SOURCE, timesGuideline, whoVerdict, comparables };"
  )(document);
} catch (e) {
  console.log("  FAIL the page's inline script did not even evaluate: " + e.message);
  process.exit(1);
}
ok(typeof runtime.whoVerdict === "function", "the page's own whoVerdict was captured");
ok(typeof runtime.timesGuideline === "function", "the page's own timesGuideline was captured");
ok(typeof runtime.comparables === "function", "the page's own comparables was captured");

// --- 3. the page's constants equal the pinned sources file ----------------------------------
ok(eq(runtime.WHO_GUIDELINES, sources.who_guidelines),
  "the page's WHO guideline values equal docs/works/air-quality-sources.json");
ok(eq(runtime.EXAMPLES, sources.demonstration.examples),
  "the page's demonstration table equals the measured examples in the sources file");
ok(runtime.EXAMPLES_DATE === sources.demonstration.date,
  "the page's example date equals the sources file's date",
  runtime.EXAMPLES_DATE + " vs " + sources.demonstration.date);

// --- 4. the sources file itself equals the WHO's published 2021 numbers ---------------------
// Hard-coded here so pinning the page to the JSON cannot pin it to a wrong JSON.
const WHO_PUBLISHED = {
  pm2_5:            { average: "24-hour", value: 15, annual: 5 },
  pm10:             { average: "24-hour", value: 45, annual: 15 },
  ozone:            { average: "8-hour",  value: 100, annual: null },
  nitrogen_dioxide: { average: "24-hour", value: 25, annual: 10 },
  sulphur_dioxide:  { average: "24-hour", value: 40, annual: null },
};
for (const [p, expected] of Object.entries(WHO_PUBLISHED)) {
  const got = sources.who_guidelines[p];
  ok(!!got, "sources file holds a guideline for " + p);
  if (!got) continue;
  ok(got.value === expected.value, "WHO 24-hr/8-hr value for " + p + " is " + expected.value, "got " + got.value);
  ok(got.average === expected.average, "WHO averaging window for " + p + " is " + expected.average, "got " + got.average);
  ok(got.annual === expected.annual, "WHO annual value for " + p + " is " + expected.annual, "got " + got.annual);
}

// --- 5. the comparison logic answers correctly, case by case --------------------------------
console.log("\nthe page's own comparison logic");
let v;
v = runtime.whoVerdict("pm2_5", 30);
ok(v.verdict === "over" && Math.abs(v.times - 2) < 1e-9, "30 ug/m3 PM2.5 is 2.0x the WHO 24-hour guideline and flagged over", JSON.stringify(v));
v = runtime.whoVerdict("pm2_5", 15);
ok(v.verdict === "under" && Math.abs(v.times - 1) < 1e-9, "exactly at the guideline counts as not over", JSON.stringify(v));
v = runtime.whoVerdict("pm2_5", 7.5);
ok(v.verdict === "under" && Math.abs(v.times - 0.5) < 1e-9, "7.5 ug/m3 PM2.5 is 0.5x the guideline", JSON.stringify(v));
v = runtime.whoVerdict("pm10", 45);
ok(v.verdict === "under", "45 ug/m3 PM10 sits at its own (higher) guideline, not the PM2.5 one", JSON.stringify(v));
v = runtime.whoVerdict("ozone", 50);
ok(v.verdict === "under" && Math.abs(v.times - 0.5) < 1e-9, "ozone is compared to its 8-hour guideline of 100", JSON.stringify(v));
v = runtime.whoVerdict("pm2_5", null);
ok(v.verdict === "unknown" && v.times === null, "a missing reading is 'unknown', never a zero", JSON.stringify(v));
v = runtime.whoVerdict("carbon_monoxide", 200);
ok(v.verdict === "unknown" && v.guideline === null, "a pollutant we hold no guideline for is 'unknown', not an invented zero", JSON.stringify(v));
ok(runtime.timesGuideline("pm2_5", null) === null, "timesGuideline returns null (not NaN) for a missing value");
ok(runtime.timesGuideline("nope", 5) === null, "timesGuideline returns null for an unknown pollutant");

console.log("\nwhich pollutants get compared");
ok(eq(runtime.comparables({ pm2_5: 3, ozone: 50, carbon_monoxide: 100 }), ["pm2_5", "ozone"]),
  "only pollutants with both a reading and a guideline are compared (carbon monoxide is dropped)");
ok(eq(runtime.comparables({}), []), "no readings means nothing to compare");
ok(runtime.comparables({ pm2_5: null }) .length === 0, "a null reading is not compared");

// --- 6. the demonstration actually demonstrates the disagreement ----------------------------
console.log("\nthe disagreement is shown, not asserted");
ok(runtime.EXAMPLES.length === 6, "six measured examples", "got " + runtime.EXAMPLES.length);
let disagreements = 0, maxGap = 0;
for (const e of runtime.EXAMPLES) {
  if (typeof e.pm2_5 !== "number" || typeof e.us_aqi !== "number" || typeof e.european_aqi !== "number") {
    ok(false, "example " + e.place + " has all three numbers");
    continue;
  }
  const gap = Math.abs(e.us_aqi - e.european_aqi);
  if (gap >= 10) disagreements++;
  if (gap > maxGap) maxGap = gap;
}
ok(disagreements >= 2, "at least two rows show the two indexes disagreeing by 10+ points", "got " + disagreements);
ok(maxGap >= 20, "at least one row disagrees by 20+ points", "max gap " + maxGap);
const london = runtime.EXAMPLES.find(e => e.place === "London");
ok(!!london && london.us_aqi !== london.european_aqi,
  "the London row the prose points at really does have two different numbers",
  london ? JSON.stringify(london) : "missing");

// --- 7. the measured inconsistency is on the page and in the sources file -------------------
const inc = sources.measured_inconsistency;
ok(inc && inc.pm2_5 === 1.7 && inc.us_aqi_pm2_5 === 114, "the sources file records the measured internal inconsistency");
ok(html.includes(String(inc.us_aqi_pm2_5)), "the page prints the inconsistent sub-index (" + inc.us_aqi_pm2_5 + ")");
ok(html.includes(String(inc.pm2_5)), "the page prints the concentration it contradicts (" + inc.pm2_5 + ")");

// --- 8. the page says the things it must say ------------------------------------------------
console.log("\nthe page states its limits");
ok(/model, not a monitor/i.test(html), "says it is a model, not a monitor");
ok(/not a diagnosis/i.test(html), "says an index is not a diagnosis");
ok(/worst pollutant, not the particles/i.test(html), "explains that the index is the worst pollutant");
ok(/two different scales/i.test(html), "says the two indexes are different scales");
ok(/not reported/.test(html), "prints 'not reported' rather than a zero for missing values");
ok(html.includes("open-meteo.com/en/docs/air-quality-api"), "links the data source");
ok(html.includes("9789240034228"), "links the WHO 2021 guidelines");
ok(/Copernicus/.test(html) || /Copernicus Atmosphere/.test(sources.data_source.upstream), "names the upstream data (CAMS/Copernicus)");
ok(sources.data_source.auth === "none (keyless)", "the sources file records that the API is keyless");

console.log("\n" + pass + " passed, " + fail + " failed");
process.exit(fail === 0 ? 0 : 1);
