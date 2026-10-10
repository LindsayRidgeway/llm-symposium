// Validation harness for docs/works/thermal.html — written 2026-10-10 by Desi (review of
// gemini-bot run 20260916T071129Z-c49c2659, item "Entry 5: thermal shelters").
//
// Why this exists: the page tells a reader how much warmth two bodies actually make inside a
// small enclosure, and then prints a survival verdict from that number. It is a life-safety
// page, so a silent drift in either the arithmetic or the verdict is the failure mode that
// matters. On review (2026-10-10) the page shipped exactly that defect: its server-rendered
// default text said "54.5 °F / +22.5 °F" while its own inline script, given the default
// selections, computes 48.8 °F / +16.8 °F — a 5.7 °F disagreement between the number a reader
// sees before the script runs and the number after. Nothing caught it, because the page had no
// test. This harness runs the page's OWN inline script against a stub DOM and (a) checks every
// printed number against the base formula the page states in its own comment, and (b) pins the
// static default text to the script's default output so the two cannot drift apart again.
//
// Same shape as tests/validate_ors_calculator.mjs and tests/validate_fetchable_page.mjs: a check
// written against the page, recorded as a check.
//
// Run: node tests/validate_thermal_page.mjs
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const html = fs.readFileSync(path.join(root, "docs/works/thermal.html"), "utf8");

let pass = 0, fail = 0;
const ok = (cond, label, extra = "") => {
  if (cond) { pass++; console.log("  ok   " + label); }
  else { fail++; console.log("  FAIL " + label + (extra ? "  [" + extra + "]" : "")); }
};

// --- 1. exactly one inline script, and it is the source of every printed number ----------
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
ok(blocks.length === 1, "exactly one inline script", "got " + blocks.length);
const code = blocks[0] || "";

// --- 2. the base constants are a claim about the world; pin them -------------------------
// Q(BTU/hr) = W * 3.41214 ; dT(°F) = Q * R / area(ft²). The page states each constant in a
// comment, so the pin is against its own stated physics, not an outside opinion.
ok(/watts\s*\*\s*3\.41214/.test(code), "Watts→BTU/hr uses the stated 3.41214 factor");
ok(/\(btuHr\s*\*\s*rVal\)\s*\/\s*areaSqFt/.test(code), "dT = Q·R/Area is the stated formula");

// --- 3. run the page's own script against a stub DOM ------------------------------------
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

let updateThermalModel;
try {
  updateThermalModel = new Function("document", code + "\nreturn updateThermalModel;")(document);
} catch (e) {
  console.log("  FAIL the page's inline script did not even evaluate: " + e.message);
  process.exit(1);
}
ok(typeof updateThermalModel === "function", "the page's own updateThermalModel was captured");

// The inputs the harness believes the page offers, and the numbers they must map to. Kept here
// (not scraped) so an edit that changes a constant fails loudly instead of silently agreeing.
const WATTS = { "1": 90, "2": 180, "3": 270, "4": 360, pet: 230 };
const AREA = { table_fort: 110, large_tent: 180, small_room: 580, large_room: 1400 };
const RVAL = { heavy_blankets: 3.0, thin_tent: 0.8, foil_blankets: 4.2, drywall: 1.5 };

// --- 4. the page offers exactly the options this harness computes over ------------------
for (const [sel, expected] of [["calcOccupants", Object.keys(WATTS)],
                               ["calcShelterType", Object.keys(AREA)],
                               ["calcInsulation", Object.keys(RVAL)]]) {
  const block = html.match(new RegExp(`<select id="${sel}">([\\s\\S]*?)</select>`));
  const opts = block ? [...block[1].matchAll(/<option value="([^"]+)"/g)].map(m => m[1]) : [];
  ok(JSON.stringify(opts) === JSON.stringify(expected),
     `${sel} offers exactly ${expected.join(",")}`, opts.join(","));
}

// --- 5. every combination: printed numbers must equal the page's own stated arithmetic ---
let checked = 0;
for (const occ of Object.keys(WATTS)) {
  for (const shelter of Object.keys(AREA)) {
    for (const insul of Object.keys(RVAL)) {
      for (const ambient of [-10, 20, 32, 45]) {
        const watts = WATTS[occ];
        const btuHr = watts * 3.41214;
        const dT = btuHr * RVAL[insul] / AREA[shelter];
        const insideF = ambient + dT;
        const insideC = (insideF - 32) * 5 / 9;

        el("calcOccupants").value = occ;
        el("calcShelterType").value = shelter;
        el("calcInsulation").value = insul;
        el("calcAmbient").value = String(ambient);
        updateThermalModel();

        ok(el("resWatts").textContent === `${watts} Watts (${btuHr.toFixed(0)} BTU/hr)`,
           `${occ}/${shelter}/${insul}: watts line`, el("resWatts").textContent);
        ok(el("resInsideTemp").textContent === `${insideF.toFixed(1)} °F (${insideC.toFixed(1)} °C)`,
           `${occ}/${shelter}/${insul}@${ambient}: inside temperature`, el("resInsideTemp").textContent);
        ok(el("resTempDiff").textContent ===
             `+${dT.toFixed(1)} °F (+${(dT * 5 / 9).toFixed(1)} °C) above room temperature`,
           `${occ}/${shelter}/${insul}@${ambient}: delta line`, el("resTempDiff").textContent);

        const band = insideF >= 60 ? "Optimal Thermal Comfort (Low Hypothermia Risk)"
          : insideF >= 45 ? "Viable Long-Term Shelter (Manageable Cold Stress)"
          : insideF >= 32 ? "Challenging Cold (Requires High-Grade Sleeping Bags)"
          : "High Hypothermia Risk (Severe Thermal Drain)";
        ok(el("resSurvival").textContent === band,
           `${occ}/${shelter}/${insul}@${ambient}: survival band`, el("resSurvival").textContent);
        checked++;
      }
    }
  }
}
ok(checked === Object.keys(WATTS).length * Object.keys(AREA).length * Object.keys(RVAL).length * 4,
   "every option combination was exercised", String(checked));

// --- 6. the 2026-10-10 regression: static default text must equal the script's default ------
// The defect found on review: the reader sees the static text for a moment before the script
// runs, and it disagreed with the script by 5.7 °F. Pin the four default render slots to the
// script's own output for the default selections (2 people, table fort, wool blankets, 32 °F).
el("calcOccupants").value = "2";
el("calcShelterType").value = "table_fort";
el("calcInsulation").value = "heavy_blankets";
el("calcAmbient").value = "32";
updateThermalModel();
const slot = (id) => {
  const m = html.match(new RegExp(`id="${id}"[^>]*>([^<]*)<`));
  return m ? m[1] : null;
};
for (const id of ["resInsideTemp", "resTempDiff", "resSurvival", "resSurvivalSub"]) {
  ok(slot(id) === el(id).textContent,
     `static default text for #${id} matches the script's default output`,
     `static ${JSON.stringify(slot(id))} vs script ${JSON.stringify(el(id).textContent)}`);
}
// And name the exact stale values so a regression is unambiguous.
ok(slot("resInsideTemp") === "48.8 °F (9.3 °C)",
   "the fixed default inside temperature reads 48.8 °F (9.3 °C)", String(slot("resInsideTemp")));
ok(!/54\.5 °F \(12\.5 °C\)/.test(html),
   "the pre-fix 54.5 °F (12.5 °C) default is gone");

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);
