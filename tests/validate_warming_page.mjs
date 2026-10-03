// Validation harness for docs/works/warming.html — 2026-10-03.
//
// Why this exists: "Your own town's temperature record" (Works entry 2) is the flagship of agenda
// item 12 — a public good a stranger can use — and it is the ONLY data-driven Works page with no
// harness. Every comparable entry (trials, retraction, recalls, unreported-trials, food-safety,
// fetchable, ors) ships one. The page's index entry states a number nobody rechecks: "Boston, 76
// complete years, +1.40 °C from the 1950s to the 2020s".
//
// Writing this harness found a real defect, in the page's own stated method. Its comment says it
// generates the small set of probable misspellings — "one letter deleted, two letters swapped, a
// doubled letter collapsed, an accent dropped" — and asks the geocoder about all of them. The
// accent-dropped form IS generated (`fold`) and then thrown away by the filter that removed the
// typed string: that filter compared against the FOLDED string, so for "München" it dropped
// "Munchen", for "Zürich" it dropped "Zurich", for "São Paulo" it dropped "Sao Paulo". The page
// claims to try the unaccented spelling and never did. Fixed the same day, in the same commit as
// this file.
//
// This harness runs the page's OWN inline script against a stub DOM and a stub fetch, offline, and
// checks: the arithmetic (decade means, the decade filter, the endpoint delta, the trend), the
// honesty behaviours (an empty answer says so; the raw query is printed), the privacy boundary
// (only the two keyless Open-Meteo hosts are contacted), and the accent-fold regression above.
// Same shape as tests/validate_ors_calculator.mjs.
//
// Run: node tests/validate_warming_page.mjs
// Optional live re-derivation of the index figure: WARMING_LIVE=1 node tests/validate_warming_page.mjs
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const html = fs.readFileSync(path.join(root, "docs/works/warming.html"), "utf8");
const indexHtml = fs.readFileSync(path.join(root, "docs/works/index.html"), "utf8");

let pass = 0, fail = 0;
const ok = (cond, label, extra = "") => {
  if (cond) { pass++; console.log("  ok   " + label); }
  else { fail++; console.log("  FAIL " + label + (extra ? "  [" + extra + "]" : "")); }
};

// --- 1. exactly one inline script, and it is the source of every printed number --------------
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
ok(blocks.length === 1, "exactly one inline script", "got " + blocks.length);
const code = blocks[0];

// --- 2. run the page's own script against a stub DOM and a controllable fetch ----------------
const els = new Map();
const el = (id) => {
  if (!els.has(id)) {
    els.set(id, {
      id, value: "", textContent: "", innerHTML: "", style: {}, disabled: false,
      addEventListener() {}, querySelectorAll() { return []; }, onclick: null,
    });
  }
  return els.get(id);
};
const document = { getElementById: (id) => el(id) };
const location = { search: "" };

let lastFetchUrl = "";
let fetchImpl = async () => ({ json: async () => ({}) });
const fetchStub = async (u) => { lastFetchUrl = u; return fetchImpl(u); };

let api;
try {
  const capture = "return { variants, levSim, dice, annualMeans, decadeMeans, chart, render };";
  api = new Function("document", "fetch", "location", code + "\n" + capture)(document, fetchStub, location);
} catch (e) {
  console.log("  FAIL the page's inline script did not even evaluate: " + e.message);
  process.exit(1);
}
ok(typeof api.render === "function" && typeof api.decadeMeans === "function" && typeof api.variants === "function",
   "the page's own functions were captured from its inline script");

// --- 3. the spelling fallback, and the accent-fold regression --------------------------------
const fold = s => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
for (const q of ["München", "Zürich", "São Paulo", "Bogotá"]) {
  const vars = api.variants(q);
  ok(vars.some(v => v.toLowerCase() === fold(q).toLowerCase()),
     `the unaccented spelling of "${q}" is actually queried (regression)`,
     JSON.stringify(vars));
}
ok(!api.variants("Bostn").includes("Bostn"),
   "the typed string itself is not re-queried as a variant");
ok(api.variants("KualaLumpur").includes("Kuala Lumpur"),
   'a missing space is proposed ("KualaLumpur" -> "Kuala Lumpur")');
ok(api.variants("Mississippi").includes("Misisipi"),
   "a doubled letter is collapsed as a variant");
ok(api.variants("Bostn").every(v => v.length >= 3),
   "no variant shorter than 3 characters is sent");

// edit-distance ranking beats bigram overlap on the case the page names in its comment
ok(api.levSim("Bostn", "Boston") > api.levSim("Bostn", "Bost"),
   "levSim(Bostn,Boston) > levSim(Bostn,Bost) — the longer correct name wins");

// --- 4. decadeMeans: grouping and the >=6-year filter ----------------------------------------
const rows = [];
for (let y = 1950; y < 1960; y++) rows.push({ year: y, mean: 10.0, n: 365 });
for (let y = 1980; y < 1990; y++) rows.push({ year: y, mean: 11.0, n: 365 });
for (let y = 2010; y < 2020; y++) rows.push({ year: y, mean: 12.0, n: 365 });
for (let y = 2020; y < 2025; y++) rows.push({ year: y, mean: 10.5, n: 365 }); // only 5 yrs: must be dropped
const dec = api.decadeMeans(rows);
ok(JSON.stringify(dec.map(d => d.decade)) === JSON.stringify([1950, 1980, 2010]),
   "a decade with fewer than 6 usable years is dropped", JSON.stringify(dec.map(d => d.decade)));
ok(dec[0].mean === 10 && dec[2].mean === 12, "decade means are the mean of their own years");

// --- 5. render(): the printed numbers are the arithmetic ------------------------------------
api.render(rows, "Testville");
const out = el("out").innerHTML;
ok(out.includes("+2.00 °C"), "the endpoint delta is last-decade minus first-decade (+2.00)", out.match(/[+-][\d.]+ °C/));
ok(out.includes("1950s → 2010s"), "the delta names the two decades it spans");
ok(out.includes("+0.33 °C"), "the trend is the delta divided by the decades spanned (2.00/6 = +0.33)");
ok(out.includes("12.0 °C") && out.includes("warmest year (2010)"), "the warmest year and its value are printed");
ok(out.includes("35 complete years, 1950–2024"), "the year range and count are printed");
ok(!out.includes("2020s"), "the dropped 5-year decade never reaches the reader");
ok(el("caveats").style.display === "block", "the caveats block is revealed with the result");
ok(el("status").textContent.includes("35 years"), "the status line reports how many years were used");

// --- 6. an empty answer says it is empty, not a chart of nothing -----------------------------
api.render([], "Nowhere");
ok(el("out").innerHTML.includes("No usable years came back"), "an empty result says so plainly");

// --- 7. annualMeans(): null handling, partial years, and the last-full-year rule -------------
const cy = new Date().getFullYear();
const times = [], vals = [];
const put = (y, days, value) => {
  for (let i = 0; i < days; i++) {
    const d = new Date(Date.UTC(y, 0, 1) + i * 864e5).toISOString().slice(0, 10);
    times.push(d); vals.push(days === 200 ? value : (i < 10 ? null : value)); // 10 nulls in full years
  }
};
put(cy - 3, 200, 8.0);      // too few days -> dropped
for (const y of [cy - 2, cy - 1]) put(y, 365, 10.0 + (y % 10) * 0.01);
put(cy, 365, 99.0);         // current year -> excluded (not a complete year yet)
fetchImpl = async () => ({ json: async () => ({ daily: { time: times, temperature_2m_mean: vals } }) });
const ann = await api.annualMeans(42.36, -71.06);
ok(!ann.some(r => r.year === cy - 3), "a year with too much missing data is dropped", JSON.stringify(ann.map(r => r.year)));
ok(!ann.some(r => r.year === cy), "the current, incomplete year is excluded", JSON.stringify(ann.map(r => r.year)));
ok(ann.length === 2 && ann.every(r => r.n === 355), "null days are skipped, not counted as zero", JSON.stringify(ann.map(r => r.n)));
ok(lastFetchUrl.includes("start_date=1950-01-01") && lastFetchUrl.includes("timezone=auto")
   && lastFetchUrl.includes("latitude=42.36"),
   "the archive query spans 1950 to now for the chosen grid point", lastFetchUrl);

// --- 8. the privacy boundary: only the two keyless Open-Meteo hosts are contacted ------------
const hosts = [...code.matchAll(/https?:\/\/([^/"'`\s)]+)/g)].map(m => m[1]);
const allowed = new Set(["geocoding-api.open-meteo.com", "archive-api.open-meteo.com"]);
ok(hosts.every(h => allowed.has(h)), "the page contacts no host but the two keyless Open-Meteo APIs",
   hosts.join(", "));

// --- 9. the Works index links this page and states the figure it must keep -------------------
ok(indexHtml.includes('href="warming.html"'), "the Works index links to the warming page");
ok(/\+1\.40\s*°C/.test(indexHtml) && /76 complete years/.test(indexHtml),
   "the index still carries the Boston figure this harness re-derives live (76 years, +1.40 °C)");

// --- 10. optional live re-derivation of the index figure (offline by default) ----------------
if (process.env.WARMING_LIVE === "1") {
  fetchImpl = (u) => fetch(u); // hand the page's own annualMeans a real network fetch for this branch
  const g = await (await fetch("https://geocoding-api.open-meteo.com/v1/search?count=1&language=en&format=json&name=Boston")).json();
  const { latitude: lat, longitude: lon } = g.results[0];
  const end = new Date(Date.now() - 6 * 864e5).toISOString().slice(0, 10);
  const url = `https://archive-api.open-meteo.com/v1/archive?latitude=${lat}&longitude=${lon}` +
    `&start_date=1950-01-01&end_date=${end}&daily=temperature_2m_mean&timezone=auto`;
  const live = await api.annualMeans(lat, lon);
  const d = api.decadeMeans(live);
  const delta = d[d.length - 1].mean - d[0].mean;
  ok(live.length === 76, "live: Boston has 76 complete years", String(live.length));
  ok(Math.abs(delta - 1.40) < 0.05, "live: the 1950s-to-2020s change is +1.40 °C", delta.toFixed(2));
} else {
  console.log("  ..   live Boston re-derivation skipped (set WARMING_LIVE=1 to run it)");
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);
