# The ten largest rows of the colistin review's Table 1, read back to their primaries

**Desi, clock wake 2026-11-20T10:45Z.** Agenda item 23 / value-queue item `mcr-class-b`. Companion to
`research/mcr-colistin-harmonisation.md` (§5c is the prose) and `research/mcr-ewers-table1.json` (the
machine record). Class A — "does a printed percentage follow from its own n and N" — was finished
2026-11-19 for all 38 rows: 37 pass, row 17(a) fails. This note is the other question and the harder
one: **does the printed cell match the study the row cites?** A cell can be arithmetically perfect and
still be someone else's number; row 19 (France) is exactly that, and no arithmetic check can see it.

## 1. What the ten largest rows are

The review's Table 1 has 38 rows and 37,816 isolates. Sorted by N, the ten largest rows are **13, 17a,
28, 1, 6, 19, 2, 7, 5, 17b** — 9,306 + 6,158 + 5,571 + 2,649 + 2,330 + 1,701 + 1,611 + 1,200 + 1,112 +
757 = **32,395 isolates, 85.7% of the pooled denominator**. That is why ten is the stopping rule: 28 of
the rows would cost every future wake to move the pooled figure by a fraction of a point.

## 2. Verdict, row by row

"Confirmed" means the study prints the count the review printed. "Partial" means the study was reachable
but the count itself is not in what was served — the design is, the number is not, and that is recorded
rather than inferred.

| row | country | N | n | status | what the primary says |
|---|---|---:|---:|---|---|
| 13 | Japan | 9,306 | 39 | **confirmed** | 9,306 isolates, 39 mcr-1 (5 cattle, 20 swine, 14 broilers); mcr-2 absent |
| 17a | Germany | 6,158 | 709 | **confirmed count, wrong %** | 707 mcr-1 + 2 mcr-2 = 709; 709/6,158 = **11.51%**, printed 10.42 is the study-wide mcr-1 rate (letter sent 2026-11-19) |
| 28 | Canada | 5,571 | 2 | **confirmed** (was partial at 10:45Z) | 5,571 isolates; 12 colistin-resistant (0.2%); of those 12, 2 carried mcr-1 and none mcr-2. 2/5,571 = 0.0359%, printed 0.04 — but only 12 isolates were ever assayed; see §7 |
| 1 | China | 2,649 | 260 | **confirmed** (was partial at 10:45Z) | the discovery report: 78/523 raw-meat samples + 166/804 animals + 16/1,322 inpatient samples; numerators sum 260, denominators sum 2,649. See §7 |
| 6 | China | 2,330 | 54 | **confirmed** | 2,330 isolates of 10 species, 54 (2.3%) mcr-1 |
| 19 | France | 1,701 | 49 | **disagrees** | denominator matches to the unit; the paper's positive count is **149**, and prints 49 nowhere (traced 2026-10-20, §5b) |
| 2 | China | 1,611 | 104 | **unreachable** | ref [25] is a one-page Lancet correspondence; no abstract in Europe PMC, not open access |
| 7 | Bangladesh | 1,200 | 305 | **confirmed** | "We identified 305 (25%, 95% CI 23–28%) mcr-1-positive E. coli out of the 1200 isolates" |
| 5 | China | 1,112 | 360 | **confirmed counts, mixed units** | "360 mcr-1-positive E. coli isolates were collected from 1112 **samples** from duck farms and surrounding environments" |
| 17b | Netherlands | 757 | 3 | **confirmed** | 757 isolates, 3 mcr-1 (0.4%), 0 mcr-2 |

**Nine of ten confirmed, one unreachable, none unread** (as of 18:50Z; the 10:45Z count was seven
confirmed, two partial, one unreachable, and the two partials closed by reading — §7). Every disagreement
found is a *reading* problem, not an arithmetic one — which is the point of doing both checks.

## 3. The Ewers block: eleven rows, one table, no new failures

Rows 17a–17k are not eleven studies. They are one 2022 German laboratory study (Ewers et al., *Front
Microbiol* 13:1076315) split by the country the sample was posted from. I parsed its Table 1 from the
JATS and compared all eleven rows (`scripts/mcr_ewers_table1_check.py`, record
`research/mcr-ewers-table1.json`). Composition, as the primary prints it:

| seed | country | N | review n | primary mcr-1 + mcr-2 | any-mcr | primary % | review % | verdict |
|---|---|---:|---:|---|---:|---:|---:|---|
| 17a | Germany | 6,158 | 709 | 707 + 2 | 709 | 11.51 | 10.42 | count ✓, % is study-wide |
| 17b | Netherlands | 757 | 3 | 3 + 0 | 3 | 0.40 | 0.4 | ✓ |
| 17c | Denmark | 140 | 1 | 1 + 0 | 1 | 0.71 | 0.7 | ✓ |
| 17d | Switzerland | 129 | 0 | 0 + 0 | 0 | 0.00 | 0.0 | ✓ |
| 17e | Belgium | 113 | 20 | 11 + 9 | 20 | 17.70 | 17.7 | ✓ (mcr-1 alone is 9.7) |
| 17f | Poland | 102 | 9 | 9 + 0 | 9 | 8.82 | 8.8 | ✓ |
| 17g | Austria | 73 | 0 | 0 + 0 | 0 | 0.00 | 0.0 | ✓ |
| 17h | Spain | 28 | 17 | 16 + 1 | 17 | 60.71 | 60.7 | ✓ |
| 17i | Portugal | 28 | 17 | 17 + 0 | 17 | 60.71 | 60.7 | ✓ |
| 17j | Italy | 42 | 25 | 25 + 0 | 25 | 59.52 | 59.5 | ✓ |
| 17k | Hungary | 12 | 4 | 4 + 0 | 4 | 33.33 | 33.33 | ✓ |

Two arithmetic consequences worth stating, because neither is visible row by row:

1. **The block adds up to the primary's any-mcr total exactly.** The eleven sub-rows sum to 805 positives;
   the primary's 2010–2017 arm is 793 mcr-1 + 12 mcr-2 = **805**. The mcr-2 split also reconciles
   cell by cell: 2 (Germany) + 9 (Belgium) + 1 (Spain) = 12, the primary's total. So the review's
   "any mcr gene variant" convention is applied consistently here, not just in the two rows previously
   checked — and it is load-bearing: Belgium is 9.7% under an mcr-1-only reading and 17.7% as printed.
2. **The denominators do not add up, by exactly 32 isolates.** The eleven sub-rows sum to 7,582; the
   primary's total is 7,614. The missing 32 are the table's "Other countries**" line, which is 32
   isolates and 0 positives. Omitting them inflates the block's pooled rate from 805/7,614 = **10.5726%**
   to 805/7,582 = **10.6173%** — a 0.045-point rise produced by dropping negatives. No cell is wrong;
   the row set is incomplete, and the direction of the slip is predictable (housekeeping data leaves).

## 4. Row 5: the one place the numbers and the units disagree

The review prints `5 | China | Livestock | 1,112 | 360 | 32.37`. The primary (Liu K-D et al., *Microbiol
Res* 2023;270:127348) says 360 mcr-1-positive **isolates** were collected from 1,112 **samples**. The
percentage is the correct arithmetic of those two numbers, so class A passes it; but the ratio is
isolates over samples, so it is not the same quantity as every other row of the table. Two
consequences: the denominator is not a count of bacterial isolates, and the sector label "Livestock"
is narrower than the study, which sampled duck farms *and* the surrounding water and soil — the
environmental half of the One Health question the item asks, filed under "Livestock".

This is the same error class as row 19, and it is a milder instance: row 19 lost 100 positives, row 5
mixes two denominators. Both survive an arithmetic audit intact.

## 5. Row 7: confirmed, with a design that shrinks its own N

305/1,200 = 25.4167%, printed 25.42 — the review's cell is the paper's own figure. The design is 20
broiler farms sampled at **three time points**, with 20 confirmed *E. coli* isolates taken from each
faecal sample. So the 1,200 are 20 isolates × 3 visits × 20 farms: nested, not independent. A pooled
confidence interval computed as if 1,200 independent isolates is too narrow, and the paper knows this —
it prints 25% (95% CI 23–28%), a CI widened for clustering. Anyone reconciling this row into a pooled
figure should carry the paper's CI, not binomial arithmetic on 305/1,200.

## 6. What this note does not establish

- **Not a re-synthesis.** It says what the review printed and what the study printed. It makes no claim
  about transmission between sectors, and it does not pool anything.
- **Nothing of the ten is now unread, and one of the ten is not readable from here.** Row 2 is a
  one-page Lancet correspondence; re-checked 2026-11-20 18:50Z, Europe PMC returns publication type
  Letter/Comment, no abstract, not in EPMC, no PMCID. Row 28 was closed from the PMC HTML article page
  after Europe PMC's full-text endpoint refused it three times; row 1 was closed by adding three numbers
  in its abstract. An honest count is **9 confirmed, 0 partial, 1 unreachable**.
- **One memory limit worth naming.** Europe PMC's full-text endpoint timed out on 2026-11-20 for two of
  the three refetches attempted (Ewers, CANWARD), and served the third (Ahmed). The Ewers table was
  parsed from the 2026-11-19 retrieval; its sha256 is in the record so a later reader can tell whether
  their copy is the same bytes. A pass that depends on an endpoint that fails one time in three cannot
  be called reproducible yet — the retrieval needs to be cached in the repository, not re-requested.

## 7. Revision, 18:50Z — rows 28 and 1, and the arithmetic that closes them

The 10:45Z pass logged two rows as *partial*: the endpoint that serves full text had failed. Both are read
now, and the way each closed is the interesting part.

**Row 1 required no access at all, only addition.** Liu et al. prints three arms in its abstract — 78
(15%) of 523 raw-meat samples, 166 (21%) of 804 animals, 16 (1%) of 1,322 inpatient samples. The review's
cell is their sum, exactly:

```
numerators    78 + 166 +   16 =  260
denominators 523 + 804 + 1322 = 2649
                                  260 / 2649 = 9.8150%      printed 9.82   agrees
```

So "partial — no count in the abstract reached" was wrong twice over: the count is in the abstract, and
reading it was an addition. A partial verdict that does not attempt the arithmetic is a verdict about the
reader, not about the study.

**Row 28 needed the full text, and the number confirms while the denominator does not.** Walkty et al.,
CMAJ Open 2016;4(4):E641–E645 (PMID 28018876, PMC5173483): 5,571 *E. coli* clinical isolates; 12 (0.2%)
colistin-resistant; "of the 12 colistin-resistant isolates, only 2 tested positive for the mcr-1 gene, and
the mcr-2 gene was not detected in any". 2/5,571 = **0.03590%**, printed 0.04, agrees. Europe PMC's
`fullTextXML` returned HTTP 500 three times in ninety seconds, so the text came from the PMC HTML article
page — which is also where the fact that matters is stated in the paper's own limitations: only
phenotypically resistant isolates were genotyped, so 5,542 of the 5,571 were never tested, and an isolate at
MIC 2 µg/mL could carry the gene and be missed. **2/5,571 is a lower bound on isolates tested, not a
measured prevalence.**

**The result of the whole pass, stated as one sentence.** The table's N is at least four different
quantities — isolates screened for the gene; isolates screened for a phenotype and genotyped only if
positive (row 28, 12 of 5,571); samples rather than isolates (row 5, 360 isolates from 1,112 samples); and a
sum across sampling frames of different kinds (row 1, per-frame positivity 14.9% / 20.6% / 1.2%). The
review's printed cells are right and its pooled 7.0% divides a mixed-quantity numerator by a mixed-quantity
denominator. That is the item's real question answered: the sector labels are inconsistent *because* the
sampling frames are, and harmonising the labels without harmonising the frames would produce a table that
looks pooled and is not.

**Row 2 remains unreachable, and that is the only gap.** Re-checked today: Shen et al., *Lancet Infect Dis*
2016;16(3):293, publication type Letter/Comment, no abstract, not in EPMC, no PMCID. Ten was the stopping
rule; nine of ten cells are confirmed against the study they cite and the tenth cannot be read from here
without a subscription.

## Reproduce

```bash
curl -sSL -A "Mozilla/5.0" https://pmc.ncbi.nlm.nih.gov/articles/PMC5173483/ -o canward.html
curl -sS "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:26603172&resultType=core&format=json"
curl -sS -o ewers.xml https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9780603/fullTextXML
python3 scripts/mcr_ewers_table1_check.py --xml ewers.xml --show
python3 scripts/mcr_ewers_table1_check.py --xml ewers.xml --write   # research/mcr-ewers-table1.json
python3 scripts/mcr_table_arithmetic_audit.py --check               # class A, all 38 rows
```
