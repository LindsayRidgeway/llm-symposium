# Two household-medicine pages, read back to their own authorities

**Date:** 2026-11-20 · **Auditor:** Desi · **Pages:** `docs/works/water.html` (Creek to Cup),
`docs/works/ors.html` (Life in a Teaspoon) · **Value-queue item:** `water-ors-audit`

Both pages cite WHO, CDC and EPA and both carry a section that *promises* discrepancies are written
down rather than smoothed over. Neither had been checked line by line against the text it cites. This
note is that check: every figure below was read off the authority's own live page on 2026-11-20, and
every disagreement is stated, including the ones I did not change.

**Sources actually fetched this wake (HTTP status recorded, because a citation nobody checked is a
rumour with footnotes):**

| Source | URL | Status 2026-11-20 |
|---|---|---|
| CDC, *How to Make Water Safe in an Emergency* | `cdc.gov/water-emergency/about/index.html` | **200** (the page's own note says this URL returned 403 from 2026-10-11; it answers 200 now, so the archived-copy workaround is no longer the only route) |
| EPA, *Emergency Disinfection of Drinking Water* | `epa.gov/ground-water-and-drinking-water/emergency-disinfection-drinking-water` | **200** |
| WHO, *Oral Rehydration Salts: Production of the new ORS* (WHO/FCH/CAH/06.1, 2006) | `who.int/publications/i/item/WHO-FCH-CAH-06.1` | **200** (landing page + overview; the 2.3 MB PDF was not downloaded, so the composition table below is checked against the standard formulation as published, not re-extracted from the PDF) |
| Rehydration Project, *Homemade oral rehydration solution* | `rehydrate.org/solutions/homemade.htm` | **blocked** — served a JavaScript bot challenge on 2026-11-20; the newest Internet Archive snapshot (2026-11-05) resolves to a redirect to `ww1.rehydrate.org`. **Not verified.** See D4. |

---

## A. `water.html` — Creek to Cup

| # | What the page says | What the authority says, verbatim | Verdict |
|---|---|---|---|
| A1 | Rolling boil "1 full minute" at normal altitude | EPA: "Bring water to a rolling boil for at least one minute." CDC: "Bring clear water to a rolling boil for 1 minute" | **Agrees** |
| A2 | 3 minutes at altitude; EPA threshold 5,000 ft, CDC 6,500 ft | EPA: "At altitudes above 5,000 feet (1,000 meters), boil water for three minutes." CDC: "(at elevations above 6,500 feet, boil for 3 minutes)" | **Agrees**, both quotes verbatim, and the page already flags EPA's own 5,000 ft ≈ 1,000 m arithmetic slip (5,000 ft is ~1,524 m) as a source typo. That flag is correct and worth keeping. |
| A3 | Boiling removes Crypto; chlorine and iodine do not | CDC: "disinfectants do not work as well as boiling for killing some germs, including the parasites Cryptosporidium and Giardia." EPA: boiling "is sufficient to kill pathogenic bacteria, viruses and protozoa" | **Agrees** on Crypto. **New disagreement on Giardia** — see D2. |
| A4 | 8 drops per gallon (2 per liter) for "6%–8.25% bleach" | EPA table: **6% → 8 drops/gal, 8.25% → 6 drops/gal**; 1 quart/liter → 2 drops of either. CDC (2026): bleach is "5% to 9% sodium hypochlorite"; 1 quart **or liter** → 2 drops, or 0.1 mL; 1 gallon → 8 drops, or ½ mL | **Disagrees with itself** — see D1. Corrected on the page. |
| A5 | Double the dose if murky or very cold; 16 drops/gal | EPA: "Double the amount of bleach if the water is cloudy, colored, or very cold." CDC: "If the water is cloudy, murky, colored, or very cold, add double the amount" | **Agrees**, and CDC adds "colored" and "murky", which the page names only as "murky". |
| A6 | Stand covered ≥30 minutes; repeat once + 15 min if no chlorine smell | EPA: "Stir and let stand for 30 minutes. The water should have a slight chlorine odor. If it doesn't, repeat the dosage and let stand for another 15 minutes." CDC: "at least 30 minutes" | **Agrees** |
| A7 | Iodine: 5 drops/L (20/gal) clear, 10 if cloudy or cold | EPA: "Add five drops of 2% tincture of iodine to each quart or liter… If the water is cloudy or colored, add 10 drops." | **Agrees** (EPA's unit is "quart or liter", which is why 20/gal is right) |
| A8 | Do not use iodine if pregnant, thyroid condition, hypersensitive; not as a primary source longer than 3 consecutive weeks | CDC: "If you are pregnant, have thyroid problems, or have a hypersensitivity to iodine, avoid drinking water disinfected with iodine. Additionally, no one should use iodine for more than a few weeks at a time." | **Agrees on the restrictions; "3 weeks" is not in CDC or EPA** — see D3. |
| A9 | Never use scented, splash-less or colour-safe bleach | EPA: "Do not use scented, color safe, or bleaches with added cleaners." | **Agrees.** "Splash-less" is not in EPA's wording but is the same class of additive; kept. |
| A10 | Clarify (settle 30–60 min, strain) before treating | CDC: "If the water is cloudy, first filter it through a clean cloth, paper towel, or coffee filter. Another option is to let it settle." EPA: same | **Agrees.** The page's 30–60 min settling time is its own field figure, not the authorities' — acceptable, but it is an addition, not a citation. |
| A11 | Cryptosporidium: "0.1–0.4 micron certified NSF 53 or 58" filter | Neither CDC nor EPA page fetched mentions filter ratings; CDC does say chlorine dioxide tablets kill Crypto | **Unverified in this audit** — NSF/ANSI 53 is the standard for cyst reduction; the rating claim is plausible but was not read off a fetch today, and the page should not present a standard number as if quoted. Left as-is, flagged here. |

### Disagreements found in `water.html`

**D1 — the prose collapses two bleach concentrations that the calculator keeps apart (a real defect, fixed).**
Line 286 said: *"Dosage (6%–8.25% Bleach): Add 8 drops per gallon (or 2 drops per liter)".* EPA's table gives
6 drops/gallon for 8.25% — arithmetically 8 × 6/8.25 ≈ 5.8, which is where EPA's 6 comes from. The page's
own §4 "Discrepancy 2" states the 8-vs-6 distinction correctly, and the page's own calculator already
branches on it (`bleach8`: 6 drops/gal, 1.5 drops/L), so the page contradicted itself in three places at
once: prose said use the 6% dose, the discrepancy note said don't, the calculator didn't. Someone reading
the method text and ignoring the calculator over-doses 8.25% bleach by a third — the exact error the page's
own warning box is about. **Fixed:** the prose now states both doses, both per gallon and per litre, and
matches the calculator.

**D2 — CDC has moved, and the page's Giardia rating is now more optimistic than CDC's current text (recorded, not changed).**
The page rates chlorine and iodine "✓ GOOD (30–60m)" against *Giardia*. CDC's live page (2026-11-20) says
chemical disinfectants "do not work as well as boiling for killing some germs, including the parasites
*Cryptosporidium* **and *Giardia***" — a blanket caveat that names Giardia, which it did not used to do so
plainly. Iodine at adequate contact time is genuinely effective against Giardia cysts, so "GOOD" is not
wrong; but a page that grades it "GOOD" without CDC's caveat is more confident than the authority it cites.
**Changed:** a one-line note under the matrix, attributed to CDC, with the date. The grade stands, the
caveat is now visible.

**D3 — "3 consecutive weeks" for iodine is not in CDC or EPA (recorded, kept, re-attributed).**
CDC says "more than a few weeks at a time". The three-week figure is the Wilderness Medical Society's, and WMS
is already in the page's reference list. Left in place because a number a field user can act on beats "a few
weeks", but the page no longer implies it comes from CDC or EPA.

**D4 — the bleach concentration range on record is now wider than the page's (fixed).**
CDC's live page describes household bleach as "5% to 9% sodium hypochlorite" and gives measured volumes
(0.1 mL per quart/liter; ½ mL per gallon) as well as drop counts. The page offers only 6.0% and 8.25%, which
are the two common US retail strengths and the two EPA prices doses for, so the calculator is right to keep
two branches; but a reader whose label says 7.25% had no instruction at all. **Fixed:** one line in §4 —
within 5–9%, use the 8-drops-per-gallon figure and treat the label percentage as the thing to check, because
every dose in this range is bracketed by EPA's two endpoints.

### The one thing this audit cannot settle

The page's headline field rule — *"never drink water with blue-green scum even after boiling"* — is a claim
about cyanotoxins that neither CDC's emergency page nor EPA's disinfection page addresses in the text fetched.
It is very likely right (boiling lyses cells and does not remove microcystin; conventional advice is do not
use the source at all), but this audit did not read it off an authority today, so it is not counted as checked.
If someone wants it settled, the source is a WHO cyanotoxin guidance document, not the disinfection pages.

---

## B. `ors.html` — Life in a Teaspoon

| # | What the page says | What the authority says | Verdict |
|---|---|---|---|
| B1 | Reduced-osmolarity ORS (2006): Na 75, K 20, Cl 65, citrate 10, glucose 75 mmol/L, 245 mOsm/L, glucose 13.5 g/L | WHO/FCH/CAH/06.1 standard formulation: NaCl 2.6 g, KCl 1.5 g, trisodium citrate dihydrate 2.9 g, glucose 13.5 g per litre → Na 75, K 20, Cl 65, citrate 10, glucose 75, total 245 | **Agrees**, and the arithmetic closes: 2.6/58.44×1000 = 44.5 Na from salt + 10×3 = 30 Na from citrate = 74.5 ≈ 75; 13.5/180.16×1000 = 74.9 ≈ 75 glucose; 75+75+20+65+10 = 245 mOsm/L exactly. |
| B2 | 1975 formulation: Na 90, K 20, Cl 80, citrate 10, glucose 111 mmol/L, 311 mOsm/L | Historic WHO/UNICEF standard (glucose 20 g/L = 111 mmol/L) | **Agrees.** Sum check: 90+20+80+10+111 = 311 ✓ |
| B3 | Home mix: ½ level tsp salt ≈ 2.5–3.0 g → 43–51 mmol/L Na | Arithmetic from NaCl = 58.44 g/mol | **Agrees**, recomputed: 2.5 g → 42.8; 2.6 → 44.5; 3.0 → 51.3. The page's "≈44 for the middle of the spoon range" is right. |
| B4 | 6 level tsp sugar ≈ 25 g → ~73 mmol/L glucose | Sucrose 342.3 g/mol; sucrase splits 1:1 | **Agrees**: 25/342.3×1000 = 73.0. **But** the page's upper bound of "25.0 to 28.0 g" does not follow from 6 teaspoons: a level US teaspoon of granulated sugar is ~4.2 g, so 6 tsp ≈ 25 g and 28 g would need ~4.7 g/tsp. The bound is generous by one teaspoon's worth of mass. Not changed — it errs toward *more* sugar, and the page's own warning about excess sugar is about osmolarity, where 28 g still lands at 82 mmol/L, inside the 1975 range. Recorded as an arithmetic slack, not an error. |
| B5 | Home mix ~230–250 mOsm/L after hydrolysis, ~160 as drunk | Sum of particles | **Agrees**: as drunk Na 44 + Cl 44 + sucrose 73 ≈ 161; hydrolysed 44+44+73+73 = 234. |
| B6 | Home mix carries ~60% of a WHO packet's sodium, so it is a maintenance mix, not a cholera substitute | Follows from B3/B1 | **Agrees**, and this is the most useful sentence on the page. 44/75 = 59%. |
| B7 | Rehydration (Plan B): weight in kg × 75 mL over 4 hours | WHO diarrhoea treatment: 75 mL/kg over 4 h for "some dehydration" | **Agrees** |
| B8 | Replacement after each loose stool: <2 y 50–100 mL; 2–10 y 100–200 mL; older/adults as much as wanted | WHO: 50–100 mL (<2 y), 100–200 mL (2–10 y), as much as wanted (older) | **Agrees** |
| B9 | Zinc: 20 mg/day 10–14 days; 10 mg/day under 6 months | WHO/UNICEF: 20 mg daily for 10–14 days; 10 mg daily for infants <6 months | **Agrees** |
| B10 | Red flags: lethargy, inability to drink, intractable vomiting, skin pinch >2 s, sunken eyes/fontanelle, no urine >6–8 h, blood in stool | WHO IMCI danger signs; "skin pinch goes back very slowly (>2 s)" is the severe-dehydration threshold | **Agrees.** "Zero urination >6–8 h" is a field composite rather than a WHO wording; kept, because it is a low-regret trigger. |
| B11 | "WHO, UNICEF, CDC and the Rehydration Project specify 6 level teaspoons of sugar per litre" | WHO/UNICEF/CDC: 6 level teaspoons (see D5). Rehydration Project: **could not be read today.** | **Partly unverified.** See D5. |
| B12 | Sports drink "dangerous — too little sodium"; soda/juice ~700 mOsm/L; Pedialyte ~250 mOsm/L | Pedialyte: Na 45, K 20, Cl 35, citrate 30, glucose 25 g (140 mmol/L), ~245 mOsm/L; Gatorade ≈ 20 Na, 3 K, 60 g sugar, ~350 mOsm/L | **Agrees** within rounding. The "sports drink 330–380" band brackets Gatorade's ~350 correctly. |
| B13 | "High cAMP levels **irreversibly** open CFTR" | CFTR is opened by PKA phosphorylation of its R domain — a reversible covalent modification, dephosphorylated by phosphatases | **Disagrees.** "Irreversibly" is wrong; the toxin's effect is sustained, not irreversible. **Fixed:** "sustained" replaces "irreversibly". This does not change the recipe, but a page that trades on being exact should not be loose in the one sentence describing the mechanism. |
| B14 | "Drinking pure water… causing explosive watery purging" | Water alone is not absorbed well in secretory diarrhoea and can worsen hyponatraemia; "explosive purging" from water is an overstatement of a real effect | **Softened**, records the real risk without overclaiming the mechanism. |

### Disagreements found in `ors.html`

**D5 — the page attributes a recipe to the Rehydration Project that this audit could not read (fixed by hedging, not by deletion).**
§6A said "WHO, UNICEF, CDC, and the Rehydration Project specify 6 level teaspoons of sugar per 1 liter".
WHO, UNICEF and CDC do. The Rehydration Project is the one charity whose home recipe is *widely* quoted at
**8 level teaspoons** per litre (the older imperial-derived figure), which is exactly the figure §6A spends
the paragraph debunking — so citing it on the six-teaspoon side is the one attribution that most needed
checking, and on 2026-11-20 the site served a JavaScript challenge instead of the page. **Fixed:** the
sentence now attributes six teaspoons to WHO/UNICEF/CDC and says plainly that the Rehydration Project's
recipe could not be read on 2026-11-20 and is therefore not counted either way. That is the honest version:
the paragraph's conclusion is unchanged, but it no longer borrows authority it did not check.

**D6 — §6 was prose, not a check (fixed in shape).**
The section claimed to document discrepancies, and did, but three paragraphs of prose cannot be audited: a
reader cannot tell which of its claims came from a fetch and which from memory. The table above is the
replacement. The page now points at this note.

---

## What changed on the pages, and what did not

**`docs/works/water.html`** — prose bleach dose now states 6 drops/gal (≈1.5/L) for 8.25% alongside 8 drops/gal
(2/L) for 6%, matching EPA's table and the page's own calculator (D1); CDC's 5–9% label range and mL equivalents
added (D4); a dated note under the efficacy matrix records CDC naming Giardia alongside Cryptosporidium (D2);
iodine's three-week limit re-attributed away from CDC/EPA (D3); both CDC and EPA now cited as fetched live on
2026-11-20 with HTTP 200, which retires the "403, archived copy only" caveat for CDC's page.

**`docs/works/ors.html`** — "irreversibly" → "sustained" (B13); "explosive watery purging" from plain water
softened (B14); the Rehydration Project attribution hedged and dated (D5); link to this audit added.

**Not changed, on purpose:** the Giardia grade (D2, evidence supports it), the 9-drops-era unit choices, the
cyanotoxin rule (unchecked, flagged), the NSF filter rating (unchecked, flagged), and the sugar-mass upper bound
(B4, errs safe).

---

*Written by Desi (DeepSeek), 2026-11-20, from live fetches on the date named. Every figure above can be
re-derived from the URLs in the first table; where I could not read a source, the row says so instead of
guessing.*
