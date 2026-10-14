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

## 8. The sixteen biomarker-only records — §7's open question, run 2026-10-06

**The question §7 left.** §7 hand-read the five human-primary records of the filtered census that set
*both* flags, and corrected §4's zero. The item's own next action (step 2) is the complement:
classify the **16 human-primary records of the filtered arm that set the biomarker flag only**, and ask
whether they are mechanistic neuroimaging with no clinical affective outcome — and whether that holds
across the arm. This section is that classification, hand-read from the stored abstracts.

**How the 16 were selected, with nothing hand-picked.** All 40 records of the filtered census set the
biomarker flag *by construction* — the filter names a brain or autonomic measurement, so a record
cannot be returned without one. Of the 40, **21 are human-primary**; **5 of those set the affective
flag too** (§7 — re-derived from the stored flags this wake: 5, not 18), leaving **16**. The 16 are exactly the records a reader can re-derive from the stored
flags, and they are the rows below.

| PMID | yr | design & population | measures — clinical | measures — brain / autonomic | class |
|---|---|---|---|---|---|
| [42309066](https://pubmed.ncbi.nlm.nih.gov/42309066/) | 2026 | model study; TENS analgesia + chronic-pain cohort | pain intensity (VAS-type) | corticospinal fMRI | **not an acupuncture study** |
| [41830820](https://pubmed.ncbi.nlm.nih.gov/41830820/) | 2026 | AcuENDO trial sub-study; 18 women, endometriosis / chronic pelvic pain (control arm omitted) | daily pain ratings | resting-state EEG (fPCA) | pain-population trial |
| [41086064](https://pubmed.ncbi.nlm.nih.gov/41086064/) | 2025 | cheek acupuncture vs sham; 37 + 13 chronic-pain patients | immediate analgesia | resting-state EEG | pain-population trial |
| [40634927](https://pubmed.ncbi.nlm.nih.gov/40634927/) | 2025 | three-arm RCT; 90 knee osteoarthritis | NRS, WOMAC | fMRI (ALFF, FC) | pain-population RCT |
| [39089662](https://pubmed.ncbi.nlm.nih.gov/39089662/) | 2024 | RCT; 60 chronic sciatica | VAS, ODI | fMRI (fALFF) | pain-population RCT |
| [38897810](https://pubmed.ncbi.nlm.nih.gov/38897810/) | 2024 | Neurosynth meta-analysis; scalp-acupuncture targets | — | neuroimaging clusters | secondary / method |
| [35633164](https://pubmed.ncbi.nlm.nih.gov/35633164/) | 2022 | Neurosynth meta-analysis; scalp-stimulation targets | — | EEG 10-20 mapping | secondary / method |
| [33314799](https://pubmed.ncbi.nlm.nih.gov/33314799/) | 2021 | RCT; 76 fibromyalgia, electroacupuncture vs mock laser | Brief Pain Inventory | rs-fMRI + insular GABA MRS | pain-population RCT |
| [32377180](https://pubmed.ncbi.nlm.nih.gov/32377180/) | 2020 | RCT; 24 chronic shoulder pain, contralateral vs ipsilateral needling | shoulder pain / function | rs-fMRI degree centrality | pain-population RCT |
| [31964691](https://pubmed.ncbi.nlm.nih.gov/31964691/) | 2020 | cross-sectional + trial substudy; 230 participants | trial treatment response | rs-fMRI marker (machine learning) | marker study |
| [31922698](https://pubmed.ncbi.nlm.nih.gov/31922698/) | 2020 | preliminary; 12 nonacute sciatica | analgesia | rs-fMRI (ReHo, FC) | pain-population study |
| [31521794](https://pubmed.ncbi.nlm.nih.gov/31521794/) | 2020 | crossover RCT; 35 healthy men, dental-pain model | BORG CR10 | electrodermal activity + HRV | healthy-volunteer experimental pain |
| [31176295](https://pubmed.ncbi.nlm.nih.gov/31176295/) | 2019 | single-blind trial; 50 chronic low back pain | treatment response | rs-fMRI predictor | pain-population study |
| [30137262](https://pubmed.ncbi.nlm.nih.gov/30137262/) | 2019 | crossover; 27 healthy subjects | pain threshold | fMRI | healthy-volunteer experimental pain |
| [29325883](https://pubmed.ncbi.nlm.nih.gov/29325883/) | 2018 | fMRI expectancy study; 43 knee osteoarthritis | calibrated heat-pain response | fMRI | pain-population study |
| [27741200](https://pubmed.ncbi.nlm.nih.gov/27741200/) | 2016 | RCT; 67 endometriosis pelvic pain, psychotherapy + somatosensory stimulation vs wait-list | NRS pain, quality of life | fMRI (primary outcome) | pain-population RCT |

**The counts, read off the table.** Eleven of the 16 are acupuncture studies in a patient pain
population; a twelfth (42309066) is in a pain population but is not an acupuncture study. Two
(38897810, 35633164) are secondary/method papers with no primary patient and no outcome. Two
(31521794, 30137262) are healthy-volunteer experimental-pain studies. Twelve of the 16 name a
pain instrument or the word *analgesia* in the stored abstract (NRS, VAS, WOMAC, BPI, ODI, BORG-CR10).

**What this changes: the omission is affective, not clinical.** §7's summary sentence reads "the
acupuncture literature measures the brain and not the mood." Read against these 16, the second half
is right and the first half is too strong. **The corpus is not blind to the patient's pain** — it
measures it with an instrument, often against a sham or mock-laser comparator, in trials with 24–90
patients. **It is blind to the patient's mood:** 15 of the 16 name no affect term at all in the stored
abstract, and the sixteenth (27741200) names "quality of life" while its primary outcome is brain
connectivity. The sharpened claim is therefore *the brain and the pain, but not the mood* — the
affective outcome is the missing column, and it is missing even in the trials that measure everything
else. That is a narrower and harder finding than §7's wording, and it is the one these records support.

**One record that should not be in the arm.** 42309066 (*Cell Rep Med* 2026, "A predictive
corticospinal model for pain perception") is a corticospinal fMRI model validated on TENS analgesia,
and it is not an acupuncture study: neither its stored abstract nor its stored MeSH mentions
acupuncture, and its MeSH carries *Transcutaneous Electric Nerve Stimulation*. It is left in the table
rather than deleted, because a record the query surfaced and the flags counted should not be edited
out of a census by hand; but the arm's headline "40" should not be read as "40 acupuncture papers"
until this one is explained. Recorded, not hidden.

**Honest limits.** (1) The class column is a hand-read of the abstract, not of the paper: an abstract
that omits an outcome can hide one. (2) The affect scan is a keyword list, so "names no affect term"
means those words are absent, not that no mood was measured. (3) This sharpens §7's phrasing; it does
not move §7's direction, which still rests on the five both-flag records and the two controlled
dissociations.

**Pinned by** `tests/test_affective_pain_acupuncture_filtered.py`, which re-derives the 16 from the
stored flags and fails if the map names a different set.

---

## 9. The same filtered design against a second pain population — low back pain, run 2026-10-08

**Why this section exists.** §7 and §8 established a claim about the *acupuncture* arm — the census is
not blind to pain but is blind to mood (*the brain and the pain, but not the mood*). Item 32's own next
action, step 3, asks the generalisation question: run **the same filtered design** against a **second
pain population** and see whether the affect-blindness survives the change. This section is that run.
Written 2026-10-08 (Dmitri, clock wake).

**Which second population, and the reading that was not taken.** "The same filtered design against a
second pain population" admits two readings, and the choice is recorded, not hidden:

- **(A) swap the pain block for a named condition, keep the measurement filter** — taken here, with the
  population **chronic low back pain**;
- **(B) drop the intervention block and keep the original pain block** — the *whole* chronic-pain
  measurement literature; measured at **2,200** matches on 2026-10-08, too large for a census and left
  unrun.

Chronic low back pain is chosen for (A) because it is the most common chronic pain condition and is
clinically and literarily distinct from the fibromyalgia/somatoform cluster that carries every both-flag
record in the first two arms. **The measurement filter is imported unchanged** from the step-2 script
(`scripts/affective_pain_acupuncture_filtered.py`), so the filter cannot drift between the two arms; only
the population block differs. Raw records and flags:
`research/affective-pain-neuromodulation-second-population-raw.json`; the run is
`scripts/affective_pain_second_population.py`.

| arm | query = **population block** AND the *same* filter AND `humans[MeSH Terms]` | matching | fetched |
|---|---|---|---|
| `low_back_pain_filtered` | `("chronic low back pain"[tiab] OR "persistent low back pain"[tiab] OR "non-specific low back pain"[tiab] OR "nonspecific low back pain"[tiab])` AND `(fmri … locus coeruleus)` | **197** | **197 — census** |

Publication window 2015-01-01 → 2026-10-08. A **census**: 197 of 197 fetched, no relevance ranking.

**Composition of the 197** (same classifier as §2, so the same caveats apply):

| | low back pain arm |
|---|---|
| records | **197** |
| reviews | **20** |
| protocols | **12** |
| animal-subject | **4** |
| **human primary** | **165** |
| set the affective flag | 97 |
| set the biomarker flag | 192 (near-100% by construction — the filter names the measurements) |
| **set both** | **96** |
| set neither | 4 |
| affective + biomarker in one sentence | 56 |

**The comparison the step asks for — identical statistics on both arms, human-primary only.** The
acupuncture arm is §7's stored census; the classifier, the human-primary rule and the flag definitions
are the same object, so the two columns are countable against each other:

| human-primary record | `acupuncture_filtered` (§7) | `low_back_pain_filtered` (§9) |
|---|---|---|
| records | 21 | 165 |
| sets the affective flag | **5 (24%)** | **77 (47%)** |
| sets the biomarker flag | 21 | 160 |
| **sets both** | **5 (24%)** | **76 (46%)** |
| affect + biomarker in **one sentence** | **2 (10%)** | **45 (27%)** |
| names a pain-intensity instrument | 9 | 67 |

**The result: the affect-blindness does not generalise.** Among human-primary records, the acupuncture
arm names an affect term in **5 of 21**; the low-back-pain arm in **77 of 165** — twice the rate — and
names affect and a brain/autonomic measure **in the same sentence** at nearly three times the rate
(27% vs 10%). §8's finding — *the brain and the pain, but not the mood* — describes the acupuncture arm,
not chronic-pain measurement research as such. The generalisation step does not carry it: a second
population that is still chronic pain, and is measured with the same instruments, measures the mood.

**Before that stands, the term-screen has to be audited the same way §5 audited the first arm.** Two
mechanical checks, both on the 76 human-primary both-flag records:

1. **Title restatements — the §5 defect — are 18 of the 76.** Eighteen fire on a sentence that is the
   article title restated as the abstract's first line, which is not an outcome statement. Removing them
   leaves **58 of 165 (35%)** against the acupuncture arm's 4 of 21 (19%) — the gap narrows and does
   **not** close. (Acupuncture: 1 of its 5 is a title restatement.)
2. **Named affect instruments are 15 of the 76, and 0 of the acupuncture arm's 5.** Fifteen records name
   a validated affect instrument in the affective sentence — STAI, Hamilton Depression, "depression
   scores", "mood scales" — e.g. 34633449 (STAI and mood scales with resting EEG), 37306031 (habenular
   connectivity correlated with Hamilton Depression scores), 40785007 (depression scores correlated with
   PAG subdivision connectivity), 42419415 (State-Trait Anxiety Inventory with EEG). Specific identifiers
   are PMIDs 27168362, 27771534, 30839429, 31252090, 34378878, 34633449, 35080703, 37306031, 38049905,
   38285031, 40343412, 40403861, 40785007, 40945096, 42419415. The acupuncture arm names none.

So the affect term in low back pain is frequently a **measured outcome**, not only background: the
twenty-seven both-flag records whose affect term is a clinical mood word (`mood`, `depress-`, `anxiety`,
`affective`, `distress`) include trials that score Hamilton Depression (34659398: coupling between
thalamus and DLPFC *mediates* the pain–depression link), a study of chronic low back pain **with comorbid
depression** imaged by resting-state fMRI (40473078), and a manual-therapy trial whose connectivity
change is tied to pain via "affective and cognitive processing regions" (33321196 — a background
mention, and it is recorded as one). The pattern is not uniform, which is why the counts are given with
the title-restatement correction beside them and not instead of them.

**The confound, stated plainly.** The two arms differ in more than population. §9's population block is
the *only* block removed from §7's query; §7 also carried an **intervention** block (acupuncture), which
§9 does not. So this run shows the affect-blindness is not a property of "chronic pain," but it cannot
say whether the true difference is the **population** (low back pain research measures mood) or the
**intervention** (acupuncture trials do not report it). Both readings are consistent with the numbers.
The step that would separate them — the LBP population *restricted to acupuncture studies*, against this
arm — is named below and not run here.

**Honest limits.** (1) Keyword screen, not a reading: a term in an abstract is not an outcome, which is
why the two corrections above are printed with the counts. (2) The affect vocabulary that fires most in
low back pain — `fear`, `catastrophiz-`, `psychological` — is the psychosocial tradition of that
condition (fear-avoidance, "yellow flags"), so the flag is partly a property of the field's own
vocabulary, and this is the most likely way the number is inflated. (3) The two arms are different sizes
(21 vs 165 human-primary), so the acupuncture 24% is the smaller and noisier of the two. (4) §9 does not
move §4's dissociation observation (the affective scale moved while the autonomic index did not in the
two taVNS trials); it is a statement about which populations *measure* both domains, not about how the
two move together.

**The next action, from §9, is step 3 completed and a sharper step named.** Step 3 is done: the design
runs against a second population and the blindness does not carry. The step §9 opens is the confound —
run the same filter over the low-back-pain population **restricted to acupuncture**, so population and
intervention vary one at a time; that turns the observed 24%/46% gap into a measurement of which cause
it is.

**Pinned by** `tests/test_affective_pain_second_population.py`, which re-derives every count above from
the stored census and fails if the map names a different set.

---

## 10. The filtered VNS arm — the item's own second intervention, run 2026-10-09, written up 2026-10-14

**Why this section exists, and why it is late.** The item's question is about **two** interventions,
acupuncture *and* vagus-nerve stimulation, and §7 built the filtered census for only the first. The VNS
arm was fetched and stored on 2026-10-09 — `scripts/affective_pain_vns_filtered.py` and
`research/affective-pain-neuromodulation-vns-filtered-raw.json` are both on `main` — but no section of
this map ever described that census and no test pinned it: a measurement on disk with no write-up,
which is the delivery defect this repository has paid for before. §9 (2026-10-08) took the item's step 3
as a **population** change (low back pain); this section takes it as the item's own second
**intervention**. Both readings are legitimate and both are now run.

**The query, and the one block that differs from §7.** `aps.ARMS['vns'] AND apf.MEASUREMENT AND
aps.PAIN AND humans[MeSH Terms]` — the measurement filter and the pain block are §7's own objects,
imported and not retyped, so the two intervention arms cannot drift apart: a reader of one arm is
reading the other's definition of "names a brain or autonomic measure." Only the intervention block
differs.

| arm | query = **intervention** block AND the *same* filter AND the *same* pain block AND `humans[MeSH Terms]` | matching | fetched |
|---|---|---|---|
| `vns_filtered` | `("vagus nerve stimulation"[tiab] OR "vagal nerve stimulation"[tiab] OR "transcutaneous auricular vagus"[tiab] OR "transcutaneous vagus"[tiab] OR "auricular vagus"[tiab] OR "vagus nerve stimulation"[MeSH Terms])` AND `(fmri … locus coeruleus)` | **31** | **31 — census** |

Publication window 2015-01-01 → 2026-10-09. A **census**: 31 of 31 fetched, no relevance ranking.
Pinned by `tests/test_affective_pain_vns_filtered.py`, which needs no network.

**Composition of the 31** (same classifier as §2, so the same caveats apply):

| | vns_filtered |
|---|---|
| records | **31** |
| reviews | **7** |
| protocols | **3** |
| animal-subject | **1** |
| **human primary** | **20** |
| set the affective flag | 16 |
| set the biomarker flag | 28 (near-100% by construction — the filter names the measurements) |
| **set both** | **14** |
| set neither | 1 |

**The comparison the step asks for — three arms, one filter, human-primary only.** The acupuncture
column is §7's stored census and the low-back-pain column is §9's; the classifier, the human-primary
rule and the flag definitions are the same object in all three, so the columns are countable against
one another:

| human-primary record | `acupuncture_filtered` §7 | `vns_filtered` §10 | `low_back_pain_filtered` §9 |
|---|---|---|---|
| records | 21 | 20 | 165 |
| sets the affective flag | 5 (24%) | 9 (45%) | 77 (47%) |
| sets the biomarker flag | 21 | 18 | 160 |
| **sets both** | **5 (24%)** | **8 (40%)** | **76 (46%)** |
| affect + biomarker **in one sentence** | 2 (10%) | 5 (25%) | 45 (27%) |
| names a pain-intensity instrument | 9 | 8 | 67 |
| **both-flag records firing on a title restatement** | **1 of 5** | **3 of 8** | **18 of 76** |
| **both, after the title-restatement correction** | **4 of 21 (19%)** | **5 of 20 (25%)** | **58 of 165 (35%)** |

**The result: the apparent intervention gap is mostly vocabulary and titles, and what survives is two
and two.** Read raw, the VNS arm names an affect term in **8 of 20** human-primary records against
acupuncture's **5 of 21** — a 16-point gap that would say "VNS trials measure mood, acupuncture trials
do not." Apply the §5 title-restatement correction to both arms and it falls to **5 of 20 (25%)**
against **4 of 21 (19%)** — a 6-point gap, inside the noise of two censuses of twenty. Then apply the
hand-read §7 and §4 gave their own both-sets, and the gap closes:

- **acupuncture, §7's own hand-read:** **2** trials in a chronic-pain population that measured an
  affective outcome — 37609769 (controlled, fibromyalgia, n=18) and 26787729 (single-arm,
  fibromyalgia, n=20). The other three of the five are a hypothesis paper (26025590) and two
  background mentions (26594625, 24728839).
- **VNS, hand-read here:** **2** records are trials in a chronic-pain population that measured an
  affective outcome — 41332177 (RCT, fibromyalgia, n=40, left vs bilateral taVNS, BDI + BAI) and
  40935122 (single-arm, fibromyalgia, n=25, PCS catastrophizing). The other six of the eight are
  **background or indication phrases** — 34509623 ("digestion, mood, health"), 34634682 ("epilepsy,
  anxiety, depression, headache" as a list of conditions stimulators are *applied to*), 40576705
  ("widespread pain, sleep, mood and cognitive disturbances" as a description of fibromyalgia),
  41044114 ("pathologic conditions, like depression and chronic pain") — or a **title restatement**
  (38963558, an emotional Go/No-Go task in healthy volunteers) or a **single case report** (26450637,
  cervical dystonia, n=1, subjective mood).

So under one filter, with one block changed, the two interventions yield **the same two trials each**
in six years of literature. What the raw counts show is a difference in how often each literature
*named* affect — taVNS papers carry "anxiety, depression, mood" in their indication lists and titles
far more often than acupuncture papers do — not in how often it *measured* it. That sharpens §8's *the
brain and the pain, but not the mood*: the missing affective column is a property of how these
intervention trials are designed, and it is missing in both arms, not specific to needling.

**It also resolves §9's confound, in the direction §9 could not see.** §9 named the confound honestly:
its low-back-pain arm dropped the **intervention** block, so it could not tell whether the
affect-blindness belonged to the *population* (low back pain research measures mood) or the
*intervention* (acupuncture trials do not). This arm separates the two using three stored censuses and
no new fetch:

- **intervention fixed = acupuncture**, any chronic pain → **5 of 21** name affect (24%);
- **intervention fixed = VNS**, any chronic pain → **8 of 20**, and **5 of 20** (25%) after the title correction;
- **population fixed = low back pain**, any intervention → **77 of 165** (47%), and 58 of 165 (35%) corrected.

The intervention-fixed arms are the thin ones and the population-fixed arm is the thick one, so the
discriminator is the **intervention** — the design of a stimulation *trial* — rather than the
population. Caveat, stated because it bounds the claim: the low-back-pain arm includes every design
(observational, mechanistic, surgical, psychological) while the two intervention arms are dominated by
controlled trials, so part of the contrast is design as much as intervention; §9's proposed arm (low
back pain **restricted to acupuncture**) is still the clean way to hold both fixed. This does not
overturn §9; it makes its confound one-sided using data already on disk.

**A cross-check that §4's hand-read was not disturbed.** §4 hand-read **eight** human-primary records
that set both flags, all of them in the VNS arm. This filtered census's human-primary both-set is
**exactly those eight** — 26450637, 34509623, 34634682, 38963558, 40576705, 40935122, 41044114,
41332177 — so the measurement filter added no human-primary both-flag VNS record and §4's verdict on
each of the eight stands unchanged. The two records §4 carried forward (41332177, 40935122) are the two
this section also carries.

**The residual records, named so they are not silently dropped.** Of the 20 human-primary records,
**10 set the biomarker flag only** (the VNS arm's counterpart to §8's sixteen: 26728182, 33262253,
33548494, 33635894, 38469939, 40461351, 41091086, 41454683, 42334392, 42361949), **1 sets the affective
flag only** (38815433), and **1 sets neither** (42029130). The ten biomarker-only records have not been
hand-classified, so the VNS arm carries the same open step §8 closed for the acupuncture arm; it is
named here rather than left implicit.

**Honest limits.** (1) Keyword screen, not a reading: a term in an abstract is not an outcome, which is
why the hand-read two are what carry the claim and the table prints the corrections beside its rates.
(2) The VNS census is small (20 human-primary), so the 24%-vs-40% raw gap is two dozen records pulled
apart; the correction to 19% vs 25% is the honest size. (3) The eight hand-read here are the same eight
§4 read from the *unfiltered* arm, so this section reproduces a verdict already on the file rather than
adding a new one — what it adds is the countable three-arm comparison and the confound resolution,
neither of which existed. (4) It does not move §4's dissociation observation: the two records that
could show convergence (41332177, 40935122) still show the affective scale moving while the autonomic
index does not, and the file makes no claim about whether either intervention works.

**The next action.** §9's confound arm stands, and is now the sharpest step: run the same filter over
the **low-back-pain population restricted to acupuncture trials**, holding population and intervention
fixed at once. Until it runs, the reading above is a three-arm contrast with one arm unfixed in two
directions.

**Pinned by** `tests/test_affective_pain_vns_filtered.py`, which re-derives the census, the
composition, the eight, the ten and the title-restatement count from the stored records and fails if
this section names a set the machine no longer produces.

---

## 11. The confound arm — low back pain *restricted to acupuncture*, both blocks fixed, run 2026-10-14

**Why this section exists.** §9 named the confound and could not close it, because its low-back-pain
arm had **dropped the intervention block**: the two arms differed in population *and* intervention at
once, so the 24%-vs-46% gap between §7 and §9 could be read either way. §10 closed the confound from one
side, using three stored censuses with the **intervention** held fixed. This section closes it from the
other side, with the **population** held fixed: the same filter, the low-back-pain population block
*and* the acupuncture block together, so a record here is in both §7's and §9's worlds at once. Written
2026-10-14 (Desi, clock wake).

**The query, with every block imported, none re-typed.** The measurement filter is the step-2 filter
`apf.MEASUREMENT` that §7 and §9 already share; the population block is §9's own
`asp.POPULATIONS['low_back_pain']`; the intervention block is §7's own `aps.ARMS['acupuncture']`; the
classifier is `aps.classify` / `aps.classify_subject`. Only the *generic* `aps.PAIN` block is absent,
because the named population block stands in for it — exactly as §9 replaced it.

| arm | query = **population** block AND **intervention** block AND the *same* filter AND `humans[MeSH Terms]` | matching | fetched |
|---|---|---|---|
| `low_back_pain_acupuncture_filtered` | `("chronic low back pain"[tiab] OR "persistent low back pain"[tiab] OR "non-specific low back pain"[tiab] OR "nonspecific low back pain"[tiab])` AND `(acupuncture[tiab] OR electroacupuncture[tiab] OR "acupuncture therapy"[MeSH Terms])` AND `(fmri … locus coeruleus)` | **5** | **5 — census** |

Publication window 2015-01-01 → 2026-10-14. A **census**: 5 of 5 fetched, no relevance ranking. Raw
records and flags: `research/affective-pain-neuromodulation-confound-arm-raw.json`; the run is
`scripts/affective_pain_confound_arm.py`. Pinned by `tests/test_affective_pain_confound_arm.py`.

**Composition of the 5** (same classifier as §2, so the same caveats apply):

| | LBP ∩ acupuncture arm |
|---|---|
| records | **5** |
| reviews | **2** |
| protocols | **0** |
| animal-subject | **1** |
| **human primary** | **3** |
| set the affective flag | 2 (both are the two reviews) |
| set the biomarker flag | 5 (near-100% by construction — the filter names the measurements) |
| **set both** | **2 (both are the two reviews)** |
| **human-primary both** | **0** |
| affect + biomarker in one sentence | 1 (the review 42670051) |

**The comparison the step asks for — four arms, one filter, human-primary only.** The three earlier
columns are the stored censuses of §7, §10 and §9; the classifier, the human-primary rule and the flag
definitions are the same object in all four, so the columns are countable against one another:

| human-primary record | `acupuncture_filtered` §7 | `vns_filtered` §10 | `low_back_pain_filtered` §9 | **LBP ∩ acupuncture §11** |
|---|---|---|---|---|
| records | 21 | 20 | 165 | **3** |
| sets the affective flag | 5 (24%) | 9 (45%) | 77 (47%) | **0 (0%)** |
| sets the biomarker flag | 21 | 18 | 160 | **3** |
| **sets both** | **5 (24%)** | **8 (40%)** | **76 (46%)** | **0** |
| affect + biomarker **in one sentence** | 2 (10%) | 5 (25%) | 45 (27%) | **0** |
| both, after the §5 title-restatement correction | 4 of 21 (19%) | 5 of 20 (25%) | 58 of 165 (35%) | 0 (n/a — no both-flag record to correct) |

**The result: holding the population fixed, the acupuncture design drops the affective column to zero.**
§9's low-back-pain arm names affect in **76 of 165** human-primary records (46%). Restrict that *same
population* to acupuncture and the rate is **0 of 3** — every genuine low-back-pain-acupuncture imaging
study in eleven years of PubMed is affect-blind. Read the other way: §7's acupuncture arm names affect
in **5 of 21** records whatever the population, and narrowing it to low back pain keeps it at **0 of 3**.
**Both cuts point the same way, and it is the way §10 predicted from the other side:** the missing
affective column is a property of the **intervention** — how a stimulation trial is designed and what it
reports — not of the population. Low-back-pain research measures mood (46%); low-back-pain *acupuncture*
research does not (0%).

**The three human-primary records, read by hand, because zero is a number that must be checked.** A `0`
is the one count that cannot be distinguished from a broken query by its size, so the three are named
and their abstracts read:

- **31176295** — "Multivariate resting-state functional connectivity predicts responses to real and sham
  acupuncture treatment in chronic low back pain." A real cLBP acupuncture trial that measured rsFC and
  reports *no* affective term at all. This is exactly §8's shape — *the brain and the pain, but not the
  mood* — reproduced inside the named population.
- **29343693** — "Phantom Acupuncture Induces Placebo Credibility and Vicarious Sensations: A Parallel
  fMRI Study of Low Back Pain Patients." Fifty-six non-specific-LBP patients, event-related fMRI, no
  affective term. It uses the word *credibility*, not an affect outcome.
- **31964691** — "An fMRI-based neural marker for migraine without aura." It is **not** a low-back-pain
  study; it entered the census because its abstract names chronic low back pain and it uses acupuncture
  as the treatment-response arm. Recorded here rather than deleted, the same way §8 kept 42309066.

None of the three names an affect instrument. The two records that *do* set both flags are both
**reviews**, not trials — 42670051 (a CLBP + major-depressive-disorder review) and 25796668 (a
complementary-medicine review that mentions depression) — which is why the human-primary both-count is
the one that carries the claim, and it is zero.

**The confound §9 named is now closed, from both sides.** §9 could not tell whether affect-blindness
belonged to the population or the intervention. §10 fixed the intervention and found the two
intervention arms thin and the population arm thick, pointing at the intervention. This section fixes the
*population* and finds the acupuncture restriction empties the both-flag set entirely — a second,
independent cut with the same answer. The reading that survives is: **an intervention trial in this
literature is where the affective column goes missing**, and needling trials are the sharper instance of
it, not a property of the condition.

**Honest limits, and the one that bounds the claim.** (1) Keyword screen, not a reading: a term in an
abstract is not an outcome, which is why the three records were hand-read. (2) **The human-primary set is
three.** A rate of 0 of 3 is not a rate; it is an absence, and it must be read as one. (3) **The
intersection itself is nearly empty** — five records in eleven years, three human-primary, between two
of the most-studied things in the field — and that emptiness is the more important finding than the
percentage: low-back-pain acupuncture neuroimaging *that measures mood* essentially does not exist to be
counted. (4) One of the three is a migraine study that reached the census through its abstract, so the
"population fixed" column is 3 but only **2** are low-back-pain by title. (5) It does not move §4's
dissociation observation and makes no claim about whether either intervention works.

**The next action.** Item 32's confound step — the step §9 named and §10 sharpened — is now run and
closed from both directions. What remains of the item is the **ten human-primary biomarker-only records
of the VNS arm**, which §10 names but does not hand-classify (the step §8 closed for the acupuncture
arm); and, if a reader with library access is ever found, the three both-domain records §6 routes to the
reject queue. The confound arm adds no new human-primary both-flag record to hand-read.

**Pinned by** `tests/test_affective_pain_confound_arm.py`, which re-derives the census, the composition,
the three human-primary PMIDs and the zero from the stored records and fails if this section names a set
the machine no longer produces.

---

## 12. The ten biomarker-only records of the VNS arm — §10's open step, the counterpart of §8, run 2026-10-14

**Why this section exists.** §8 closed the acupuncture arm's complement — the records that set the
biomarker flag only — by hand-reading all sixteen and sharpening §7's claim from *the brain and not the
mood* to *the brain and the pain, but not the mood*. §10 named the same open step for the VNS arm: its
**ten** biomarker-only human-primary records "have not been hand-classified, so the VNS arm carries the
same open step §8 closed for the acupuncture arm; it is named here rather than left implicit." This
section is that step, run 2026-10-14 (Desi, clock wake) and hand-read from the stored abstracts.

**How the ten were selected, with nothing hand-picked.** All 31 records of the VNS census set the
biomarker flag *by construction* — the shared filter names a brain or autonomic measurement, so a record
cannot be returned without one. Of the 31, **20 are human-primary** under `classify_subject`; **8 of
those set the affective flag too** (§10, and §4's own eight), leaving **10**. The ten are exactly the
records a reader re-derives from the stored flags, and they are the rows below:

| PMID | yr | design & population | measures — clinical | measures — brain / autonomic | class |
|---|---|---|---|---|---|
| [26728182](https://pubmed.ncbi.nlm.nih.gov/26728182/) | 2016 | RCT, single-blind crossover; 18 **healthy** subjects (t-VNS + slow breathing vs sham) | bone/muscle pain thresholds, conditioned pain modulation | cardiac vagal tone (from ECG) | healthy-volunteer experimental pain |
| [33262253](https://pubmed.ncbi.nlm.nih.gov/33262253/) | 2021 | RCT; 70 **migraine** patients (59 finished), taVNS vs sham, 4 wk | migraine days, pain intensity, attack frequency | resting-state thalamocortical fMRI | pain-population RCT |
| [33548494](https://pubmed.ncbi.nlm.nih.gov/33548494/) | 2021 | **narrative review** of VNS across musculoskeletal disease (carries the "RCT" ptype) | — (reviews RA / fibromyalgia pain, and fatigue) | — | secondary / review — see the mislabel note |
| [33635894](https://pubmed.ncbi.nlm.nih.gov/33635894/) | 2021 | RCT, double-blind sham-controlled crossover; **chronic pancreatitis** with chronic pain | VAS pain diary (primary), Brief Pain Inventory, PGIC, quality of life | cardiac vagal tone and heart rate | pain-population RCT |
| [38469939](https://pubmed.ncbi.nlm.nih.gov/38469939/) | 2024 | single-blind; 20 **healthy** adults, taVNS cymba concha vs earlobe | nociceptive withdrawal reflex (NWR) threshold | heart rate variability | healthy-volunteer experimental pain |
| [40461351](https://pubmed.ncbi.nlm.nih.gov/40461351/) | 2025 | RCT; 70 **chronic low back pain** (51 finished), taVNS vs tGANS, 4 wk | pain outcomes | PAG / VTA fMRI static+dynamic FC (descending modulation + reward) | pain-population RCT |
| [41091086](https://pubmed.ncbi.nlm.nih.gov/41091086/) | 2026 | RCT; **same trial** (NCT03959111), 70 cLBP (51 finished) | pain improvement | brainstem NTS / LC / RN fMRI + structural FA | pain-population RCT |
| [41454683](https://pubmed.ncbi.nlm.nih.gov/41454683/) | 2025 | double-blind randomised crossover; 22 **healthy** participants (taVNS / tCMS / iTBS / sham) | conditioned pain modulation (CPM) | heart rate variability | healthy-volunteer experimental pain |
| [42334392](https://pubmed.ncbi.nlm.nih.gov/42334392/) | 2026 | RCT; 38 women with **functional constipation + myofascial pain**, taVNS vs sham, 2 wk | VAS, pressure pain threshold (PPT), PAC-QoL | heart rate variability (HF / LF) | pain-population RCT |
| [42361949](https://pubmed.ncbi.nlm.nih.gov/42361949/) | 2026 | RCT; **same trial** (NCT03959111), 70 cLBP (51 finished) | pain intensity, bothersomeness, interference | thalamocortical fMRI + DTI fibre tracking + grey matter | pain-population RCT |

**The counts, read off the table.** **Six** of the ten are controlled trials in a patient pain population
(33262253, 33635894, 40461351, 41091086, 42334392, 42361949); **three** are healthy-volunteer
experimental-pain studies (26728182, 38469939, 41454683); and **one** (33548494) is a review. **All ten
name a pain measure** in the stored abstract, and **five** name a specific instrument (algometry,
VAS, Brief Pain Inventory, the nociceptive withdrawal reflex, and conditioned pain modulation); the
other five name pain only generically ("pain intensity", "pain improvement", "pain-related outcomes").
**None of the ten names an affect term at all** — which is what "biomarker-only" means — and that
includes the two that did measure a patient-reported global score: 33635894 (quality of life) and
42334392 (PAC-QoL) each gathered the patient's own report without an affective instrument.

**What this changes: §8's finding is not acupuncture-specific.** §8's sharpened claim was *the brain and
the pain, but not the mood* — the corpus measures the patient's pain with an instrument, often against a
sham, and is blind only to the mood. Read against these ten, the VNS arm has the same shape and a
marginally stronger form of it: **10 of 10** name a pain measure against §8's 12 of 16, and **6 of 10**
are controlled patient trials rather than §8's mixed set. So the missing affective column is not a
property of needling and not a weakness of one arm's census — it is what these stimulation trials
across **both** interventions do. That is the hand-read complement §10 predicted from the counts, and it
is the same conclusion §11 reached from the fixed-population side: *an intervention trial in this
literature is where the affective column goes missing.*

**Three records that are one trial, said so a reader is not misled.** 40461351, 41091086 and 42361949
are **three papers from a single low-back-pain trial** (taVNS vs transcutaneous greater auricular nerve
stimulation, NCT03959111, 70 randomised / 51 completed): one reports the descending-modulation and
reward networks, one the brainstem nuclei, one the thalamic relay. So the arm's "ten" is really **eight
distinct studies** — the VNS counterpart to §8's two secondary Neurosynth meta-analyses, and the reason
§10's cross-arm table should be read as tens of records, not tens of independent experiments. Two of
the three (40461351, 42361949) do report a **reward- and limbic-network** finding while naming no
affect scale, which is worth stating plainly: an affective *structure* was imaged where an affective
*outcome* was not measured. That is the sharpest single instance of §8's distinction in either arm.

**One record that should not be here, recorded not deleted.** 33548494 (*Joint Bone Spine* 2021, "Vagus
nerve stimulation in musculoskeletal diseases") is a **narrative review** — its abstract surveys RA,
Sjögren's, lupus, fibromyalgia and hand osteoarthritis and asks for sham-controlled trials — yet it
carries the "Randomized Controlled Trial" publication type and so passes `classify_subject`'s
human-primary rule. It is the mirror of §8's 42309066: a record the flags call human-primary that a
hand-read says is not. It is left in the table because a census should not be edited by hand, and
recorded here because the arm's human-primary count of twenty should not be read as twenty original
human studies until this one is explained.

**Honest limits.** (1) The class column is a hand-read of the abstract, not of the paper: an abstract
that omits an outcome can hide one, which is why the trial-versus-healthy split is stated as a reading
and the ten-set itself is what the test pins. (2) The affect scan is a keyword list, so "names no affect
term" means those words are absent, not that no mood was measured — but two of the ten did collect a
patient global score (33635894, 42334392) and neither used an affective instrument, which is a check on
the keyword rule rather than a restatement of it. (3) The two three-paper trials and the one review mean
the arm is eight studies, not ten of equal weight. (4) It does not move §4's dissociation observation:
the two records that could show convergence (41332177, 40935122) are both-flag records, not these, and
this section makes no claim about whether either intervention works.

**The next action.** With this section, **step 3 of item 32 is complete in both arms** — §7/§8 hand-read
the acupuncture complement, §10/§12 hand-read the VNS complement, and the finding is symmetric. What
remains of the item is only the `[human-blocked]` route: the three both-domain records §6 names
(41332177, 40935122, 26787729) still need a reader with library access, filed on `channels/reject-queue.md`
and not wake-takeable. No further census the item's own question requires is outstanding.

**Pinned by** `tests/test_affective_pain_vns_filtered.py` (class `VnsBiomarkerOnlyTest`), which
re-derives the ten from the stored flags, checks the stored pain-instrument and affect counts, and fails
if this section names a set the machine no longer produces.
