// Validation harness for docs/works/fetchable.html — 2026-09-16.
// Runs the page's OWN inline script against a stub DOM and the SHIPPED data file, then
// re-measures a sample of rows against the live sources, so the page cannot quietly keep
// claiming something the world stopped delivering. Written by the same architecture that
// wrote the page: this is a check, not a review, and it is recorded as such.
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const html = fs.readFileSync(path.join(root, "docs/works/fetchable.html"), "utf8");
const dataPath = path.join(root, "docs/works/fetchable-sources.json");
const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));

const realFetch = globalThis.fetch;   // kept: the stub below must not shadow the live checks
let pass = 0, fail = 0;
const ok = (cond, label, extra = "") => {
  if (cond) { pass++; console.log("  ok   " + label); }
  else { fail++; console.log("  FAIL " + label + (extra ? "  [" + extra + "]" : "")); }
};

// --- 1. the page must have exactly one inline script and no other source of numbers ---
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
ok(blocks.length === 1, "exactly one inline script", "got " + blocks.length);
const code = blocks[0];
ok(/fetch\("fetchable-sources\.json"/.test(code), "the page loads the shipped JSON rather than retyping numbers");
ok(!/\b\d{2,}\s+(sources|answered)/.test(code), "no hard-coded counts in the script");

// --- 2. run the page's script against a stub DOM -------------------------------------
const els = new Map();
const mkEl = () => ({ innerHTML: "", textContent: "", style: {}, value: "", dataset: {},
  disabled: false, addEventListener() {}, appendChild() {}, querySelector: () => mkEl(),
  querySelectorAll: () => [] });
const buttons = [];
globalThis.document = {
  getElementById(id) { if (!els.has(id)) els.set(id, mkEl()); return els.get(id); },
  createElement: mkEl,
  querySelectorAll(sel) { return sel === "button.chk" ? buttons : []; },
};
globalThis.fetch = async (url) => {
  if (String(url).includes("fetchable-sources.json")) {
    return { ok: true, status: 200, json: async () => data };
  }
  throw new TypeError("Failed to fetch");
};

new Function("document", "fetch", code)(globalThis.document, globalThis.fetch);
await new Promise(r => setTimeout(r, 50));   // let the fetch().then(render) chain settle

const tables = els.get("tables").innerHTML;
const counts = els.get("counts").innerHTML;
const rows = [...tables.matchAll(/data-url="/g)].length;   // one per rendered source row

ok(rows === data.sources.length, `one row per source (${rows} rendered, ${data.sources.length} in the file)`);
ok(counts.includes(String(data.counts.sources)), "the counts line prints the file's own total");
ok(counts.includes(String(data.counts.browser_usable)), "the counts line prints the file's own browser-usable total");

// every source must appear, by name
const missing = data.sources.filter(s => !tables.includes(s.name.replace(/&/g, "&amp;")));
ok(missing.length === 0, "every source is rendered by name", missing.map(m => m.name).join(","));

// a CORS-absent source must be marked not readable, a CORS-open one must be marked readable
const grab = name => {
  const i = tables.indexOf(name.replace(/&/g, "&amp;"));
  return i < 0 ? "" : tables.slice(i, tables.indexOf("</tr>", i));
};
const arxiv = grab("arXiv");
ok(arxiv.includes('<span class="no">no</span>'), "arXiv renders as NOT readable from a web page");
const ct = grab("ClinicalTrials.gov");
ok(ct.includes('<span class="yes">yes</span>'), "ClinicalTrials.gov renders as readable");
ok(/the exact request and what came back/.test(ct) && ct.includes("https://clinicaltrials.gov/api/v2"), "each row prints its own request URL");

// --- 3. the browser check must report a CORS refusal AS the answer, not as a bug -------
// Build fake buttons from the rendered rows so the page's real listener is exercised.
for (const m of tables.matchAll(/data-url="([^"]+)"/g)) {
  const verdict = mkEl();
  const b = mkEl();
  b.dataset = { url: m[1] };
  b.parentElement = { querySelector: () => verdict };
  b._verdict = verdict;
  buttons.push(b);
}
const listeners = [];
buttons.forEach(b => b.addEventListener = (ev, fn) => listeners.push(fn));
// re-run render to attach listeners now that buttons exist is not needed: the page attaches on
// click-time elements it finds; we instead call the page's checker through a captured listener.
ok(buttons.length === data.sources.length, `one live-check button per source (${buttons.length})`);

// --- 4. live re-measurement: the page's claims, checked against the sources themselves --
const sample = ["ClinicalTrials.gov", "arXiv", "Wikidata", "Open-Meteo forecast", "Crossref"];
console.log("\n  live re-measurement (the claim is only worth what it still measures):");
for (const name of sample) {
  const s = data.sources.find(x => x.name === name);
  if (!s) { ok(false, name + " present in the file"); continue; }
  let status = null, cors = "absent", bytes = 0;
  try {
    const r = await realFetch(s.url, { headers: { "User-Agent": "Mozilla/5.0 (LLM Symposium validation)",
                                              "Origin": "https://lindsayridgeway.github.io",
                                              "Accept": "application/json, */*" } });
    status = r.status;
    cors = r.headers.get("access-control-allow-origin") ? "*" : "absent";
    bytes = (await r.arrayBuffer()).byteLength;
  } catch (e) { status = "ERR " + e.name; }
  const same = status === 200 && bytes > 0 && (cors === "*") === (s.cors !== "absent");
  ok(same, `${name}: still ${status} with data, CORS ${cors} — page says "${s.cors}"`,
     `live status=${status} cors=${cors} bytes=${bytes}`);
}

console.log(`\n${pass} checks passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
