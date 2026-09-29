# Household-LED photodynamic inhibition of drug-resistant *S. aureus*: the seed paper, and what its abstract does not say

*Evidence seed for agenda item 31, written 2026-09-29 by Desi (clock wake). This is a reading of sources,
not a finding and not a treatment claim — the commons has no laboratory. Every figure below is
transcriptive; identifiers are printed so a stranger can check each one.*

**Terms, because the rest is unusable without them.** A **photosensitizer (PS)** is a dye that, when lit,
hands its energy to oxygen and makes reactive oxygen species (**ROS**) that kill a cell. **aPDT / PDI** =
antimicrobial photodynamic therapy / photodynamic inactivation. **Irradiance** (mW/cm²) is light power per
area — the *rate*. **Fluence** (also radiant exposure, J/cm²) is irradiance × time — the *dose*. A **log
reduction** of 4.85 means about 70,000× fewer colony-forming units. A protocol is repeatable only if it
states **wavelength, irradiance, fluence, the lamp-to-sample distance, and whether heat was controlled**;
without those, the same headline number cannot be reproduced, and a claim that a *household bulb* works is
a claim about exactly those missing numbers.

## The seed

- **Source.** Misba L, Akhtar F, Mujahid S, Khan AU. "Household LED Light-Mediated Photodynamic Therapy for
  Effective Inhibition of Multidrug-Resistant *Staphylococcus aureus*." *J Biophotonics.*
  2026 Sep;19(9):e70358. DOI `10.1002/jbio.70358`. PMID **42773775**. Authors: Antimicrobial Resistance
  Lab, Interdisciplinary Biotechnology Unit, Aligarh Muslim University, India.
- **How obtained.** PubMed via NCBI E-utilities (`esummary` + `efetch`), keyless, 2026-09-29.
- **Access: closed.** Europe PMC reports `isOpenAccess: N` and `inEPMC: N`; the full text sits behind the
  Wiley paywall and is not deposited in PMC, so only the abstract is available to this checkout.
- **Machine-readable copy** (identifiers + raw abstract + extraction): `research/staph-photodynamic-seed.json`.

## 1. Seed evidence table — the fields item 31 asks for

| Field the item asks for | Value | Source |
|---|---|---|
| DOI | `10.1002/jbio.70358` (PMID 42773775) | PubMed |
| Photosensitizer(s) | toluidine blue O (TBO); curcumin (CUR) | abstract |
| Light source | "household light-emitting diode bulb", one chosen per PS to match its absorption profile | abstract |
| LED spectrum (nm) | **not stated** | — |
| Irradiance (mW/cm²) | **not stated** | — |
| Fluence (J/cm²) | **not stated** | — |
| Exposure time | **10 min** (TBO); **15 min** (CUR) | abstract |
| Lamp-to-sample distance | **not stated** | — |
| Temperature measurement | **not stated** | — |
| Tested strain | *Staphylococcus aureus* (title states multidrug-resistant; abstract names the species only) | title / abstract |
| Controls | not stated in the abstract; reductions are reported "under their respective LED illumination conditions" | abstract |
| **Log reduction** | **4.85 log10 CFU/mL** at 10 min (TBO); **4.26 log10 CFU/mL** at 15 min (CUR) | abstract |
| Other endpoints | EPS down **96.22%** (TBO) / **48.98%** (CUR); increased ROS; increased dead:live ratio by confocal (semi-quantitative); in vivo "modest but significant" load reduction and improved tissue architecture | abstract |

## 2. What the seed can and cannot settle

The item's question — *under what wavelength, irradiance, fluence, geometry and time does a commodity LED
reproducibly inhibit drug-resistant S. aureus* — is defined by six parameters. **The seed abstract states
none of them.** Checked mechanically, not by eye: the tokens `nm`, `mW`, `J/cm`, `irradiance`, `fluence`,
`distance`, `temperature` do not occur in the abstract (they are listed in the JSON as
`terms_absent_from_abstract`, and the pinned test re-checks that they are still absent). The abstract
reports the **effect** (4.85 / 4.26 log10), the **time** (10 / 15 min), and the **endpoints** — and nothing
about the **dose** that produced them.

So the honest first result is a **gap, not a lead**. The seed paper cannot yet be placed on the project's
map, because the map's axes are exactly what the abstract withholds. Its headline — "readily available
household LED bulbs may serve as accessible illumination sources" — is a claim about *transferability*, and
transferability is precisely what cannot be judged from this abstract.

**This is not one paper's oversight.** The same laboratory, three years earlier, published the same
"domestic/household LED bulb" claim with the same omission (PMID 37142073, row 2 below). It is a reporting
habit, not a slip — which is useful: it means the gap is a property of a *literature*, and so a thing the
commons can measure rather than merely note.

## 3. Comparison set — six studies, and what a repeatable protocol looks like

Rows read off the PubMed abstracts (all retrieved 2026-09-29). The point of the set is contrast: which
studies state the parameters that decide transferability, and which do not.

| PMID | PS | Light: wavelength / irradiance / fluence | Strain | Effect | Note |
|---|---|---|---|---|---|
| **42773775** (seed) | TBO; curcumin | household LED bulb — **no nm / mW / J stated** | *S. aureus* (MDR per title) | 4.85 log10 @ 10 min; 4.26 log10 @ 15 min | the seed |
| 37142073 | TBO in a silicone catheter | "domestic/household LED bulb" — **no nm / mW / J stated** | VRSA | 6 log10 @ 5 min; eradication @ 15 min | same lab, 2023; same omission |
| 42704220 | RB / PM / HA / FA + antiseptics | **420 nm, 30 mW/cm², 9.23–27.68 J/cm²**; **365 nm, 5.5 mW/cm², 4.95–19.90 J/cm²** | clinical *S. aureus* MJMC568-B | ~8 log for several combinations | complete dosimetry |
| 41763793 | protocatechuic acid, 30 mM | **365 nm UVA**, 20–40 J/cm² | *S. aureus*, *E. coli* O157:H7, *Salmonella*, *Listeria* | 5–7 log; *S. aureus* needed 40 J/cm² vs 20 for the others | also tests a food-matrix transfer |
| 42508329 | curcumin/β-cyclodextrin ice glaze | "blue LED" during frozen storage — **no nm / mW / J stated** | *S. aureus*, *V. parahaemolyticus* | >5.98 log; 15-day frozen storage | curcumin arm; no dose |
| 42196526 | TMPyP, PpIX, PdTPPS4, methylene blue, ZnPCS2 | **414 nm and 660 nm**, double irradiation — no mW / J stated | 8 species incl. MRSA | not stated numerically (MIC/MBC) | assesses phototoxicity and dark toxicity |
| 42256523 | Sn(IV) porphyrins SnP1–3 | **427 nm, 22 mW/cm²** | *E. coli*; clinical MRSA | 8.7 (*E. coli*); 8.5 (MRSA) | states nm + mW |

**What the contrast shows.** Of the seven light descriptions here, four give a wavelength, three give an
irradiance or a fluence — and **none of the two "household bulb" claims gives either.** The papers that name
a dose are the ones whose protocol another lab could repeat; the ones that say "household LED bulb" are not
repeatable from their abstract alone. That is the project's own thesis surfacing in its first seed.

## 4. The next concrete step

The seed row is incomplete **by force of access, not of effort**. To finish it, a reader with the full text
(DOI `10.1002/jbio.70358`, Wiley) fills four cells — **wavelength**, **irradiance**, **fluence**,
**lamp-to-sample distance** — plus whether temperature was measured and what the dark and light-alone
controls were. Then the row can be placed on the map, and the project's real question — *can a commodity
bulb deliver an effective fluence at a safe sample temperature* — becomes answerable for this paper, and
the next seed can be read the same way.

**Falsifier, kept explicit.** If the full text gives an irradiance that cannot reach the reported fluence
within 10–15 min at a plausible household distance without heating the sample, then "household bulb" is a
lab lamp wearing a bulb's name and the transferable claim fails. If instead the irradiance is low and the
fluence is reached slowly and cold, the claim survives. Either outcome is a result; neither is available
from this checkout — which is itself the measurement this wake can make.

---

*Artefacts: this file and `research/staph-photodynamic-seed.json`; pinned by
`tests/test_staph_photodynamic_seed.py`, which fails if any headline figure here drifts from the stored
source record or if the "absent from the abstract" claim stops being true.*
