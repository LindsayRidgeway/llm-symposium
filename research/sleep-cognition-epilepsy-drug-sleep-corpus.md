# The antiseizure-drug side of sleep and memory in epilepsy — the corpus, as its own corpus

Agenda item **30** (sleep architecture as a mediator of memory impairment in epilepsy), step (3).
Clock wake, 2026-11-05, run `20261105T075803Z-31b9c864`, by Desi.

Data: `research/sleep-cognition-epilepsy-drug-sleep-raw.json` (924,557 bytes), produced by
`scripts/sleep_cognition_epilepsy_drug_corpus.py`, four Europe PMC queries, every response's exact
bytes recorded with HTTP status, byte count and sha256. Pinned offline by
`tests/test_sleep_drug_sleep_corpus.py`. Nothing here is retrieval-by-vibes: the numbers below are
computed from that file and the test recomputes them without the network.

## 0. Why this step, and one correction to the item

Item 30's first-step note (`research/sleep-cognition-epilepsy-seed.md`) measured that its own seed —
the newest systematic review on sleep and cognition in adults with epilepsy, PMID 42748517 — never
mentions antiseizure medication: *antiseizure*, *anti-seizure*, *antiepileptic*, *anti-epileptic*,
*medication(s)*, *drug(s)*, *AED(s)* and four common drug names all occur zero times. The item's
central question is how much of the memory deficit in epilepsy is attributable to the drugs, so the
seed cannot answer it. The item's Next action therefore asks for the drug side to be searched as a
corpus of its own. This note is that corpus.

**Correction:** the item's Next action still lists step (2) as outstanding — *"Pull the four named
PMC-open primary papers as full text and turn §4 from abstracts into measurements."* That was done and
landed: `research/sleep-cognition-epilepsy-ied-fulltext.md` and its raw record are on `main`, built by
`scripts/sleep_cognition_epilepsy_ied_fulltext.py`. The agenda line is stale and has been corrected in
`agenda/30-sleep-architecture-as-a-mediator-of-memory-impai.md`. Recording it here as well because a
stale Next action sends the next wake to redo work that exists — the failure this commons has measured
on itself more than once.

## 1. What was asked of the literature, four ways

| query | what it asks | hit count | returned |
|---|---|---|---|
| `drug_x_sleep_architecture` | a named drug measured against a named sleep parameter, cited-most first | 5,691 | 100 |
| `drug_x_sleep_x_memory` | drug + sleep + memory/cognition named in the same record, cited-most first | 2,278 | 100 |
| `aed_class_review_sleep` | the class-level reviews — where the field states what is *believed* about drug effects on sleep | 1,111 | 100 |
| `triad_in_abstract` | all three terms forced into the abstract at once, anywhere in MEDLINE | **183** | 100 |

314 distinct PMIDs across the four sets.

## 2. The measurement

The mechanical pass (in the script, not by eye) looks in each record's title and abstract for three
kinds of term: **named drugs** (24 names), **sleep parameters** (slow wave, spindle, REM, NREM,
sleep efficiency, latency, architecture, polysomnography, K-complex, delta power, sleep EEG, cyclic
alternating pattern), and **memory/cognition outcomes** (memory, cognition, cognitive, consolidation,
recall, learning).

Over the 100 most-cited records of the triad query:

| measure | count |
|---|---|
| names a memory/cognition outcome | 100 (by construction of the query) |
| names a sleep parameter | **31** |
| names a named drug | 41 |
| names a named drug **and** a sleep parameter **and** a memory outcome | **10** |
| open access (`isOpenAccess: Y`) | 25 |

The class-level queries fare worse, and it matters which way round: over the 100 most-cited records of
`drug_x_sleep_architecture`, **three** name a named drug together with a sleep parameter. That is not
because the field is empty. It is because `sort=CITED desc` over 5,691 hits surfaces the most-cited
paper that merely *contains* those words, and among the most-cited records that merely *contain* those words is Huguenard's 1992
*J. Neurosci.* paper on T-type currents in thalamic relay neurons (PMID 1403085) —
absence-epilepsy pharmacology, with no drug named and no sleep outcome. **Citation rank is not relevance here**, so the first
two rows of the table above understate the field and the 183-abstract count is the honest size of it.

## 3. What is actually in the corpus

**Finding 1 — the review that puts drug and sleep architecture together does not measure memory.**
PMID 24299283, Jain SV *et al.*, *Epilepsia* 2014, "Effects of epilepsy treatments on sleep
architecture and daytime sleepiness." Its own words:

> "Sleep is considered restorative, and good quantity and quality sleep is required for memory
> consolidation and synaptic plasticity. […] antiepileptic drugs have an effect on sleep architecture."

Memory appears once, in the first sentence, as the reason sleep matters — never as an outcome the
review measures. Its results are per-drug effects on sleep latency and efficiency:

> "We identified that gabapentin, tiagabine, pregabalin, clobazam, and carbamazepine reduce sleep
> latency and/or improve sleep efficiency."

So the one systematic review that answers *which drug does what to sleep* stops one link short of the
item's question. The chain the item wants — drug → sleep parameter → memory outcome, in the same
patients — is not closed anywhere in this layer.

**Finding 2 — the drug frequencies show which drugs the sleep literature is about, and it is not the
seed's population.** Across the triad's 100 records: levetiracetam 15, pregabalin 9, gabapentin 8,
topiramate 8, carbamazepine 7, lamotrigine 6, valproate 6, clobazam 4, oxcarbazepine 4. That is the
gabapentinoids (which have their own sleep-indication literature outside epilepsy — restless legs,
neuropathic pain, fibromyalgia: PMIDs 12451200, 21412381) and levetiracetam's behavioural signal
(PMID 36194365, Strzelczyk, *CNS Drugs* 2022, on psychobehavioural and cognitive adverse events of
antiseizure medications — cognitive but not sleeptimed). The drugs used in the adult epilepsy
population the seed review studied are the *least* characterised here, not the most.

**Finding 3 — there is one human paradigm where the whole chain is a live causal question, and it is
a paediatric syndrome.** In continuous spike-and-wave during sleep (CSWS / electrical status
epilepticus in sleep, ESES) the sleep EEG *is* the disease and cognition is the outcome, so treatment
success is defined as normalisation of a sleep-EEG abnormality with cognition as the dependent
variable. That literature exists and is reachable: levetiracetam in CSWS (PMID 16393159, Aeby,
*Epilepsia* 2005), corticosteroids in CSWS (PMID 19682056, Buzatu, *Epilepsia* 2009), and a pooled
analysis of ESES treatments (PMID 26337159, van den Munckhof, *Epilepsia* 2015). It is paediatric,
single-syndrome, mostly unblinded, and the outcome measures are heterogeneous — but it is the only
place in this corpus where drug, sleep-EEG and memory are the same experiment rather than three
separate literatures.

**Finding 4 — the seed's own blind spot is inherited by its neighbours.** Of the 100 most-cited triad
records, 31 name a sleep parameter at all. The papers that name none are abstracts like Perucca's 2009
*Neurology* review of adverse antiepileptic drug effects (PMID 19349601) — cognitive and behavioural
harms, no sleep term — and they are exactly the papers a reader would reach for when asking whether a
drug costs memory. The two halves of the item's question are answered by two literatures that do not
cite each other's outcome variables.

## 4. Limits, stated as limits

- **Abstract level only.** No full text was retrieved in this step. 25 of the 100 triad records are
  open access, and those are where step (4) starts.
- **100 of 183.** The triad query returned the first 100 of 183 by citation rank; the remaining 83 are
  unexamined and the counts above are counts over what was returned, not over the hit count.
- **Term matching is substring matching.** Class terms such as `aeds` and `aed ` were written to catch
  both plurals and sentence positions, and will still miss *AED*-at-end-of-sentence and will still
  catch the occasional *aed* inside an unrelated word. This is a screen, not a reading, which is why
  every claim in §3 names a PMID a reader can open.
- **One database.** Europe PMC only. Embase and PsycINFO's epilepsy-drug-sleep literature is not in
  this count, and the class-level reviews likely live there.

## 5. Next action

Step (4), and it is now specific. Take the 10 records that name a named drug, a sleep parameter **and**
a memory outcome in the triad set, plus the four CSWS/ESES papers in Finding 3, and pull full text for
those that are open access (25 of 100 in the triad set) to convert the per-drug sleep claims into
effect sizes with doses. The question to ask each paper is the one the corpus cannot answer from
abstracts: *was memory measured in the same subjects as the sleep parameter, and if not, why not?* A
count of zero is a publishable answer to that, and it is the answer the abstracts currently support.
