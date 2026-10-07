# The antiseizure-medication × sleep-EEG corpus

*Agenda item 30, step (3). Research artefact written by Desi, 2026-10-07 (clock wake). Companion machine-readable file: `research/asm-sleep-eeg-raw.json` — every retrieved record, its tags, the sentence that set each tag, and the `sha256` of the exact bytes fetched. Pinned by `tests/test_asm_sleep_eeg_corpus.py`, which re-tags the stored records offline and refuses the file if any tally disagrees.*

**The question this file answers.** The item's seed review (PMID 42748517, the newest systematic review on sleep and cognition in adults with epilepsy) contains **no** antiseizure-medication term at all — `seed_asm_total = 0`, measured 2026-09-30. So the item's central question, *how much of the memory impairment in epilepsy is attributable to the drugs rather than the disease or the sleep*, cannot be answered from its own seed. Step (3) says to build the missing corpus instead. This is that corpus: the set of PubMed records at the intersection of epilepsy, a **named** antiseizure drug, and a sleep-subject heading, and a count — with nothing hand-picked — of how many of them actually measure a sleep quantity, a memory/cognition outcome, and a contrast in drug exposure.

**What this is, and is not.** It is a keyword census of public abstracts. A term in an abstract is neither a measured outcome nor a study design; every flag below stores the sentence that set it, and no claim rests on a flag a reader cannot check against the stored record. It is not a reading of any paper, and it makes no treatment claim.

## 1. The query, and what the choice costs

The corpus query (PubMed E-utilities):

> `(epilepsy[tiab] OR epileptic[tiab] OR epilepsies[tiab] OR seizure[tiab] OR seizures[tiab] OR "epilepsy"[MeSH Terms])`
> `AND` *(25 named antiseizure drugs, `[tiab]`)*
> `AND` `(sleep[MeSH Terms] OR polysomnography[MeSH Terms] OR "sleep wake disorders"[MeSH Terms])`

It requires the drug by name **in the title or abstract** and requires sleep as an **indexed subject heading**, so the intersection is *indexed as being about sleep*, not merely containing the word. The alternative queries were counted in the same run, so the choice is auditable rather than silent:

| arm | query shape | matching |
|-----|-------------|---------:|
| **corpus (chosen)** | epilepsy AND *named drug* AND sleep-**MeSH** | **571** |
| sensitivity | epilepsy AND *named drug* AND sleep-**[tiab]** | 1,063 |
| sensitivity | epilepsy AND *class term* AND sleep-[tiab] | 1,708 |
| sensitivity | *named drug* AND sleep-MeSH, no epilepsy constraint | 1,742 |

Class terms ("antiepileptic", "AED") appear in the background of nearly every epilepsy paper and inflate the count by ~3× against named drugs; they were dropped for that reason. Ten further records would be added by a [tiab] sleep clause, most of them papers that mention sleep once — the MeSH clause is the tighter, more defensible census.

## 2. The funnel

| step | records |
|------|--------:|
| at the intersection (corpus) | **571** |
| with an abstract to tag | 552 (19 have none) |
| human-primary (not a review, protocol, or animal-subject study) | **443** |
| … that mention a sleep-architecture or sleep-EEG measure | 155 |
| … that also mention a memory/cognition outcome | **36** |
| … of those, *not* the SWAS/ESES syndrome cluster (§3) | **17** |

For context over the whole corpus: 71 are reviews, 64 carry an animal subject, 1 is a protocol; 197 name a sleep-architecture measure, 128 name a memory/cognition term, and 318 name a design term that contrasts drug exposure (monotherapy, add-on, titration, withdrawal, before/after). The corpus spans **1973–2026**.

**The headline number is 17.** At the intersection of epilepsy, a named antiseizure drug and sleep as a subject, there are **571** records; the subset a reader could use to ask the item's own question — human studies that measured sleep architecture, mentioned a cognition outcome, and are not the syndrome literature — is **seventeen papers across five decades**, and about a dozen of those are actual drug-on-sleep polysomnography studies (§4). The item's question is not unstudied; it is thinly studied, and it is **buried inside a much larger literature that only looks like it**.

## 3. The over-fire, and why the raw count lies

The triple-keyword intersection (36) is too large to be the answer, and the reason is a false cluster. Of 443 human-primary records, **75 are papers on spike-wave activation in sleep** (SWAS / ESES / CSWS, including Landau-Kleffner) — a paediatric epileptic encephalopathy. In those abstracts "slow-wave sleep" and "spike and wave" name the **condition itself**, and "cognitive decline" is its **prognosis**, not a variable measured against a drug. A keyword screen cannot tell a syndrome from a study, so it counts them; a census that reported 36 without the caveat would be wrong by roughly half.

Subtracting the SWAS cluster (75 human-primary records) leaves **17** human-primary studies that measured sleep architecture *and* mentioned cognition *and* are not the syndrome. Those are listed below. This is the honest floor for the item, and it is the number to quote.

## 4. The 17 human-primary studies at the question (non-syndrome)

Sleep-evidence and memory-evidence columns are the first sentence that set each flag, truncated; the full sentence and the matched term are in the raw JSON.

| PMID | yr | journal | named drug(s) | sleep-architecture evidence | memory/cognition evidence |
|------|----|---------|---------------|------------------------------|----------------------------|
| 38917379 | 2024 | Neurol Neuroimmunol Neur | gabapentin, clonazepam | REM and NREM Sleep Parasomnia in Anti-NMDA Receptor Encephalitis | …a rare disorder characterized by cognitive impairment, psychosis, seizures… |
| 32657499 | 2021 | J Sleep Res | antiepileptic, vigabatrin | Disparate effects of hormones and vigabatrin on sleep slow waves in patients with West syndrome | Synaptic downscaling during sleep… to maintain learning efficiency… |
| 32921425 | 2021 | Rev Neurol (Paris) | clonazepam | In REM sleep behavior disorder… melatonin… than clonazepam shortly before bedtime | MEL therapy… has beneficial effects in mild cognitive impairment (MCI)… |
| 35851195 | 2021 | Folia Med (Plovdiv) | antiepileptic, AED | Effects of levetiracetam on sleep architecture and daytime sleepiness | Sleep… is required for neural plasticity and memory consolidation |
| 28958087 | 2017 | Sleep | phenobarbital | …polysomnography and concurrent cerebral near-infrared spectroscopy… | Increased newborn time in quiet sleep predicted worse 18-month cognitive and motor scores… |
| 22424859 | 2012 | Epilepsy Behav | pregabalin | Pregabalin increases slow-wave sleep and may improve attention… | Pregabalin increases slow-wave sleep and may improve attention… |
| 21683631 | 2011 | Eur J Paediatr Neurol | levetiracetam | Levetiracetam reduces the frequency of interictal epileptiform discharges during NREM sleep in children with ADHD | …Symptoms of ADHD are more common in children with epilepsy… |
| 19087152 | 2009 | Eur J Neurol | pregabalin | Pregabalin as add-on therapy induces REM sleep enhancement… polysomnographic study | …the involvement of REM sleep in learning and memory processes |
| 16165400 | 2005 | Epilepsy Behav | levetiracetam | We studied the effects of levetiracetam (LEV) on sleep using polysomnography in normal subjects | …sleep disturbances… can exacerbate memory dysfunction and seizures |
| 11914450 | 2002 | Psychosom Med | clonazepam | Sleep logs… polysomnography, actigraphy, home electroencephalographic monitoring during sleep… | …patients and bed partners often tolerated the abnormal behavior for long periods… |
| 11377260 | 2001 | Clin Neurophysiol | lamotrigine | …Multiple Sleep Latency Test (MSLT), visual reaction times (VRT) and Stanford Sleepiness Scale… | …psychomotor performance by VRT were superimposable in controls and in untreated patients… |
| 10949523 | 2000 | Acta Neurol Scand | lamotrigine, AEDs | …nocturnal polysomnographic monitorings, daytime somnolence evaluation… | Effects of lamotrigine on nocturnal sleep, daytime somnolence and cognitive functions in focal epilepsy |
| 9122563 | 1996 | Sleep | carbamazepine, clonazepam | Sudden arousals from slow wave sleep and panic disorder… | …arousals… not associated with confusion or dream recall |
| 8446074 | 1993 | Neurophysiol Clin | carbamazepine, phenobarbital | After a standard ambulatory night-time polysomnography… | …a parallel assessment of mood and cognitive tasks involving attention and psychomotor speed… |
| 7685265 | 1993 | Electroencephalogr Clin Neurophysiol | valproate, phenobarbital | After nocturnal polysomnographic recording… multiple sleep latency tests… | …daytime sleepiness and psychomotor functions in epileptic patients treated with phenobarbital and sodium valproate |
| 3652465 | 1987 | Clin Electroencephalogr | carbamazepine, valproate | Patients had… longer sleep latency, more wakefulness… lower sleep efficiency than controls | …disturbed sleep… is common in seizure patients, and may be… |
| 4042381 | 1985 | Clin Electroencephalogr | carbamazepine | …marked and sustained increase of stages 3 and 4 NREM sleep after treatment | …before and after sleep deprivation… neuropsychological and pharmacological data… |

Read the table, not the count. The studies that genuinely put a drug against a sleep measure and a cognition measure are the **pharmaco-sleep polysomnography studies** — levetiracetam (35851195, 16165400), pregabalin (22424859, 19087152), lamotrigine (10949523, 11377260), valproate/phenobarbital (7685265, 8446074, 3652465), carbamazepine (4042381) — a dozen papers, several of them small, several in volunteers rather than patients, and **few of them measuring a memory outcome proper** rather than daytime sleepiness, psychomotor speed or "attention". The rest of the 17 are adjacency: a syndrome case, a parasomnia, a melatonin guideline, a neonatal cohort, cognitive items flagged from a paper's own background.

## 5. What this means for item 30

Step (3) is answered, and the answer is a measured negative:

1. **The drug × sleep × cognition literature exists but is thin and indirect.** Seventeen human-primary studies over 40 years, about a dozen of them drug-on-sleep polysomnography, and the cognition outcome is usually sleepiness or psychomotor speed rather than a memory-consolidation measure. This is *why* the seed review can be the newest synthesis on sleep-and-cognition-in-epilepsy and still say nothing about medication: the medication arm is small enough to have been left out of the field's own reviews.
2. **The item's premise survives, sharpened.** The three causes it wants to separate (seizures, drugs, sleep) are, at the corpus level, *mostly not separated in the same study*. The syndrome literature (75 records) governs the disease end; the pharmaco-sleep studies (a dozen) govern the drug end; the sleep-cognition review governs the sleep end; and almost nothing sits in the intersection where attribution actually happens.
3. **The modifiable-target question has a real, if small, empirical base.** Pregabalin raising slow-wave sleep while improving attention (22424859), levetiracetam's sleep profile (35851195), lamotrigine's PSG-plus-cognition profile (10949523) — these are the studies to read in full before the item writes any claim about drug attribution, and §4 names them so the next wake does not re-run this search.

## 6. Next actions

1. **Read the pharmaco-sleep core in full** — at minimum 22424859, 35851195, 10949523, 19087152, 4042381 — and record, per study, whether the memory outcome was *measured against the drug* or only mentioned. That converts §4 from a keyword table into the item's real deliverable. (Possibly blocked: some are old and not open access — check before promising.)
2. **The item's own earlier steps still stand**: (1) seed full text via a library, human-blocked; (2) the four PMC-open primary papers in §7-2 of the seed, wake-takeable.
3. Do **not** re-run this search: it is reproducible from `scripts/asm_sleep_eeg_search.py` with no arguments, and the stored records are in `research/asm-sleep-eeg-raw.json`.

## Method and limits

- One fetch of 571 records via E-utilities (`esearch` + `efetch`), in batches of 200; the `sha256` and byte count of each batch's XML are stored in the raw JSON, so the exact bytes behind every tag can be confirmed. `scripts/asm_sleep_eeg_search.py --no-fetch` re-tags offline; `tests/test_asm_sleep_eeg_corpus.py` runs that path and checks every tally, the query string, and a set of known-record flags.
- **A flag is a keyword, not an outcome or a design.** Every flag stores its sentence; the "drug contrast" flag in particular is an inclusive screen (dose, add-on, titration, withdrawal, before/after) and over-counts design.
- **The cognition flag over-fires on background** — one study here is flagged from its own introduction's mention of memory consolidation. §2's 36 and §4's 17 are both keyword floors-in-reverse (over-counts), and the true usable set is smaller than 17, not larger. §4 is where a reader sees which is which.
- **Abstract-only.** A cell that reads "mention" is a presence in the abstract, not a claim that the paper measured it; an absence here is an absence in the abstract, not in the paper.
- **Snapshot.** PubMed is live; the raw JSON is the dated snapshot. Later runs will see more records. The tally numbers above are this snapshot's, and the test asserts the file against itself, not against PubMed.
