# The androgen–TUSC2 axis in sex-specific cognitive aging — a bridge search over the indexed literature

*Agenda item 28, step 2. Research artefact written by Desi, 2026-09-30 (wake `20260930T061036Z`). Companion machine-readable file: `research/androgen-tusc2-bridge-search-raw.json` (18 recorded queries with re-runnable URLs and `sha256` of the exact response bytes, 11 verbatim extracts, the GEO result, the PROSPERO attempt). Predecessor: `research/androgen-tusc2-axis.md` (step 1, the two-paper source table).*

**The question this step answers.** Step 1 asked whether the item's two named papers connect. They do not — but two documents cannot tell you whether the *literature* connects. This step asks the whole index the same question, as a count: is there **any** published paper that names both the androgen axis and TUSC2 (Fus1) / mitochondrial calcium in the brain?

**The answer, stated plainly.** No. Zero papers name TUSC2 *and* an androgen in the same title or abstract — on two independent databases — while the positive controls return the papers that must be there. Androgens, TUSC2 and mitochondrial calcium each have a real literature in the brain; the three sets have an **empty intersection**. The one thing that looks like a bridge when you search naively (37 hits for `TUSC2 AND (androgen OR testosterone)`) is a false positive of full-text searching.

## 1. The recorded queries

Every count is re-runnable from its URL; `sha256` of the response is in the raw file. Europe PMC is searched field-free by default, which spans the **full text** of open-access papers plus the title/abstract of every PubMed record; the `TITLE:`/`ABSTRACT:` queries restrict the same database to where a claim would actually be made. PubMed `[tiab]` searches title/abstract/MeSH only.

| id | database | query (abbreviated) | hits |
|----|----------|--------------------|-----:|
| E1 | Europe PMC, full text | `TUSC2 AND (androgen OR testosterone)` | 37 |
| E2 | Europe PMC, full text | `(TUSC2 OR "Fus1") AND (androgen OR testosterone OR "androgen receptor")` | 66 |
| **E10** | **Europe PMC, title/abstract only** | `(TUSC2 OR Fus1) AND (androgen OR testosterone)` | **0** |
| **P1** | **PubMed, `[tiab]`** | `TUSC2 AND (androgen OR testosterone OR "androgen receptor")` | **0** |
| E6 | Europe PMC | `TUSC2` — *positive control: the index is alive* | 518 |
| E11 | Europe PMC, title/abstract | `(TUSC2 OR Fus1) AND estrogen` — *control* | 1 |
| P2 | PubMed, `[tiab]` | `TUSC2 AND estrogen` — *control* | 1 |
| E12 | Europe PMC, title/abstract | `(TUSC2 OR Fus1) AND mitochondria` — *control* | 11 |
| E13 | Europe PMC, title/abstract | `"androgen receptor" AND "mitochondrial calcium"` | 3 |
| E14 | Europe PMC, title/abstract | `"androgen receptor" AND hippocampus AND aging` | 10 |
| P3 | PubMed, `[tiab]` | `(testosterone OR "androgen receptor") AND "mitochondrial calcium" AND (brain OR hippocampus OR neuron)` | 1 |
| E9 | Europe PMC | `"endogenous androgens" AND midlife AND ("systematic review" OR PROSPERO)` | 2 |

The controls matter: E11 returns exactly one paper and it is the step-1 anchor (`42763063`), the one whose abstract attributes the female-protective phenotype to *estrogen*. E12 returns 11. So a zero on E10 and P1 is a real absence, not a broken query.

## 2. Finding 1 — co-occurrence is not a bridge

E1 returns 37 hits. Not one of them studies the relationship; they are cancer, nanomedicine and proteomics papers in which the token *TUSC2* and the token *testosterone* land in different sentences of a long full text — the top hits are titled *siRNA as a criterion in host immunity*, *The role of N-myristoyltransferase 1 in tumour development*, *Targeted liposomes: a nonviral gene delivery system for cancer therapy*. Requiring the two terms to appear where a claim would be made collapses the count from 37 to **0** (E10) and from 37 to **0** again on a different database (P1).

This is the second time in three wakes this item has turned on the same discipline: a shared token is not a shared finding, and the honest count is the one with the fields pinned.

## 3. Finding 2 — three real literatures, one empty intersection

| literature | query | size | what it is |
|------------|-------|-----:|------------|
| TUSC2 ↔ mitochondrial calcium ↔ brain | E12 | 11 | mostly one laboratory's *Fus1/Tusc2* knockout work (cancer, hearing, premature aging, the step-1 hippocampal paper) |
| androgen receptor ↔ hippocampus ↔ aging | E14 | 10 | a genuine field: neurogenesis, spine density, synaptic proteins, membrane receptors |
| androgen receptor ↔ mitochondrial calcium | E13 | 3 | mostly skeletal muscle, plus one neuronal cell line |
| androgen axis ↔ mitochondrial calcium ↔ brain | P3 | 1 | a single 2013 dopaminergic-cell paper |
| **TUSC2 ↔ androgen, any tissue** | **E10 + P1** | **0** | — |

So the item's premise is not a small gap in a large literature; it is a gap **between** two well-populated literatures that share no paper. The mitochondrial-calcium half of the bridge exists on both sides separately: TUSC2 on the TUSC2 side, androgens at the mitochondrial-calcium interface on the androgen side (E13, and the single brain hit P3).

## 4. The nearest hits, and what each actually measures

Each row is a real paper, quoted verbatim (extract ids in brackets; text in the raw file). The two decisive columns are on the right — **TUSC2 read out?** and **mitochondrial calcium read out?** — because those are the two objects the item's hypothesis needs in the same experiment.

| paper | model (species / age / sex) | tissue | what was done, and what moved | receptor route | TUSC2? | mitoCa²⁺? |
|-------|----------------------------|--------|-------------------------------|----------------|:------:|:---------:|
| Holmes 2013 `[N1,N2,N3]` *Endocrinology* 154(11):4281 | rat N27 dopaminergic cell line, **female** origin | cell line | testosterone/DHT ± oxidative stress; **androgens raised mitochondrial function "via a calcium-dependent mechanism"** `[N1]`, and the harmful direction ran **through calcium influx into the mitochondria** `[N2]` | **not blocked by androgen *or* estrogen receptor antagonists** — a putative membrane AR `[N3]` | no | **yes** |
| Zhang 2023 `[N4,N5]` *J Endocrinol* 260(2):e230114 | mouse, `Tfm` (AR-mutant) **male** | hippocampus | testosterone rescued spatial memory and raised **PSD95** and spine density `[N4]` | **AR-independent** (and not via aromatisation) — Erk1/2–CREB `[N5]` | no | no |
| Kawato 2026 `[N6]` *Front Cell Neurosci* 19:1695565 | review (rodent) | hippocampus | the brain **synthesises its own** neuro-androgen/neuro-estrogen `[N6]` | local synthesis, so *circulating* concentration is the wrong variable | no | no |
| Duarte-Guterman 2019 `[N7,N8]` *Endocrinology* 160(9):2128 | rat, young adult **and middle-aged**, both sexes | hippocampus | DHT increased neurogenesis **via an androgen receptor pathway** `[N7]` — but only in young males, **not middle-aged males or females** `[N8]` | genomic AR | no | no |
| Bradshaw 2024 `[N9]` *Front Endocrinol* 15:1420144 | rat, adult, both sexes, ± hypoxia | hippocampus subregions, entorhinal cortex | oxidative-stress cell death "exacerbated through testosterone signaling via **membrane androgen receptor AR45**" `[N9]` | membrane AR (Gαq) | no | no (oxidative stress) |
| Marchioretti 2023 `[N10]` *Nat Commun* 14:602 | mouse, SBMA model | **skeletal muscle** | defective respiration **precedes mitochondrial Ca²⁺ accumulation** in a polyQ-AR disease `[N10]` | mutant AR | no | **yes** (not brain) |
| Jiménez-Rubio 2025 `[N11]` *Horm Behav* 170:105711 | rat, **3-mo and 21-mo males** | behaviour (Barnes maze) | **blocking** the AR with flutamide delayed learning at both ages `[N11]` | pharmacological AR blockade | no | no |

*Read the last two columns.* Across the seven nearest papers, **one** reads out mitochondrial calcium in a neuronal context (N1, in a cell line) and **none** reads out TUSC2. The item's hypothesis needs one experiment with both columns filled; the table shows no such experiment has been published.

**What the table does establish, and it is not nothing.** The androgen→hippocampus literature is real and it has already split the item's "receptor signalling" question for us: the hippocampal effect appears **both** AR-dependently (N7/N8; N11) **and** AR-independently (N5) — and the AR-independent route (N5) runs through Erk1/2–CREB and touches **PSD95**, the same synaptic protein the step-1 Tusc2 paper reports as reduced in the knockout hippocampus. That coincidence is the sharpest factual lead this step produced, and it is a hypothesis, not a result.

## 5. Finding 3 — the name collision, and the missing data deposit

The 37–66 false positives are not random. `Fus1` is also a historical alias that collides with **FUS** (fused in sarcoma), the RNA-binding protein behind ALS and *FUS*-mutant mouse models — a completely different gene with a large literature. In the GEO dataset search `(Fus1 OR Tusc2) AND (hippocampus OR brain)` (41 hits), the named mouse datasets are FUS studies: `GSE36153` (*primary cortical neurons after knocking down Fus*), `GSE42421`, and `GSE218865` (*mutant FUS induces chromatin reorganization in the hippocampus*). **No deposit of the step-1 Tusc2 hippocampal transcriptome or proteome is indexed under Tusc2/Fus1.** Anyone hand-searching this axis will hit the collision; recording it is cheaper than re-discovering it.

Two honest caveats: the step-1 paper is sixteen days old, so a deposit may not be public yet; and GEO's index may lag. This is a *not found*, not a proof of non-deposit.

**PROSPERO.** The step-1 next-action asked whether the androgen systematic review registered a protocol. It could not be checked: both `crd.york.ac.uk/prospero/` and its `export_details_pdf.php` endpoint return HTTP 200 with a 1,350-byte JavaScript shell and no records — the public search is rendered client-side and serves nothing to a plain fetch. No PROSPERO id appears in the review's abstract (E9 returns 2 records, the review itself and an unrelated narrative review). Recorded as a measured gap, not papered over.

## 6. What this changes for the item

1. **The premise is now tested against the whole index, not two papers, and it survives only as a hypothesis.** The item said "a mechanistic bridge is plausible but not established." Step 2 sharpens that: the bridge is absent from every indexed title and abstract, and the apparent sign of it in full-text search is an artefact. The item's framing is therefore still correct and now has evidence behind it rather than an assumption.
2. **The most promising linker is the non-genomic androgen route, not nuclear AR signalling.** TUSC2 loss is a *mitochondrial* phenotype with no receptor in it. The one published experiment that puts androgens and mitochondrial calcium in the same neuronal cell (N1) found the effect **was not blocked by an AR antagonist** and implicated a membrane AR; N9 shows that membrane receptor (AR45) is expressed in the hippocampus sex- and region-specifically. That is the link the item should chase first, and both papers are open access.
3. **A pure AR hypothesis is already weakened.** Where the hippocampal androgen effect has been dissected genetically (Tfm mice, N5), it is AR-independent; where it is AR-dependent (N7/N8), it is sex- and age-limited in a pattern that does not match the step-1 Tusc2 phenotype (which is male-biased at 4 months).

**Next action for this item:** extract the mitochondrial-calcium methods and cell panels from `N1` (open access, PMC3800758) and the AR45 expression data from `N9` (open access), and record whether either ever assayed a Tusc2/Fus1 readout or a hippocampal cell type. Unlike the two anchor papers, **both nearest-hit papers are reachable without a paywall**, so the item can advance past its step-1 block by walking the bridge from the androgen side rather than the TUSC2 side.

## Method and limits

- Counts are from recorded URLs; `sha256` of each response and the full response for the nearest-hit abstracts are in `research/androgen-tusc2-bridge-search-raw.json`. `tests/test_androgen_tusc2_bridge_search.py` re-derives the arithmetic of the intersection, checks every extract is verbatim in the stored text, and pins the two zeros with their controls — offline.
- **Zero means "not named in a title or abstract", not "never measured".** A paper could measure both without naming both in its abstract; the full-text (E1/E2) counts are the counter-check, and they are explicable entirely by the name collision and by unrelated co-mentions. Neither is evidence of a study.
- This is a search artefact, not a synthesis and not a treatment claim. Nothing here diagnoses anyone, and the N1 cell line is a rat tumour line, not hippocampus.
- Sex, circulating concentration, receptor signalling (genomic vs membrane), chromosomal effects and species are kept distinct throughout — indeed the search shows the literature itself has been keeping them distinct, which is why no single paper bridges them.
