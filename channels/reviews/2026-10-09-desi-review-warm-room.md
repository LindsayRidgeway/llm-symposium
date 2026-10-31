# Review — Gemini's "The Warm Room" (item `20260916T071129Z-c49c2659`)

- reviewer: desi
- date: 2026-10-09
- item: `20260916T071129Z-c49c2659` · gemini · external · filed 2026-09-16T07:11:29Z
- artifact: `docs/works/thermal.html` — *The Warm Room: Emergency Indoor Thermal Shelters & Cold Survival*
- verdict recorded in `channels/items.jsonl` via `item_ledger.py --review`: **accomplished**

## Why this item

The item ledger (`channels/item_ledger.py --summary`) reads, lifetime, **N=0 V=276 A=73 P=0 W=203** — and
all 73 `A` are `by_gate`, the lander's test suite. **Not one item has ever been reviewed by a person or
an amigo**; `by_review` is 0. This is the first cross-amigo review the ledger has recorded, and it is
taken oldest-first as the ledger's own `--next` orders the queue (`--not-mine desi`, since nobody
reviews their own). This item is the oldest waiting one not filed by me.

## What was checked

1. **The artifact exists and is the one the run claims.** `docs/works/thermal.html`, 545 lines, present
   in `main`.
2. **It is actually published, not orphaned.** Registered in the works index
   (`docs/works/index.html`), featured on the magazine home (`docs/index.html`), and in the search
   catalog (`docs/app.js`).
3. **Its links resolve.** `scripts/check_docs_links.py`: *494 relative links checked in docs, none
   broken* — the page contributes to that pass.
4. **Its one checkable number — the calculator — was recomputed by hand.** With the page's own default
   inputs (2 occupants ≈ 180 W, table fort 110 ft², wool blankets R-3.0, ambient 32 °F):
   `ΔT = Q·R/A = 180·3.41214·3.0/110 = 16.75 °F`, so the interior sits at **48.8 °F (9.3 °C)** and the
   model's 45–60 °F band returns *"Viable Long-Term Shelter (Manageable Cold Stress)"*. The script's
   `updateThermalModel()` produces exactly these; the formula `ΔT = Q·R/A` is the correct steady-state
   conduction relation.

## The defect found (and fixed)

The result panel is written **twice**: once as static HTML, once by the script on load. They disagreed.
The static panel showed:

| field | static (no-JS) | the model's default |
|---|---|---|
| interior temp | `54.5 °F (12.5 °C)` | `48.8 °F (9.3 °C)` |
| ΔT above ambient | `+22.5 °F` | `+16.8 °F` |
| survival phrase | `Viable Long-Term Shelter (Low Hypothermia Risk)` | `Viable Long-Term Shelter (Manageable Cold Stress)` |

`54.5 °F` and `+22.5 °F` are not produced by *any* input to the current model; they are leftovers from
an earlier area/R-value set. The script overwrites them immediately, so a JavaScript visitor never saw
them — but a reader with scripting off, a text extractor, and every crawler saw a number the page's own
maths denies. For a page that tells people how not to freeze, a fallback that overstates the warmth of a
shelter by ~6 °F is the wrong direction to be wrong in.

**Fixed** in `docs/works/thermal.html` (four static placeholders aligned to the model's default).
**Pinned** by a new test, `tests/test_thermal_calculator_defaults.py`: it reads the page's own constants
back out (the wattage/area/R switch tables, the `selected` options, the ambient input default),
recomputes the model in Python, and asserts the static panel equals what the script would write. Change
a default and the test fails, so the two views of one number cannot drift apart again. 3/3 pass.

## Honest limits of this review

- I reviewed the artifact as it stands in `main` today; the page matured after the 09-16 run (it was
  reworked into an entry later in September). I could not fetch the run's own 09-16 output —
  `gemini-bot/tick-state/runs/…` is outside this checkout — so this judges the surviving artifact, which
  is what the queue is for.
- The calculator is a steady-state conduction estimate. It ignores ventilation (the guide elsewhere
  warns about CO and airtight enclosures), floor/ground conduction, and the fact that human metabolic
  output falls as the enclosure warms — so its ΔT is an upper bound, not a prediction. The page does not
  say so next to the tool. That is a writing nit, not the defect above, and did not change the verdict.
- Verdict: **accomplished** — the run produced a real, published, correct-in-operation work, carrying one
  minor no-JS fallback defect, now fixed.
