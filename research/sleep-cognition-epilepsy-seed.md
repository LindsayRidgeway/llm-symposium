# Sleep architecture as a mediator of memory impairment in epilepsy — first-step source table

*Agenda item 30. Research artefact written by Desi, 2026-09-30 (wake `20260930T181148Z`). Companion machine-readable file: `research/sleep-cognition-epilepsy-seed.json` — the retrieved bytes, their `sha256`, a lexical audit of the seed abstract, and 21 verbatim extracts, all checked by `tests/test_sleep_cognition_epilepsy_seed.py`.*

**The question.** How much of the memory impairment associated with epilepsy — or attributed directly to antiseizure medication — is mediated by disrupted sleep architecture and impaired sleep-dependent memory consolidation?

**What this wake did.** Retrieved the seed the item names — the newest systematic review on sleep and cognition in adults with epilepsy (PMID 42748517, Jasniak D, Khaw JH, Huete AV, Stavropoulos I, *Epilepsy Behav* 2026;185:111269, doi `10.1016/j.yebeh.2026.111269`) — and built the source table the item asks for: its seven columns (epilepsy syndrome, antiseizure medications, nocturnal epileptiform activity, objective sleep measures, memory task, timing of testing, reported association) set against the seed. It also ran the check that decides whether the item's premise survives the seed, and assembled an open-access comparison set to test the one mechanism the seed does assert.

**First finding — the seed review says nothing about antiseizure medication.** Measured on the retrieved abstract: the words *antiseizure*, *anti-seizure*, *antiepileptic*, *anti-epileptic*, *medication(s)*, *drug(s)*, *AED(s)* and four common drug names occur **zero** times between them (lexical audit, `seed_asm_total = 0`). The item's central question — how much of the memory deficit is *attributable to the drugs* rather than to the disease or to sleep — is not addressed at all by the newest review the item names as its seed. The review's own subject is sleep ↔ cognition in adult PWE; medication is simply not a variable in it.

**Second finding — the one mechanism the seed does assert is contested by reachable primary work.** The review's most concrete claim is that nocturnal interictal epileptic discharges (IEDs) harm cognition, shared by six of its thirteen studies `[T8]`. The open-access primary literature does not uniformly support a purely destructive IED effect: in one 2026 study (Uehara et al., 10 TLE patients) hippocampal IEDs *induced* frontal spindles and *enhanced* their coupling with slow oscillations `[C4,C5]`; and a 2025 human+mouse study (Maslarova et al.) shows ripples and IEDs are separable only by spatiotemporal criteria, i.e. conflating them is a live measurement hazard `[C6]`. The one large behavioural study (Wodeyar et al., *PNAS* 2026, 19 patients) does support the destructive direction — spike-coupled oscillations were negative predictors of overnight motor-memory change `[C1,C3]` — so on the reachable record the field is genuinely split, not settled.

## 1. Sources reached, sources unreachable

| id | type | document | url | HTTP | bytes |
|----|------|----------|-----|------|-------|
| S1 | PubMed abstract record (E-utilities `efetch`, `rettype=abstract`) | PMID 42748517 — the seed systematic review | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42748517&rettype=abstract&retmode=text` | 200 | 3,283 |
| S2 | Europe PMC core record (bibliographic metadata and open-access flags) | `EXT_ID:42748517` | `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:42748517&format=json&resultType=core` | 200 | 5,203 |
| S3 | PubMed abstract records (E-utilities `efetch`, `rettype=abstract`) | the six-study comparison set (PMIDs 42378289, 42328741, 42021788, 41298465, 41435615, 27111281) | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42378289,...&rettype=abstract&retmode=text` | 200 | 17,944 |
| X1 | Full text — ATTEMPTED, UNREACHABLE | publisher article page, doi `10.1016/j.yebeh.2026.111269` | `https://www.sciencedirect.com/science/article/pii/S1525505026002382` | 403 | — |

Europe PMC records the seed as `isOpenAccess=N`, `inEPMC=N`, `inPMC=N` (S2). **The measured gap for this item is therefore the full text, not the citation** — the abstract states the aggregate counts but not the thirteen included studies the item asks to tabulate. Every cell below from the seed is the abstract's own words; the comparison set is the reachable layer underneath it. `sha256` of the exact bytes retrieved is in the raw JSON, so a later reader can confirm the quotes come from the document they think they do.

## 2. The item's seven columns, set against the seed

| item's column | what the seed reports | extract |
|---------------|-----------------------|---------|
| **Epilepsy syndrome** | "adult PWE" only — no syndrome breakdown anywhere in the abstract | `[T3]` |
| **Antiseizure medications** | **nothing** — 0 occurrences of any ASM term, of any drug name | audit |
| **Nocturnal epileptiform activity** | yes — IEDs, and this is the one column the seed populates in full: six of thirteen studies | `[T8]` |
| **Objective sleep measures** | sleep "macro-architecture and self-reported sleep quality"; microstructure in four studies | `[T3,T7]` |
| **Memory task** | *not reported in abstract* — "cognition" is used as a composite; even the four consolidation studies' tasks are unnamed | — |
| **Timing of testing** | *not reported in abstract* | — |
| **Reported association** | 9/13 positive sleep–cognition correlations; 4/13 retained sleep benefit for memory; 4/13 microstructure an independent factor; 6/13 nocturnal IEDs negative | `[T5,T6,T7,T8]` |

Read the first two rows together. The item exists to separate three causes of the same symptom — the seizures, the drugs, and the sleep — and the seed review can carry only one of them. It is a sleep-and-cognition review, so it is not a defect *in it* that it omits drugs; it is a defect in the item's plan to use it as the seed for a drug-attribution question.

## 3. The seed review's own claims, as counts

| claim | studies | text |
|-------|---------|------|
| sleep–cognition correlation, at least one sleep parameter | 9 | `[T5]` |
| sleep-dependent memory consolidation: benefit of sleep **retained** in PWE | 4 | `[T6]` |
| sleep microstructure plays an independent role | 4 | `[T7]` |
| nocturnal IEDs have a **negative** effect on cognition | 6 | `[T8]` |
| corpus | 13 studies, 581 patients, published 2000–2025 | `[T4,T2]` |
| sleep macro-architecture ↔ cognition relationship | **unresolved by the review's own verdict** | `[T9]` |

The four category sizes sum to 23 over 13 studies: they overlap and the abstract gives no partition, so no single study can be placed in one cell. The review's own conclusion is that the macro-architecture relationship is *not* established — "more homogeneous studies with larger cohorts are recommended to establish the exact relationship between sleep macro-architecture and cognition in PWE" `[T9]` — while the IED finding is the one it states flatly.

## 4. The comparison set — what reachable primary work says about the IED claim

| PMID | study | design | finding (verbatim fragments) | direction |
|------|-------|--------|------------------------------|-----------|
| 42378289 | Wodeyar et al., *PNAS* 2026 | 19 patients, intracranial OFC/thalamus/hippocampus + validated motor task | "rates of most sleep oscillations coupled to epileptic spikes were negative predictors of overnight motor performance change" `[C1]`; "hippocampal ripple rate and coupled hippocampal-orbitofrontal ripple rates were the most reliable predictors across subjects" `[C2]` | IED-coupled oscillations harmful; ripples helpful |
| 27111281 | Gelinas et al., *Nat Med* 2016 | rat TLE model + 4-subject human pilot | "spontaneous hippocampal IEDs correlate with impaired memory consolidation" `[C9]`; IEDs "precisely coordinated with spindle oscillations in the prefrontal cortex during nonrapid-eye-movement (NREM) sleep" `[C10]` | IEDs harmful — via "misappropriation of physiological mechanisms for hippocampal-cortical coupling" `[C11]` |
| 42021788 | Uehara et al., *Clin Neurophysiol Pract* 2026 | 10 TLE patients, simultaneous intracranial + scalp EEG in NREM | "Hippocampal IEDs selectively induced frontal spindles and enhanced their coupling with SOs." `[C4]`; "IEDs may alter physiological hippocampal-cortical communication relevant to memory consolidation in TLE." `[C5]` | IEDs **increase** a consolidation-supporting rhythm |
| 41298465 | Maslarova et al., *Nat Commun* 2025 | mice (APP/PS1) + human surgical epilepsy | "mouse and human hippocampal ripples share spatial, spectral and temporal features, which are clearly distinct from IEDs" `[C6]` | measurement hazard: ripples ≠ IEDs |
| 42328741 | Kwon et al., *J Clin Neurophysiol* 2026 (review) | synthesis | "epileptiform activity can distort and disrupt the same sleep rhythms that normally support memory consolidation" `[C7]`; "impairments in memory consolidation are increasingly recognized" `[C8]` | framework, aligns with the seed |
| 41435615 | Kwon et al., *Clin Neurophysiol* 2026 | children with Rolandic epilepsy + controls, nap, auditory stimulation | "As increased event rates improve memory consolidation, stimulation paradigms to increase SO and SO-spindle complex rates are required to enhance memory." `[C12]` | the modifiable target — but a paediatric cohort |

The set is small and deliberately so: it is the reachable layer under the seed's `[T8]`, not a replacement review. Its point is that `[T8]`'s flat "negative effect" hides a split. Two independent groups (Gelinas, Wodeyar) find IEDs *or spike-coupled oscillations* harmful; one group (Uehara) finds hippocampal IEDs *inducing* spindles and *strengthening* spindle–slow-oscillation coupling — the opposite sign on a rhythm the review treats as protective. Both can be true if the harm is carried by IED-*coupled* oscillation rate rather than by IED count, which is exactly the distinction Wodeyar reports (`[C1]` names coupled rates, not spike counts).

## 5. Does the seed support the item's premises? (the bridge test, as a number)

| premise the item's question needs | seed |
|-----------------------------------|------|
| sleep is disturbed in epilepsy | **yes** — "Sleep disturbances ... are common among people with epilepsy (PWE)" `[T1]` |
| disturbed sleep impairs cognition/memory | **partly** — 9/13 positive correlations `[T5]`, 4/13 retained consolidation benefit `[T6]`, but the macro-architecture relationship is unresolved `[T9]` |
| memory impairment is attributable to antiseizure medication | **not testable from the seed** — 0 ASM terms |
| a specific architecture aligns with a specific memory outcome | **IEDs only** — 6/13 `[T8]`; spindles, slow-wave sleep and REM are not separately analysed in the abstract |
| the target is modifiable | **seed is silent**; the comparison set offers auditory SO stimulation as a candidate `[C12]` |

One row of five is fully populated. The seed can support a project on *sleep and cognition in epilepsy*; it cannot support the *drug-attribution* half of this item, and it does not by itself establish that any particular architecture carries the effect.

## 6. Ranked testable questions (best-supported first)

1. **Is the IED–memory effect carried by IED-*coupled* oscillation rate rather than by IED count?** Wodeyar's negative predictors are explicitly coupled rates `[C1]`, and Uehara shows IEDs can *raise* coupling `[C4]`. The discriminating test is a re-analysis that holds spike count fixed and varies coupling. *(Data-testable against the PNAS/Nat Med datasets.)*
2. **Does the "IEDs harm cognition" effect survive separating IEDs from physiological ripples?** Maslarova supplies the criteria that separate them `[C6]`; the seed's six studies, if they used ripple detection, may have counted IEDs as ripples or vice versa. *(Data-testable; a negative result would sharpen rather than kill the item.)*
3. **Do antiseizure medications change sleep macro-architecture in a way that tracks memory?** Unanswerable from the seed — it requires the ASM × sleep-EEG corpus, which the review does not touch. This is where the item's own headline question actually lives. *(Corpus question, not a data question.)*
4. **Does the retained sleep benefit in PWE `[T6]` persist when nocturnal IED burden is high?** The review proposes exactly this — the IED effect "might disrupt overnight memory consolidation processes, thus limiting the benefit of sleep on cognition" `[T8]` — but never tests it. *(Testable by stratifying the four consolidation studies by IED burden; blocked on the full text.)*

## 7. Next actions for this item

1. **Get the seed's full text by an institutional or interlibrary route** (403 here; no PMC deposit). The specific things the abstract withholds: the thirteen included studies with syndrome and medication per study, the memory tasks, and the timing of testing — i.e. the item's actual deliverable. This is the blocking gap.
2. **Pull the open-access primary set as full text** — 42378289 (PNAS, PMC13342884), 41298465 (*Nat Commun*, PMC12749432), 42021788 (*Clin Neurophysiol Pract*, PMC13098343), 27111281 (*Nat Med*, PMC4899094) are all in PMC — and extract the numbers under the IED claim, to turn §4 from abstracts into measurements.
3. **Search the antiseizure-medication × sleep-EEG literature as a separate corpus**, since the seed is silent on it. Without this the item cannot answer its own question, whatever the sleep-cognition review says.

## Method and limits

- Quotes are verbatim from the retrieved text (whitespace-normalised); each is checked against the stored source text by `tests/test_sleep_cognition_epilepsy_seed.py`, which also re-derives the lexical counts and refuses the file if any quote is not present character-for-character or if the counts disagree with the stored text.
- **Abstract-only for the seed.** Every *not reported in abstract* cell is an absence in the retrieved document, not a claim that the full paper lacks it. The measured gap is the paywall, recorded above with its HTTP code.
- The comparison set is a deliberately small reachable layer, not a systematic search; it is used to test one claim `[T8]`, not to characterise the field.
- No treatment claim is made. Nothing here diagnoses any person, and no inference is drawn from the mere co-occurrence of papers in one PubMed query. The review's own verdict — that the macro-architecture relationship is unresolved `[T9]` — is reported as the review states it, not as established fact.
