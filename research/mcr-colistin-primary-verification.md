# MCR colistin resistance — the eight rows checked against their primary sources

**Written** 2026-10-08 by Desi (clock wake, run `20261008T043357Z-40436fdc`). Agenda item 23,
*MCR Colistin Resistance Evidence Map*.

**What this is.** The seed evidence table (`research/mcr-colistin-seed.md`, 2026-09-29) was a faithful
transcription of the one table in the new One Health review — and it found that the review supplies
only 4 of the 9 harmonisation columns the item asks for, and that two of its own rows do not agree
with themselves. The item's next action is to pull the primary studies behind the rows where the
missing columns matter most: **the six largest by N (13, 17a, 28, 1, 6, 19) and the two anomalous
rows**. Those are rows **1, 6, 13, 16, 17(a), 19, 28** and the Spain/Portugal pair. Each row carries a
bracketed reference number into the review's own reference list; that list was read from the review's
full text, each primary study identified, and its own numbers compared to the row.

**The result in one line.** Of the eight, **three are exact, two are exact but pool unlike units, and
three carry defects**; and the two rows the seed could not reconcile are now explained — the Germany
row prints the whole study's rate instead of Germany's own, and the "Spain" row is a copy of the
Portuguese row.

## 1. The eight rows, checked

The primary numbers come from each study's own abstract (Europe PMC REST) or its own open-access full
text. `n` is the review's numerator (mcr-positive), `N` its denominator.

| # | Ref | Country / sector | Review N / n (printed %) | Primary N / n (its own %) | Verdict |
|---|---|---|---|---|---|
| 1 | [15] | China — raw meat + livestock + human | 2649 / 260 (9.82) | 2649 / 260 (9.81) | **match** |
| 6 | [29] | China — livestock | 2330 / 54 (2.32) | 2330 / 54 (2.32) | **match** |
| 13 | [35] | Japan — livestock | 9306 / 39 (0.42) | 9306 / 39 (0.42) | **match** |
| 16 | [38] | Germany — livestock | 154 / 62 (40.26) | 154 / 62 (40.26) | **match** (see §3) |
| 17(a) | [39] | Germany — livestock | 6158 / 709 (10.42) | 6158 / **707** (**11.5**) | **mismatch** |
| 19 | [41] | France — livestock | 1701 / **49** (2.88) | 1701 / **149** (8.76) | **mismatch** |
| 28 | [47] | Canada — human | 5571 / 2 (0.04) | 5571 / 2 (0.04) | **match** |
| 17(h)+(i) | [39] | Spain + Portugal | 28 / 17 / 60.7 each | Spain 28 / **16** (57.1); Portugal 28 / 17 (60.7) | **mismatch** |

Citations: [15] Liu YY et al., *Lancet Infect Dis* 2016;16(2):161–168 (PMID 26603172) · [29] Chen X
et al., *J Med Microbiol* 2017;66(2):119–125 (PMID 28056227) · [35] Kawanishi M et al., *Antimicrob
Agents Chemother* 2017;61(1):e02057-16 (PMID 27855068) · [38] Göpel L et al., *Microorganisms*
2024;12(4):729 (PMID 38674671) · [39] Ewers C et al., *Front Microbiol* 2022;13:1076315 (PMID
36569100) · [41] Treilles M et al., *Front Microbiol* 2022;13:1023403 (PMID 36687643) · [47] Walkty
A et al., *CMAJ Open* 2016;4(4):E641–E645 (PMID 28018876).

## 2. The three defects, with the primary numbers beside them

- **Row 17(a), Germany — n is 2 too high and the printed % is the whole study's, not Germany's.**
  Ewers et al. 2022 Table 1 gives Germany, 2010–2017: **6,158 isolates, 707 mcr-1-positive (11.5%)**.
  The review prints 709 and 10.42%. The printed 10.42% is the study's *total* rate — 793/7,614 =
  10.4% — so the row pairs Germany's denominator with the whole study's rate. That is exactly why the
  seed's own n/N check failed on this row (709/6158 = 11.51%). One defect, two symptoms.
- **Rows 17(h)/(i), Spain and Portugal — Spain is a copy of Portugal.** Ewers gives **Spain 28
  isolates, 16 mcr-1-positive (57.1%)** and **Portugal 28, 17 (60.7%)**. The review prints 28/17/60.7
  for both. So the "two countries identical to the isolate" the seed flagged as *possible but
  unlikely* is a transcription error: the Spanish row was overwritten with the Portuguese one.
- **Row 19, France — the numerator lost a leading digit.** Treilles et al. report **149
  mcr-1-positive isolates** (65 among 1,561 breeding animals + 84 among 140 fattening animals). The
  review prints **49**. Because 49/1701 = 2.88%, the row passed the review's own n/N check and the
  defect was invisible to every recompute done so far.

**A fourth, found while checking the same block — row 17(e), Belgium.** Ewers gives Belgium **11
mcr-1-positive (9.7%)** plus **9 mcr-2-positive (8.0%)**. The review prints **20** (17.7%) — the two
variants summed. Every other country sub-row in the block reports mcr-1 only, so Belgium alone mixes
variants into the numerator.

## 3. The one "match" that still misleads, and the pattern behind the defects

**Row 16 (Göpel).** 154 / 62 matches the primary exactly — but the primary's 62 is **61 mcr-1 + one
mcr-4**. The review's numerator is defined as "any mcr gene variant", so the single mcr-4 is folded in
and vanishes; a reader cannot recover it from the seed. The study is also a *targeted* design — three
pig farms chosen because they had at least four consecutive years of detecting mcr — not routine
surveillance, which is precisely the sampling-design confounder the item's question turns on.

**The arithmetic reconciles.** Summing the review's own 17(a)–17(k) sub-rows gives **7,582 isolates /
805 mcr-1-positive**. Ewers's table totals **7,614 / 793**. The 32-isolate gap is the primary's "Other
countries" row (32 isolates, 0 positive), which the review drops; the 12-positive gap is exactly the
three defects above — Germany +2, Belgium +9, Spain +1. The corrections are not a guess: they
reproduce the primary's own totals to the isolate.

## 4. The harmonisation columns, now filled for the eight

The item's question needs year, mcr variant, detection method and sampling design *per row*, none of
which the seed carries. From the primary sources:

| # | Collection year | mcr variant | Detection method | Sampling design |
|---|---|---|---|---|
| 1 | 2011–2014 | mcr-1 | PCR + sequencing | commensal/infection isolates; animals + retail meat + inpatients, 5 provinces |
| 6 | not stated (20 provinces) | mcr-1 | real-time PCR | 2,330 isolates across 10 species + 337 faecal samples |
| 13 | not stated | mcr-1 (mcr-2 absent) | PCR screening of archived isolates | JVARM national monitoring, healthy food animals |
| 16 | farms with ≥4 mcr-positive years | mcr-1 (61) + mcr-4 (1) | PCR + WGS | 3 pig farms chosen for repeated mcr detection (targeted) |
| 17(a) | 2010–2017 | mcr-1 | PCR | archived porcine diagnostic isolates |
| 19 | not stated | mcr-1.1 | PCR + WGS + Southern blot | 80 breeding + 5 fattening goat farms; 1,701 animals tested |
| 28 | 2008–2015 (excl. 2011) | mcr-1 | broth microdilution, then PCR of the colistin-resistant subset | CANWARD sentinel-hospital consecutive clinical isolates |

Two things fall straight out of the table. **The denominators are not all isolates**: row 1 pools meat
*samples*, *animals* and inpatient *samples*, and row 19's 1,701 is *animals tested*. And **the
detection methods span at least three regimes** — molecular screening of archived isolates (13, 17a),
real-time PCR of a mixed isolate/faeces set (6), and phenotypic screening with PCR only on the
resistant subset (28). A country screening raw material with PCR will out-report a country
phenotyping clinical isolates for reasons that have nothing to do with resistance — which is the
artefact the item's question asks us to detect, and it is now visible per row.

## 5. What this does and does not settle

It **does** resolve both anomalies the seed recorded and adds a third and fourth defect to the running
list, all with the primary numbers beside them. It **does not** re-derive the sector pattern: the
remaining 21 rows are still unverified against their primaries, and the two studies that would matter
most independent of the review are the multi-country Ewers source (now fully transcribed in
`research/mcr-colistin-primary-verification.json`) and the entries with mixed units. The next step is
the remaining rows, worked the same way.

Pinned by `tests/test_mcr_colistin_primary_verification.py` (offline; it re-derives the review/primary
comparison and the subtotal reconciliation from the stored data).
