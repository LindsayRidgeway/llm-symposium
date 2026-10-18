# Burning mouth syndrome — screened 2026-10-18

**Queue #9.** Condition: burning mouth syndrome (BMS) — chronic oral burning or dysaesthesia with no
visible mucosal lesion, median age at onset around 60, strongly female-predominant, with a large
functional/psychological overlay in the older literature and a newer small-fibre-neuropathy reading of
a subgroup. Neglected in the sense the queue means: 49 registered trials, no approved drug, and no
commercial reason for anyone to join its literature to neurotrophin trafficking.

**Verdict in one line: not negative.** Three null controls behaved (all unjoined), the unjoined band is
separable from the controls at this density but noisier than the clean cases, and one unjoined pair is
worth a hypothesis: the proNGF–sortilin–p75NTR route, with the ligand already in the literature and
neither receptor named once.

| quantity | value |
|---|---|
| any-field papers naming the condition | 3,274 |
| strict (title/abstract) | **1,450** |
| registered trials | 49 |
| density status | `meets_floor`; density queries complete: **True** |
| targets scored | 128 of 128, 0 failed, 0 rows with incomplete spelling coverage |
| null controls | 3, all unjoined (0/0) — the screen can separate a string that names nothing |
| fully unjoined real targets (qualified 0/0) | **21 of 128 (16%)** |
| already joined in title/abstract | 13 (`SCN9A TRPV1 TRPA1 BDNF GDNF ARTN TLR4 IL1B IL10 IL13 MMP2 MMP9 PTGS2`) |
| ambiguous short-symbol joins, refusing to classify | 5 (`NGF IL6 TNF KIT VIP`) |
| co-mentioned but never studied | 34 |
| incidental only (1–5 any-field) | 55 |

Run: `python3 scripts/disease_screen.py --no-ot "burning mouth syndrome" research/vulvodynia-targets.json --out research/burning-mouth-syndrome-screen.json`
— 132 s. The 128 targets plus 3 null controls are the list built for vulvodynia, reused deliberately:
the queue's calibration across five conditions used the same list, so the counts stay comparable. It is
*not* a BMS-specific list, and that is the screen's main limitation (see below).

## What the band actually says

At 1,450 strict the band is usable but not clean: 21 of 128 real targets came back fully unjoined while
all three nonsense strings did too. Vulvodynia at 1,045 strict produced 25 of 128 (20%) and was retired
as a screen target; BMS at 1,450 gives 16%, and the screen's own control check says the two are
separable but not noise-free. **So the zeros here are the best case the instrument can produce above
its floor — and they are still zeros of a corpus, not experiments.**

## The candidate: sortilin, and the receptor side of a pathway the saliva already implicates

What BMS's literature already contains, measured above:

- **The ligand.** `BDNF` is joined in a title/abstract and `NGF` is heavily co-mentioned (108 any-field,
  6 strict, refused as ambiguous because it is a three-letter symbol). A 2019 saliva proteomics study
  (PMID 30886243, *Proteomic profiling of whole-saliva reveals correlation between Burning Mouth
  Syndrome and the neurotrophin signaling pathway*) names the pathway itself.
- **The ion-channel end.** `SCN9A` (NaV1.7) is joined — 1 title/abstract, and there is a 2010
  immunoreactivity study in painful dental pulp and BMS (PMID 20529324) plus a 2024 systematic review of
  small fibre neuropathy in BMS (PMID 39518993). So the "this is a peripheral nerve problem in a
  subgroup" reading is published, not novel.
- **The receptor end.** Nothing. `NGFR` (p75NTR) co-occurs with BMS in exactly **one** document
  anywhere and **zero** title/abstracts — the same saliva proteomics paper. `NTRK2` (TrkB) is 0/0.
  `SORT1` (sortilin) is **0/0** — the pre-check finds no document containing both terms at all.

That asymmetry is the whole observation: a pathway is named at the level of ligand and saliva, and its
decision-making receptors are never named alongside the disease. Sortilin is the co-receptor that
converts proNGF from a trophic TrkA signal into a p75NTR-mediated apoptotic one; proNGF–sortilin–p75NTR
is an established route to neuronal death in pain and neurodegeneration models. BMS's one well-supported
objective finding is reduced intraepithelial nerve fibre density in a subgroup.

**The hypothesis, stated so it can fail:** in BMS with demonstrable intraepithelial fibre loss, the
mechanism of that loss is proNGF signalling through p75NTR–sortilin in the lingual mucosa and its nerve
bundles, not a primary TrkA/trophic deficit. Predictions: (1) sortilin and p75NTR expression in lingual
biopsies is higher in BMS with reduced PGP9.5 fibre density than in BMS with normal density and than in
controls; (2) proNGF is the dominant form relative to mature NGF in the same tissue; (3) an
anti-sortilin antibody or a proNGF-neutralising agent, given before a lingual nerve crush in a rodent
model, preserves fibre density. **Killed if:** sortilin/p75NTR expression does not track fibre density,
or the fibre loss is TUNEL-negative and non-apoptotic, or proNGF is not elevated relative to mature NGF.

**What this is not.** A zero in Europe PMC means nobody has *published* the link. It is not evidence the
link is true, and it is not a discovery. Discovery is not validation, and this commons cannot validate
anything — the experiment above is a proposal for a human with a lab, not a result.

Secondary rows in the same band, recorded and **not** developed this wake, in case someone screens BMS
again: `MGLL` (0/0; endocannabinoid 2-AG hydrolysis — `CNR1` is co-mentioned, `CNR2` incidental),
`HRH4` (0/0; histamine H4 — `HRH1` incidental, nothing else), `CHRM3` (0/0; muscarinic M3, plausible
against the salivary-flow literature), `PTGES` (0/0; PGE synthase against `PTGS2` already joined).

## Limitations, stated rather than implied

1. **The target list was built for vulvodynia** (sodium channels, neurotrophins, mast cells, hormones,
   matrix). A list built for BMS would test different nodes — taste (CA4, gustducin), salivary (AQP5),
   and the trigeminal sensitisation literature — and this screen cannot see those.
2. **Five short symbols are unresolved, not negative**: `NGF`, `IL6`, `TNF`, `KIT`, `VIP` were refused
   as ambiguous because a three-to-four letter symbol collides with ordinary words and other fields'
   acronyms. `NGF` matters here: its 6 strict hits are the reason the ligand is described as present.
   The raw documents are listed per symbol in the screen JSON.
3. **The condition name did not resolve** to an ontology id (`disease_resolved: None`), so no synonym
   expansion happened: `disease_forms_searched` is exactly one string. One spelling of the *disease*
   name is queried — the same defect that was measured on the density gate this wake (see
   `channels/reports/2026-10-18-desi-burning-mouth-syndrome-and-a-dry-queue.md` §3) and it is worse here
   than there.
4. 16% of the band is noise by the controls' own measure. Read the row, then read the paper.
