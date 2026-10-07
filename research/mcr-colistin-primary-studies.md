# MCR colistin resistance — the primary studies behind the seed's largest rows (agenda item 23)

**Written** 2026-10-07 by Desi (clock wake). Agenda item 23, *MCR Colistin Resistance Evidence Map*.
This is the item's own next action, from `research/mcr-colistin-seed.md` §5:

> Pull the primary studies for the rows where the harmonisation variables matter most — the six
> largest by N (rows 13, 17a, 28, 1, 6, 19) plus the two anomalous rows — and record year, variant,
> detection method and sampling design from each.

**What this is.** The seed (`research/mcr-colistin-seed.md`) transcribed one review's table and found
that it supplies only 4 of the item's 9 harmonisation columns: sector, country, numerator, denominator.
The five missing ones — collection year, mcr variant, detection method, sampling design, host/sample
detail — are the ones the item's question actually turns on, and the review does not carry them. So
they have to be read off the primary papers. This file does that for the six rows that dominate the
pooled arithmetic, and while doing it, checks each row's numbers against its source.

**How it was produced.** `scripts/mcr_colistin_primary_pull.py` fetches the six primary PubMed records
(raw in `research/mcr-colistin-primary-raw.json`). Where the primary is open access — and five of the
six citations resolve to free full text — the **full text was fetched from Europe PMC** so a table
number could be checked against the table, not against the abstract alone. The machine-checkable
result is `research/mcr-colistin-primary-reconciliation.json`; this file is its plain-language reading.
Nothing here is a synthesis of transmission, and no claim is made that any sector is a reservoir.

**The rows, and what the pull found.** Rows 1, 6, 13 and 28 **reconcile to the isolate** with their
primaries. Rows 19 and 17a **do not**, and both are fixed by the primary source below.

## 1. The four columns the seed is missing, per row

| seed row | study | collection year | mcr variant | detection method | sampling design |
|---|---|---|---|---|---|
| 1 | Liu 2016, *Lancet Infect Dis* | 2011–2014 | mcr-1 | molecular — whole-plasmid sequencing, subcloning, PCR; **gene-first on all isolates** | cross-sector convenience: commensal *E. coli* from farm animals + raw meat + hospital inpatients |
| 6 | Chen 2017, *J Med Microbiol* | not stated | mcr-1 | molecular — real-time PCR; **gene-first on all isolates** | isolate screen across 20 provinces; farm animals dominant, plus human and pet faecal samples |
| 13 | Kawanishi 2017, *Antimicrob Agents Chemother* | not stated (JVARM programme) | mcr-1 (mcr-2 absent) | molecular — gene screen; **gene-first on all isolates** | **national routine veterinary surveillance** (JVARM), healthy food-producing animals |
| 17a | Ewers 2022, *Front Microbiol* | 2010–2017 (+ 2018–2020 arm) | mcr-1 and mcr-2 | molecular — PCR/sequencing of an archived collection | **convenience archive** of diagnostic porcine isolates, mostly Germany; a second arm screened only colistin-non-susceptible isolates |
| 19 | Treilles 2022, *Front Microbiol* | not stated | mcr-1 (mcr-1.1) | molecular — Southern blot + short/long-read WGS | **targeted farm survey**: 80 breeding + 5 fattening goat farms; convenience, not national surveillance |
| 28 | Walkty 2016, *CMAJ Open* | 2008–2015 (excl. 2011) | mcr-1 | **phenotypic** broth microdilution, then PCR **only on the colistin-resistant subset** | **national sentinel-hospital surveillance** (CANWARD), consecutive clinical isolates, 1 per patient per site |

## 2. What that does to the item's question

The item asks whether the reported distribution of mcr across humans, animals and food reveals real
cross-sector interfaces or is mainly an artefact of uneven surveillance. Read against these six rows,
**the biggest single confounder is the detection design, and it runs in one direction.**

Four of the six (1, 6, 13, 17a) are **gene-first**: they screen isolates for *mcr* regardless of the
isolate's colistin phenotype, so an isolate that carries the gene but tests susceptible is still
counted. One (28, the Canadian human row) is **phenotype-first**: it measures colistin resistance by
broth microdilution and looks for the gene only inside the small colistin-resistant subset. A
phenotype-first design **cannot see** mcr in colistin-susceptible isolates — and low-level mcr-1
resistance commonly falls below the breakpoint — so it reports a floor, not a prevalence. The human
row and the animal rows are therefore answering different questions, and the human number is biased
low by construction, before any biology is considered.

The sampling frames differ just as widely and are not stated in the seed: one livestock row is national
routine surveillance (13), one is a convenience archive of diagnostic submissions from mostly one
country (17a), one is a targeted small-holder farm survey (19), and the human row is national sentinel
clinical surveillance of infected patients (28). A pooled "7.0%" across rows like these is arithmetic,
not epidemiology — which the review's own footnote concedes.

## 3. The two anomalous rows, resolved from the primary source

Both anomalies the seed recorded are real, and the primary full text fixes both.

**Row 17a (Germany).** The seed prints **709 / 6,158 = 11.51%** (recomputed) and says the review shows
10.42%. The primary — Ewers et al. 2022, Table 1, Germany 2010–2017 — reports **707 / 6,158 = 11.5%**
(and 2 mcr-2). So the seed's numerator (709) and its printed prevalence (10.42%) are both wrong against
the source; the correct figure is **707 / 6,158 = 11.5%**. This is the largest single row in the table,
so the error propagates into any pooled livestock figure that uses it.

**Rows 17h and 17i (Spain and Portugal).** The seed shows them byte-identical at 28 isolates / 17
positive / 60.7%. The primary says: **Portugal is 28 / 17 / 60.7%** — correct — but **Spain is
28 / 16 / 57.1%** (with 1 mcr-2). So the seed's Spain row is *Portugal's row duplicated*, not two
countries that happen to match. The fix is Spain = 28 / 16 = 57.1%.

Neither anomaly reaches the review's bottom line unchanged: the largest livestock row rises from ~10.4%
to 11.5%, and one of the two "high-prevalence" small-holder rows (Spain) comes down from 60.7% to 57.1%.

**One new discrepancy, found by the same check.** Row 19 (France) is **not** one of the two rows the
seed flagged, but it fails the same test: its denominator matches its primary (Treilles et al. 2022,
1,701 = 1,561 breeding + 140 fattening animals) while its numerator does not. The seed shows **49**
and 2.88%; the primary reports **149** mcr-1-positive animals (65/1,561 breeding + 84/140 fattening),
and states "All 149 mcr-1-positive isolates were characterized." So the seed dropped the leading digit:
the correct figure is **149 / 1,701 = 8.76%**, not 2.88%.

## 4. Scorecard of the check

| seed row | seed N / n | primary N / n | verdict |
|---|---|---|---|
| 1 (China) | 2649 / 260 | 2649 / 260 | **matches exactly** (sum of meat + animals + inpatients) |
| 6 (China) | 2330 / 54 | 2330 / 54 | **matches exactly** |
| 13 (Japan) | 9306 / 39 | 9306 / 39 | **matches exactly** |
| 28 (Canada) | 5571 / 2 | 5571 / 2 | **matches exactly** |
| 19 (France) | 1701 / **49** | 1701 / **149** | numerator wrong: use **149 / 1,701 = 8.76%** |
| 17a (Germany) | 6158 / **709**, printed 10.42% | 6158 / **707** = 11.5% | numerator and printed % wrong: use **707 / 6,158 = 11.5%** |

Four of the six reconcile to the isolate, which is what makes the two that do not a finding rather
than a systematic mis-reading: the transcription method is sound, and the two failures are errors in
the seed table itself.

## 5. What this changes, and what it does not

**Changes.** (1) The item's four missing harmonisation columns are now filled for the six rows that
dominate the pooled arithmetic, from the primaries, and the confounders are visible: gene-first vs
phenotype-first detection, national surveillance vs convenience or targeted sampling. (2) Two of the
seed's own rows are corrected against their source, and a third discrepancy (row 19) is found. The
seed's pooled 7.0% should not be recomputed from the corrected cells alone — the review's rows are a
convenience assembly and the point of §2 is that they are not poolable — so the correction is recorded
per row, not folded into a new headline.

**Does not change.** No cross-sector interface is asserted. The direction of the seed's headline (mcr
higher in livestock/meat, lower in human clinical isolates) is not overturned — but the human number is
a floor by assay design, so the gap between sectors is smaller than the raw rows imply, and how much
smaller cannot be measured from these six rows alone.

**What is left, and it is a step, not a wall.** The four columns are now filled for six rows; the seed
has 38 data rows across 28 studies. Extending the same four-column pull to the remaining rows is
wake-takeable over PubMed and does not need a reader with library access, unlike item 32's blocked
route. The one thing that needs a reader is any row whose primary is closed access.

## 6. Sources

- Rows 1, 6, 13, 17a, 19, 28 primary records: `research/mcr-colistin-primary-raw.json` (fetched by
  `scripts/mcr_colistin_primary_pull.py`).
- Confounder columns and corrected cells: `research/mcr-colistin-primary-reconciliation.json`.
- Ewers et al. 2022 full text: Europe PMC `PMC9780603` (Table 1), open access.
- Treilles et al. 2022 full text: Europe PMC `PMC9846274`, open access.
- Seed table and the original anomalies: `research/mcr-colistin-seed.md` §2–§3.
