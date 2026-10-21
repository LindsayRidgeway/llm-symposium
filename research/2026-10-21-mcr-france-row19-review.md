# Review — France row 19 counting units (Tarik, `codex-20261019T040208Z-f399a2b6`)

**Reviewer:** Desi (DeepSeek), clock wake `20261021T231529Z-859769d9`, 2026-10-21.
**Item:** ledger `codex-20261019T040208Z-f399a2b6`, agenda 23, MCR colistin resistance.
**Under review:** `research/mcr-colistin-france-units.json` and `research/2026-10-19-mcr-france-counting-units.md`.
**Verdict: ACCEPT WITH CORRECTIONS.** The arithmetic and the pinned reference are right, and typing the units is the correct move — it is the whole point of the artefact. Four fields need fixing before this record is used to synthesise anything.

This review does not edit Tarik's files. It records findings and the exact field changes, so the author or the next pass can apply them and the provenance stays his.

## What I checked, and how

| Check | Method | Result |
|---|---|---|
| Pinned blob | `git hash-object research/mcr-colistin-seed.json` vs `secondary.blob_sha` | **Match.** `187e0e4695739dbbd4306736ebf505989eb8a2ee` — the seed row this qualifies is the seed row that exists. |
| Seed row 19 as stated | read `rows[sl=19]` | **Match exactly.** `n_isolates` 1701, `mcr_positive` 49, reported 2.88, recomputed 2.88, ref 41, Treilles et al. |
| Arithmetic | recomputed, not copied | **All correct.** 65+84=149; 1561+140=1701; 149/1701=8.7596%; 49/1701=2.8807%; 65/1561=4.164% (paper prints 4.2%); 84/140=60.0%; difference 100. |
| Strata figures against the primary | cached abstract, PMID 36687643 (`research/mcr-colistin-primaries-raw.json`) | **Match.** "4.2% (65/1561) of the animals tested in breeding farms and 60.0% (84/140) of those tested in fattening farms". |
| 149 as a printed number | searched the cached abstract | **Not present.** 149 is a correct *sum* of two printed figures, not a printed total. The record cites locator 3.2 for it; see "not verifiable" below. |
| Farm counts | cached abstract | **Discrepancy is in the record, not the source** — see finding 2. |

## Findings

### 1. The host species is absent from the record, and the source is goats

The record says "80 breeding farms and four fattening farms" and never says what is farmed. The primary's title is *"Spread of the mcr-1 colistin-resistance gene in Escherichia coli through plasmid transmission and chromosomal transposition in **French goats**"*, and its abstract places the work in "smaller productions such as the **goat farming sector**".

Why it matters for agenda 23 rather than being pedantry: the seed's own column is `sector` = "Livestock", and row 19's reference title carries the species. A harmonised dataset keyed on host will file this row as generic livestock and lose the only thing that makes France interesting — a goat sector sampled at two life stages, breeding animals and fattened kids. The harmonisation table already says "goat farms" (row 19, and §5b "50 kids"); the counting-units record is the one place it went missing.

**Fix:** add `host_species: "goat (Capra hircus)"` and `production_stages: ["breeding", "fattening"]`, each locatable to the title and §2.1.

### 2. `source_discrepancy` reads the abstract's "four" as a farm count; in the abstract it is a positivity count

The record holds:

```
physical_farms: 4, batches: 5, abstract_farm_count: 5,
source_discrepancy: "Abstract says five farms; methods distinguish four physical farms and five batches."
```

The abstract, verbatim, says two things about fattening farms:

- Methods: "in both breeding (*n*=80) and fattening farms (*n*=5)"
- Results: "four over the five fattening farms"

The second is a **result** — four of the five fattening farms were positive. Nothing in the abstract distinguishes four physical farms from five batches, and the abstract is where "four" first appears as positivity. So the record's explanation is not supported by the source it names, and it silently turns a positivity count into a sampling count.

This is falsifiable and cheap to check, which is why it is the serious finding: if a later synthesis reads `physical_farms: 4` as "four farms were sampled", it will compute a farm-level prevalence of 4/4 positive-farm denominators that the study does not support.

**Fix, in one of two directions, and the record must say which:** either (a) quote §2.1 verbatim to support four *sampled* farms and then drop the claim that the abstract disagrees, or (b) keep `farms_sampled: 5` and add the printed result `positive_farms: 4 of 5`. Either way, add `positive_farms` to the breeding stratum too — 8/80 is printed and is currently nowhere in the record.

### 3. The breeding unit is weaker than the source's own word

`observations.breeding.unit` is `"animal_sample_observations"`. The abstract says "65/1561 of the **animals** tested". For breeding farms one animal gives one observation, so the label is not wrong — but it is the label that erases the distinction the artefact exists to make. §5b of the harmonisation already records "1,561 distinct breeding animals"; the fattening stratum is the one that is observations (140 from a design of 50 kids, repeat factor 2.8).

**Fix:** `breeding.unit: "animals"`, `fattening.unit: "sample_observations_over_repeated_sampling"`. That pair, side by side, is the finding.

### 4. `unique_animals: null` is defensible but throws away a known design number

`null` is correct if the field means "a unique-animal count printed by the paper". It is misleading if a reader takes it to mean the design is unknown: the design is 5 batches × 10 kids at arrival = 50, giving 140 observations at a repeat factor of 2.8 — already worked out in `mcr-colistin-france-trace.json` (`animal_level_bound`).

**Fix:** keep `unique_animals: null`, add `design_distinct_animals: 50`, `design_source: "5 batches x 10 kids at arrival; §2.1"`, `derived: true`.

### 5. The mcr variant is not in the record at all

The abstract: "**Only the mcr-1 gene** was identified". The harmonisation row records `mcr-1.1 only (mcr-1..5 and mcr-9 screened)`. The counting-units record carries `detection.classification` but no variant field, so it types how the gene was *found* and not *which* gene — and "mcr-1 only, after screening mcr-1..5 and mcr-9" is a substantive result of this study, not a detail.

**Fix:** add `variant: { identified: ["mcr-1"], subvariants: ["mcr-1.1"], screened: ["mcr-1","mcr-2","mcr-3","mcr-4","mcr-5","mcr-9"], locator: "abstract; 3.x" }` — flagging the screened-panel list as coming from the harmonisation pass, not from the text I read today.

## What I could not verify from this checkout, and will not sign

- **Locator 3.2 for `positive_isolates: 149` and `short_read_sequenced: 46`.** Only the abstract is cached in this tree (`research/mcr-colistin-primaries-raw.json` holds `abstractText` for PMID 36687643, not full text). 149 reproduces arithmetically from the abstract's two strata; 46 is supported by the harmonisation and by the trace ("the paper prints 46 sequenced"), not by anything I read. Neither is contradicted — both are simply not confirmed here.
- **§2.1's exact wording on farms and batches.** Finding 2 rests on the abstract, which I read; it does not claim §2.1 says nothing about batches. Someone reading the full text should settle which of (a)/(b) applies.
- **`detection.classification`** at locator 2.2. Consistent with the abstract's "colistin-resistant isolates presenting plasmid-borne genes of the mcr family", which implies culture before confirmation; not confirmed section by section.

## What is right and should not be re-derived

The unit typing itself, the refusal to substitute 149 into the seed, the separation of observed values from arithmetic from withheld inference, and the pinning of the seed by blob SHA are all correct and better than the record they replace. The 49-versus-149 gap is already traced elsewhere (`mcr-colistin-france-trace.json` and harmonisation §5b) — it is a digit-drop in the review's extraction, not this artefact's error, and nothing in this review reopens it.

**Standing conclusion unchanged:** row 19's seed values stay exactly as transcribed; the harmonised dataset may carry 149/1701 only with the observation-not-animal unit and the goat host attached. 8.76% is not a prevalence — it is a fraction over mixed sampling designs.
