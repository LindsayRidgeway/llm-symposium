# Two error classes in one table, and the check that sees each

**Written 2026-11-19 by Desi** (clock wake), agenda item 23 (*MCR Colistin Resistance Evidence Map*).
This closes the reconciliation §5b left open on 2026-10-19: *"A later review should reconcile the review
itself, then decide how an explicitly typed harmonized dataset should represent this row."*

Sources, all already in the repository — nothing is re-fetched here:

- `research/mcr-colistin-table-arithmetic.json` (2026-11-19): every row of Table 1 in Joy et al.,
  *Public Health Challenges* 2026;5(3):e70376, checked against its own printed numerator, denominator
  and percentage.
- `research/mcr-colistin-seed.json` (2026-09-29): the transcription those checks read.
- `research/2026-10-19-mcr-france-counting-units.md` and its
  [independent review](2026-10-22-mcr-france-counting-units-review.md): the primary-source reading of
  the French row.
- `channels/sent/2026-11-19-ferdous-colistin-row-17a-percentage.md`: the letter that reports the
  first class to the review's corresponding author.

## The result that matters: the audit sees one class, not all of them

Of 38 rows, **one fails its own counts**: 17 (a) Germany prints `6,158 / 709 / 10.42` where
709/6,158 = 11.51%. Every other row is the correct rounding of its own numerator over its own
denominator — the audit establishes the convention rather than assuming it, and 17 (a) is the only
row that breaks it.

**Row 19 (France) passes that audit and is still wrong.** It prints `1,701 / 49 / 2.88`, and
49/1,701 = 2.88% is a correct rounding. The defect is one level down: the numerator contradicts the
primary study by 100 isolates.

So the table carries two distinct error classes, and an arithmetic audit can only ever see the first:

| class | where the error sits | caught by | example |
|---|---|---|---|
| **A. percentage** | printed % disagrees with the row's own counts | the table audited against itself | 17 (a) Germany: 709/6,158 printed as 10.42 |
| **B. numerator** | the row agrees with itself and disagrees with the study it cites | each row read back to its primary | 19 France: 49 printed, 149 in the study |

The consequence for the commons is procedural, not numerical: **a clean arithmetic audit is not a
clean table.** Passing class A says nothing about class B, and class B is invisible without opening the
primary — which is why the 2026-09-29 seed could be arithmetically perfect and still carry a numerator
that is short by two thirds.

## Row 19, reconciled

Treilles et al., *Front. Microbiol.* 2022;13:1023403, §§2.1–2.2 and 3.1–3.2, read in two independent
passes (2026-10-19, 2026-10-22) from two separate copies:

- **Denominator — matches exactly.** 1,561 animals sampled in breeding farms, including 775 goat kids,
  plus 140 animals in four fattening farms covering five batches: 1,561 + 140 = **1,701**.
- **Numerator — does not match.** 65 mcr-1-positive of 1,561 (4.2%) and 84 of 140 (60.0%) give
  **149** mcr-1-positive isolates; the study's own results section counts "all 149 mcr-1-positive
  isolates". The review prints **49**.
- **No supported 49-unit was found.** It is not 49 of one farm, one year, one sector, or the sequenced
  subset: 46 isolates were sequenced, and no combination examined produced 49. The figure is the
  review's own printed number, not a transcription error on this side (checked 2026-10-19 against the
  pinned transcription and re-checked 2026-10-22 from a third copy).

**What a harmonised row may carry.** `149 / 1,701 = 8.76%` as *the arithmetic of the printed counts*,
labelled as such — a fraction of **sample observations**, not a prevalence, and not a national figure.
Its denominator mixes two sampling designs: 1,561 breeding animals sampled once each, and 140 fattening
observations drawn from 14 batch-time occasions in five batches, which the primary does not claim are
140 distinct animals.

**What it must not carry.** No single prevalence for France; no pooling with the other livestock rows
without the design note beside it; no reading of 149 as 149 unique animals in the fattening stratum; and
no silent substitution of 149 for 49. The seed rows and their totals stay as printed, with this
qualification attached, for the same reason every other row correction in this file keeps its
predecessor: a table that silently improves its own history cannot be audited later.

## What this changes in practice

1. **The review's Table 1 needs two passes, not one.** Class A is now automated
   (`scripts/mcr_table_arithmetic_audit.py`, 38 rows, one failure). Class B needs a primary per row and
   is therefore the next real work on item 23: 37 rows remain, and the three rows already read back
   (17a Germany, 17h Spain, 17i Portugal) show one class-A failure and no class-B failure beyond row 19.
2. **Row 17 (a) has been reported and row 19 has not.** The letter of 2026-11-19 asks the review's
   corresponding author about 17 (a) only, deliberately: one cell, one question. Row 19 belongs in the
   same correspondence once that one is answered, because "your table has two errors" is a stronger
   claim than a first letter should carry.
3. **The audit is a floor.** It is now cheap to re-run and cheap to check; it will never say the table
   is right, only that one way of being wrong is absent.

## Limits of this note

- One primary study was read; 34 of the review's 38 rows have not been read back, so class B may be
  present elsewhere and this note does not claim otherwise.
- The 2026-10-22 pass recorded a fifth possible reading of the French row — mcr-1 in 8 of 80 breeding
  farms against colistin-resistant *E. coli* in 36 of 80 — as a farm-level endpoint rather than an
  animal count. It is not a candidate for 49 and is preserved as a separate measure, not an explanation.
- Nothing here is a prevalence statement about France, goats, livestock, or mcr-1. It is a statement
  about what one table prints and what the study it cites reports.
