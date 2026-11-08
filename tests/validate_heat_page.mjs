#!/usr/bin/env node
/*
 * validate_heat_page.mjs — pin docs/works/heat.html to its source record, offline.
 *
 * Written 2026-11-08 (Desi) with the page and `docs/works/heat-sources.json`, the second
 * emergency-method entry after The Warm Room (cold) and the same shape as the pattern Dmitri set
 * in `tests/validate_co_safety_page.mjs`.
 *
 * Why it exists. This page's whole claim to be worth reading is that its quotations are the
 * authorities' own and that its thresholds are WHO's and the NHS's rather than ours. That claim is
 * false the moment a later edit can move a threshold, soften a quotation or drop a number on the
 * page alone, with the record still saying what was fetched. So this harness loads the page's own
 * LIMITS object and verdictFor() out of its inline <script> and checks, WITHOUT a network:
 *
 *   1. every quotation in the record appears VERBATIM in the page — a quote cannot be softened on
 *      the page or invented in the record;
 *   2. every threshold the page uses equals the record's `numbers` — neither side can move alone;
 *   3. every figure the page states in prose is present in the record's `numbers`, and the ones a
 *      reader would check by hand (the WHO death counts) are formatted on the page as the record
 *      holds them;
 *   4. the page's own verdictFor still behaves the four ways it must: emergency on confusion, on
 *      hot dry skin, contested at and above WHO's fan line, ordinary cooling below it — re-derived
 *      from the page's own code, including the boundary.
 *
 * It cannot re-fetch the sources (tests run offline). It pins provenance and the numbers a reader
 * would otherwise have to recompute by hand. Run: node tests/validate_heat_page.mjs
 */

import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, "..");
const PAGE = path.join(REPO, "docs", "works", "heat.html");
const RECORD = path.join(REPO, "docs", "works", "heat-sources.json");

const failures = [];
let checks = 0;

function check(name, cond, detail) {
  checks++;
  if (cond) {
    console.log("  ok: " + name);
  } else {
    failures.push(name + (detail ? " — " + detail : ""));
    console.log("  FAIL: " + name + (detail ? " — " + detail : ""));
  }
}

function fail(msg) {
  console.log("FAIL: " + msg);
  process.exit(1);
}

if (!fs.existsSync(PAGE)) fail("page not found: " + PAGE);
if (!fs.existsSync(RECORD)) fail("record not found: " + RECORD);

const page = fs.readFileSync(PAGE, "utf8");
const record = JSON.parse(fs.readFileSync(RECORD, "utf8"));

// ---------------------------------------------------------------- script extraction
const scriptMatch = page.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) fail("no inline <script> found in the page");
const script = scriptMatch[1];

const start = script.indexOf("const LIMITS");
const end = script.indexOf("function render()");
if (start < 0 || end < 0 || end <= start) {
  fail("cannot locate the LIMITS block and verdictFor() in the page's script");
}
const logic = script.slice(start, end) + "\n;({ LIMITS, verdictFor })";

let api;
try {
  api = vm.runInNewContext(logic, {}, { timeout: 2000 });
} catch (e) {
  fail("the page's inline logic does not evaluate: " + e.message);
}
const { LIMITS, verdictFor } = api;
check("page exposes a LIMITS object", LIMITS && typeof LIMITS === "object");
check("page exposes verdictFor()", typeof verdictFor === "function");

// ---------------------------------------------------------------- 1. quotations
console.log("\nquotations (" + record.quotes.length + "):");
check("the record holds quotations at all", record.quotes.length >= 15, "got " + record.quotes.length);
for (const q of record.quotes) {
  check(
    "verbatim on the page: " + q.text.slice(0, 58).replace(/\s+/g, " ") + (q.text.length > 58 ? "…" : ""),
    page.includes(q.text),
    q.source
  );
}

// ---------------------------------------------------------------- 2. thresholds
console.log("\nthresholds:");
const recordNumbers = record.numbers || {};
check("the record holds numbers", Object.keys(recordNumbers).length >= 15);
for (const [k, v] of Object.entries(LIMITS)) {
  check(
    "page LIMITS." + k + " = record numbers." + k,
    Object.prototype.hasOwnProperty.call(recordNumbers, k) && recordNumbers[k] === v,
    "page " + v + " vs record " + recordNumbers[k]
  );
}
check(
  "the fan line is WHO's 40 °C, not an invented one",
  LIMITS.fan_max_c === 40,
  "got " + LIMITS.fan_max_c
);
check(
  "the two spellings of the fan line agree (40 °C / 104 °F)",
  LIMITS.fan_max_c === 40 && LIMITS.fan_max_f === 104
);

// ---------------------------------------------------------------- 3. prose figures
console.log("\nfigures stated in prose:");
const fmt = (n) => n.toLocaleString("en-US");
const proseFigures = [
  ["WHO annual heat deaths", recordNumbers.who_heat_deaths_annual],
  ["WHO Europe 2022 excess deaths", recordNumbers.who_europe_2022_excess],
  ["2003 Europe deaths", recordNumbers.who_2003_europe_deaths],
  ["2010 Russia excess deaths", recordNumbers.who_2010_russia_excess]
];
for (const [label, n] of proseFigures) {
  check(label + " = " + fmt(n) + " appears on the page", page.includes(fmt(n)), String(n));
}
check(
  "Falmouth case count (" + recordNumbers.falmouth_cases + ") appears on the page",
  page.includes(String(recordNumbers.falmouth_cases))
);
check(
  "Falmouth cooling rate (" + recordNumbers.falmouth_cooling_c_per_min + " °C/min) appears on the page",
  page.includes(String(recordNumbers.falmouth_cooling_c_per_min) + " °C per minute")
);
check(
  "the sunshine penalty (" + recordNumbers.heat_index_sun_penalty_f + " °F) is stated as the NWS states it",
  page.includes(String(recordNumbers.heat_index_sun_penalty_f) + "°F")
);

// ---------------------------------------------------------------- 4. behaviour
console.log("\nbehaviour of the page's own verdictFor():");
const cases = [
  ["confusion beats every other input", "41", "yes", "no", "emergency"],
  ["hot dry skin is an emergency even at a mild temperature", "31", "no", "yes", "emergency"],
  ["the WHO fan line itself is already contested (>= 40)", "40", "yes", "yes", "contested"],
  ["above the line is contested", "42.5", "yes", "yes", "contested"],
  ["below the line is ordinary cooling", "34", "yes", "yes", "cool"],
  ["a cold room with a sweating, alert person is not an emergency", "22", "yes", "yes", "cool"]
];
for (const [name, t, sweating, alert, want] of cases) {
  const got = verdictFor(t, sweating, alert);
  check(name, got && got.level === want, "got " + (got && got.level) + ", wanted " + want);
  check(
    "  …and it always says what to do (" + name + ")",
    got && Array.isArray(got.steps) && got.steps.length >= 2 && typeof got.headline === "string" && got.headline.length > 10
  );
}

// The emergency branch must never be reachable-but-empty: a page that answers "emergency" with no
// instruction is worse than one that answers nothing.
const emergency = verdictFor("41", "yes", "no");
check(
  "the emergency answer sends the reader to the emergency number first",
  emergency.steps[0].toLowerCase().includes("emergency") || emergency.headline.toLowerCase().includes("emergency"),
  emergency.headline
);

// ---------------------------------------------------------------- honesty markers
console.log("\nhonesty markers:");
check(
  "the page says what it does not do",
  page.includes("What this page does not do"),
  "missing section"
);
check(
  "the page states that it cannot diagnose",
  /cannot diagnose/i.test(page)
);
check(
  "the page states the CDC fetch was refused",
  /403/.test(page) && /CDC/.test(page)
);
check(
  "the page states the sourced record and this harness exist",
  page.includes("docs/works/heat-sources.json") && page.includes("tests/validate_heat_page.mjs")
);
check(
  "the page yields to local authority explicitly",
  /they are right and this page is wrong/i.test(page)
);
check(
  "the record keeps the unfetchable sources as unfetched, not as citations",
  record.sources.filter((s) => s.http_status === 403 || s.http_status === 410).every((s) => s.used === false)
);

// ---------------------------------------------------------------- result
console.log("\n" + checks + " checks, " + failures.length + " failure(s)");
if (failures.length) {
  console.log("\nFAILURES:");
  for (const f of failures) console.log(" - " + f);
  process.exit(1);
}
console.log("OK — docs/works/heat.html is pinned to docs/works/heat-sources.json");
