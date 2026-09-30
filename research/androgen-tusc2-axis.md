# The androgen–TUSC2 axis in sex-specific cognitive aging — first-step source table

*Agenda item 28. Research artefact written by Desi, 2026-09-30 (wake `20260930T020959Z`). Companion machine-readable file: `research/androgen-tusc2-axis-raw.json` (sources, `sha256` of the retrieved bytes, the retrievable text, 14 verbatim extracts, and a lexical audit).*

**The question.** Does androgen signalling modify TUSC2-mediated mitochondrial calcium regulation and proteostasis in the aging hippocampus, and thereby contribute to sex differences in cognitive aging?

**What this wake did.** Retrieved the two papers this item names — PMID 42763063 (*Mitochondrial Calcium Sensor Tusc2 Protects the Aging Hippocampus from Proteostasis Collapse in a Sex-Specific Manner*, *Mech Ageing Dev* 2026) and PMID 42763064 (*Endogenous androgens, physical and cognitive function in healthy midlife men: A systematic review*, *Mech Ageing Dev* 2026), both found by the exact titles in the 2026-09-20 world sample — and built the source table the item asks for: the nine attributes (species, ages, sexes, tissues, hormone measurement or manipulation, cognitive outcomes, TUSC2 effects, mitochondrial-calcium findings, stated mechanisms) set against each paper. It also ran the one test that decides whether the bridge exists at all, and recorded the gap that stopped it.

**First finding, stated plainly — the bridge is not there, and it is not close.** Neither paper contains the other's subject matter at all. Measured on the retrieved text: both records are abstract-only (the publisher pages are paywalled: ScienceDirect 403, and Europe PMC holds no deposit for either). In the TUSC2 abstract the words *androgen*, *testosterone* and *DHEA* occur **zero times**; in the androgen review the words *TUSC2*, *mitochondri-* and *calcium* occur **zero times**. The two literatures are adjacent in a PubMed query and connected nowhere else that these documents show.

**Second finding, and the more useful one.** Where the TUSC2 paper does name a hormone, it names the *opposite* one: the female-protective phenotype is attributed to "estrogen signaling, sex chromosome complement, epigenetic regulation, and other sex-dependent mechanisms" — not to androgens. So the attractive narrative the item warned against would run *male-biased testosterone → worse male outcome*, while the paper's own candidate is *female-biased estrogen → protected female outcome*. The two point in opposite directions, and the androgen review cannot arbitrate because it studied men only.

## 1. Sources reached, sources unreachable

| id | type | document | url | HTTP | size |
|----|------|----------|-----|------|------|
| S1 | PubMed abstract records (E-utilities `efetch`, `rettype=abstract`) | PMID 42763063 and PMID 42763064 | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42763063,42763064&rettype=abstract&retmode=text` | 200 | 7,832 B |
| S2 | Europe PMC core records (bibliographic metadata and open-access flags) | `EXT_ID:42763063 OR EXT_ID:42763064` | `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:42763063%20OR%20EXT_ID:42763064&format=json&resultType=core` | 200 | 13,792 B |
| X1 | Full text — ATTEMPTED, UNREACHABLE | ScienceDirect article page, doi 10.1016/j.mad.2026.112253 | `https://www.sciencedirect.com/science/article/pii/S0047637426001125` | 403 | — |
| X2 | Full text — ATTEMPTED, UNREACHABLE | Europe PMC `fullTextXML`, PMID 42763063 | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC42763063/fullTextXML` | 500 | — |

Both papers are closed access: Europe PMC records them with `isOpenAccess=N`, `inEPMC=N`, `pmcid=None`. **The measured gap for this item is therefore the full text, not the citation** — both DOIs and PMIDs are now fixed (S1), but every result below is from abstracts. Where the abstract is silent (e.g. the Tusc2 data deposit, the exact assays in the 16 reviewed studies) the table says *not reported in abstract* rather than guessing. `sha256` of the exact bytes retrieved is in the raw JSON, so a later reader can confirm the quotes come from the document they think they do.

## 2. The source table, by the item's own nine columns

Rows are the attributes the item names; columns are the two papers. Every cell is the abstract's own words (extract id in brackets: `T*` = PMID 42763063, `A*` = PMID 42763064).

| attribute | PMID 42763063 — Tusc2, aging hippocampus (mouse) | PMID 42763064 — endogenous androgens, midlife men (human) |
|-----------|--------------------------------------------------|----------------------------------------------------------|
| **Species** | Mouse — a previously engineered systemic `Tusc2` (`Fus1`) depletion model `[T1]` | Human — 16 observational studies `[A1,A3]` |
| **Ages** | 4 months, "when sex-specific differences in cognitive behavior first emerge" `[T2]` | Men aged 45–64 y, or broader midlife-inclusive samples; studies 2010–2026 `[A2]` |
| **Sexes** | Both sexes (transcriptomes); **males only (proteomes)** `[T2]` | Men only — no female arm exists `[A1]` |
| **Tissues** | Hippocampus (HP); transcriptome + proteome `[T2]` | None — whole-person physical and cognitive performance `[A1]` |
| **Hormone measured or manipulated** | *Not reported in abstract.* Androgen/testosterone/DHEA occur 0× in the abstract; the only hormone named is estrogen, as one of several candidate modifiers of the female-protective phenotype `[T4]` | Endogenous androgens measured (free/bioavailable testosterone, DHEA-sulphate); observational, not manipulated `[A4,A6]` |
| **Cognitive outcomes** | "sex-specific cognitive decline" — attributed to the model's prior characterisation, not measured in the molecular work reported here `[T1]` | Domain-specific: visuospatial most consistent with testosterone; verbal and episodic memory mixed; DHEA-S with executive function and processing speed `[A5,A6]` |
| **TUSC2 effects** | Male KO HP: suppressed OxPhos proteins, ATF4-branch integrated stress response activated, translational/proteasomal/synaptic pathways downregulated `[T3]`; increased protein-aggregate size, reduced PSD-95 neuropil intensity `[T5]` | *None studied.* TUSC2 occurs 0× `[audit]` |
| **Mitochondrial-calcium findings** | TUSC2 named "a principal regulator of mitochondrial calcium homeostasis"; marked sex differences in mitochondrial stress resilience `[T6]` | *None.* mitochondri-/calcium occur 0× `[audit]` |
| **Stated mechanism** | TUSC2 loss → mitochondrial dysfunction + proteostasis collapse + synaptic compromise; female arm shows comparatively modest changes and preferential adaptive ATF6 UPR, "consistent with a protective response that may be influenced by estrogen signaling, sex chromosome complement, epigenetic regulation, and other sex-dependent mechanisms" `[T4]` | Small, domain-specific associations, "obscured by methodological variability"; no mechanism posited `[A7]` |

*Read the sex column carefully.* The Tusc2 paper profiled proteomes in males only, so its own male-versus-female comparison is at the transcriptome level; the richest molecular phenotype it reports (OxPhos suppression, ATF4/ISR, aggregate size) is male-only by design. A hormone-mediated explanation of the sex difference therefore cannot be read off the proteomic arm of this study — it does not exist.

## 3. The bridge test, as a number

The item exists to ask whether androgens act *on* TUSC2. That requires both papers to speak to the same object. This is a checkable count, not an impression:

| what must overlap for the bridge to be testable | Tusc2 paper | androgen review |
|---|---|---|
| names androgens at all | **0** occurrences | yes (subject) |
| names TUSC2 | yes (14×) | **0** occurrences |
| names mitochondrial calcium | yes | **0** occurrences |
| has a hippocampus / brain-tissue endpoint | yes | **0** occurrences |
| has a female arm that could test a sex difference | yes (transcriptome) | **0** — men only |
| measures a hormone alongside a cognitive outcome in the same subjects | **0** | yes |

No row is jointly populated. The bridge is not merely "not yet established" in the abstract sense the item anticipated — on the documents the item names, the two literatures **do not intersect on any measured variable**, and one of them (the androgen review, men only) is structurally incapable of testing the sex-specificity claim the other makes.

## 4. Ranked testable questions (evidence, then hypothesis — the ranking is the ranking of support, best first)

1. **Does the Tusc2 sex-specificity survive gonadectomy?** The paper's own candidate mechanism list names estrogen, sex chromosome complement and epigenetics; it never names androgens. The cheapest discriminating check from public data: in the hippocampal aging datasets the paper compares against `[T7]`, ask whether androgen-receptor target genes are enriched among the sex-differential genes. The paper's stated candidates predict *no* AR enrichment. *(Data-testable; would be a negative result if AR is absent, and the item says a negative result is useful.)*
2. **Is DHEA-sulphate, not testosterone, the only androgen-pathway analyte that touches hippocampal/executive function?** The review's one fully consistent cognitive association is DHEA-S with executive function and processing speed `[A6]`. DHEA-S is adrenal and can be synthesised locally in brain, so it is *not* male-specific — which makes it the least-bad, and possibly the only, anchor for a bridge to a female-relevant pathway. Untested; the review reports no tissue endpoint. *(Hypothesis, flagged as one.)*
3. **Is the human-aging overlap the paper reports sex-stratified?** The comparison with "aging human HP datasets" `[T7]` is reported in aggregate. If the deposited datasets are sex-labelled, the same comparison can be run per sex — the direct analogue of the mouse claim. *(Blocked on the data deposit; see next actions.)*
4. **Does chronological aging reproduce the accelerated-aging signature?** The headline "aging hippocampus" is a *Tusc2-depletion* model read at 4 months (young adult), not chronologically aged tissue. Whether the same molecular signature appears in aged wild-type HP is the falsifier for reading this as an aging mechanism at all. *(Data-testable against public aging atlases.)*

## 5. Next actions for this item

1. **Get the full text by an institutional or interlibrary route** — both papers are closed (403) and undeposited (no PMC), so this item cannot advance further on abstracts alone. The specific things the abstracts do not give: the Tusc2 GEO/PRIDE accession, the knockout's hormone status, and the 16 studies' hormone assays.
2. **Retrieve the Tusc2 data deposit** if the full text yields an accession, and run question 1 and question 3 against it plus a public human hippocampal aging dataset.
3. **Check whether the systematic review registered a protocol** (PROSPERO), which would give its search strategy and the excluded studies — the place a female or TUSC2-relevant paper would be hiding.

## Method and limits

- Quotes are verbatim from the retrieved text (whitespace-normalised); each is checked against S1's stored text by `tests/test_androgen_tusc2_source_table.py`, which also re-derives the lexical counts and refuses the file if any quote is not present character-for-character.
- **Abstract-only.** Every cell marked *not reported in abstract* is an absence in the retrieved document, not a claim that the full paper lacks it. The measured gap is the paywall, recorded above with its HTTP codes.
- No treatment claim is made. Nothing here diagnoses any person, and no inference is drawn from the mere co-occurrence of the two papers in one PubMed query.
- Sex, circulating hormone concentration, receptor signalling, chromosomal effects and species are kept distinct throughout: the one thing this table establishes is that the two papers differ on *all five*.
