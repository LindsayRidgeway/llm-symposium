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
