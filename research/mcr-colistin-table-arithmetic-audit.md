# The review's Table 1, checked against itself — 38 rows, one cell that does not add up

**Written 2026-11-19 by Desi** (clock wake). Agenda item 23 (`23 — MCR Colistin Resistance Evidence Map`),
the arithmetic half of the reconciliation promised in
`channels/sent/2026-11-19-ferdous-colistin-row-17a-percentage.md`. Machine-readable output:
`research/mcr-colistin-table-arithmetic.json` (`python3 scripts/mcr_table_arithmetic_audit.py --write`).

**What this is.** Every row of Table 1 in Joy et al., *Public Health Challenges* 2026;5(3):e70376 — the
28-study, 38-row cross-sector table of mcr prevalence that agenda item 23 is built on — printed
numerator, printed denominator, printed percentage — checked against each other. Nothing is
re-fetched: the transcription is `research/mcr-colistin-seed.json`, taken from the Europe PMC JATS on
2026-09-29, and this file asks only whether the table agrees with itself.

**What this is not.** It is not a prevalence statement about any country, sector or population, and no
figure here should be pooled or published as one: the review's own note (a) defines the column as
(n/N) × 100 for "isolates carrying any mcr gene variant", and its methodological note says the rows are
not directly comparable. A table that adds up is not a table that means anything — it is only a table
whose arithmetic can be relied on when you cite a cell.

## 1. The rule, and why the rule is not a matter of taste

A row is **consistent** if its printed percentage is the correct rounding of 100·n/N *at the number of
decimals it printed*. The table is not column-aligned in precision — 26 rows print two decimals, 12
print one — so the tolerance is per row: 0.05 percentage points at one decimal, 0.005 at two. A row
printed `0.4` for `3/757 = 0.396` is right; judging it against two decimals would be a false positive.

Two conventions were possible — round, or truncate — and the table's own rows decide which it uses.
Fifteen rows discriminate, because truncation and rounding disagree about them; every one of the
fifteen reads as **rounding** (row 6: 54/2,330 = 2.3176 printed `2.32`; row 13: 39/9,306 = 0.4191
printed `0.42`; row 28: 2/5,571 = 0.0359 printed `0.04`). Rows like 17 (f) (`8.82` → `8.8`) carry no
evidence either way and are not counted. So the convention is read off the table rather than assumed
against it — which matters, because the one failing cell fails under both conventions.

## 2. Result: 37 of 38 rows reconcile to their own counts; one does not

**Row 17 (a), Germany, livestock: printed `6,158 / 709 / 10.42`.**

| | value |
|---|---:|
| printed denominator (N) | 6,158 |
| printed numerator (n) | 709 |
| exact 100·n/N | **11.5135%** |
| printed percentage | 10.42% |
| error | **−1.09 pp** |
| tolerance at two decimals | ±0.05 pp |

Under the convention the other 37 rows use, that cell should read **11.51**. The error is 22 times the
largest residual any consistent row carries (0.0286 pp, and that row prints one decimal, where 0.05 is
allowed).

## 3. Where the printed value comes from instead

Three candidate sources were tested against 10.42 at its own precision:

| candidate | value | matches 10.42? |
|---|---:|---|
| pooled rate of its own sector (Livestock, this table's counts) | 8.2043% | no |
| pooled rate of the whole table (Σn/ΣN = 2,647/37,816) | 6.9997% | no |
| **Ewers et al. 2022 study-wide mcr-1 rate (793/7,614)** | **10.4150%** | **yes** |

So the printed figure is not borrowed from anywhere else in the review's own table: it is the
study-wide **mcr-1** rate of the primary study the row is drawn from (Ewers et al., *Front Microbiol*
2022;13:1076315), whose Table 1 gives 7,614 isolates and 793 mcr-1-positive and prints 10.4%. Row 17
(a) is one of eleven sub-rows of that study. The numerator in the cell (709 = 707 mcr-1 + 2 mcr-2) is
that study's Germany row; the percentage is the study's total. And the two are not even the same
quantity: 709 is an **any-mcr** numerator, 10.42 is an **mcr-1** rate. By the review's own note (a),
11.51 is the figure the cell defines; by Ewers' own mcr-1 column, 11.5.

**The reverse question, which the letter to the author asked and could only be guessed at there:** was
the study-wide rate pasted into any *other* row? Tested over all 38 rows, at each row's own precision:
**no other row carries it.** The slip is one cell, not a method. (The honest limit: this test can only
find a pasted rate that is the *Ewers* study-wide rate. A different study's overall figure pasted into
one of the other 27 studies' rows would be invisible here, because those studies' own totals are not on
disk. That check needs the primaries, row by row, and is not done.)

## 4. What the one cell moves, if anyone uses the printed percentages

| figure | from the counts | from the printed percentages | gap |
|---|---:|---:|---:|
| Livestock (25 rows, N = 27,132) | 8.20% | 7.96% | **−0.248 pp** |
| Human (5 rows, N = 6,932) | 0.346% | 0.349% | +0.003 pp |

The whole of the livestock gap is row 17 (a): a reader who recomputes from the printed percentages
gets 0.25 percentage points less livestock prevalence than the same reader gets from the counts in the
same table, and cannot tell why. Row 17 (a) is 16.3% of the table's entire denominator (6,158 of
37,816), which is why one cell is worth that much. The human-sector gap is rounding noise across five
rows and is not an error.

The table sums to **37,816 isolates and 2,647 mcr-positive**, i.e. 7.00% — consistent with the review's
"more than 36,000 isolates". That sum is arithmetic; it is not a pooled prevalence estimate and the
review's own footnote forbids reading it as one.

## 5. The error this method cannot see, stated so it is not mistaken for a clean bill of health

This audit checks each row against **itself**. It therefore catches one of the two error classes in
this table and is blind to the other:

- **Internal errors** (a cell that contradicts its own counts): one found — 17 (a).
- **External errors** (a cell that is internally perfect and contradicts the primary study): row 19,
  France, prints `1,701 / 49 / 2.88` — and 49/1,701 *is* 2.88, so this audit passes it. The primary
  (Treilles et al. 2023) reports **149** positive isolate observations against the same 1,701; the
  review's 49 is short by 100, and no number in that paper yields 49. That trace is
  `mcr-colistin-france-trace.json` and §5b of `research/mcr-colistin-harmonisation.md`.

So a fully reconciled table can still be wrong in 1 row of 38, and this file will say nothing about
it. Arithmetic consistency is cheap and worth having; it is not evidence of correctness. Anyone
citing this table should treat §5b and this file as one check with two halves, not as two votes.

## 6. Reproduce, and what would falsify it

```bash
python3 scripts/mcr_table_arithmetic_audit.py --show     # the summary above, recomputed
python3 scripts/mcr_table_arithmetic_audit.py --write    # regenerate the JSON
python3 -m pytest tests/test_mcr_table_arithmetic.py
```

Falsifiers, in order of likelihood:

1. **A transcription error on our side.** If `research/mcr-colistin-seed.json` misreads the review's
   cell, the whole finding collapses into our own typo. Checked once, directly: §5b step 1 read the
   cell literally off the JATS as `19 France Livestock 1701 49 2.88 [41]`, and the same retrieval
   covers row 17 (a). It has not been re-fetched for this file, which is why the script refuses to
   fetch and points at the transcription instead.
2. **A column definition that is not note (a).** If "Prevalence (%)" is not (n/N)×100 — the note says
   it is — then 37 rows agreeing with it to their last decimal is a coincidence rather than a
   convention, and the audit's premise is wrong.
3. **A different convention.** Ruled out by the fifteen discriminating rows, not by assertion.

## 7. Sources

- **Joy FU, Mouree TZ, Das M, Kabir A.** *mcr-Mediated Colistin Resistance in Escherichia coli: A One
  Health Review of Reported Prevalence Across Human, Animal, Food, and Environmental Sectors.* Public
  Health Challenges 2026;5(3):e70376. DOI `10.1002/puh2.70376`. PMC13577934. Table 1 and notes (a)–(b),
  retrieved 2026-09-29 via the Europe PMC `fullTextXML` endpoint (170,499 bytes).
- **Ewers C. et al.** *Occurrence of mcr-1 and mcr-2 colistin resistance genes in porcine Escherichia
  coli isolates (2010–2020) …* Front Microbiol 2022;13:1076315. DOI `10.3389/fmicb.2022.1076315`.
  PMC9780603. Table 1 (7,614 / 793 / 10.4%; Germany 6,158 / 707 / 11.5 / 2 mcr-2), read 2026-11-19.
- **Treilles M. et al.** *Spread of the mcr-1 colistin-resistance gene in Escherichia coli through
  plasmid transmission and chromosomal transposition in French goats.* Front Microbiol
  2023;13:1023403. DOI `10.3389/fmicb.2022.1023403`. PMID 36687643 (§5 only).
