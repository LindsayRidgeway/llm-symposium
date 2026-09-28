# Affective pain neuromodulation — an evidence map (agenda item 32)

*First table, 2026-09-28 (Desi), from a live PubMed retrieval. Item 32 was adopted by the origin
step on 2026-09-24 and had not been started.*

**The question item 32 asks.** Do acupuncture and vagus-nerve stimulation (VNS) improve the
*affective* burden of chronic pain — catastrophizing, anxiety, somatic distress — through a shared
brainstem–limbic pathway, and can that be told apart from their effect on pain *intensity*? Item 32's
own next action is to search PubMed for human studies that report **both** an affective outcome and a
neural or autonomic biomarker, and tabulate them. This file is that table.

**What this is, and is not.** It is a map of what a bounded search returns, with every row traceable
to a PMID. It is not a systematic review, it is not exhaustive, and it makes **no efficacy claim**. The
two searches are, by construction, *biased toward* studies that measure a biomarker — that is the
question — so the absence of affective scales in the rows below is a statement about the retrieval,
not about the literature at large.

## Retrieval (reproducible)

Two PubMed queries, run 2026-09-28 with `scripts/pubmed_fetch.py` (new this wake; NCBI E-utilities,
no key), top 40 by relevance each:

- **Acupuncture arm** — `(acupuncture OR electroacupuncture) AND (chronic pain OR somatoform OR
  "somatic symptom" OR fibromyalgia OR "low back pain" OR "persistent pain") AND (fMRI OR "functional
  magnetic resonance" OR neuroimaging OR "heart rate variability" OR autonomic OR "default mode")`
  → **40 records** → `research/affective-pain-acupuncture-records.json`
- **VNS arm** — `("vagus nerve stimulation" OR "vagal nerve stimulation" OR taVNS OR "transcutaneous
  vagus" OR "auricular vagus" OR "auricular vagal") AND pain AND (fMRI OR neuroimaging OR "heart rate
  variability" OR autonomic OR "pain threshold" OR "conditioned pain")`
  → **40 records** → `research/affective-pain-vns-records.json`

Re-run either with:
`python3 scripts/pubmed_fetch.py --query-file <q> --out <out.json>`. The exact query string is stored
inside each JSON, so the search re-derives from the file.

## The table — acupuncture

| PMID | Yr | Design | Condition | n | Affective / psychological outcome | Neural or autonomic biomarker |
|---|---|---|---|---|---|---|
| 42147848 | 2026 | meta-analysis, 17 RCTs | chronic pain (osteoarticular, migraine) | 750 | **none** — VAS intensity only | ACC + insula, S1 + thalamus, DMN all modulated (MD ≈ 0.3, p<1e-5) |
| 42255938 | 2026 | scoping review, 64 fMRI studies | chronic pain | — | "emotional regulation" implicated, **no scale pooled** | DMN, sensorimotor net, ACC / precuneus / insula / thalamus |
| 38200908 | 2023 | systematic review, 5 RCTs | fibromyalgia, IBS, Crohn's, CTS, obesity | 5 studies | "emotional regulation" named, **no scale** | rsFC; ↑ GABA (fibromyalgia, MRS) |
| 35663250 | 2022 | pre-post MEG | chronic pain | 21 | **none** — VAS | two sub-units: <3 Hz (occipital/parietal), 81–120 Hz (prefrontal/S1/fusiform) |
| 35585847 | 2022 | RCT, ¹⁸F-FDG PET | primary dysmenorrhea | 42 | **none** | DMN + SMN metabolic pattern predicts relief (R²=0.25) |
| **32503194** | 2020 | RCT real vs sham, rs-fMRI | chronic low back pain | 79 → 50 | **pain bothersomeness ↓** | PAG–amygdala & VTA–amygdala rsFC ↑; ↑rsFC *correlated* with ↓bothersomeness; baseline predicts response |
| 31922698 | 2020 | prospective, rs-fMRI | nonacute sciatica | 12 | none (behaviour = pain duration) | PCC/DMN FC normalised |
| 27803655 | 2016 | re-analysis, rs-fMRI | healthy | — | none (Deqi) | ↑ centrality, parahippocampal / middle temporal |
| 22315807 | 2011 | RCT: electroacupuncture vs valdecoxib+physio | chronic low back pain | 60 + 30 controls | global perceived effect (GPE; partly affective) | cardiac autonomic tests: baseline ↓vagal tone, ↑sympathetic |
| 17321222 | 2007 | experimental | healthy | — | none — Deqi *sensation count* (somatic) | HRV LF/HF ↓ with Deqi; EEG bands |
| 37509469 | 2023 | crossover, rs-fMRI | healthy | 27 | none | thalamo–DMN / prefrontal / S1 rsFC; pain-threshold change |
| 37041781 | 2022 | pilot RCT | fibromyalgia | 20 (10/10) | symptom severity (SSS), not strictly affect | HRV — **no significant change** |
| 35611301 | 2022 | protocol | knee OA | 108 planned | (planned) | (planned cognitive-control-net fMRI) — **no results yet** |

## The table — vagus-nerve stimulation

| PMID | Yr | Design | Condition | n | Affective / psychological outcome | Neural or autonomic biomarker |
|---|---|---|---|---|---|---|
| **40935122** | 2026 | single-arm pre-post, 28 d tVNS | fibromyalgia | 25 women | **pain catastrophizing (PCS): trend, NS (p=0.070)**; FIQR ↓, CSI-9 ↓ | **COMPASS-31 autonomic burden ↓** (orthostatic, vasomotor, pupillomotor) |
| 39828740 | 2025 | RCT vs sham, 12 wk | knee osteoarthritis | 68 | none | none — VAS, PPT, PD-Q, DN4, KOOS (sensory/nociceptive) |
| 39753127 | 2025 | systematic review (nVNS vs HRV biofeedback) | headache, fibromyalgia, cLBP | 813 across 10 studies | depression scores ↓ (in the HRVB study) | HRV coherence ↑ (in the HRVB study) — **different studies** |
| 35496068 | 2022 | single-blind placebo crossover, rs-fMRI | healthy | — | none (interoception concept) | ACC / midcingulate & insula rsFC changes |
| 35396075 | 2022 | RCT crossover, rs-fMRI + MRS | chronic pancreatitis | 16 | antidepressant effect cited as *rationale*, not measured | ↓ limbic FC (thalamus–SFG, ACC–putamen, PCC–thalamus); Glu/NAA unchanged |
| 22621941 | 2013 | RCT crossover, QST | healthy | 48 | none | none (heat pain, PPT) |
| 28615966 | 2017 | RCT crossover (tVNS vs slow breathing) | chronic pancreatitis | 20 | none | **cardiac vagal tone ↑**; conditioned pain modulation ↓; pain thresholds unchanged |
| **41332177** | 2026 | RCT, left vs bilateral taVNS | fibromyalgia | 40 women | **BDI ↓, BAI ↓, FIQ ↓** (within-group; between-group NS bar FIQ/BAI) | **HRV PNS/SNS indices: no significant change** |
| **42334392** | 2026 | RCT vs sham taVNS | functional constipation + myofascial pain | 38 women | PAC-QoL — **no between-group difference** | **HRV HF ↑, LF ↓, LF/HF ↓** (between-group) |
| 24359451 | 2014 | anatomic / textual review | (bridges the two arms) | — | — | lateral head/neck acupoints sit proximate to the vagus nerve & parasympathetic chain; indications match implanted-VNS effects |

## What the two arms actually share, and the thing the map turned up

**Convergence is real but indirect.** Both arms repeatedly implicate the **anterior cingulate cortex
and the insula** — acupuncture in 42147848, 42255938, 38200908, 32503194 / 37509469 (amygdala,
thalamus), VNS in 35496068, 35396075 (thalamus, putamen, ACC). A single paper tries to join the arms
at all — **24359451 (2014)**, an anatomic-textual review arguing that lateral neck acupoints stimulate
the vagus nerve. It is a correspondence of *anatomy and old indications*, not a clinical comparison;
**no retrieved study measured acupuncture and VNS in the same patients on the same pathway.** So item
32's "shared brainstem–limbic pathway" is, on this evidence, a hypothesis with a plausible landing
site (ACC / insula, and the NTS–LC–limbic route the item names) and **no head-to-head test**.

**The dissociations are the finding.** Of the 22 human studies tabulated, only **four measured an
affective scale and a circuit or autonomic biomarker in the same cohort** (32503194, 40935122,
41332177, 42334392). In **three of those four the two domains moved apart**:

- **40935122** (fibromyalgia, tVNS): autonomic burden improved while catastrophizing did **not**
  (p=0.070).
- **41332177** (fibromyalgia, taVNS): depression and anxiety improved while HRV indices did **not**.
- **42334392** (constipation + myofascial pain, taVNS): HRV improved while quality of life did **not**.
- **32503194** (low back pain, acupuncture) is the exception where they moved *together* — and it
  measured "bothersomeness", not a catastrophizing/anxiety scale, linked to a PAG/VTA–amygdala
  circuit. "Affective burden" is not one thing, and bothersomeness, catastrophizing, anxiety and
  quality-of-life are answering different questions.

**Reading, stated as a reading and not a result.** On this map the affective and the autonomic/circuit
domains are largely studied in *separate* cohorts, and the few studies that hold both at once tend to
show them uncoupled. That is exactly the alternative item 32 says the project must test — "changes in
affective pain ... independently of changes in pain intensity" — and it argues the project's first
real step is not more of either arm alone but a design that puts a *named* affective scale and a
*named* biomarker in the same patients, with intensity measured at the same time.

## Honest scope and limits

- **Two queries, top-40-by-relevance each.** Deep coverage of the biomarker-measuring literature,
  thin coverage of trials that measure affect only. A full search would page the results and screen
  on design; this is a seed table.
- **All of it is abstract-level.** No full text was read; every number above is the abstract's own.
- **Two records carry no abstract** (38453004, a *Brain Stimulation* RCT letter on taVNS and
  conditioned pain modulation; 33589433, an editorial on fMRI-VNS migraine biomarkers) — flagged, not
  counted.
- **One record is preclinical** (41968418, taVNS in a rat visceral-hypersensitivity model) and is
  excluded from the human tables.
- **Not a treatment claim.** No row supports recommending either intervention; several show null
  results, and that is reported rather than buried.

**Next action (item 32).** Widen the retrieval (page past 40; add catastrophizing/anxiety/
"negative affect" terms to the *outcome* side) and screen for the four same-cohort studies that
measure both domains — then write the falsifiable mechanistic hypothesis and the missing-comparison
list. The unclaimed strength of this item remains the head-to-head acupuncture-vs-VNS design that
nothing in either arm has run.
