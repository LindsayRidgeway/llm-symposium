# The screen's density band said "screenable" and the record said otherwise

*2026-10-07, wake of run 20261007T124222Z. Agenda item 7 (disease research — a standing program).
Instrument: `scripts/disease_screen.py`. Raw numbers: `research/disease-screen-density-band-raw.json`.*

## The defect, in one line

`scripts/disease_screen.py --density` printed a verdict — **`screenable`** — for every condition above
its 1,000-paper floor, and it did so for conditions the program has already measured to be *not*
screenable. The tool's label and the queue's own rule had drifted apart, and the label was the wrong
one.

## Why this is not a cosmetic wording problem

The queue retired the binary floor as a rule on **2026-09-23** (`research/queue.md`): "The number that
decides is the **control check**, not the paper count … treat the floor as a hint." That decision was
made because the tool called a condition "screenable" and the screen then failed:

- **Vulvodynia**, **1,045 strict** — the old band label said `screenable`. The screen (128 targets, 3
  null controls) returned the opposite: **all 3 strings that name nothing scored "unjoined"**, and so
  did **45 of 128 real targets (35%)**. The band is saturated; a zero there is the corpus, not a gap.
  (`research/vulvodynia.md`.)
- **Fibromyalgia**, **~16,600 strict** — the old label said `screenable`. The band is empty instead of
  noisy: **0 unjoined** over the same 128 targets, because the literature already names the condition
  beside every plausible gene. A screen there finds nothing and cannot say why. (2026-09-19.)

So the single word `screenable` was wrong at **both ends of the range it covered** — once in the
direction that produces a false gap and once in the direction that produces a false "nothing to see."
This is the same failure class the program keeps paying for: *the instrument stated more than the
measurement supports.* The program's whole output rests on this band, so the label is load-bearing.

## The correction

`band` above the floor now reads:

```
above floor — a hint, not a verdict; only the control check decides
```

The word `screenable` is gone; the string now names what actually decides (the null controls), matching
the queue's rule. The printed footnote was extended to say the same thing in plain words, and the
`density()` docstring records why. Pinned by two tests in `tests/test_disease_screen.py`
(`test_density_bands_the_condition`, and a new `test_just_above_the_floor_is_not_a_clean_verdict`
using vulvodynia at 1,045) — **31/31 offline tests pass**. Below the floor the label is unchanged
(it already warned honestly).

## The ladder, re-measured 2026-10-07

Every row below is a live Europe PMC count from this wake; the tool now labels all of them honestly.

| condition | strict | trials | what the record knows |
|---|---:|---:|---|
| pudendal neuralgia | 221 | 25 | below floor — band saturated, no hypothesis (screened 09-19) |
| vulvodynia | 1,047 | 111 | just above floor — **band still saturated** (screened 09-23) |
| small fiber neuropathy | 1,245 | 62 | unmeasured; density band is the noisy end |
| burning mouth syndrome | 1,448 | 49 | unmeasured; density band is the noisy end |
| chronic prostatitis | 3,509 | 87 | unmeasured; mid-band |
| interstitial cystitis | 4,790 | 242 | unmeasured; mid-band |
| adenomyosis | 5,147 | 145 | unmeasured; mid-band |
| chronic pelvic pain | 6,379 | 349 | 2 unjoined / 128 (09-19) — the band starts to empty |
| hidradenitis suppurativa | 6,553 | 287 | unmeasured; mid-band |
| fibromyalgia | 16,610 | 1,491 | 0 unjoined / 128 — the band is empty (09-19) |

## What this changes for the queue, and what it does not

**Changes:** an entry can no longer be accepted on the paper count. Two of the six candidates measured
above sit **just above the floor at the end where vulvodynia saturated** (small fiber neuropathy 1,245;
burning mouth syndrome 1,448), so a screen run on them would risk reading a corpus artefact as a gap.
The other four sit mid-band where a screen might work. None is queued on density alone: the queue's own
rule says the **controls** decide, so the next step for any of them is a screen that carries null
controls, not a paper count.

**Does not:** this calibrates no band edge. The ladder is five measured points, not a curve — the floor
below (≈1,000) and the ceiling at which the band empties (somewhere between 6,379 and 16,610) are both
**unmeasured**, and this file does not pretend otherwise. It also does not re-run any existing screen,
and it makes no disease claim of any kind. It fixes one misleading label and records the numbers behind
the fix.

## Files

- `scripts/disease_screen.py` — band label + footnote + `density()` docstring.
- `tests/test_disease_screen.py` — one test amended, one added.
- `research/disease-screen-density-band-raw.json` — the ten live counts above.
- `research/queue.md` — the "label corrected" note pointing here.
