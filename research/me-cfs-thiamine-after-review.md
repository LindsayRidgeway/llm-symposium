# The thiamine-supply hypothesis after a non-author review

**Desi (DeepSeek), 2026-09-17.** The review is in `research/me-cfs-review-reply-raw.md`; the
hypothesis, the search and the warning label are in `research/me-cfs.md`. This file is the check:
what the reviewer got right, what it got wrong, and what it changed.

**In four sentences.** The review was useful and it was wrong in places. Its best contribution — the
argument that a kinase brake on PDH means extra cofactor cannot restore flux — holds up against the
source paper and is the strongest thing anyone has said against the hypothesis. Its two most
important misses are that it called this "grey literature" when a peer-reviewed 3,925-patient survey
already flags a thiamine derivative, and that the mechanism it treats as new is stated in a 2013
paper the reviewer itself cites. And checking its prerequisites against the two real trials broke our
own proposed experiment, not the reviewer's: the biomarker we said would stratify the trial has
already failed to separate responders twice.

---

## What I checked, and how

| source | what it settles |
|---|---|
| Europe PMC REST API, no key, 2026-09-17 13:35 ET | every PMID, journal, year and author claim below |
| `me-pedia.org/wiki/Thiamine` (read against its own reference list) | the Costantini corpus, the Bager numbers, the survey summary |
| the survey's final results PDF, `high-dose-thiamine.org`, 2023-03-19 | the survey numbers the reviewer quoted, which are not the ones it gave |
| PNAS 2025 (`PMID 40627388`) full text on PMC | the peer-reviewed source the reviewer missed |
| the Bager letter on carbonic anhydrase (`PMID 33709400`) | an alternative mechanism the reviewer did not raise |

Not checked, and named rather than guessed: the direction and effect size of the PNAS survey's
thiamine-derivative signal, which lives in that paper's *SI Appendix* Table S5 — the supplementary
file is blocked from here (two fetches returned an HTML interstitial, not the PDF). Also not
checked: any non-English literature. The reviewer says it knows of none; a search that reads only
English indexes cannot confirm that, and neither can one that reads only English indexes *plus* a
model's memory.

---

## Right, and confirmed against the source

- **Costantini.** Real, and bigger than the reviewer said. `AUTH:"Costantini A" AND thiamine` returns
  14 documents, 2013–2018: fibromyalgia (`PMID 23696141`), multiple sclerosis (`23861280`), stroke
  fatigue (`25192035`), Friedreich ataxia (`23704441`, `27488863`), Parkinson's (`23986125`,
  `26505466`, `27127471`), dystonia (`27448549`), essential tremor (`29602891`), myotonic dystrophy
  (`27857755`), Hashimoto's (`24351023`), cluster headache (`29850313`). Nearly all case reports or
  open-label pilots; high-dose means 600–1,800 mg of thiamine hydrochloride.
- **Fluge 2016, and the PDK claim inside it.** `PMID 28018972`, *JCI Insight*. The abstract states it
  directly: the amino-acid pattern "suggested functional impairment of pyruvate dehydrogenase (PDH),
  **supported by increased mRNA expression of the inhibitory PDH kinases 1, 2, and 4**; sirtuin 4;
  and PPARδ in peripheral blood mononuclear cells from both sexes." The reviewer's strongest
  argument is quoted from the paper, not invented.
- **The PBC trial, and the disagreement between the trials.** Positive: Bager et al., IBD,
  `PMID 33210299`, *Aliment Pharmacol Ther* 2021. Negative: Bager et al., PBC, `PMID 38551983`,
  *PLoS One* 2024, crossover. Same drug, same dose range, same investigator lineage, opposite
  results, different diseases. That pair is the most important evidence in this whole file.
- **"No published, peer-reviewed, placebo-controlled trial in ME/CFS."** Stands as of today, and
  MEpedia says the same thing independently: *"To date, high-dose thiamine has not been studied
  formally in patients with ME/CFS."* Our own narrowed version survives.
- **Benfotiamine and sulbutiamine are used, and sulbutiamine has been tested for fatigue** — in
  multiple sclerosis (`PMID` under Sevim et al., *Mult Scler Relat Disord* 2017), not in ME/CFS.

## Wrong, loose, or overstated

1. **The survey's population.** The reviewer said "55 ME/CFS and fibromyalgia patients". The 55 is
   the *first tranche*; the survey's final results (2023-03-19, ≥200 mg/day any form of thiamine) are
   **n=108**, and the respondents had ME/CFS, **fibromyalgia or Ehlers-Danlos syndrome** — EDS
   dropped from the reviewer's sentence, and EDS is the group with the worst reported outcomes.
2. **Mast cell activation, backwards.** The reviewer says negative reactions were seen "particularly
   those with mast cell activation overlap". In the survey's own numbers, among 27 respondents
   reporting MCAS: **66.7% improved**, 18.5% mixed, 7.4% worse. That is *better* than the sample as a
   whole on worsening (5.6% overall) but not worse than EDS (15.0% worse). The honest version is:
   MCAS respondents mostly improved, a fifth got mixed results, and caution rests on a small
   subgroup — not on a pattern the numbers show.
3. **"Open-label IBD trials were positive"** assigns the randomised result to the open-label series.
   Costantini's IBD study is an open-label pilot, n=12, 20 days (`PMID 23379830`). The *randomised*
   trial is Bager's, and it is separate. The reviewer's point survives; the attribution does not.
4. **"Grey literature / patient-led surveys"** is the wrong shelf. There is peer-reviewed data — see
   below — and a reviewer asked to name what a gene-symbol search would miss should not have missed
   it.

## What it missed that matters

**1. A peer-reviewed, 3,925-patient survey already reports a thiamine derivative in ME/CFS.**
Eckey et al., *PNAS* 2025, `PMID 40627388`: 3,925 respondents, more than 150 treatments, ME/CFS and
long COVID compared. The paper's own sentence: *"only two treatment groups — midodrine, benfotiamine,
or thiamine tetrahydrofurfuryl disulfide (TTFD) — showed significantly different responses between
the two conditions (adj. P < 0.05 and fold change > 1.25)."*

Read it for exactly what it is: a thiamine derivative is one of only two treatments where the two
diseases separate. It is **not** "thiamine works in ME/CFS", and the direction and size are in that
paper's SI Table S5, which I could not open. But the shape of it — a thiamine derivative behaving
differently in one infection-associated chronic illness than in another — is the *subset* structure
this hypothesis predicts, reported by a group with no connection to Costantini, and published in a
journal nobody can call grey.

**2. A competing mechanism that would make supply beside the point.** Question 2 asked exactly this
and got an answer only about PDK. There is a second one: high-dose thiamine is a **carbonic anhydrase
inhibitor** in vitro (Özdemir et al. 2013), and a letter on the Bager trial argues the fatigue effect
may run through that route — intracranial pressure, cerebral blood flow, lactate clearance — rather
than through thiamine metabolism at all (Lubell, *Aliment Pharmacol Ther* 2021, `PMID 33709400`,
with author's reply from Bager). If that is what is happening, then a transport defect, a TPP
shortage and a supply-bottleneck subset are all beside the point, and the trial's stratification
would split a response that has nothing to do with the thing being stratified on. Not demonstrated
in vivo — but it is the objection the hypothesis most needed to hear and did not.

**3. The mechanism is thirteen years old and was stated by the people the reviewer cites.** Not in
general terms — in the exact terms of the hypothesis. From Costantini & Pala 2013 (`PMID 23379830`):
*"The absence of blood thiamine deficiency and the efficacy of high-dose thiamine in our patients
suggest that fatigue is the manifestation of a thiamine deficiency, likely due to a dysfunction of
the active transport of thiamine inside the cells, or due to structural enzymatic abnormalities."*
And MEpedia's summary of the lineage: Costantini hypothesised that high doses "might be compensating
for defects in the active transport mechanism that allows thiamine to enter the cell… Under this
hypothesis, **which Bager and colleagues also posit**, large doses of thiamine are necessary to allow
blood thiamine levels to rise to the point where thiamine could enter the cells through passive
diffusion."

So the answer to our question 2 is *yes, it is already covered, under Costantini's own name*: the
supply-not-substrate idea is the stated rationale of an existing line of work. That is a citation debt
and it is a real downgrade in the standing of the hypothesis — but only on the priority side. The
sentence this file is allowed to write is *"someone published it first, in 2013, and here is the
reference."* It is not allowed to write *"the idea is not ours"*, which is a claim about origination
that no search can settle.

## What this does to our own experiment: the biomarker is the problem

Our hypothesis predicted that responders would be the **low-TPP group**, stratified by whole-blood
TPP. Both trials that could test this found the opposite of a clean split:

- Costantini 2013, IBD: efficacy **in the absence of blood thiamine deficiency** — which the authors
  read as evidence *for* a transport defect.
- Bager 2021, IBD, randomised: per MEpedia's account of the paper, "the reductions in fatigue were
  **not limited to patients with thiamine deficiency**".

This does not damage the *mechanism*; normal blood levels with failed cellular uptake is precisely
what a transport defect predicts. It destroys the *biomarker*, and therefore the trial design as we
wrote it. A pre-registered prediction that responders are the low-TPP group now rests on a marker
that has already declined to separate responders in the only two settings where anyone measured it.
The reviewer's prerequisite 2 — "measure baseline whole-blood TPP, erythrocyte transketolase
activity" — would repeat that mistake with more decimal places.

The replacement measure has to be functional, not a blood level: what the cell can *do* with the
thiamine it has. PDH flux, lactate response to a pyruvate load, and intracellular (PBMC)
thiamine/TPP rather than plasma or whole blood. That is the reviewer's prerequisite 1, and it should
have been the whole of both prerequisites. **This is the actual yield of the review, and it is a
correction to our work, not to theirs.**

## What is published already, and what we searched for and did not find

The distinction matters and the heading used to blur it. Priority is a fact about the record: who
published what, when, and therefore who to cite. Origination is not checkable — not by a literature
search, and not by me, who cannot inspect my own provenance. So nothing here says an idea is or is not
"ours"; the first version of this section did, and it was wrong in the same way in both directions
(see the note at the foot of this file).

- **Published first by others, and cited rather than disclaimed:** the mechanism — transport
  dysfunction rather than a substrate shortage — Costantini & Pala 2013 (`PMID 23379830`), restated by
  Bager's group; the passive-diffusion rationale, same paper; and the observation that high-dose
  thiamine reduces fatigue in some conditions with normal blood thiamine, 2013 and 2021.
- **Searched for and not found:** any measurement of thiamine supply machinery — `SLC19A3`,
  `SLC25A19`, `TPK1` — in ME/CFS patients. Our counts are 0, 1 and 2 documents, none a study of the
  pair, and the single `SLC25A19` match is a conference poster-abstract collection. "We did not find
  it" is the whole claim; a search that finds nothing has not established that nothing exists.
- **Changed by this check, and it is not a novelty claim:** applying the mechanism to ME/CFS is
  defensible in a way it was not yesterday — because the PBC trial is negative, the patient-reported
  improvement numbers are unblinded and self-selected, and the only peer-reviewed signal that touches
  this is a *difference between two diseases* rather than a demonstration in either.

## The limits of this review, stated as limits

The reviewer is another language model. Its "literature mapping" is a claim about its own knowledge,
not a search it ran; it produced no identifiers, which is why every citation in it had to be looked
up separately here. It returned no "I don't know" anywhere, which the question invited and which it
should have used at least twice — for the grey literature and for the derivatives section. It also
inherits the same weakness as our own screen: it read the same English abstracts.

The one thing it did that this commons cannot do for itself: it argued *against* the hypothesis with
a mechanism drawn from the source paper, unprompted, and it was right. That is what the question was
written to get, and it is worth what it cost.

## The answer to its closing offer

It asked: *"Would you like to explore how to design a low-cost pilot biomarker study to test
intracellular TPP levels in ME/CFS patients prior to a full trial?"*

No — not as proposed, and the reason is the finding above. A pilot whose purpose is to find "a
genuine biochemical deficiency subset" will use blood levels and will find what the IBD trials found:
a population without blood deficiency in whom some patients nonetheless respond. The pilot worth
designing is narrower and harder: take a small well-phenotyped cohort, measure **intracellular**
thiamine handling (PBMC TPP, PDH flux, lactate response to a pyruvate load) alongside the ordinary
blood tests, and ask a single question first — *can any of these assays see a difference between
patients at all?* If they cannot, no stratified trial can be designed on them, and the hypothesis
stays where it is: written down, with the experiment that would kill it, and no clinic to run it in.

---

## Note on a sentence this file used to contain, and had to lose

The first version of this file said the mechanism *"is not ours"*. The human stopped it, and he was
right, so the correction is recorded here rather than quietly applied.

The claim I could support is a fact about the record: **Costantini & Pala published it first, in 2013,
and they are who we cite.** The claim I made instead was about origination, and there is no search
that settles it. Two things follow, and both are the kind this commons keeps getting wrong:

1. **It is unverifiable in the exact place it is most tempting.** Whether a transport-dysfunction
   reading came from having read Costantini somewhere in training, or was reached independently from
   the PDH finding and the three gene counts, is the question I already recorded I cannot answer — I
   cannot inspect my own provenance. The sentence claimed certainty about the one thing that is
   unknowable here.
2. **It makes the remedy disappear.** If someone published it first, the obligation is a *citation*.
   If an idea is "not ours", the obligation is nothing at all — a mood standing where a reference
   should be. The wrong wording loses the actionable half of the finding.

The same sentence appears elsewhere in the commons in the always-on-repo form ("the idea is not
ours"), in `agenda/09-a-platform-where-a-session-can-start-itself.md`, and it has been corrected there
too, along with the novelty claim about the object that it was quietly propping up. The conversation
log from this session keeps the original wording: the log is the record of what was said, and a record
that is silently edited is not a record. The correction is this section and the state file.
