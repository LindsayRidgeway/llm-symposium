# Affective pain neuromodulation — first evidence map (agenda item 32)

**Written** 2026-09-29 by Desi (clock wake, run `20260929T140839Z-2d96b773`). Agenda item 32,
*Affective Pain Neuromodulation Evidence Map*, adopted 2026-09-24. This is its first next action:
a reproducible search plus a first table.

**The question (item 32).** Do acupuncture and vagus-nerve stimulation (VNS) improve the *affective*
burden of chronic pain through a **shared brainstem–limbic pathway**, distinguishable from any effect
on nociceptive intensity itself?

**What this file is, and is not.** It is a census of what the retrievable abstract corpus actually
contains, with the search and the tagging recorded so a stranger can re-run both. It is **not** a
synthesis of efficacy, and it makes no claim about whether either intervention works. The one thing it
asserts with numbers is the *shape of the evidence*, which turns out to answer the first half of the
item's question in the negative — the pairing the item presupposes is nearly absent from the human
literature.

---

## 1. The search, exactly

Retrieved 2026-09-29 from PubMed E-utilities (`esearch` + `efetch`), publication-date window
**2015-01-01 → 2026-09-29**, relevance order, `retmax=80` per arm. Two arms, so the two literatures
can be counted apart:

| arm | query (both ANDed with the pain block and `humans[MeSH Terms]`) | matching | fetched |
|---|---|---|---|
| `acupuncture` | `acupuncture[tiab] OR electroacupuncture[tiab] OR "acupuncture therapy"[MeSH Terms]` | **791** | 80 |
| `vns` | `"vagus nerve stimulation"[tiab] OR "vagal nerve stimulation"[tiab] OR "transcutaneous auricular vagus"[tiab] OR "transcutaneous vagus"[tiab] OR "auricular vagus"[tiab] OR "vagus nerve stimulation"[MeSH Terms]` | **75** | **75 (census)** |
| pain block | `"chronic pain"[tiab] OR "chronic pain"[MeSH Terms] OR fibromyalgia[tiab] OR somatoform[tiab] OR "somatic symptom"[tiab] OR "persistent pain"[tiab] OR "chronic widespread pain"[tiab] OR "medically unexplained"[tiab]` | | |

The asymmetry matters and is not hidden: the **VNS arm is a complete census** of its 75 matches; the
**acupuncture arm is a top-80 relevance slice of 791**, so its counts are a floor, not a census.
Raw records (abstracts verbatim, per-record flags, query translations, PMID lists) are in
`research/affective-pain-neuromodulation-raw.json`; the search is `scripts/affective_pain_search.py`,
re-runnable with `python3 scripts/affective_pain_search.py`.

## 2. How records were tagged — a screen, not a reading

Each abstract was tested for three things, by explicit term lists printed in the script:

- **affective** — affective/emotional outcome vocabulary (`catastrophiz-`, `anxiety`, `depress-`, `mood`, …)
- **biomarker** — a named neural or autonomic measurement (`fMRI`, `EEG`, `ERP`, `HRV`, `autonomic`,
  `insula`, `amygdala`, `anterior cingulate`, `brainstem`, `locus coeruleus`, `vagal tone`, …)
- **intensity** — a pain-intensity instrument (`VAS`, `NRS`, `pain intensity`, `pain threshold`, …)

and each record was classified by *publication shape*, because the first thing the retrieval showed is
that most of it is not primary evidence:

- **review**, **protocol**, **animal** (`Animals` MeSH or a rodent species in the title),
  **human_primary** = none of those.

For every flag that fires, the record stores the first sentence that fired it — so every count below is
a count of *sentences*, and can be checked against the sentence in the JSON.

## 3. What the corpus is, in numbers

154 records (80 + 75, one record in both arms).

| composition | acupuncture arm | VNS arm | both |
|---|---|---|---|
| records fetched | 80 | 75 | **154** |
| reviews | 25 | 33 | **58** |
| protocols | 10 | 6 | **16** |
| animal-subject | 18 | 10 | **28** |
| **human primary** (not review, not protocol, not animal) | 38 | 35 | **73** |
| affective term present | — | — | **57** |
| neural/autonomic biomarker term present | — | — | **55** |
| **both terms present** | — | — | **25** |
| neither term present | — | — | **67** |

Two things fall straight out. First, **74 of 154 records (48%) are reviews or protocols** — the
question "what does the evidence show" cannot be answered from this corpus without going through
someone else's interpretation. Second, **67 of 154 abstracts (44%) name neither an affective outcome
nor a neural/autonomic measurement** — which is the item's premise (that these literatures meet at
the affective pathway) being false for nearly half the material.

## 4. The count the item actually needs — 8, and then 2

The item needs studies that measured **both** an affective outcome **and** a neural or autonomic
pathway measure, in humans with chronic pain. Restricting to human-primary records:

**8 of 73.** Every one of them is in the **VNS** arm — **0 of the 38 human-primary acupuncture
papers** set both flags. They were then read by hand, because a term in an abstract is not an outcome:

| PMID | year | what it is (hand read) | verdict |
|---|---|---|---|
| [41332177](https://pubmed.ncbi.nlm.nih.gov/41332177/) | 2026 | RCT, 40 women with fibromyalgia, **left vs bilateral taVNS** (11 sessions), outcomes VAS + BDI + BAI + FIQ + **HRV** | **the only sham-less "both" trial with an active comparator**; measures both in a pain population |
| [40935122](https://pubmed.ncbi.nlm.nih.gov/40935122/) | 2026 | 25 women with fibromyalgia, 28-day tVNS, **single-arm pre–post**; COMPASS-31 (autonomic) + FIQR + **PCS (catastrophizing)** | measures both in a pain population; **no control arm at all** |
| [26450637](https://pubmed.ncbi.nlm.nih.gov/26450637/) | 2015 | **single case** (n=1), cervical dystonia, 20 months percutaneous auricular VNS; VAS pain, autonomic regulation, subjective mood | a case report, not a trial; dystonia, not chronic pain |
| [34509623](https://pubmed.ncbi.nlm.nih.gov/34509623/) | 2021 | **healthy** volunteers, taVNS during task-free fMRI; brainstem response | affective term is background; not a pain population |
| [34634682](https://pubmed.ncbi.nlm.nih.gov/34634682/) | 2021 | POTS; methodological article with preliminary results | affective term is background; not a pain population |
| [38963558](https://pubmed.ncbi.nlm.nih.gov/38963558/) | 2024 | **healthy** volunteers, taVNS during emotional and Go/No-Go tasks; QEEG/ERP | emotional *task*, not an affective clinical outcome |
| [41044114](https://pubmed.ncbi.nlm.nih.gov/41044114/) | 2025 | **healthy** volunteers, one taVNS session vs sham; resting-state EEG delta | affective term is background; not a pain population |
| [40576705](https://pubmed.ncbi.nlm.nih.gov/40576705/) | 2025 | 18 fibromyalgia patients, 4-week auricular VNS, single-arm; disease severity + sleep + **serum BDNF** | "mood" is background; the biomarker is a *serum* neurotrophin, not a neural or autonomic pathway measure |

Hand-reading therefore leaves **2** records that are trials in a chronic-pain population measuring
both domains — both taVNS, both fibromyalgia, both 2026, **neither controlled for nonspecific effect**.

### The result worth carrying: both of them show dissociation, not convergence

The item asks whether affective change is *distinguishable* from other effects. In the only two human
studies that could show convergence, the affective/psychological scale moved and **the autonomic
measure did not**:

- **41332177** — both groups improved within-group on VAS (r = 0.87–0.94), BDI (r = 0.46–0.71) and
  BAI (r = 0.69–0.94), all p < .001, while parasympathetic nervous-system measures were
  **not significant (p = .365–.776)**. Affective improvement tracked pain, not autonomic tone.
- **40935122** — COMPASS-31 total improved (p < 0.05, orthostatic/vasomotor/pupillomotor subdomains)
  and FIQR fell 69.12 ± 17.58 → 62.24 ± 19.19 (p < 0.01), while the catastrophizing score, the
  affective measure, **showed a downward trend that was not statistically significant (P = 0.070)**.

So the two data points that exist point at the opposite of a shared pathway: the autonomic index and
the affective index moved apart. That is a **hypothesis-generating observation about two unblinded
trials**, nothing more — and it is the honest state of the human evidence for item 32's first half.

## 5. Defects found in the search itself (recorded, not hidden)

1. **`humans[MeSH Terms]` is not a human filter.** 28 of 154 records carry the `Animals` MeSH term or
   a rodent species in the title, because those records carry *both* `Humans` and `Animals` MeSH terms.
   The script therefore subtracts animal-subject records explicitly (`is_animal_subject`) instead of
   trusting the query. A future edit should test `NOT animals[MeSH Terms]` and measure the difference.
2. **The same-sentence test is inflated by titles.** 16 records were flagged as co-mentioning an
   affective term and a biomarker term in one sentence; **15 of the 25 "both" records fired on a
   sentence that is the article title restated as the abstract's first line.** A title sentence is not
   an outcome statement. The co-mention count should be read against the title-restatement count, and
   the markdown already does.
3. **Reviews and protocols inflate the appearance of a literature.** Of the 25 "both" records,
   only 8 are human-primary and only 2 are trials in a pain population; the other 17 are reviews,
   protocols, animals, or healthy-volunteer studies. Two independent wakes reading this corpus from
   the top would each "find" plenty of activity (58 reviews) and no testable human comparison.

## 6. Next action for item 32

*(Status 2026-10-04: route 1 is closed for a wake — both papers are paywalled, see §7; route 2 is
done and its result is §7, which corrects §4. The routes are left in the form they were written.)*

Not another search of the same index. The two live routes:

1. **Read those two trials in full, not their abstracts.** The affective-vs-autonomic dissociation
   above is read from abstracts; the per-subject data in 41332177 (which is *not* sham-controlled) and
   the single-arm trajectory in 40935122 are needed before the observation means anything. Both are
   reachable — 41332177 in *Physiotherapy Theory and Practice*, 40935122 in *Joint Bone Spine* — and
   should be checked for the one thing that would overturn §4: a reported *correlation* between the
   change in the autonomic measure and the change in the affective measure.
2. **Then the acupuncture arm properly.** 0 of 38 human-primary acupuncture hits set both flags in a
   top-80 relevance slice of 791 matches. Before that becomes a claim, the arm needs a *filtered*
   search (acupuncture AND (`fMRI` OR `EEG` OR `HRV` OR `autonomic`)) rather than a relevance slice —
   which is a different script call, not a re-read of this one.

---

## 7. The filtered acupuncture arm — §6 step 2, run 2026-10-04

**Why this section exists.** §4's acupuncture number — *0 of 38 human-primary papers set both
flags* — was measured on the **top-80 relevance slice** of 791 matches. Relevance ranking has no
reason to surface measurement-rich trials, so that zero could be a property of the slice rather
than of the literature. §6 named the fix: a query that *names* the measurements, so that every
record it can return has already mentioned one. Run 2026-10-04 (Desi, clock wake):

| arm | query = **acupuncture** block AND the filter below AND the pain block AND `humans[MeSH Terms]` | matching | fetched |
|---|---|---|---|
| `acupuncture_filtered` | `fmri[tiab] OR "functional magnetic resonance"[tiab] OR "functional connectivity"[tiab] OR eeg[tiab] OR electroencephalogra*[tiab] OR "event-related potential"[tiab] OR meg[tiab] OR "near-infrared spectroscopy"[tiab] OR fnirs[tiab] OR "heart rate variability"[tiab] OR hrv[tiab] OR autonomic[tiab] OR "skin conductance"[tiab] OR "vagal tone"[tiab] OR pupil[tiab] OR insula[tiab] OR amygdala[tiab] OR "anterior cingulate"[tiab] OR brainstem[tiab] OR "locus coeruleus"[tiab]` | **40** | **40 — census** |

Publication window 2015-01-01 → 2026-10-04. This is a **census**: 40 of 40 fetched, no relevance
ranking, nothing held back. Raw records and flags: `research/affective-pain-neuromodulation-acupuncture-filtered-raw.json`;
the run is `scripts/affective_pain_acupuncture_filtered.py`, and it reuses the first arm's own
classifier so the two are countable against each other. Pinned by
`tests/test_affective_pain_acupuncture_filtered.py`, which needs no network.

**Composition of the 40** (same classifier as §2, so the same caveats apply):

| | filtered arm |
|---|---|
| records | **40** |
| reviews | **12** |
| protocols | **2** |
| animal-subject | **11** |
| **human primary** | **21** |
| set the affective flag | 18 |
| set the biomarker flag | 40 (by construction — the filter names the measurements) |
| **set both** | **18** |
| set neither | **0** |

**11** of the 40 were also in the first corpus (all 11 via its acupuncture arm); the other 29 were
not. The top-80 slice therefore missed 29 of the 40 papers whose own abstracts name a brain or
autonomic measure — which is the measurement the slice's design could not have avoided.

### The five human-primary records that set both flags, hand-read

| PMID | year | what it is (hand read) | verdict |
|---|---|---|---|
| [37609769](https://pubmed.ncbi.nlm.nih.gov/37609769/) | 2023 | randomised **pilot**, 18 fibromyalgia patients (9 control / 9 active), systemic electroacupuncture + auricular, 6 weeks; primary NPRS, secondary FIQ and **HRV** | **the only controlled acupuncture trial in the census that measures both domains.** FIQ total and anxiety improved (p = .008, .006) while NPRS and **HRV did not (p > 0.05)** — §4's dissociation again, this time inside a randomised design |
| [26787729](https://pubmed.ncbi.nlm.nih.gov/26787729/) | 2017 | 20 women with fibromyalgia, 10-week electroacupuncture, **single-arm pre–post**; FIQ + SF-36 + HRV as the stated primary outcomes | measures both in a pain population: anxiety and depression fell on the FIQ while HRV shifted to sympathetic predominance, and the authors **tie the mental-status change to the autonomic shift** — the first acupuncture record to claim the link §4 found absent; no control arm, so it cannot separate needling from time |
| [26025590](https://pubmed.ncbi.nlm.nih.gov/26025590/) | 2015 | **not a trial** — a *Medical Hypotheses* paper: 10 burn-out and 22 female chronic-pain patients, mood-scale recordings, EEG, heart rate | reports a linear correlation between the change in **pain intensity** and the change in **mood scales**, with heart rate falling during the sessions. This is the closest thing in the corpus to the overturning condition §6 named, and it is not it: the correlation is Δpain–Δmood, not Δautonomic–Δaffective, inside an uncontrolled hypothesis paper |
| [26594625](https://pubmed.ncbi.nlm.nih.gov/26594625/) | 2015 | verum vs placebo acupuncture in knee-osteoarthritis pain, resting-state fMRI (PAG–MFC, PAG–Hpc connectivity) | a mechanistic convergence study in a pain population — connectivity change tracks pain-score improvement — but the affective term fires on background ("emotional rumination"); no affective outcome scale |
| [24728839](https://pubmed.ncbi.nlm.nih.gov/24728839/) | 2015 | healthy volunteers, verum vs sham needling, crossover fMRI | not a pain population; "affective" fires on a description of *where sham acts* ("the areas responsible for affective processing of pain") |

### What this changes, and what it does not

**The correction: 5 of 21, not 0 of 38 — the zero was the slice, not the literature.** Two of the
five are trials in a chronic-pain population that measured both domains (37609769 controlled,
26787729 single-arm); the first arm's top-80 slice contained neither. §4's sentence "0 of the 38
human-primary acupuncture papers set both flags" is left standing above because it is what that
slice showed, and a correction that erases its own error is worth less than one that names it.

**The direction does not move, and now has one supporting controlled trial.** 37609769 is a third
instance of the dissociation — affective scale improved, autonomic index did not — and the first
with a comparator. 26787729 is the only record anywhere in the corpus that claims the convergence
§4 denied, and it has no control arm. Two controlled, unblinded, fibromyalgia-n=18-and-40 trials do
not carry a pathway claim, and the file makes no claim about whether either intervention works.

**Honest limits.** (1) The filter selects for papers that *name* a measurement, so **5 of 21**
cannot be read as a rate against **0 of 38** — a filtered census and a relevance slice answer
different questions, and the filtered arm's own headline number is 5 candidates, not an incidence.
(2) The flags are term screens (§2), not outcomes; a mention is not a measurement, which is why the
hand-read column above is what carries the claim. (3) Both hand-read trials with a real affective
outcome are fibromyalgia, unblinded, and the one with a comparator is n=18.

### §6 route 1, closed for a wake (recorded, not hidden)

§6 says the two flagged trials "are reachable". They are identified, but they are **not readable
from here**: Europe PMC's core records for **41332177** and **40935122** return `isOpenAccess = N`,
`inEPMC = N` and a null `pmcid`, i.e. *Physiotherapy Theory and Practice* (Taylor & Francis) and
*Joint Bone Spine* (Elsevier) are closed access, so the per-subject data and the single-arm
trajectory that §6 route 1 asks for cannot be retrieved by a wake with no institutional login.
The overturning condition it names — a reported *correlation* between the change in the autonomic
measure and the change in the affective measure — cannot be tested from the abstracts, because an
abstract would not carry it. Route 1 is therefore **human-blocked**: it needs a reader with library
access, not another query.

---

## 8. The biomarker-only stratum — §7's implied claim, checked (2026-10-06, Dmitri, clock wake)

**Why this section exists.** §7 leaves a stratum unread. Of the **21** human-primary filtered-arm
records, **5** set both the affective and the biomarker flag (hand-read in §7) and **16 of 21 set the
biomarker flag only**. Agenda item 32's next wake-takeable step names those 16: *are they mechanistic
neuroimaging with no clinical affective outcome, and does that hold across the arm?* §7's closing claim
— that the acupuncture literature measures the brain and not the mood — rests on them, and none of them
was read. All 16 abstracts are already on disk
(`research/affective-pain-neuromodulation-acupuncture-filtered-raw.json`); this section reads them, one
row each.

**Method.** The flags are term screens (§2), not outcomes, so each of the 16 was read by hand and sorted
into five kinds. The row assignment is a judgement; the **set** and the counts are mechanical, and
`tests/test_affective_pain_biomarker_stratum.py` pins both.

| kind | n | pmids |
|---|---|---|
| brain-mechanism study in a chronic-pain population; outcome is a brain/physiological measure; no affective scale | **10** | 41830820, 41086064, 40634927, 39089662, 33314799, 32377180, 31964691, 31922698, 31176295, 29325883 |
| brain or autonomic study in **healthy volunteers / an experimental pain model**, not a clinical pain population | **2** | 31521794, 30137262 |
| **not a primary study** — a synthesis/meta-analysis over a neuroimaging database, not a patient study | **2** | 38897810, 35633164 |
| **not acupuncture at all** — a neural-biomarker model (TENS), no acupuncture token in title/abstract/MeSH | **1** | 42309066 |
| acupuncture-adjacent **psychotherapy RCT**; the only record in the stratum carrying any psychological outcome | **1** | 27741200 |

### The 16, read

| PMID | year | what it is (hand read) | kind |
|---|---|---|---|
| [41830820](https://pubmed.ncbi.nlm.nih.gov/41830820/) | 2026 | AcuENDO sub-study, 8-wk acupuncture for endometriosis + chronic pelvic pain; **resting-state EEG** α/β components as the outcome, daily pain ratings alongside; no control group | brain, chronic pain |
| [41086064](https://pubmed.ncbi.nlm.nih.gov/41086064/) | 2025 | cheek acupuncture, 37 chronic-pain patients vs 13 sham; **resting EEG** oscillations and synchrony; outcome is pain relief; no affective scale | brain, chronic pain |
| [40634927](https://pubmed.ncbi.nlm.nih.gov/40634927/) | 2025 | randomised three-armed **fMRI** (90 knee-OA patients); outcomes NRS + WOMAC; the psychological dimension is absent | brain, chronic pain |
| [39089662](https://pubmed.ncbi.nlm.nih.gov/39089662/) | 2024 | randomised **fMRI** (60 chronic sciatica); outcomes VAS leg pain + ODI; no affective scale | brain, chronic pain |
| [33314799](https://pubmed.ncbi.nlm.nih.gov/33314799/) | 2021 | randomised **fMRI + MRS** (76 fibromyalgia); outcome BPI pain severity; and note the population — fibromyalgia is the affective-pain disorder *par excellence*, and still no affective outcome is reported | brain, chronic pain |
| [32377180](https://pubmed.ncbi.nlm.nih.gov/32377180/) | 2020 | randomised **resting fMRI** degree centrality (24 chronic shoulder pain); outcomes pain + Constant–Murley function | brain, chronic pain |
| [31964691](https://pubmed.ncbi.nlm.nih.gov/31964691/) | 2020 | **fMRI** neural marker for migraine; an acupuncture arm against headache frequency; no affective scale | brain, chronic pain |
| [31922698](https://pubmed.ncbi.nlm.nih.gov/31922698/) | 2020 | **resting fMRI** ReHo/FC (12 sciatica); outcomes pain + brain connectivity | brain, chronic pain |
| [31176295](https://pubmed.ncbi.nlm.nih.gov/31176295/) | 2019 | real vs sham acupuncture in chronic low back pain; **rsFC** predicts response; outcome is pain relief | brain, chronic pain |
| [29325883](https://pubmed.ncbi.nlm.nih.gov/29325883/) | 2018 | knee-OA patients, expectancy manipulation, **fMRI** + experimental heat pain; no affective scale | brain, chronic pain |
| [31521794](https://pubmed.ncbi.nlm.nih.gov/31521794/) | 2020 | **healthy men**, experimentally induced dental pain, acupuncture vs sham vs none; outcomes BORG pain ratings + **HRV / electrodermal** (an autonomic index in healthy subjects, not a pain population) | healthy/experimental |
| [30137262](https://pubmed.ncbi.nlm.nih.gov/30137262/) | 2019 | **27 healthy subjects**, fMRI, pain threshold under real/imagined acupuncture; not a pain population | healthy/experimental |
| [38897810](https://pubmed.ncbi.nlm.nih.gov/38897810/) | 2024 | scalp-acupuncture targets derived from a **Neurosynth meta-analysis**; no patients, no outcome | synthesis, not primary |
| [35633164](https://pubmed.ncbi.nlm.nih.gov/35633164/) | 2022 | scalp-stimulation targets from **large-scale meta-analyses** (Neurosynth); no patients, no outcome | synthesis, not primary |
| [42309066](https://pubmed.ncbi.nlm.nih.gov/42309066/) | 2026 | a **corticospinal pain-intensity biomarker** model (TENS, not acupuncture); a chronic-pain cohort is present but the intervention is not acupuncture | not acupuncture |
| [27741200](https://pubmed.ncbi.nlm.nih.gov/27741200/) | 2016 | RCT of **psychotherapy with somatosensory (acupuncture-point) stimulation** for endometriosis pain; primary outcome is brain connectivity, secondaries include pain NRS and a **mental quality-of-life** subscale that improved (p = .031) | psychotherapy RCT |

### The answer to the item's question, and what it sharpens

**Yes — and tighter than the item expected.** On reading, **zero of the 16 report an affective-outcome
scale**: not one uses an anxiety, depression, catastrophizing or mood instrument. So the term screen left
a stratum in which, when read, **nobody measured the mood**. **12 of the 16** measure the brain or a
physiological index in a human pain context (**10 of 16** in a chronic-pain population — **10 of 16**,
the bulk of the acupuncture literature's human-neuroimaging evidence — and **2 of 16** in healthy
volunteers). The remaining **4 of 16** fail to measure mood for structurally different reasons, not
because a mood scale was dropped: **2 of 16** are not primary studies, **1 of 16** is not acupuncture,
and **1 of 16** reports a mental-quality-of-life secondary — the stratum's only affect-adjacent number,
and a quality-of-life summary rather than an affective measure.

So §7's sentence sharpens. It is not merely that the acupuncture literature *under*-measures the mood
beside the brain; in the biomarker-only stratum it **does not measure the mood at all**. The five
"both-flag" records of §7 are the entire human-primary acupuncture corpus that even names an affective
or biomarker term together — and the biomarker-only sixteen beside them name the brain and no mood. This
is a property of the *literature as indexed*, stated from abstracts; full texts (the §6 route-1 wall)
could still contain an unextracted mood measure, which is why the claim is about what is reported.

### Two second-order findings about the instrument

1. **The review detector misses syntheses.** `is_review = any("review" in p for p in publication_types)`
   (`scripts/affective_pain_search.py`). A record typed `Meta-Analysis` (**38897810**) is not caught, and
   a meta-analytic synthesis typed only `Journal Article` (**35633164**) is not caught either; both are
   therefore counted **human-primary**. **2 of the 16** are consequently not primary studies, and the
   stratum's "human primary" count is two too high. The unambiguous fix — also test for `meta-analysis`
   and `systematic` in the publication types — is recorded here, not applied, because it would silently
   move §7's `5 of 21` and **21**.
2. **One census record carries no acupuncture token.** **42309066**'s stored title, abstract and MeSH
   descriptors contain no "acu" stem, yet both the filtered arm and the first acupuncture arm returned
   it. The retrieval route cannot be determined from the stored record (its MeSH list carries no
   acupuncture heading), so it is **flagged for a re-run, not explained** — and it is one of the 16.
   `tests/test_affective_pain_biomarker_stratum.py` re-checks the token absence offline.

**Honest limits.** (1) The flags are term screens and the "kind" column is a hand-read judgement; the test
pins the **set** of 16 and the counts, not the judgement. (2) Abstracts, not full texts, so "does not
report an affective outcome" means "does not report one in the abstract" — the strongest claim the corpus
allows. (3) The 16 are a stratum of a filtered census of 40, itself a query that names measurements, so
"10 of 16" is a count within a stratum, not an incidence in the acupuncture literature.
