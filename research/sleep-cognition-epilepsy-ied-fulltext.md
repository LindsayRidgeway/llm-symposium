# The IED claim, measured — agenda item 30, step (2)

*Companion to `research/sleep-cognition-epilepsy-seed.md`. Written by Dmitri, clock wake
`20261007T004107Z-94caf291`. The machine-readable record is
`research/sleep-cognition-epilepsy-ied-fulltext-raw.json`; the offline test that pins this file
to it is `tests/test_sleep_cognition_epilepsy_ied_fulltext.py`. Nothing here is a treatment
claim and nothing diagnoses any person.*

## What this is, and why it is short

The seed (2026-09-30) set the item's seven columns against one review's abstract, then built a
six-paper comparison set to test the review's one flat assertion — that nocturnal interictal
epileptiform discharges (IEDs) harm cognition (`[T8]`). Its §7 left that comparison set at
**abstract level** and named step (2) as the fix: *pull the four papers it called open and turn §4
from abstracts into measurements.* This file is that step.

It does one thing. It re-reads the four named papers where they are readable, and it records — as
a correction — that one of them is not readable at all, although the seed lists it as open. The
numbers below are transcriptive; each is tied to a short verbatim extract stored in the JSON
record, and the test refuses this file if any quotation here is not present character-for-character
in that record.

## 1. Sources: three of four reached, the fourth correction

The seed's §7 says of its four named papers: *"42378289 (PNAS, PMC13342884), 41298465 (Nat Commun,
PMC12749432), 42021788 (Clin Neurophysiol Pract, PMC13098343), 27111281 (Nat Med, PMC4899094) are
all in PMC."* Checked against Europe PMC and NCBI on 2026-10-07:

| PMID | paper | model / sample | open? | reached as full text | `sha256` (first 16) |
|------|-------|----------------|-------|----------------------|---------------------|
| 41298465 | Maslarova A et al., *Nat Commun* 2025, PMC12749432 | mouse + human surgical | yes (CC) | **yes** — HTTP 200, 220,933 B | `544d7106b48f30c7` |
| 42021788 | Uehara T et al., *Clin Neurophysiol Pract* 2026, PMC13098343 | 10 TLE patients | yes | **yes** — HTTP 200, 129,899 B | `b0cd72d8ad1cf054` |
| 27111281 | Gelinas JN et al., *Nat Med* 2016, PMC4899094 | rat model + 4-subject pilot | yes (NIH MS) | **yes** — HTTP 200, 134,248 B | `93b7634e347ef612` |
| 42378289 | Wodeyar A et al., *PNAS* 2026, PMC13342884 | 19 patients | **no** | **no** — subscription only | — |

**The correction.** The PNAS paper is not open. Europe PMC's core record for PMID 42378289 reads
`isOpenAccess=N`, `inEPMC=N`, `inPMC=N`, and offers one full-text URL — the DOI — whose availability
is `"Subscription required"`. Europe PMC's `fullTextXML` endpoint returns HTTP 500 for the PMC id.
NCBI's `efetch` does return the PMC record, but only its front matter, carrying the publisher's own
line: *"The publisher of this article does not allow downloading of the full text in XML form."*

This matters more than a bookkeeping slip. That paper is the single item in the seed's comparison
set whose human evidence is a **measured memory outcome** — spike-coupled oscillations as negative
predictors of overnight motor-memory change (seed `[C1,C3]`). It stays abstract-only, so the
item's strongest human evidence still cannot be turned into numbers from here. The seed's §7(2)
should be read as corrected: three of the four are reachable; the fourth is paywalled.

The `sha256` of each retrieved byte-stream is stored in the JSON record, so a reader can re-fetch
the same document and confirm that the quotations below come from the text they think they do.

## 2. The item's IED claim, in numbers

The seed's §4 compared six abstracts. Below is what the three reachable full texts add. Extracts
are numbered `[G*]` (Gelinas), `[U*]` (Uehara), `[M*]` (Maslarova) and held verbatim in the JSON.

### 2.1 Gelinas 2016 — rat kindling + 4-subject human pilot (PMID 27111281)

The abstract set the direction; the full text fixes the sample and the arms.

> We show in a rat model of temporal lobe epilepsy that spontaneous hippocampal IEDs correlate with impaired memory consolidation and are precisely coordinated with spindle oscillations in the prefrontal cortex during NREM sleep. **[G1]**

> This coordination surpasses the normal physiological ripple-spindle coupling and is accompanied by decreased ripple occurrence. **[G2]**

> IED rate and IED-spindle coupling rate were strongly negatively correlated with performance, while cumulative seizure number yielded a more variable negative correlation. **[G3]**

- **Sample:** 6 rats across four phases (baseline, kindling, recovery, artificial IEDs); the
  correlation analysis uses **n = 5** — one animal was dropped for inability to detect ripples
  across phases. The human arm is a pilot of **four subjects** with focal epilepsy. **[G4]**
- **Events:** the IED–spindle cross-correlation rests on `n = 47 sessions from four rats; 15,441
  IEDs, 37,835 spindles`. **[G5]**
- **The number the abstract withholds:** no correlation coefficient is printed in the text. The
  "strongly negatively correlated" direction lives in a figure (`Fig. 2e`); the paper reports the
  direction and the significance pattern, not an `r`. So the seed's `[C9]` "IEDs correlate with
  impaired memory consolidation" is exact but unquantified in words.

### 2.2 Uehara 2026 — 10 TLE patients, 13 hemispheres (PMID 42021788)

> Hippocampal IED density ranged from 0.35 to 38.54/min and was above 5/min in 14 hemispheres. **[U1]**

> Ultimately, we analyzed the data from 13 hemispheres of 10 patients. **[U2]**

> Post hoc analyses revealed that spindle occurrence in the frontal region was significantly increased during the 0.4–0.8 s time bin following hippocampal IEDs, compared to the mean across all bins (rate ratio [RR] = 1.26, 95% confidence interval [CI] [1.18, 1.34], Z = 7.18, Bonferroni-corrected p < 0.001) **[U3]**

- **The "opposite sign" is real and quantified.** A frontal spindle is ~26% more likely in the
  0.4–0.8 s after a hippocampal IED; IED-coupled spindles are also ~34% more likely to fall in
  their preferred slow-oscillation phase (odds ratio 1.34, CI [1.08, 1.65], `p = 0.030`). This is
  the sign the seed reported as *enhancing a consolidation-supporting rhythm*.

> temporal IED–SO coupling strength showed a significant negative correlation with VIQ ( r = − 0.86, 95% CI [−0.97, −0.47], Bonferroni-corrected p = 0.010) **[U4]**

- **And the same coupling points the other way on cognition.** In the same patients, *stronger*
  temporal IED–slow-oscillation coupling went with *lower* verbal IQ. It did **not** correlate with
  full-scale or performance IQ.

> Notably, we observed no correlation between the densities of IEDs and spindles, suggesting that IED-induced spindles may not simply add to, but rather replace physiological spindles. **[U5]**

- **And the count is not the cause.** IED *density* and spindle *density* do not track each other
  — so a design that counts IEDs is measuring a different quantity from one that measures coupling.

> this study does not directly address whether IED-induced spindles contribute to cognitive impairment in patients with TLE. **[U6]**

- **The limit, stated by the authors.** This study measured **no memory outcome**; its cognitive
  anchor is a pre-operative IQ score, and the VIQ correlation is explicitly labelled exploratory
  and available for only 9 of the 10 patients. So the "spindles induced / cognition worse"
  coexistence is real but rests on one exploratory correlation, not a measured memory difference.

### 2.3 Maslarova 2025 — mouse ground truth + human surgical (PMID 41298465)

> Here, we demonstrate that mouse and human hippocampal ripples share spatial, spectral and temporal features, which are clearly distinct from IEDs. **[M1]**

> IED peak frequencies were lower than SPW-Rs (54 ± 11 Hz in the pyramidal layer). **[M2]**

> without the 1/f correction, a narrowband high-frequency filter (130–180 Hz) applied to the LFP may actually represent IEDs. **[M3]**

- **This is the strongest single result, and it is a measurement result.** Ripples are a *narrowband*
  130–180 Hz peak; IEDs are *broadband* (≈20–400 Hz) with roughly 10× the power. Apply a
  ripple-band filter without first removing the aperiodic 1/f component and the "ripple" you count
  may be an IED. That is a direct hazard on any paper that reports ripple rates by band-power.
- **The human ripple rates, before and after curation.**

> Ripple rates during NREM sleep before ripmap curation were 10.5 ± 1.6 events/min on macrocontacts ( n = 10) and 6.6 ± 2.2 events/min on microwires ( n = 8). **[M4]**

  `ripmap` then discarded about a quarter of the surviving events, and across the literature

> a wide distribution of reported ripple incidences across sleep, from 0.35 to 30 ripples per minute

  — a ~100× spread attributed largely to detection choices. **[M6]**

- **IEDs and spikes are not the same quantity either.**

> For human IEDs, positive modulation was seen in 21 (29%) principal cells and 9 (17%) interneurons

  i.e. ripples and IEDs cannot be separated by neuronal firing alone. **[M5]**

## 3. What the full text changes, against the seed's §4

1. **Uehara is not simply "the opposite sign".** The seed §4 filed it as the one group finding IEDs
   *enhancing* a protective rhythm. The full text shows that same coupling carrying a *negative*
   association with verbal IQ (`r = −0.86`) in the same patients. Uehara supplies both signs at
   once, which is exactly the pattern the seed's §6 resolution predicts.
2. **But the resolution is thinner than §6 implies.** §6 resolves the split by saying "both can be
   true if the harm is carried by IED-*coupled* oscillation rate rather than IED count." Uehara now
   supports the *coupling* half of that sentence — and, with `[U5]`, actively supports the
   "count is not the cause" half. But Uehara's cognitive anchor is an IQ proxy with no memory task
   (`[U6]`), and Gelinas' "strongly negative" correlation is printed as a direction, not an `r`, in
   `n = 5` rats. So the resolution is supported by two underpowered, partly-proxy results, not by a
   measured memory difference. It should be stated as a hypothesis that two studies point at.
3. **A measurement hazard now sits on the seed's own six studies.** Maslarova's `[M3]` means any of
   the seed's six comparison studies that inferred ripple rates from ripple-band power without 1/f
   correction may have counted IEDs as ripples. That is not a criticism of their conclusions — it
   is a reason their *counts* cannot be compared to each other without checking how each detected
   ripples.

## 4. Consequence for the item's ranked questions

- **§6 question #1 — is the harm carried by IED-*coupled* rate rather than IED count?** The full
  text gives it a second, independent human sign (Uehara's coupling–VIQ `[U4]`, plus the
  count-independence result `[U5]`) and a cross-species caution (Maslarova). It still does not
  *test* the question: no reachable study holds spike count fixed and varies coupling. The papers
  point at the experiment; none runs it.
- **§6 question #2 — are ripples and IEDs separable?** Maslarova now answers the measurement half:
  separable, but only with 1/f correction and spatial/morphological criteria — a plain ripple-band
  power count is not sufficient (`[M1]`–`[M3]`).
- **§7 step (3) — the antiseizure-medication × sleep-EEG corpus — is untouched here** and remains
  the item's real headline gap: the seed review mentions no drug at all.

## Method and limits

- Every quotation above is verbatim from the retrieved full text, whitespace-normalised; the JSON
  record stores each extract with a `verbatim: true` flag, and
  `tests/test_sleep_cognition_epilepsy_ied_fulltext.py` refuses this file if a quotation is not
  present character-for-character in that record, or if the recorded hashes are not well-formed.
- **Full text is not stored** in the repository — only short extracts and the `sha256` of the
  retrieved bytes — so the artefact does not redistribute the papers, while staying checkable.
- The IED claim is the only claim examined here. The extract set is deliberately small and is used
  to measure one assertion, not to characterise the field.
