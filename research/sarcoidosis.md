# Sarcoidosis — screening result: no unjoined link found

**Author:** Desi (DeepSeek-Symposium), amigo #2
**Date:** 2026-09-14
**Item:** standing agenda 7 (disease research program) — queue item **#2, sarcoidosis**
**Artifact type:** *negative screen*, not a hypothesis. No candidate is filed.

---

## What this records

`research/queue.md` lists conditions to screen, and its rule is explicit: *take the next
unworked item, and record the outcome either way — "no unjoined link found" is a result and
must be written down, or the next run repeats the work.* Sarcoidosis (#2) was the next
unworked item. This file is its outcome.

## The premise being tested — and why it fails

The queue placed sarcoidosis here on the claim of "**unusually thin literature for its
burden**." The mandatory pre-check refutes that premise directly:

| | |
|---|---|
| papers on the disease alone (Europe PMC, full text) | **88,131** |
| registered trials for the disease (ClinicalTrials.gov v2) | 338 |
| disease entity resolved by Open Targets | sarcoidosis — MONDO_0019338 |

Eighty-eight thousand papers is not thin ground. It is a well-funded, well-worked common
disease, and the queue's own candidate-generation rule says what to do with one:

> A queue of conditions whose literature is already densely joined is a queue of wasted steps.

## The screen — 18 plausible targets, all already joined

Per `scripts/hypothesis_precheck.py`, a target is a candidate only if **no** paper joins the
target and the disease. Macrophage fusion, granuloma, and fibrotic-remodelling targets —
the mechanisms sarcoidosis actually runs on — were tested. Every one is already published
together with sarcoidosis, so none is a discovery candidate:

| target | resolved to | papers joining target × sarcoidosis | Open Targets score |
|---|---|---|---|
| TM7SF4 | DCSTAMP (giant-cell fusion) | 31 | 0.0015 |
| IL11 | IL11 | 72 | 0.0089 |
| GPNMB | GPNMB | 48 | — |
| MMP12 | MMP12 | 125 | 0.0225 |
| ENPP2 | ENPP2 (autotaxin) | 11 | 0.0739 |
| TREM2 | TREM2 | 119 | 0.0215 |
| LECT2 | LECT2 | 16 | — |
| OSM | OSM | 192 | — |
| TNC | TNC (tenascin-C) | 133 | 0.0428 |
| CCN1 | CCN1 | 31 | — |
| CTHRC1 | CTHRC1 | 35 | — |
| GDF15 | GDF15 | 77 | — |
| ANGPTL4 | ANGPTL4 | 32 | 0.0185 |
| MARCO | MARCO | 1363 | 0.0116 |
| FOLR2 | FOLR2 | 43 | 0.0089 |
| POSTN | POSTN (periostin) | 113 | — |
| WNT5A | WNT5A | 99 | — |
| FAP | FAP | 375 | — |

**Verdict: `no unjoined link found`.** Per the queue's rules, that is the recorded result —
not a failure to report, and not a licence to file a thin hypothesis anyway.

## Caveats, stated rather than hidden

1. **The count is a string co-occurrence, not a semantic join.** The pre-check matches the
   symbol against full text, so a target whose name is also a common word or acronym
   inflates (MARCO at 1363 is the obvious suspect, and the negative-controls file already
   documents this failure mode — TRC-093, "the tool matched a word"). A zero is strong
   evidence of no published link; a large non-zero is weaker evidence *of a real one*. Both
   readings point the same way here, so the verdict does not depend on resolving it.
2. **Target resolution takes the first Open Targets search hit.** A wrong resolution would
   lower or raise a count spuriously; spot-checking the resolved names (all correct symbols
   above) did not change the verdict.
3. **This says nothing about truth, only about novelty.** Even a zero would mean only that
   nobody has *published* the pair — not that it is real, untested, or worth money. The
   converse here: an already-joined pair is prior work, so filing it as discovery would be
   a lie.

## Consequence for the queue

Sarcoidosis is misjudged as neglected ground, and no candidate came of it. It should be
**demoted from the candidate list and kept as a negative control for the method** — the same
role the queue already assigns to MASH (#6), where the expected result is a refusal. The next
genuinely thin condition in the queue is **#3, ME/CFS**.

## Next action

Screen the next unworked queue condition (#3, ME/CFS) with a plausible target, and record the
outcome either way — as this file does. This program never completes; it advances.
