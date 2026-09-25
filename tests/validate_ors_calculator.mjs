// Validation harness for docs/works/ors.html — 2026-09-24.
//
// Why this exists: the page is a field guide for mixing rehydration fluid by hand, where both
// errors are dangerous — too little salt is hyponatraemia, too much sugar worsens the diarrhoea
// it is meant to treat. Its calculator had no test, and it shipped a defect for months: the
// 1.5–3.0 teaspoon branch printed a hardcoded "2 level teaspoons", so the 250 mL cup (which
// scales to exactly 1.5 tsp) prescribed about a third too much sugar. It was found by reading,
// not by a machine (2026-09-16) and fixed the same day — but nothing stopped the class of bug
// from returning, so this runs the page's OWN inline script against a stub DOM and checks the
// printed numbers against the base ratios the page states. Same shape as
// tests/validate_fetchable_page.mjs: a check written by the architecture that wrote the page,
// recorded as a check and not a review.
//
// Run: node tests/validate_ors_calculator.mjs
//      ORS_HTML=/path/to/candidate.html node tests/validate_ors_calculator.mjs   (to test a page
//      that is not the one on disk — used on 2026-09-25 to prove section 6 fails on the pre-fix
//      page, so the check has teeth rather than being written to agree with what it found)
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const htmlPath = process.env.ORS_HTML || path.join(root, "docs/works/ors.html");
const html = fs.readFileSync(htmlPath, "utf8");

let pass = 0, fail = 0;
const ok = (cond, label, extra = "") => {
  if (cond) { pass++; console.log("  ok   " + label); }
  else { fail++; console.log("  FAIL " + label + (extra ? "  [" + extra + "]" : "")); }
};

// --- 1. exactly one inline script, and it is the source of every printed number ----------
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
ok(blocks.length === 1, "exactly one inline script", "got " + blocks.length);
const code = blocks[0];

// The base ratios are a claim about the world; pin them so a later edit cannot move them
// silently. 1/2 level tsp salt ~ 2.6 g/L, 6 level tsp sugar ~ 25 g/L (the WHO/UNICEF home mix).
ok(/saltGrams\s*=\s*\(2\.6\s*\*\s*ratio\)/.test(code), "salt base is 2.6 g per litre");
ok(/sugarGrams\s*=\s*\(25\.0\s*\*\s*ratio\)/.test(code), "sugar base is 25.0 g per litre");
ok(/const\s+sugarTsp\s*=\s*6\.0\s*\*\s*ratio/.test(code), "sugar base is 6.0 teaspoons per litre");
ok(/const\s+saltTsp\s*=\s*0\.5\s*\*\s*ratio/.test(code), "salt base is 0.5 teaspoon per litre");

// --- 2. run the page's own script against a stub DOM ------------------------------------
const els = new Map();
const el = (id) => {
  if (!els.has(id)) {
    els.set(id, {
      id, value: "", textContent: "", style: {},
      classList: { contains: () => false, add() {}, remove() {} },
      addEventListener() {},
    });
  }
  return els.get(id);
};
const document = { getElementById: (id) => el(id), body: { classList: { contains: () => false, add() {}, remove() {} } } };

// Throws here = the page's script no longer runs at all, which is itself a failure worth seeing.
let updateCalculator;
try {
  updateCalculator = new Function("document", code + "\nreturn updateCalculator;")(document);
} catch (e) {
  console.log("  FAIL the page's inline script did not even evaluate: " + e.message);
  process.exit(1);
}
ok(typeof updateCalculator === "function", "the page's own updateCalculator was captured");

// --- 3. every container option, household spoons and grams ------------------------------
const selectBlock = html.match(/<select id="containerSelect">([\s\S]*?)<\/select>/);
const options = [...selectBlock[1].matchAll(/<option value="([^"]+)"/g)].map(m => m[1]);
ok(options.length >= 6, "container options found", options.join(","));

const sugars = {};
let checked = 0;
for (const opt of options) {
  if (opt === "custom") continue;
  const volMl = parseFloat(opt);
  const ratio = volMl / 1000;
  const sugarGrams = (25.0 * ratio).toFixed(1);
  const saltGrams = (2.6 * ratio).toFixed(1);

  // grams mode: the printed mass must be exactly the stated ratio, not an approximation.
  el("containerSelect").value = opt;
  el("measureUnit").value = "grams";
  updateCalculator();
  ok(el("resSugar").textContent === `${sugarGrams} grams`,
     `${volMl} mL grams-mode sugar = ${sugarGrams} g`, el("resSugar").textContent);
  ok(el("resSalt").textContent === `${saltGrams} grams`,
     `${volMl} mL grams-mode salt = ${saltGrams} g`, el("resSalt").textContent);

  // household mode: the sugar mass in the parenthetical must still be the stated ratio.
  el("measureUnit").value = "household";
  updateCalculator();
  const printed = el("resSugar").textContent;
  sugars[opt] = printed;
  const g = printed.match(/([\d.]+) g\)$/);   // last figure before the closing paren
  ok(g && g[1] === sugarGrams,
     `${volMl} mL household sugar mass = ${sugarGrams} g`, printed);

  // The exact regression this harness was written for: every option whose sugar scales into
  // the 1.5–3.0 tsp band must print its OWN amount, and never the same constant.
  const sugarTsp = 6.0 * ratio;
  if (sugarTsp < 3.0) {
    const tsp = printed.match(/^([\d.]+) level teaspoons/);
    ok(tsp && Math.abs(parseFloat(tsp[1]) - sugarTsp) < 0.05,
       `${volMl} mL prints its own sugar teaspoons (${sugarTsp.toFixed(1)}), not a constant`,
       printed);
  }
  checked++;
}
ok(checked >= 6, "every container option was exercised", String(checked));

// --- 4. the specific 250 mL defect, named so a regression fails loudly -------------------
ok(sugars["250"] === "1.5 level teaspoons (~6.3 g)",
   "the 250 mL cup prints 1.5 level teaspoons (~6.3 g)", sugars["250"]);
ok(sugars["200"] === "1.2 level teaspoons (~5.0 g)",
   "the 200 mL glass prints 1.2 level teaspoons (~5.0 g)", sugars["200"]);
ok(sugars["1000"] === "6 level teaspoons (~2.0 tbsp / 25.0 g)",
   "the 1 L batch prints 6 level teaspoons", sugars["1000"]);
ok(!/level teaspoons \(~8\.3 g\)/.test(sugars["250"]),
   "the old hardcoded 8.3 g branch is gone", sugars["250"]);

// --- 5. custom volume path, and the salt figure the page's table now states -------------
el("containerSelect").value = "custom";
el("customVolume").value = "2600";
el("measureUnit").value = "household";
updateCalculator();
const g26 = el("resSugar").textContent.match(/([\d.]+) g\)$/);
ok(g26 && g26[1] === "65.0", "a custom 2600 mL batch scales sugar to 65.0 g", el("resSugar").textContent);

// The table's home-mix sodium row must be the arithmetic of the recipe, not a round guess:
// 2.6 g/L of NaCl (58.44 g/mol) is 44.5 mmol/L.
const naRow = html.match(/Canonical Home Recipe \(SSS\)<\/strong><\/td>\s*<td>([^<]+)<\/td>/);
ok(naRow && /4[0-9]/.test(naRow[1]) && !/50/.test(naRow[1]),
   "home-mix sodium row is the corrected ~43-51, not ~50-60", naRow && naRow[1]);

// --- 6. the osmolarity column, on one convention -----------------------------------------
// The defect this catches (2026-09-25). The home-mix row printed its osmolarity AFTER
// brush-border sucrase splits the sucrose — 220-245 first, then 230-250 — while every other row
// printed the solutes as dissolved. The column therefore compared two different quantities, and
// because nothing checked it, the number was hand-edited twice without the mismatch being named.
// Every row is now summed from its own listed solutes and held to the page's own convention.
const table = html.slice(html.indexOf("<table"), html.indexOf("</table>"));
const rows = [...table.matchAll(/<tr>([\s\S]*?)<\/tr>/g)]
  .map(m => [...m[1].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map(c => c[1].replace(/<[^>]+>/g, "").trim()))
  .filter(cells => cells.length === 8);
ok(rows.length === 6, "six solution rows each carry eight numbers", String(rows.length));

// Midpoint of "~43–51" / "10 (Citrate)"; an unquantified cell ("Low") contributes nothing.
// Units differ per column — the sugar column is mmol/L, its parenthetical grams must not be
// added — so each column is parsed on its own terms rather than "all numbers in the cell",
// which is the bug that made this check fail on the first run.
const firstFigure = (cell) => {
  const m = cell.match(/\d+(?:\.\d+)?/);
  return m ? Number(m[0]) : 0;
};
const mid = (cell) => {
  const r = cell.match(/(\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)/);
  return r ? (Number(r[1]) + Number(r[2])) / 2 : firstFigure(cell);
};
const ions = (cell) => {        // "~43–51" -> [43,51]; "45" -> [45,45]; "Low" -> [0,0]
  const r = cell.match(/(\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)/);
  if (r) return [Number(r[1]), Number(r[2])];
  const n = firstFigure(cell);
  return [n, n];
};
// The sugar column: mmol/L as dissolved, so the range must come from it and not from "(25 g)".
const sugarSpan = (cell) => {
  const mmol = cell.match(/([\d.]+)(?:\s*[–-]\s*([\d.]+))?\s*mmol\/L/);
  return mmol ? [Number(mmol[1]), Number(mmol[2] ?? mmol[1])] : [0, 0];
};
const totalSpan = (cell) => {
  const m = cell.match(/([\d.]+)(?:\s*[–-]\s*([\d.]+))?\s*mOsm\/L/);
  return m ? [Number(m[1]), Number(m[2] ?? m[1])] : [0, 0];
};
const span = totalSpan;

const dissolved = rows.map(c => mid(c[1]) + mid(c[2]) + mid(c[3]) + mid(c[4]) + mid(c[5]));
rows.forEach((c, i) => {
  const sum = dissolved[i], printed = mid(c[6]);
  const dev = Math.abs(printed - sum) / sum;
  ok(dev <= 0.12, `${c[0]} prints ${printed} against ${sum} as dissolved`,
     `${c[0]}: ${(dev * 100).toFixed(1)}% off`);
});

// The convention is provable here, not assumed: the two WHO rows sum exactly to their printed
// totals, which is what fixes "as dissolved" as the column's unit.
const row = (name) => rows.find(c => c[0].startsWith(name));
ok(dissolved[rows.indexOf(row("WHO Original"))] === 311, "the 1975 WHO row sums exactly to 311");
ok(dissolved[rows.indexOf(row("WHO Reduced"))] === 245, "the 2006 WHO row sums exactly to 245");

const home = row("Canonical Home Recipe");
const na = ions(home[1]), sucrose = sugarSpan(home[5]);
const drunk = [2 * na[0] + sucrose[0], 2 * na[1] + sucrose[1]];
const hydrolysed = [2 * na[0] + 2 * sucrose[0], 2 * na[1] + 2 * sucrose[1]];
const shown = totalSpan(home[6]);
ok(Math.abs(shown[0] - drunk[0]) <= 3 && Math.abs(shown[1] - drunk[1]) <= 3,
   `the home-mix cell states the as-drunk figure (${drunk[0]}–${drunk[1]})`, home[6]);
ok(/as drunk/i.test(home[6]), "the home-mix cell names its convention", home[6]);
ok(!/2[3-6]\d/.test(home[6]), "no post-hydrolysis number is the column's headline", home[6]);
ok(html.includes(`${hydrolysed[0]}–${hydrolysed[1]}`),
   `the post-hydrolysis figure (${hydrolysed[0]}–${hydrolysed[1]}) is still stated in the footnote`);
const footnote = html.slice(html.indexOf("</table>"), html.indexOf("</table>") + 3000);
ok(/sucrase/i.test(footnote) && /fructose/i.test(footnote),
   "the footnote explains where the post-hydrolysis figure comes from");

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);
