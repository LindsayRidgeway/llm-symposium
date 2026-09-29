// Validation harness for docs/works/food-safety.html — 2026-09-29.
//
// Why this exists: the page answers the question "is this still good?" after a power outage, and
// both directions of error matter — telling someone to keep spoiled food risks foodborne illness,
// telling someone to throw out good food costs a household that may have no way to replace it.
// So there are two things to check, and neither needs a network:
//
//   1. The page's thresholds equal the numbers in docs/works/food-safety-sources.json, which were
//      read from the sources on 2026-09-29 and record their own HTTP status. A threshold cannot be
//      edited on the page alone.
//   2. The page's own verdict function gives the right answer for each case, including the one
//      case the page exists for: a reading between the FDA's 4-hour clock and FEMA's 2-hour clock,
//      where the authorities disagree and the page must say so rather than pick a side.
//
// Same shape as tests/validate_ors_calculator.mjs and tests/validate_recalls_page.mjs: the page's
// OWN inline script is run against a stub DOM. Offline, so it can be run on every landing.
//
// Run: node tests/validate_food_safety_page.mjs
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const html = fs.readFileSync(path.join(root, "docs/works/food-safety.html"), "utf8");
const sources = JSON.parse(fs.readFileSync(path.join(root, "docs/works/food-safety-sources.json"), "utf8"));

let pass = 0, fail = 0;
const ok = (cond, label, extra = "") => {
  if (cond) { pass++; console.log("  ok   " + label); }
  else { fail++; console.log("  FAIL " + label + (extra ? "  [" + extra + "]" : "")); }
};

// --- 1. exactly one inline script, and it is the source of every printed number -------------
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
ok(blocks.length === 1, "exactly one inline script", "got " + blocks.length);
const code = blocks[0];

// --- 2. run the page's own script against a stub DOM ----------------------------------------
const els = new Map();
const el = (id) => {
  if (!els.has(id)) {
    els.set(id, {
      id, value: "", textContent: "", className: "", style: {},
      classList: { contains: () => false, add() {}, remove() {} },
      addEventListener() {},
    });
  }
  return els.get(id);
};
const document = { getElementById: (id) => el(id), body: { classList: { contains: () => false, add() {}, remove() {} } } };

let runtime;
try {
  runtime = new Function("document", code + "\nreturn { verdictFor: verdictFor, THRESHOLDS: THRESHOLDS, updateCalculator: updateCalculator };")(document);
} catch (e) {
  console.log("  FAIL the page's inline script did not even evaluate: " + e.message);
  process.exit(1);
}
ok(typeof runtime.verdictFor === "function", "the page's own verdictFor was captured");
ok(typeof runtime.updateCalculator === "function", "the page's own updateCalculator was captured");

// --- 3. the page's thresholds must equal the measured file, key for key ---------------------
const pageT = runtime.THRESHOLDS, fileT = sources.thresholds;
const keys = Object.keys(fileT);
ok(keys.length >= 10, "the measurement file carries the thresholds", String(keys.length));
for (const k of keys) {
  ok(pageT[k] === fileT[k], `threshold ${k} on the page equals the measurement file (${fileT[k]})`, String(pageT[k]));
}
ok(Object.keys(pageT).every(k => k in fileT), "the page invents no threshold the file does not carry",
   Object.keys(pageT).filter(k => !(k in fileT)).join(","));

// --- 4. the verdicts, case by case -----------------------------------------------------------
const cases = [
  // appliance,        hours, temp, expected level, a phrase the headline must carry
  ["fridge",          1,     "",   "safe",     "inside every published window"],
  ["fridge",          3,     "",   "disagree", "the authorities disagree"],
  ["fridge",          6,     "",   "discard",  "past both clocks"],
  ["fridge",          3,     38,   "safe",     "keep it"],
  ["fridge",          3,     43,   "cook",     "cook it now"],
  ["fridge",          3,     50,   "discard",  "throw it out"],
  ["freezer-full",    20,    "",   "safe",     "holding time"],
  ["freezer-full",    60,    "",   "discard",  "treat it as a refrigerator"],
  ["freezer-half",    10,    "",   "safe",     "holding time"],
  ["freezer-half",    30,    "",   "discard",  "treat it as a refrigerator"],
  ["freezer-full",    10,    35,   "safe",     "keep it"],
  ["freezer-full",    10,    50,   "discard",  "throw it out"],
  ["cooler",          5,     "",   "unknown",  "no published clock"],
  ["fridge",          "",    "",   "unknown",  "Enter how long"],
];
for (const [appliance, hours, temp, level, phrase] of cases) {
  const v = runtime.verdictFor(appliance, hours, temp);
  ok(v.level === level && v.headline.toLowerCase().includes(phrase.toLowerCase()),
     `${appliance} ${hours}h ${temp === "" ? "(no temp)" : temp + "°F"} → ${level}, "${phrase}"`,
     `${v.level} / ${v.headline}`);
}

// --- 5. the case the page exists for: 2 < hours <= 4 on a fridge must show BOTH clocks -------
const straddle = runtime.verdictFor("fridge", 3, "");
ok(straddle.level === "disagree", "the 3-hour fridge case is flagged as a disagreement, not a verdict", straddle.level);
ok(straddle.bothClocks === true, "the disagreement case shows both clocks", String(straddle.bothClocks));
ok(/disagree/i.test(straddle.detail) || /disagree/i.test(straddle.headline),
   "the disagreement is stated in words, not only by a colour");
ok(/4 h/.test(straddle.detail) && /2 h/.test(straddle.detail),
   "the disagreement names both clocks (4 h and 2 h)", straddle.detail);
ok(runtime.verdictFor("fridge", 1, "").bothClocks === true &&
   runtime.verdictFor("fridge", 6, "").bothClocks === true,
   "both clocks are also shown when the authorities agree");
ok(runtime.verdictFor("fridge", 3, 38).bothClocks === false,
   "a measured temperature replaces the clocks rather than sitting beside them");

// --- 6. updateCalculator must actually write the verdict through the DOM --------------------
el("applianceSelect").value = "fridge";
el("hoursInput").value = "3";
el("tempInput").value = "";
runtime.updateCalculator();
ok(el("verdictBox").className === "verdict disagree", "the box takes the disagreement class", el("verdictBox").className);
ok(/disagree/i.test(el("verdictHeadline").textContent), "the headline reaches the DOM", el("verdictHeadline").textContent);
ok(el("clocks").style.display === "grid", "the clocks strip is shown", el("clocks").style.display);
ok(/4 h/.test(el("clockFda").textContent) && /2 h/.test(el("clockFema").textContent),
   "each clock is labelled with its own agency and figure",
   el("clockFda").textContent + " | " + el("clockFema").textContent);
el("tempInput").value = "43";
runtime.updateCalculator();
ok(el("verdictBox").className === "verdict cook", "a 43 °F reading in a fridge becomes 'cook', not 'discard'", el("verdictBox").className);
ok(el("clocks").style.display === "none", "the clocks strip is hidden once a reading exists");

// --- 7. the page must quote the disagreement, not characterise it ---------------------------
ok(html.includes("for 4 hours or more"), "the FDA four-hour sentence is quoted verbatim");
ok(html.includes("40 degrees or higher for two hours or more"), "the FEMA two-hour sentence is quoted verbatim");
ok(html.includes("has been warmer than 40 degrees F"), "the Red Cross sentence, which states no time, is quoted verbatim");
ok(/cannot rely on appearance or odour/.test(html), "the page repeats the FDA's own warning about appearance and odour");
ok(/even when they are thoroughly cooked/.test(html), "the page repeats that cooking does not make spoiled food safe");

// --- 8. the two authorities this session could not read must be marked, not silently dropped --
ok(/HTTP 403/.test(html), "the pages that blocked this session are marked on the page, with the status");
ok(/NOT VERIFIED HERE/.test(html), "the unreachable sources are labelled as not verified here");
const byId = Object.fromEntries(sources.sources.map(s => [s.id, s]));
ok(byId.fsis && byId.fsis.http_status === 403 && byId.fsis.used_by_page === false,
   "the measurement file records FSIS as 403 and not used");
ok(byId.cdc && byId.cdc.http_status === 403 && byId.cdc.used_by_page === false,
   "the measurement file records CDC as 403 and not used");
ok(byId.fda.http_status === 200 && byId.fda.used_by_page === true, "FDA is recorded as read and used");
ok(sources.discrepancies.length >= 2, "the file records the disagreements it exists to preserve",
   String(sources.discrepancies.length));

// --- 9. the page is honest about what it cannot do ------------------------------------------
ok(/cannot tell you whether a specific item is safe/.test(html),
   "the page says plainly that it cannot judge a particular item");
ok(/no fridge or freezer was measured|no fridge or freezer/i.test(html),
   "the page states that nothing was measured in a real kitchen");

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);
