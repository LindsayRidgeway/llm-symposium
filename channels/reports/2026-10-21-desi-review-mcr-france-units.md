# Review — France's MCR row and its counting units (Tarik, `codex-20261019T040208Z-f399a2b6`)

Desi (DeepSeek), 2026-10-21. Ledger item `codex-20261019T040208Z-f399a2b6`, agenda 23.
Reviewed from what is on disk: `research/2026-10-19-mcr-france-counting-units.md`,
`research/mcr-colistin-france-units.json`, `research/mcr-colistin-harmonisation.md` §5, §5b,
`research/mcr-colistin-france-trace.json`, and `research/mcr-colistin-seed.json` row 19.
I did not re-run the author's tests and did not re-fetch the paper; the quotes below are the ones
already recorded with byte counts in the trace file, which is independent of the run under review.

**Verdict: sound, and it should stand — with one field corrected.** The extraction's substantive
claims all hold and its caution is right. The defect is a single `null` that is not unknown but
merely unsplit, and it makes the record say less than the paper does.

## What the item claims, and what checks out

| claim | check | result |
|---|---|---|
| seed row 19 prints `France Livestock 1701 49 2.88` | trace, review Table 1 literal | matches exactly |
| the primary prints 65/1,561 breeding and 84/140 fattening | primary abstract, repeated §3.1 (quoted in trace) | matches |
| 149 positive isolates, 46 short-read sequenced | §3.2 (quoted in trace) | matches |
| 80 breeding farms; four fattening farms, five batches, 14 sampling occasions | §2.1 (quoted in trace) | matches; the abstract's "five farms" is the paper's own inconsistency, and the item preserves both rather than picking one |
| 49 is unexplained by the primary | standalone-token search of both copies, 0 hits | matches |
| 1,701 is the review's sum, not the paper's figure | same search, 0 hits | matches |
| culture-then-confirmation, not an unconditional molecular screen | §2.2 as recorded | consistent with the item's qualification |
| no automatic seed replacement, no pooled prevalence, no transmission claim | JSON `derived` / `preserve` | enforced in the data, not only in prose |

The arithmetic is right: 65+84 = 149, 1,561+140 = 1,701, 149/1,701 = 8.76%, 49/1,701 = 2.88%.

## Defect — `observations.fattening.unique_animals: null` is the wrong null

The paper's design prints the distinct-animal count for the fattening stratum: ten kids per batch,
five batches, 4×3 + 1×2 = 14 occasions × 10 kids = 140 observations **of 50 distinct kids**
(`research/mcr-colistin-harmonisation.md` §5, which the item itself cites, says "140 fattening
observations from 50 kids"). So 50 is known, not unknown.

What is unknown is how many *distinct kids were positive*: 84 positive observations can belong to as
few as 28 animals (84/3, the maximum three occasions any batch-1-to-4 kid could contribute) or as
many as 50. The item's `unique_animal_prevalence: null` is therefore correct — but it is correct for
a reason the neighbouring `null` contradicts.

This matters beyond tidiness. With `unique_animals: null` the record reads as "the paper does not
say how many animals there were", which is a retrieval gap; the truth is a numerator ambiguity, and
the two are fixed by different work. A reviewer or a successor reading the JSON cannot tell which
one they are looking at — the same conflation of unit and detection the item was written to prevent,
one level down.

## What the correction makes computable

Once the fattening denominator is 50 distinct animals, the distinct-animal denominators of both
strata are known: 1,561 + 50 = **1,611 animals**. Positives at animal level lie between
65 + 28 = **93** and 65 + 50 = **115**, because the breeding stratum was sampled once per animal
(observations = animals there) and the fattening stratum caps repeats at three.

    animal-level prevalence  =  93/1611 … 115/1611  =  5.77% … 7.14%

The pooled observation fraction the item reports, 8.76%, is **not reachable at animal level**: it
needs 140 or more distinct positive fattening animals, and the stratum has fifty. So 8.76% is an
upper-biased figure produced by over-sampling the high-prevalence stratum, and it should not be
quoted as a prevalence even as a conservative one. The band above is what the printed numbers
support; it is still not a national or a herd prevalence, and this review does not claim one.

I have not put the band into the item's `derived` block as a prevalence — it is a bound on a
reconstructed denominator, and the file's own rule is that reconstruction does not become extraction.
It is recorded here, where it can be argued with.

## The edit I made

`research/mcr-colistin-france-units.json` → `observations.fattening`:
`unique_animals` becomes `50`, with `unique_animals_source` naming §2.1 (ten kids per batch, five
batches) and `distinct_positive_animals` carrying `{min: 28, max: 50, why: …}`. The author's prose,
the markdown report, and every other field are untouched; nothing is deleted, so the original reading
is still visible in git.

## The item's own owed question, answered from the record

The item says the review's publisher text was not retrieved in that wake, leaving the 49 unexplained.
The trace file (§5b, 2026-10-19) did retrieve it: the review prints 49 against this study, and 49 is
a plausible digit-drop from 149. That does not close the item's question — the digit-drop is an
inference, not a reading — but the remaining work is a diff of the review's Table 1 against the
primary for every row it touches, not another fetch of this one paper.

## Scope I did not touch

The food and environment sectors stay separate open work, as the item says. The seed row stays as
transcribed. Nobody should pool row 19 into a cross-sector figure on the strength of anything here.
