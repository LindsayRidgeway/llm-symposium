#!/usr/bin/env node
/*
 * validate_co_safety_page.mjs — pin docs/works/co-safety.html to its source record, offline.
 *
 * Written 2026-10-07 (Dmitri) with the page `docs/works/co-safety.html` and its record
 * `docs/works/co-safety-sources.json`, the first Works page for the CO-after-a-power-cut candidate
 * (`works/queue/08-carbon-monoxide-after-a-power-cut.md`).
 *
 * Why it exists. The page's value is that its numbers and its quotations are the agencies' own,
 * with the fetch dates and HTTP statuses recorded beside them. That claim is false the moment a
 * later edit can move a number or alter a quote on the page alone. So this harness loads the page's
 * own decision function (verdictFor) out of its inline <script>, and checks three things WITHOUT a
 * network:
 *
 *   1. every quotation in the record appears VERBATIM in the page — a quote cannot be softened on
 *      the page or invented in the record;
 *   2. the page's THRESHOLDS object equals the record's `numbers` — a threshold cannot be edited on
 *      the page alone (and the reverse: the record cannot change while the page stays put);
 *   3. the page's own verdictFor still refuses indoors, still says "move it" under 20 feet, and
 *      still permits 20 feet or more — the load-bearing behaviour, re-derived from the page's code.
 *
 * It cannot re-fetch the sources (tests run offline); it pins provenance and the numbers a reader
 * would otherwise have to recompute by hand. Run: node tests/validate_co_safety_page.mjs
 */

import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, "..");
const PAGE = path.join(REPO, "docs", "works", "co-safety.html");
const RECORD = path.join(REPO, "docs", "works", "co-safety-sources.json");

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

// ---- load the two artefacts ----------------------------------------------------------------
if (!fs.existsSync(PAGE)) fail("page missing: " + path.relative(REPO, PAGE));
if (!fs.existsSync(RECORD)) fail("record missing: " + path.relative(REPO, RECORD));

const html = fs.readFileSync(PAGE, "utf8");
let record;
try {
  record = JSON.parse(fs.readFileSync(RECORD, "utf8"));
} catch (e) {
  fail("record is not valid JSON: " + e.message);
}

console.log("co-safety page vs " + path.relative(REPO, RECORD));

// ---- 1. every recorded quotation is on the page, verbatim -----------------------------------
const quotes = record.quotes || {};
const quoteKeys = Object.keys(quotes);
check("the record carries a real quotation set (>= 8)", quoteKeys.length >= 8, "found " + quoteKeys.length);
for (const key of quoteKeys) {
  check("quote '" + key + "' appears verbatim on the page", html.includes(quotes[key]));
}

// ---- 2. the page's THRESHOLDS equals the record's numbers -----------------------------------
const script = html.match(/<script>([\s\S]*?)<\/script>/);
if (!script) fail("page has no inline <script> to read THRESHOLDS from");

const sandbox = {
  document: {
    getElementById: () => null,
    querySelectorAll: () => [],
    addEventListener: () => {},
  },
};
vm.createContext(sandbox);
try {
  vm.runInContext(
    script[1] +
      "\n;globalThis.__THRESHOLDS = THRESHOLDS;" +
      "\n;globalThis.__INDOOR = INDOOR;" +
      "\n;globalThis.__verdictFor = verdictFor;",
    sandbox,
  );
} catch (e) {
  fail("the page's inline script threw when loaded: " + e.message);
}

const pageT = sandbox.__THRESHOLDS;
check("the page exposes a THRESHOLDS object", !!pageT);

// record-key -> page-key, stated explicitly so a rename cannot quietly pass.
const NUMBER_MAP = {
  distance_feet: "distance_feet",
  cdc_deaths_unintentional: "cdc_deaths",
  cpsc_deaths_consumer_products: "cpsc_deaths",
  cpsc_deaths_generators: "cpsc_generator_deaths",
  cdc_ed_visits: "cdc_ed_visits",
  cdc_hospitalizations: "cdc_hospitalizations",
  alarm_replace_years_cdc: "alarm_replace_years",
  emergency_number: "emergency_number",
};
if (pageT) {
  for (const [recKey, pageKey] of Object.entries(NUMBER_MAP)) {
    check(
      "number " + recKey + " matches the page (" + pageKey + ")",
      pageT[pageKey] === record.numbers[recKey],
      "record " + record.numbers[recKey] + " vs page " + pageT[pageKey],
    );
  }
}

// ---- 3. the page's own decision still refuses indoors and still permits 20 ft ----------------
const vf = sandbox.__verdictFor;
check("the page exposes verdictFor", typeof vf === "function");
if (typeof vf === "function") {
  const indoors = vf("generator", "indoors", "yes");
  check("verdictFor: indoors is refused", indoors.level === "deadly", "got " + indoors.level);

  const close = vf("generator", "outdoors_close", "yes");
  check("verdictFor: under 20 feet says move it", close.level === "move", "got " + close.level);

  const far = vf("generator", "outdoors_far", "yes");
  check("verdictFor: 20 feet or more is permitted", far.level === "ok", "got " + far.level);

  const noAlarm = vf("generator", "outdoors_far", "no");
  check("verdictFor: a missing alarm is named at 20 feet too", /alarm/i.test(noAlarm.detail || ""));

  const indoorQ = vf("grill", "indoors", "yes");
  check("verdictFor: the indoor rule quotes the authority", !!indoorQ.quote && html.includes(indoorQ.quote));
}

// every INDOOR quotation the page carries is also in the record
const indoor = sandbox.__INDOOR || {};
for (const [k, v] of Object.entries(indoor)) {
  check("indoor rule '" + k + "' is in the record", Object.values(quotes).includes(v.quote));
}

// ---- 4. the unfetchable source stays marked, and the fetch states stay honest ----------------
const refused = (record.sources || []).filter((s) => s.used === false);
check("the record keeps its refused source(s)", refused.length >= 1);
for (const s of refused) {
  check("refused source '" + s.name + "' records HTTP " + s.http_status, s.http_status === 403);
}
check(
  "the page marks the unverified source rather than dropping it",
  html.includes("NOT VERIFIED HERE"),
);
check("the page names its fetch date", html.includes(record.fetched));

// ---- result --------------------------------------------------------------------------------
console.log("");
if (failures.length) {
  console.log(failures.length + " FAILED of " + checks + ":");
  for (const f of failures) console.log("  - " + f);
  process.exit(1);
}
console.log("co-safety page validation: ALL " + checks + " CHECKS PASSED");
