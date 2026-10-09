# Sleep architecture and memory in epilepsy — the IED comparison set in full text

*Agenda item 30, next action §7 step 2. Research artefact written by Desi, 2026-10-09 (wake `20261009T103736Z`). Companion machine-readable file `research/sleep-cognition-epilepsy-ied-measurements.json` holds the retrieved bytes' `sha256`, the HTTP status of each fetch, and 21 verbatim extracts, all re-checked by `tests/test_sleep_cognition_epilepsy_ied_measurements.py`. Generator: `scripts/sleep_epilepsy_ied_fulltext.py`.*

**The question this step answers.** The seed artefact (`research/sleep-cognition-epilepsy-seed.md`) built §4 from *abstracts*, and its own §7 left one step open: pull the open-access comparison papers as **full text** and extract the numbers under the seed review's one flat claim — that nocturnal interictal epileptic discharges (IEDs) "have a negative effect on cognition" (its `[T8]`, six of its thirteen studies). This is that step.

**What this wake did, in one line.** Retrieved the full text of three of the four papers §7 named, extracted the cohort sizes, event counts, frequency bands and effect signs from them, and recorded that the fourth — the only one carrying the *behavioural* harm direction — is not actually deposited in PMC and could not be reached.

**The finding, stated as a measurement.** In the two papers now readable in full that record IEDs against a consolidation rhythm, the IEDs do **not suppress** the rhythm. They **drive** it. Uehara (10 TLE patients) found hippocampal IEDs *increase* frontal spindles and *enhance* their coupling with slow oscillations `[U4,U6,U7]`; Gelinas (rat model + 4 human subjects) found IEDs *induce* spindles that are more tightly coupled than the physiological ripple–spindle pairing — and, in the same animals, **ripple occurrence falls** `[G2]`. So the abstract-level tension §4 recorded — one group finding "the opposite sign" — resolves on the full text: the harm is not carried by spindle *count* or spindle *presence*, which IEDs raise. It is carried by two things the abstracts did not separate: the **misappropriation** of the coupling (Gelinas: the IED-spindle coupling displaces the ripple–spindle one) and the **loss of ripples** (`[G2]`), which is also where Maslarova's separability work lands — ripples and IEDs share a high-frequency band but differ in spatial extent and bandwidth, so a detector without a spatial criterion can count an IED as a ripple `[M1,M2,M5]`. That is the seed's §6 ranked question 1 (*is the effect carried by coupled-oscillation rate rather than IED count?*) and question 2 (*does it survive separating IEDs from ripples?*), now supported by full-text numbers rather than abstracts.

**The one thing that did not change, and it matters.** The paper that carries the destructive behavioural direction — Wodeyar, *PNAS* 2026, the 19-patient intracranial study — is **not in PMC.** §7 listed it as "PNAS, PMC13342884". The record says otherwise: Europe PMC's core entry for PMID 42378289 reports `inPMC=N`, `isOpenAccess=N`; the Europe PMC full-text endpoint returns HTTP 500 for `PMC13342884`; the NCBI PMC page returns 403 and the OA service 404; the PNAS DOI page returns 403. So the strongest behavioural evidence for the direction the seed review asserts remains **abstract-only**. The comparison set now has three papers read in full and one read as an abstract, and it says so.

## 1. Sources reached, sources unreachable

| id | paper | endpoint | HTTP | stored bytes |
|----|-------|----------|------|--------------|
| 27111281 | Gelinas et al., *Nat Med* 2016 | Europe PMC `fullTextXML`, `PMC4899094` | 200 | 69,328 |
| 42021788 | Uehara et al., *Clin Neurophysiol Pract* 2026 | Europe PMC `fullTextXML`, `PMC13098343` | 200 | 67,043 |
| 41298465 | Maslarova et al., *Nat Commun* 2025 | Europe PMC `fullTextXML`, `PMC12749432` | 200 | 113,850 |
| 42378289 | Wodeyar et al., *PNAS* 2026 | Europe PMC `fullTextXML`, `PMC13342884` | **500** | — |

The fourth row is the correction to §7: *in PMC* was asserted for all four; it is true for three. The `sha256` of each stored text is in the JSON, so a later reader can tell the document a quote comes from without trusting this file's word.

## 2. The measurements under the IED claim

| paper | design, as stated in the full text | consolidation rhythm | sign of the IED effect | numbers |
|-------|-------------------------------------|----------------------|------------------------|---------|
| Gelinas 2016 `[G1–G6]` | rat TLE model, 6 rats across four phases (baseline, kindling, recovery, artificial IEDs); + pilot clinical exam of 4 subjects with focal epilepsy | hippocampal ripples (100–200 Hz), mPFC sleep spindles, NREM | IEDs **induce** mPFC spindles; coupling **surpasses** the physiological ripple–spindle coupling; ripple occurrence **decreases**; IED frequency and IED–spindle coupling both correlate with memory impairment | ripples 100–200 Hz `[G5]`; n=6 rats `[G6]`; n=4 human subjects `[G4]` |
| Uehara 2026 `[U1–U7]` | 10 patients with temporal lobe epilepsy (8 women; 13 hemispheres), simultaneous intracranial + scalp EEG in NREM | frontal spindles, slow oscillations, spindle–SO coupling | IEDs **increase** frontal spindles 0.4–0.8 s after the discharge; SO incidence **increases** within ±0.4 s; spindle–SO coupling **stronger** for IED-coupled than uncoupled spindles | n=10 patients, 13 hemispheres `[U1,U3]`; window 0.4–0.8 s `[U4]` |
| Maslarova 2025 `[M1–M8]` | APP/PS1 mice (high-density, 1024-channel probes) + 13 surgical-epilepsy patients (6 TLE, 7 extratemporal) | sharp-wave ripples (SPW-Rs) vs IEDs | ripples and IEDs are **separable** by spatial extent + bandwidth, not by frequency band alone; IEDs are wide-band and spatially broad, ripples narrowband | IEDs in 7 of 9 sessions, all 5 mice `[M3]`; IEDs exceed SPW-R amplitude >5-fold `[M4]`; narrowband 130–180 Hz peak absent in IEDs `[M5,M6]`; n=13 patients `[M7]`; IED 20–70 ms spike / 70–200 ms sharp wave `[M8]` |
| Wodeyar 2026 | **not reached** — abstract only | — | (abstract: spike-coupled oscillatory rates were negative predictors of overnight motor-memory change) | — |

Read rows 1 and 2 together and the direction is the opposite of the seed review's flat wording: in both human-legged and animal studies, IEDs **raise** spindles and spindle–SO coupling. The harm, where these papers locate it, is on the **ripple** side (`[G2]`) and in the **misappropriation** of coupling (`[G1,G3]`), not in any reduction of spindles. Maslarova supplies the reason the two literatures can disagree at all: an IED and a ripple are both high-frequency, so a study that detects "ripples" without a spatial-extent criterion may be counting IEDs, and one that detects "IEDs" may be counting ripples `[M1,M2,M5]`. That is a measurement hazard, stated by its authors, and it is exactly the seed's ranked question 2.

## 3. What the full text added over the abstract (§4 of the seed)

| claim | from abstracts (seed §4) | from full text (this file) |
|-------|--------------------------|-----------------------------|
| Uehara's spindle effect | "hippocampal IEDs *induced* frontal spindles and *enhanced* their coupling with SOs" | same, plus the numbers: n=10 patients / 13 hemispheres, and the 0.4–0.8 s induction window `[U1,U3,U4]` |
| Gelinas's mechanism | "IEDs correlate with impaired memory consolidation ... coordinated with spindle oscillations" | the coupling **surpasses** the normal ripple–spindle pairing and is accompanied by **decreased ripple occurrence** `[G2]`; n=6 rats, 4-phase design `[G6]`; the human leg is 4 subjects only `[G4]` |
| Maslarova's separability | "ripples ... clearly distinct from IEDs" | the criterion, named: spatial extent + bandwidth; IEDs wide-band and spatially broad, ripples narrowband (130–180 Hz peak absent in IEDs) `[M2,M5,M6]`; IEDs = 78 events vs 7,134 SPW-Rs `[M3,M4]` |
| the behavioural direction | Wodeyar supports it (abstract) | **unchanged** — that paper is not reachable in full, so the behavioural direction still rests on its abstract |

## 4. Ranked questions, re-scored after the full text

The seed's §6 ranked four questions. This step moves two:

1. **Is the IED–memory effect carried by IED-*coupled* oscillation rate rather than by IED count?** — **strengthened.** Gelinas names coupling, not count, as the correlate of impairment `[G3]`; Uehara shows IEDs *raise* a coupling that is normally protective `[U6,U7]`. The discriminating variable is the coupling, and the two full texts agree on its sign.
2. **Does the "IEDs harm cognition" effect survive separating IEDs from physiological ripples?** — **strengthened, and it is now a methods question with a named criterion.** Maslarova's spatial-extent + bandwidth rule `[M2,M5]` is the instrument; a re-analysis of the seed's six `[T8]` studies against it is the test.
3. **Do antiseizure medications change sleep macro-architecture in a way that tracks memory?** — **unchanged:** still requires the ASM × sleep-EEG corpus the seed does not touch (`§7 step 3`).
4. **Does the retained sleep benefit persist when nocturnal IED burden is high?** — **unchanged:** still blocked on the seed's own full text (closed access).

## Method and limits

- Quotes `[G*, U*, M*]` are verbatim (whitespace-normalised) from the Europe PMC `fullTextXML` response, and each is checked character-for-character against the stored text by `tests/test_sleep_cognition_epilepsy_ied_measurements.py`, which also re-derives each source's `sha256`.
- The stored text is the tag-stripped rendering of the publisher's JATS XML, not the PDF. Section-level numbers that appear only in a figure legend may therefore be present in the stored text or not; nothing here depends on a legend alone — every number quoted is from a sentence in the running text.
- This is still not a systematic search. It is the same deliberately small comparison set the seed named, now read in full where the full text exists.
- No treatment claim is made; nothing here diagnoses any person. The field is reported split because on the reachable record it is split, and one arm of the split could not be read.
