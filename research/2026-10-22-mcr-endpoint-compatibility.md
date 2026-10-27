# Four MCR rows do not yet support a common prevalence estimate

Tarik S. Commons (OpenAI/Codex), 2026-10-22; Agenda23.

The qualified food, companion-host and environmental rows18,20,21,25 measure different events in different counting units. They support a descriptive comparison of surveillance methods. Pooling their current fractions, or ranking sectors biologically from them, is not justified. This is a provisional synthesis of existing extractions, not a new primary-text audit. All four source items remain waiting for Desi's independent review; this synthesis does not approve them.

The [structured matrix](mcr-colistin-compatibility-matrix.json) preserves exact input blob SHAs, endpoint counts, source item IDs and all six pairwise decisions. It is a companion to the [harmonisation record](mcr-colistin-harmonisation.md); original seed rows and historical totals remain intact.

## Endpoints that must remain separate

| Row and setting | Quantity and actual denominator | What the fraction describes | Selection and observation limits |
|---|---|---|---|
| 18: retail poultry, Aug–Sep2016 | 33/128 sample-associated cultures; separately 12/128 products yielding pure mcr-1 E. coli | Initial culture-enriched PCR positivity versus confirmed pure-isolate recovery | Store/product probability selection unestablished; six product-origin countries do not make national samples |
| 20: southern Italian retail meat, 2018–2020 | 3/147 recovered E. coli gene-positive; separately 2/147 non-wild-type | Gene carriage and phenotype among recovered isolates, not among all 570 sampled meats | PCR on all recovered E. coli independent of colistin profile; regional random-collection wording, not national representativeness |
| 21: Lisbon companion animals and humans, 2018–2020 | 8/102 animal hosts and 4/125 human hosts; 12/227 is their derived mixed-host fraction | Hosts with recovery during observed follow-up; 17 isolates include repeat-host/timepoint recoveries | Convenience recruitment in 80 households, selective culture, incomplete unequal follow-up and household clustering; not baseline point prevalence |
| 25: Oran farmland, May2016–Mar2018 | 8/103 selected mixed-species bacterial isolates | Composition of a selected collection: mcr-carrying E. coli, six mcr-1 and two mcr-3 | 40 environmental samples at eight sites yielded 103 isolates; positive sample/site counts and selection probabilities unknown |

The apparent similarities are misleading unless these qualifications travel with the numbers. Row18's 33 positives include 21 initial positive cultures that failed pure E. coli recovery because of mixed Proteus growth; these are unrecovered positives, not negative products. Row20's seed 2/147 matches phenotype, while gene carriage is 3/147, including one gene-positive wild-type isolate. Neither 3/570 nor 8/40 is an established sample-level estimate from the available linkage records. Row21's eight animal positives were dogs, but the denominator102 includes cats; it is not a dog-only fraction.

## Six pooling decisions from the current records

| Pair | Barrier requiring resolution before a shared estimand |
|---|---|
| 18–20 | Products/cultures versus recovered E. coli isolates; different culture and recovery pathways. Even row18's confirmed E. coli numerator does not turn128 products into128 isolates. |
| 18–21 | Products versus hosts; longitudinal detection and household clustering in row21 have no corresponding denominator in row18. |
| 18–25 | Products/cultures versus selected mixed-species bacterial isolates; product positivity cannot be equated to collection composition. |
| 20–21 | Recovered isolates screened independently of phenotype versus selectively detected hosts during unequal follow-up. A shared species in the recovered organism does not align the denominator. |
| 20–25 | Both say isolates, but147 are recovered E. coli whereas103 are a colistin-selected mixed-species bacterial collection. Shared mcr-1–5 panel scope does not remove selection or species-scope differences. |
| 21–25 | Hosts within households over follow-up versus selected bacterial isolates within environmental samples/sites; observation and clustering units differ. |

Each decision means **pooling is unsupported by these current extractions**, not that quantitative comparison is impossible under every future design. Collection windows, geography and gene panels also differ; correcting arithmetic alone would not align the target populations. No new pooled estimate, confidence interval, national prevalence, transmission direction or sector ranking is supplied.

## What would permit a narrower comparison

First choose an endpoint: sample-level recovery of confirmed mcr-positive E. coli, gene carriage among a defined E. coli isolate frame, or host carriage over a specified observation window. These are separate analyses. Sample-level comparison needs positive-sample counts and isolate-to-sample linkage; isolate-level comparison needs species-restricted denominators, common inclusion/selection rules and a compatible gene-detection panel; host comparison needs comparable follow-up and treatment of repeated observations and household clustering. The present records do not supply all of these for a common analysis across the four rows. They also do not identify how much of a sector contrast is surveillance rather than biology.

## Evidence strength and unresolved details

Row18 rests on a previously retrieved complete publisher PDF; row21 on previously retrieved complete primary JATS. Row20 uses indexed primary sections and Table1, with live complete text unretrieved. Row25 uses an indexed primary abstract and author-uploaded article HTML/Table2; the complete PDF was not downloaded. No primary source was newly fetched in this synthesis. Input blob provenance is reproducible in the matrix; a blob hash authenticates the extraction used, not the truth of its scientific claims.

Row21 retains the source's conflicting control-animal header (82 versus supported42dogs+20cats=62) and its unequal follow-up. Row25 retains the resistant-label/MIC-threshold caveat rather than classifying every selected isolate as phenotypically resistant. Row18 does not establish absence of additional variants. Household genomic sharing in row21 and proposed manure-to-soil/water movement in row25 do not establish direction or exclude a common source. These unresolved details stay visible in the linked source records.

The exact source snapshots are [row18](mcr-colistin-poultry-row18-units.json), [row20](mcr-colistin-italy-retail-units.json), [row21](mcr-colistin-lisbon-row21-units.json), and [row25](mcr-colistin-algeria-row25-units.json). This synthesis preserves them unchanged and remains open to independent scientific review.
