// Validation harness for docs/works/sanitation.html — 2026-09-28.
//
// Why this exists: the page is a field method a person may act on in an emergency, and it
// carries a calculator. The two things a machine can catch cheaply are (a) that the sourced
// constants did not drift — 30 m, 2 m, 128 g (0.13 L), 1.4 L — and (b) that the page's own
// arithmetic still agrees with the ratios it prints. Same shape as the other Arcade harnesses:
// it lifts the page's SINGLE inline script, runs it against a stub DOM, and checks the numbers
// the page would print. It does not and cannot judge the method; only a reader can.
//
// Run: node tests/validate_sanitation_page.mjs
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const html = fs.readFileSync(path.join(root, "docs/works/sanitation.html"), "utf8");

let pass = 0, fail = 0;
const ok = (cond, label, extra = "") => {
  if (cond) { pass++; console.log("  ok   " + label); }
  else { fail++; console.log("  FAIL " + label + (extra ? "  [" + extra + "]" : "")); }
};
const near = (a, b, eps = 0.005) => Math.abs(a - b) <= eps;

// --- 1. exactly one inline script, and the sourced constants are pinned ----------------
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
ok(blocks.length === 1, "exactly one inline script", "got " + blocks.length);
const code = blocks[0];

ok(/FAECES_L:\s*0\.13/.test(code), "stool constant is 0.13 L (128 g/person/day)");
ok(/URINE_L:\s*1\.4/.test(code), "urine constant is 1.4 L/person/day");
ok(/DIST_MIN_M:\s*30/.test(code), "pit-to-water minimum is 30 m");
ok(/GW_MIN_M:\s*2/.test(code), "pit-bottom-above-groundwater minimum is 2 m");
ok(/WELL_WEAK_M:\s*10/.test(code), "the weaker, disagreeing guideline is 10 m");
ok(/COVER_L:\s*0\.5/.test(code), "cover allowance is 0.5 L/person/day (our figure, labelled)");

// the fetch date must be stated on the page
ok(/2026-09-28/.test(html), "the page states its fetch date, 2026-09-28");
// the deliberate omission must be acknowledged rather than silently missing
ok(/refused (an automated fetch|live fetching)|would not answer/.test(html),
   "the page names the sources that refused a fetch");

// --- 2. run the page's own script against a stub DOM ------------------------------------
const els = new Map();
const el = (id) => {
  if (!els.has(id)) {
    els.set(id, {
      id, value: "", textContent: "", className: "",
      classList: { contains: () => false, add() {}, remove() {} },
      addEventListener() {},
    });
  }
  return els.get(id);
};
const document = { getElementById: (id) => el(id), body: { classList: { contains: () => false, add() {}, remove() {} } } };

let page;
try {
  page = new Function("document", code + "\nreturn { sitingVerdict, bucketFill, updateAll, SAN };")(document);
} catch (e) {
  console.log("  FAIL the page's inline script did not even evaluate: " + e.message);
  process.exit(1);
}
const { sitingVerdict, bucketFill, updateAll, SAN } = page;
ok(typeof sitingVerdict === "function" && typeof bucketFill === "function",
   "the page's own sitingVerdict and bucketFill were captured");

// --- 3. the siting rule, both directions, and the disagreement it names -----------------
let v = sitingVerdict(35, 3, false);
ok(v.ok === true, "35 m & 3 m above water: OK");
v = sitingVerdict(12, 3, false);
ok(v.ok === false && v.fails.indexOf("distance") >= 0, "12 m from water: refused on distance");
ok(v.meetsWeak === true, "12 m still meets the weaker 10 m guideline");
v = sitingVerdict(12, 3, true);
ok(v.ok === false && v.clayMayExcuse === true, "12 m + clay: still refused, but the clay note is raised");
v = sitingVerdict(35, 1, false);
ok(v.ok === false && v.fails.indexOf("groundwater") >= 0, "1 m above the water table: refused on groundwater");
v = sitingVerdict(5, 3, false);
ok(v.ok === false && v.meetsWeak === false, "5 m: even the weak guideline is not met");
v = sitingVerdict(35, "", false);
ok(v.ok === true, "unknown water-table depth is not itself a failure");

// --- 4. the fill estimate, arithmetic on the face ---------------------------------------
let f = bucketFill(4, 7, 20, false);
ok(near(f.perDay, 0.63), "per-day rate without urine is 0.63 L", String(f.perDay));
ok(near(f.litres, 17.64), "4 people x 7 days = 17.64 L", String(f.litres));
ok(f.buckets === 1, "17.64 L fits one 20 L bucket", String(f.buckets));
f = bucketFill(4, 7, 20, true);
ok(near(f.perDay, 2.03), "per-day rate with urine is 2.03 L", String(f.perDay));
ok(f.buckets === Math.ceil((4 * 7 * 2.03) / 20), "the bucket count is the ceiling of volume/size", String(f.buckets));
ok(f.litres > bucketFill(4, 7, 20, false).litres, "mixing urine in raises the volume (the point of keeping it out)");
f = bucketFill(1, 1, 20, false);
ok(near(f.litres, 0.63), "one person, one day = 0.63 L", String(f.litres));

// --- 5. the wired page prints a verdict on its HTML defaults, without throwing -----------
// The stub does not read the `value=` attributes, so seed the values the page ships with.
els.clear();
el("distM").value = "35"; el("gwM").value = "3"; el("clay").value = "no";
el("persons").value = "4"; el("days").value = "7"; el("bucketL").value = "20"; el("urine").value = "no";
updateAll();
const so = el("sitingOut").textContent;
const fo = el("fillOut").textContent;
ok(/OK:/.test(so), "default siting (35 m / 3 m) prints an OK verdict", so);
ok(/0\.63 L per person per day/.test(fo), "default fill prints the per-day rate", fo);
ok(/about 1 bucket/.test(fo), "default fill prints the container count", fo);

// and a siting that fails must actually say so
el("distM").value = "8";
el("gwM").value = "1";
updateAll();
ok(/FAIL:/.test(el("sitingOut").textContent), "a bad siting prints FAIL", el("sitingOut").textContent);
ok(/water table|groundwater/.test(el("sitingOut").textContent), "the water-table failure is named", el("sitingOut").textContent);

console.log(`\n${pass}/${pass + fail} checks passed`);
process.exit(fail ? 1 : 0);
