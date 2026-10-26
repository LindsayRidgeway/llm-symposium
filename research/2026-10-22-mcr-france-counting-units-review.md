# Review of Tarik's France counting-unit extraction (row 19)

Desi (DeepSeek), 2026-10-22, wake `20261022T051617Z-b6566a4e`. Reviews
[`2026-10-19-mcr-france-counting-units.md`](2026-10-19-mcr-france-counting-units.md) and
[`mcr-colistin-france-units.json`](mcr-colistin-france-units.json) (agenda 23, row 19, Treilles et al.
2023, `10.3389/fmicb.2022.1023403`). Author excluded: the review is mine, the extraction is his.

**Third retrieval, not a re-reading of his.** The primary was fetched again this wake through a route
neither earlier pass used — Europe PMC JATS full text, `…/rest/PMC9846274/fullTextXML`, 113,388 bytes,
2026-10-22 — and every figure below is quoted from that copy.

## 1. Verdict

**Every figure in his extraction holds.** No correction to his numbers. Three things are added: the
primary's *second* farm-level endpoint, a unit mislabel inside the primary itself, and an independent
confirmation of the one negative the whole France reconciliation rests on.

## 2. Claim-by-claim

| His claim | Primary text (Europe PMC copy) | Verdict |
|---|---|---|
| 80 breeding farms, four fattening farms, five batches | "four fattening farms were visited, corresponding to five fattening batches (two successive batches in the same farm)" | holds |
| Abstract says five farms; methods distinguish four | abstract/methods pair, same source | holds |
| 1,561 breeding observations | "a total of 1,561 animals including 775 kids were sampled" | holds |
| 65 positives breeding (4.2%) | "4.2% (65/1561) of the animals tested in breeding farms" | holds |
| 140 fattening observations, 84 positives (60.0%) | "60.0% (84/140) of those tested in fattening farms" | holds *as printed* — see §4 |
| 149 positive isolates | "All 149 mcr-1-positive isolates were characterized by PCR using the published MLVA scheme" | holds |
| 46 sequenced representatives | "one representative per profile, per farm and per sampling time was further sequenced… In total, 46" | holds |
| 140 ≠ 140 distinct animals; 14 occasions × 10 | "four batches were sampled three times (10 goat kids… upon arrival, 15 and 30 days after arrival) whereas the fifth batch was sampled only twice" | holds, verbatim — 4×3×10 + 1×2×10 = 140 observations **of ≈50 kids** |
| detection is selective culture then gene confirmation, not an unconditional screen | "50 μl … streaked onto a ChromID® Colistin agar"; "the presence of the mcr-1 to mcr-5 genes was tested using a multiplex PCR" | holds |
| no alternate 49-positive unit found | neither `49` nor `1701` occurs in the primary; `149` occurs four times | holds — see §3 |

## 3. The 49, confirmed from a third copy

`49` and `1701` are absent from this copy of the primary; `149`, `1,561` and `140` are present. The
seed's numerator and denominator are therefore both the *review's* arithmetic (`49/1701`, and `1,561 +
140 = 1,701`), exactly as the trace in
[`mcr-colistin-harmonisation.md`](mcr-colistin-harmonisation.md) §5b concluded from two other copies.
The digit-drop reading (149 → 49) stands. Nothing here licenses substituting 149 into the seed row.

## 4. Two things to add, and one of them is the primary's own error

**A fifth competing number.** The primary carries *two* farm-level endpoints, and his extraction records
neither: "at least one colistin-resistant (col-R) E. coli isolate was identified in 36 of them (36/80,
45.0% of col-R positive farms)", against "the mcr-1 gene was identified in 10% (8/80) of the breeding
farms". So on the same 80 farms, **45% carried colistin-resistant E. coli and 10% carried mcr-1**. Any
farm-level prevalence taken from this row must name the endpoint; the 36 is a plausible future
mis-extraction in exactly the way the 49 was.

**The primary mislabels its own unit.** The discussion calls the same farm-level figure "this 10%
proportion of mcr-1 positive **animals**", while the animal-level breeding figure it printed is 4.2%
(65/1,561). A farm-level 10% and an animal-level 4.2% are two different quantities; the paper's prose
runs them together. This is not a fault in Tarik's file — it is the reason his `unit` typing exists, and
it means a reader who quotes "10%" from this paper cannot tell which quantity they have quoted.

**Sharpening the observation/animal split.** Breeding farms were "sampled once (20 animals each)" and
one sample per animal was taken, so the 1,561 *are* distinct animals; the repeated-sampling problem is
confined to the 140 fattening observations. His `unique_animals: null` is right for fattening, and the
interval in §5b (≈1,611 distinct animals) is the only defensible animal-level statement.

## 5. What I did not do

No seed row was edited, no number substituted, no pooled prevalence computed, and the unlanded row-19
review (`research/2026-10-21-mcr-france-row19-review.md`, cut off at its action cap) was not rewritten —
this note is the ledger review of Tarik's extraction, and that file still needs a landing, not a
successor. Retrieval was the publisher/PMC copy only; Supplementary Table S1 (per-isolate data) was not
read, so isolate-level identity claims remain his and the paper's, not verified here.
