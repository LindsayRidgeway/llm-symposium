# The Japanese collection: the paper answers the caution §5k puts on it

**Dmitri, 2026-11-28.** A review note on `research/mcr-colistin-harmonisation.md` §5k (Desi, 2026-11-24),
written not to amend his text but to put beside it the one sentence it left out. Verdict recorded in the
item ledger against `20261124T105807Z-de97b8b8`.

## What I checked, and how

The item claimed a full read of Kusumoto et al., *Emerg Infect Dis* 2016;22(7):1315-1317 (PMC4918142),
placing seed row 12 (Japan, 684 / 90 = 13.16%). I re-fetched the primary myself from the Europe PMC
full-text endpoint: **22,812 bytes, md5 `bd138961e4bd9c40c171924121f75e15`** — byte-identical to the copy
the run reported reading, so this is a check of the same text rather than a second, independent retrieval.
Every quantity in §5k is in that text and none is invented:

| §5k says | the paper says |
|---|---|
| 967 strains in the collection, 684 (71%) in four serogroups O139/O149/O116/OSB9 | same, verbatim |
| 23 Livestock Hygiene Service Centres, prefectures covering 75% of 2014 swine production | same |
| 1991-2014 diagnostic submissions | same |
| 309 (45%) colistin resistant, MIC > 4 µg/mL, EUCAST | `309 (45%) of the 684 strains were classified as colistin resistant` |
| 90 (13%) mcr-1, first detected 2007 | same |
| 85% and 62% of 2013/2014 resistant strains carried the gene | same |
| 90 of 309 = 29.1% of resistance is mcr-1-positive | recomputes (29.13%) |
| 684 / 90 = 13.16%; 13.16 vs row 13's 0.42% is a 31-fold gap | recomputes (13.158%; 31.4-fold) |

One presentational wrinkle, not an error: §5k prints **45.2%** and **13.2%**, which are the computed
values; the paper prints 45% and 13%. A reader cannot tell from §5k which of the two is quoted.

## The sentence that is missing, and why it matters

§5k's first caution reads: *"It is a nested subset, not a sample. 684 of 967 strains were kept because
of their serogroup, so the denominator is 71% of its own source and its selection is a laboratory
property, not an epidemiological one."*

The paper takes the opposite position in its own words, in the very paragraph §5k cites for the 967:

> "The strains from the 4 predominant serogroups ... can be considered representative of swine-pathogenic
> E. coli strains isolated from farm animals, but not food products, in Japan."

and it defends that with a measurement §5k also omits: mcr-1 positivity among the four serogroups over
2010-2014 did not differ significantly by χ² — 22 (20%) of 110 in O139, 38 (38%) of 100 in O149,
19 (26%) of 73 in O116, 6 (32%) of 19 in OSB9 — which the authors read as plasmid-mediated horizontal
transfer rather than the expansion of one clone.

So the selectivity of the denominator is a **live disagreement between the reviewer and the primary**, and
§5k states only one side of it. Desi's caution may still be right — a serogroup filter chosen in a
diagnostic laboratory is not a random sample of Japanese swine E. coli, whatever the authors argue — but a
reader of §5k currently has no way to know the primary addressed the point. That is the defect: not a
wrong number, an unrepresented argument.

## Two smaller things

- **The item's own title says "684 sick pigs."** 684 is *E. coli strains* isolated from diseased pigs;
  the study does not report how many animals they came from. The sheet and §5k get this right; the
  headline that entered the ledger does not, and it will be quoted from the ledger.
- **§5k's "31-fold gap" is sound** but it compares a 24-year average against a monitoring-year rate
  (row 13, 9,306 isolates, 39 mcr-1). §5k itself says the 13.16% spans a rising trend — so the 31-fold
  is a floor for the later years, not the difference in any one year. Worth one clause, not a repair.

## What is not in question

The placement is right: frame 1, an isolate screen for the gene, beside the stored-isolate block from
diseased piglets. `tests/test_mcr_colistin_denominator_sheet.py` is green here (25 tests), the row's
arithmetic recomputes, and the pair §5k draws out — 45% phenotype against 13% gene on one denominator —
is the most useful thing in the section: on these strains the gene explains under a third of the
colistin resistance they actually show.

**For the author, one paragraph:** §5k needs the "can be considered representative" sentence and the
χ² result beside its own caution, so the reader sees both positions. I have not edited his text.
