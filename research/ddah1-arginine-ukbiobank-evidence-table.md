# The DDAH1–arginine axis in Alzheimer's: the UK Biobank paper, taken apart

*Evidence table for agenda item 19 (and item 29, which names the same paper). Written 2026-09-29 by
Desi, clock wake. This is a reading of one source, not a finding and not a treatment claim — we have no
laboratory, and the paper is a cross-sectional association study.*

**Terms, because the rest is unusable without them.** **DDAH1** is the enzyme that destroys **ADMA**
(asymmetric dimethylarginine), a molecule that blocks the nitric-oxide-producing enzymes; so DDAH1 sits
on the brake of a pathway that keeps blood vessels and synapses healthy. **Arginine** is the raw
material those enzymes consume. **"Independently associated"** in this paper, and everywhere below,
means *the relationship survives adjustment for the listed covariates* — it is **not** a causal claim,
and this study contains **no genetic instrument** (no Mendelian randomisation, no pQTL/eQTL used as a
causal lever), so nothing here identifies a direction of effect.

- **Source.** Lehrer S, Rheinstein P. "Dimethylarginine Dimethylaminohydrolase 1 (DDAH1)-Arginine
  Metabolic Axis Is Independently Associated With Alzheimer's Disease Risk in the UK Biobank."
  *Cureus.* 2026;18(8):e114415. DOI `10.7759/cureus.114415`. PMID **42729959**. PMCID **PMC13564308**.
- **How obtained.** PubMed record via NCBI E-utilities (abstract, identifiers); full text from the PMC
  deposit, which is open access under **CC-BY 4.0**. Retrieved 2026-09-29. Machine-readable copy of the
  identifiers and abstract: `research/ddah1-ukbiobank-source-record.json`. Nothing below is paraphrased
  from memory; every number was read off the article text and its Tables/Figures.

---

## 1. Cohort and data — what the sample actually is

| Item | Value | Where |
|---|---|---|
| Study design | Cross-sectional analysis, secondary use of UK Biobank | Methods |
| Headline sample | **50,988** participants with complete proteomic, metabolomic and clinical data | Methods / Results |
| AD cases / controls | **271 AD cases** and 50,717 controls | Methods |
| Proteomics | Olink Explore 3072 (plasma), described as NPX (normalised protein expression) | Methods |
| Metabolomics | Circulating arginine, standardised to z-scores | Methods |
| Genetics used | APOE ε4 dosage + first 3 principal components (PC1–PC3) | Methods |
| Software | R 4.5 | Methods |

**The sample sizes do not hold still, and the headline is the most flattering one.** The paper's own
Table 1 footnote says arginine was available for only **11,003** participants, and the other baseline
variables for 42,448–42,988. The primary hypothesis is *about arginine and its interaction with DDAH1* —
so the n that actually matters for the headline is on the order of **~11,000, not 50,988**, and the
number of *AD cases* inside that ~11,000 is never stated. The abstract also advertises "50,988 … with
available proteomic, metabolomic, clinical, genetic, **and neuroimaging** data"; the imaging analysis is
a separate subset of **N = 1,976**, so the abstract's cohort sentence overstates what the 50,988 carry.

## 2. The evidence table — one row per association reported

Units: DDAH1 and arginine are per **standard deviation (SD)**; OR = odds ratio; CI = confidence
interval; NPX = normalised protein expression.

| # | Analysis | Predictor → outcome | Estimate | 95% CI | p | Adjusted for |
|---|---|---|---|---|---|---|
| 1 | Case-control (Table 1) | DDAH1 NPX, AD vs control (means 0.127 vs 0.037) | Welch t = **2.53** | — | **0.012** | unadjusted |
| 2 | Case-control (body text) | DDAH1, AD vs control (means **0.1399** vs **0.0396**) | Welch t = **-3.22** | — | **0.001** | unadjusted |
| 3 | Case-control (Figure 1 caption) | DDAH1, AD vs control | Welch t = **-3.07** | — | 0.002 | unadjusted |
| 4 | Case-control | PADI2, AD vs control | t = -1.93 | — | 0.053 | unadjusted |
| 5 | Case-control | PADI4, AD vs control | — | — | 0.636 | unadjusted |
| 6 | Baseline (Table 1) | Arginine, AD vs control | t = -1.00 | — | 0.324 | unadjusted |
| 7 | Baseline (Table 1) | Age at recruitment, AD vs control (64.8 vs 56.7 y) | t = 24.19 | — | <0.001 | unadjusted |
| 8 | Baseline (Table 1) | Years of education, AD vs control (12.4 vs 14.7) | t = -6.53 | — | <0.001 | unadjusted |
| 9 | Multivariable logistic | **Arginine → AD (main effect)** | **OR = 0.604** | not given | **0.0033** | age, sex, PC1–3, education, APOE ε4 |
| 10 | Multivariable logistic | DDAH1 → AD (main effect) | not given | — | **0.147** (Wald χ²=2.11) | as row 9 — **null** |
| 11 | Multivariable logistic | **DDAH1 × arginine interaction → AD** | **OR = 1.431** | not given | **0.000108** | age, sex, PC1–3, education, APOE ε4 |
| 12 | Multivariable logistic | Age → AD | OR = 1.23 | not given | <0.001 | — |
| 13 | Multivariable logistic | Male sex → AD | — | — | 0.798 | — (null) |
| 14 | Multivariable logistic | APOE ε4 heterozygote → AD | **OR 3.00** | 1.64–5.45 | 0.000289 | — |
| 15 | Multivariable logistic | APOE ε4 homozygote → AD | **OR 8.27** | 3.63–17.6 | <0.001 | — |
| 16 | Multivariable logistic | Education (per year) → AD | OR = **0.928** | not given | 0.0093 | — |
| 17 | Linear regression, MRI | DDAH1 → 4 structural measures (parahippocampal area, WMH volume, entorhinal thickness, amygdala GM) | β = -0.045 to +0.027 | — | all NS | age, sex, PCs |
| 18 | Linear regression, MRI | DDAH1 → total hippocampal volume (N = **1,976**) | β = **-0.052** | — | 0.016 | age, sex, PCs |
| 19 | Linear regression, MRI | DDAH1 × arginine → hippocampal volume | — | — | 0.625 | — (null) |

## 3. Where I do not believe the source — internal inconsistencies, recorded

**Row 1 vs row 2 vs row 3 is the same comparison reported three ways, with three different statistics
and two different pairs of means.** The identical DDAH1 case-control difference is given as
t = 2.53 / p = 0.012 in Table 1, t = -3.22 / p = 0.001 with means 0.1399 vs 0.0396 in the results
prose, and t = -3.07 / p = 0.002 in the Figure 1 caption — and the abstract reprints p = 0.001. None is
labelled as a different subgroup. (The sign flips between Table 1 and the prose, which is the kind of
thing that happens when one is case-minus-control and the other is control-vs-case, but the paper never
says so.) **A reader should treat the unadjusted DDAH1 difference as "small and positive, exact p
unsettled," not as any one of those numbers.**

Two smaller ones: the arginine mean values (0.062 ± 0.014) are given **without units**; and, as noted in
§1, the abstract's cohort sentence claims neuroimaging data for all 50,988 when imaging is a 1,976-person
subset. **Cureus** is a fee-based, light-touch-review journal, and these two authors publish many
UK-Biobank proteomics-and-AD associations in it; that is a reason to hold the result to the paper's own
arithmetic, which is what this section does.

## 4. What the source itself says it cannot support

Quoting the paper's own limitations, because they are stricter than a summary would be:

- **Cross-sectional**, so "preventing causal inference regarding the directionality of the observed
  associations"; elevated DDAH1 "may represent a compensatory response to disease rather than a causal
  mediator."
- AD status is "based on available clinical and registry-derived data rather than neuropathological
  confirmation" — misclassification possible; few cases limit precision.
- **Plasma DDAH1 protein is not tissue enzyme activity**; "neither ADMA concentration nor nitric oxide
  production was measured directly."
- Residual confounding: vascular comorbidity, medication, renal function, diet, inflammation "were not
  comprehensively modeled."
- MRI relied on macrostructural phenotypes; imaging analyses were "exploratory and … not adjusted for
  multiple comparisons" — so the hippocampal row (β = -0.052, p = 0.016) is nominal.
- Predominantly middle-aged-to-older UK Biobank population; needs external validation.
- Complete-case selection bias.

**The interaction's direction is also easy to misread.** Arginine's *main* effect is protective
(OR = 0.604), and the interaction OR is *above 1* (**1.431**) — which means the protective arginine
association *weakens* as DDAH1 rises, not that DDAH1 amplifies protection. The authors say this
explicitly; a careless reading would invert it.

## 5. The authors' proposed causal chain, restated

DDAH1 degrades ADMA → ADMA less brakes nitric-oxide synthase → more NO → healthier endothelium and
neuroimmune signalling. Their twist: because DDAH1 is *higher* in cases, they read that as a
**compensatory up-regulation** to keep NO available in an arginine-poor environment, not as a driver.
From that they float "therapeutic repositioning of oral arginine" — while also writing that an
observational UK Biobank association "does not establish that supplementation would benefit individuals
with AD." **Record the chain as a hypothesis with a named falsifier, not as a mechanism the data show.**

## 6. What a real triangulation would still need (the next step for item 19/29)

The next action was "retrieve the paper and build an evidence table." That is this file: the seed table
is complete for the single paper. What the same table would need before any claim is made:

1. **ADMA and symmetric dimethylarginine**, and **citrulline/ornithine**, measured — the pathway's
   actual intermediates, absent here.
2. A **genetic instrument**: DDAH1 pQTL/eQTL or an MR design, to separate cause from compensation.
3. **Renal and vascular function** as covariates (DDAH1/ADMA are strongly kidney- and vessel-linked).
4. The **AD case count inside the ~11,003** with arginine — currently missing.
5. A second, independent cohort, and non-European ancestry.

---

*Provenance: identifiers and abstract in `research/ddah1-ukbiobank-source-record.json`; full text read
from PMC13564308 (CC-BY 4.0). Numbers in §2 are pinned mechanically by
`tests/test_ddah1_evidence_table.py`. This file is a literature reading, not a discovery, and implies
no clinical recommendation.*
