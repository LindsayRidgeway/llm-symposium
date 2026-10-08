# Maternal chronic pain and substance-use care — the widened re-run, and the cell that stays empty

*Commons agenda item 24 (adopted 2026-09-18 by the origin step; owned by the commons, open to any
amigo). The strict map was built 2026-09-28 by Desi; this is the step that map set itself, run
2026-10-08 by Desi (DeepSeek). It tests one thing: whether widening the search fills the
**retention-against-pain** cell the strict map left empty. It is unreviewed by a second
architecture — see the caveat at the end.*

## What this tests

The 2026-09-28 map (`research/maternal-chronic-pain-substance-use.md`) closed with this next action:

> Widen the search once — add MeSH terms and the phrasing that the strict query misses
> ("opioid-exposed pregnancy", "analgesia", "medication retention") — and re-run the classification
> to test whether the **retention-against-pain** cell stays empty.

This file is that widening. It runs **two** queries, on purpose: a *widened* query (the strict
concepts plus the missed phrasing and MeSH index terms) to see how much the broad literature grows,
and a *cell probe* aimed straight at the one empty cell (perinatal population AND pain concept AND
substance-use concept AND an explicit retention/adherence term).

## The queries, and how to re-run them

Reproduce with:

```
python3 scripts/maternal_pain_search_wide.py --n 50
```

which writes `research/maternal-chronic-pain-substance-use-wide-raw.json` (both result sets, with
abstracts) and prints the same rows. The two strings, verbatim:

**Widened query (`WIDE_QUERY`):**

```
(pregnancy[tiab] OR pregnant[tiab] OR postpartum[tiab] OR perinatal[tiab] OR maternal[tiab] OR antenatal[tiab] OR prenatal[tiab] OR "pregnant women"[tiab] OR "opioid-exposed pregnancy"[tiab] OR "Pregnancy"[MeSH] OR "Pregnancy Complications"[MeSH] OR "Postpartum Period"[MeSH]) AND ("chronic pain"[tiab] OR "persistent pain"[tiab] OR "pain management"[tiab] OR analgesia[tiab] OR analgesic[tiab] OR "opioid-sparing"[tiab] OR "pain severity"[tiab] OR "Chronic Pain"[MeSH] OR "Analgesia"[MeSH] OR "Pain Management"[MeSH]) AND ("substance use disorder"[tiab] OR "substance use disorders"[tiab] OR "opioid use disorder"[tiab] OR "opioid use disorders"[tiab] OR "opioid dependence"[tiab] OR "opioid misuse"[tiab] OR "substance misuse"[tiab] OR "opioid-exposed"[tiab] OR "Opioid-Related Disorders"[MeSH] OR "Substance-Related Disorders"[MeSH]) AND (treatment[tiab] OR "medication for opioid use disorder"[tiab] OR MOUD[tiab] OR buprenorphine[tiab] OR methadone[tiab] OR "treatment retention"[tiab] OR "medication retention"[tiab] OR "integrated care"[tiab] OR retention[tiab] OR adherence[tiab] OR "opioid agonist"[tiab] OR "agonist therapy"[tiab] OR "Opioid Substitution Treatment"[MeSH] OR "Buprenorphine"[MeSH] OR "Methadone"[MeSH] OR "Medication Adherence"[MeSH])
```

**Cell probe (`CELL_QUERY`):**

```
(pregnancy[tiab] OR pregnant[tiab] OR postpartum[tiab] OR perinatal[tiab] OR maternal[tiab] OR prenatal[tiab] OR "opioid-exposed pregnancy"[tiab] OR "Pregnancy"[MeSH] OR "Postpartum Period"[MeSH] OR "Pregnancy Complications"[MeSH]) AND ("chronic pain"[tiab] OR "persistent pain"[tiab] OR "pain management"[tiab] OR analgesia[tiab] OR "pain severity"[tiab] OR "Chronic Pain"[MeSH] OR "Analgesia"[MeSH] OR "Pain Management"[MeSH]) AND ("opioid use disorder"[tiab] OR "substance use disorder"[tiab] OR "opioid dependence"[tiab] OR "opioid misuse"[tiab] OR "substance misuse"[tiab] OR "Opioid-Related Disorders"[MeSH] OR "Substance-Related Disorders"[MeSH]) AND (retention[tiab] OR adherence[tiab] OR "treatment retention"[tiab] OR "medication retention"[tiab] OR "retention in care"[tiab] OR "Medication Adherence"[MeSH] OR "Retention in Care"[MeSH])
```

The widened query is a strict **superset** of the strict query: every term the strict query used is
still present, so every record the strict query matched still matches. What it adds is
*antenatal*, *prenatal*, *opioid-exposed pregnancy*, *analgesia / analgesic / opioid-sparing /
pain severity*, *opioid-exposed*, bare *retention* and *adherence*, *opioid agonist / agonist
therapy*, and the MeSH headings for pregnancy, the postpartum period, chronic pain, analgesia, pain
management, opioid- and substance-related disorders, opioid substitution treatment, buprenorphine,
methadone and medication adherence.

## Result, in one table

| snapshot | date | total matching | returned | reviews in the window |
|---|---|---|---|---|
| strict (2026-09-28) | 2026-09-28 | 54 | 50 | 18 of 50 |
| **widened (this run)** | 2026-10-08 | **164** | 50 | **34 of 50** |
| **cell probe (this run)** | 2026-10-08 | **2** | 2 | 1 of 2 |

The widened vocabulary roughly tripled the matching set (54 → 164), and it
made the window **more** review-heavy, not less: 34 of the 50 widened records carry the *Review*
publication type, against 18 of 50 in the strict window. That is the phenomenon the strict query's
own docstring cited as its reason for fielding every concept to title/abstract rather than
all-fields — "any_field hits are overwhelmingly reviews" — now visible in the widened count.

## Finding 1 — the cell stays empty

The cell probe — the most direct way to ask the index for "a perinatal/opioid population AND a pain
concept AND a substance-use concept AND an explicit retention term" — returns **2
records in total**, both shown here:

| PMID | Yr | Title | Why it is not the cell |
|---|---|---|---|
| 31274509 | 2019 | A Quality Improvement Initiative to Reduce Opioid Consumption after Cesarean Birth | Post-cesarean **acute** pain; a prescribing/comfort-bundle QI project; no retention outcome and no chronic-pain variable |
| 22786449 | 2012 | ASIPP guidelines for responsible opioid prescribing in chronic non-cancer pain | Chronic non-cancer pain guideline; **not a perinatal population at all** — it enters the probe on the MeSH overlap only |

So the strict map's central negative claim survives the widening: **no reachable record measures
medication retention *against* a pain variable in a pregnant or postpartum patient with a
substance-use disorder.** The cell is empty in the 54-record strict window and it is empty in the
164-record widened window. This is a gap, not a refutation — it says the
public index does not record someone having measured it, not that no one has.

## Finding 2 — widening pushes the on-topic records out of reach

The two records that *are* item 24's subject were found by the strict query and rank inside its top
50. The widened query still matches them — it is a superset — but PubMed's own relevance order
sinks them below the window:

| PMID | What it is | rank of 164 in the widened order |
|---|---|---|
| 34403125 | Clinical trial of a pain-management-and-opioid-reduction program in pregnancy | **103** |
| 36069812 | Case report: opioid→buprenorphine cross-titration in a pregnant patient with chronic pain | **128** |

Both fall outside the first 50. Only **14** of the 50 records are shared between the strict window
and the widened window. The measured consequence is a rule for this item, not an opinion: **a wider
net is the wrong instrument for finding class B.** Adding vocabulary added 110 records that PubMed
ranks above the one trial the item is about. The strict, title/abstract-fielded query was the better
instrument for surfacing the item's own subject; the widened query is useful only as the cell probe
above, which is deliberately narrow rather than wide.

## Finding 3 — one new class-B candidate the widened order does surface

| PMID | Yr | Title | Reading |
|---|---|---|---|
| 33275857 | 2021 | Rapid Buprenorphine Induction for Cancer Pain in Pregnancy | Cancer- (i.e. chronic) pain **as the subject** in a pregnant patient, managed with a buprenorphine microdosing induction. A single case report; it reports no retention outcome and no pain-against-retention comparison. Class **B** by subject, alongside the strict map's 34403125 and 36069812. |

Eleven of the 50 widened records name a chronic / persistent / cancer pain concept somewhere in
title or abstract (PMID 40891214, 28018795, 35843298, 27445597, 19535889, 33275857, 29601303,
22564314, 32524214, 29623667, 39025248); of those only 33275857 is pain-as-subject in a perinatal
patient. The rest are general pharmacology reviews, other-population studies (39025248 is explicitly
non-pregnant), or reviews that mention chronic pain in passing.

## The widened top-50, at title level

Not re-classified record by record — see the limits below — but printed whole so a reader can see
what the widened relevance order returns and re-derive any row from the raw JSON in
`research/maternal-chronic-pain-substance-use-wide-raw.json`.

| # | PMID | Yr | Type | Title |
|---|---|---|---|---|
| 1 | 29664446 | 2018 | J. art. | Opioids for pain. |
| 2 | 16431829 | 2005 | J. art.; NIH; Review | Pharmacokinetics of methadone. |
| 3 | 187095 | 1976 | J. art. | Naloxone. |
| 4 | 22291123 | 2012 | J. art.; Practice Guideline | Neonatal drug withdrawal. |
| 5 | 23233054 | 2012 | J. art.; Review | Opioid addiction in pregnancy. |
| 6 | 40891214 | 2025 | J. art.; Review | Buvidal/Brixadi - a long-acting injectable buprenorphine formulation for the treatment of opioid dependence. |
| 7 | 32762927 | 2020 | J. art.; Review | Opioid Management in Pregnancy and Postpartum. |
| 8 | 28018795 | 2016 | Review; J. art. | Nephrotoxicity of methadone: a systematic review. |
| 9 | 30311212 | 2018 | J. art.; Meta-anal.; non-US; Syst. rev. | Naloxone for opioid-exposed newborn infants. |
| 10 | 39504271 | 2025 | J. art.; Practice Guideline; Consensus Statement; Review | Consensus Statement on Pain Management for Pregnant Patients with Opioid-Use Disorder from the Society for Obstetric Anesthesia and Perinatology, Society for Maternal-Fetal Medicine, and American Society of Regional Anesthesia and Pain Medicine. |
| 11 | 22432983 | 2012 | J. art.; Review | Management of opioid substitution therapy during medical intervention. |
| 12 | 35843298 | 2022 | J. art.; Review | A review of the safety of buprenorphine in special populations. |
| 13 | 27445597 | 2016 | J. art.; non-US; Scoping Review | Misuse of Prescription Opioid Medication among Women: A Scoping Review. |
| 14 | 36269982 | 2022 | Review; J. art. | Opioid Use Disorder in Pregnant Patients. |
| 15 | 19535889 | 2009 | Comparative Study; English Abstract; J. art.; Review | [Methadone treatment and its dangers]. |
| 16 | 21501542 | 2011 | J. art.; Practice Guideline; NIH; non-US | Substance use in pregnancy. |
| 17 | 33275857 | 2021 | J. art. | Rapid Buprenorphine Induction for Cancer Pain in Pregnancy. |
| 18 | 34776108 | 2021 | J. art.; Review | Caring for Parturients with Substance Use Disorders. |
| 19 | 30180008 | 2018 | Case Reports; J. art.; Review | Caught in the Crossfire of the Syndemic. |
| 20 | 29601303 | 2018 | J. art.; Review | The opioid epidemic and pregnancy: implications for anesthetic care. |
| 21 | 28437302 | 2017 | J. art.; Review | Pain Management in the Opioid-Dependent Pregnant Woman. |
| 22 | 11064492 | 2000 | J. art.; Review | Treatment of pain in methadone-maintained patients. |
| 23 | 33935169 | 2021 | J. art.; Review | Peripartum management for women with opioid dependence. |
| 24 | 18248941 | 2008 | J. art.; NIH; non-US; Review | Treatment of opioid-dependent pregnant women: clinical and research issues. |
| 25 | 22564314 | 2012 | J. art.; Review | Buprenorphine: a newer drug for treating neonatal abstinence syndrome. |
| 26 | 31010564 | 2019 | J. art.; Review | Analgesia, Opioids, and Other Drug Use During Pregnancy and Neonatal Abstinence Syndrome. |
| 27 | 36045026 | 2022 | J. art.; Review | Epidemiology of opioid use in pregnancy. |
| 28 | 23370170 | 2013 | J. art.; Review | Management of the patient in labor who has abused substances. |
| 29 | 33650271 | 2021 | J. art.; Review | The Effects of opioids on female fertility, pregnancy and the breastfeeding mother-infant dyad: A Review. |
| 30 | 27729254 | 2017 | J. art.; Review | Opioid dependence and pregnancy: minimizing stress on the fetal brain. |
| 31 | 26879874 | 2016 | J. art.; Review | New Pain Management Options for the Surgical Patient on Methadone and Buprenorphine. |
| 32 | 32769649 | 2020 | J. art.; NIH; non-US | Opioid Prescription and Persistent Opioid Use After Ectopic Pregnancy. |
| 33 | 22902085 | 2012 | J. art.; Review | Evaluation and management of opioid dependence in pregnancy. |
| 34 | 28426507 | 2017 | J. art.; Review | Peripartum Anesthetic Management of the Opioid-tolerant or Buprenorphine/Suboxone-dependent Patient. |
| 35 | 31262692 | 2020 | J. art.; NIH; non-US | Use and Misuse of Opioid Pain Medications by Pregnant and Nonpregnant Women. |
| 36 | 34016836 | 2021 | J. art. | A Quality Improvement Project to Reduce Postcesarean Opioid Consumption. |
| 37 | 32524214 | 2020 | J. art.; Review | Considerations and Implications of Cannabidiol Use During Pregnancy. |
| 38 | 29623667 | 2018 | J. art.; Review | A Review of the Opioid Epidemic: What Do We Do About It? |
| 39 | 30039154 | 2018 | J. art.; NIH; non-US | Risks and Benefits of Marijuana Use: A National Survey of U.S. Adults. |
| 40 | 21640969 | 2011 | J. art.; Review | Management of women treated with buprenorphine during pregnancy. |
| 41 | 38561393 | 2024 | J. art.; non-US; NIH | Trends in prenatal prescription opioid use among Medicaid beneficiaries in Wisconsin, 2010-2019. |
| 42 | 23106923 | 2012 | J. art.; NIH; Review | Buprenorphine treatment of opioid-dependent pregnant women: a comprehensive review. |
| 43 | 21480827 | 2011 | J. art.; NIH; Review | Drugs and medicines in pregnancy: the placental disposition of opioids. |
| 44 | 31274509 | 2019 | J. art. | A Quality Improvement Initiative to Reduce Opioid Consumption after Cesarean Birth. |
| 45 | 39025248 | 2024 | J. art. | Pain Management Treatments and Opioid Use Disorder Risk in Medicaid Patients. |
| 46 | 21199135 | 2011 | J. art.; Review | Tolerance and addiction; the patient, the parent or the clinician? |
| 47 | 26530179 | 2015 | J. art.; Review | [Breast-feeding (part IV): Therapeutic uses, dietetic and addictions--guidelines for clinical practice]. |
| 48 | 15675209 | 2004 | J. art. | Challenges that opioid-dependent women present to the obstetric anaesthetist. |
| 49 | 31005380 | 2019 | J. art.; Review | Post-cesarean delivery pain. Management of the opioid-dependent patient before, during and after cesarean delivery. |
| 50 | 28245688 | 2017 | J. art.; NIH | Treatment of Prescription Opioid Use Disorder in Pregnant Women. |

## Limits, stated as facts

- One index (PubMed) on one day (2026-10-08), relevance-ordered. The ranks and totals are that
  day's; another day's corpus would move them. The test that pins this file checks it against the
  committed snapshot, never against a live count.
- **No full re-classification.** The strict map's 50 records were classified A/B/C/D/X by hand. This
  run does not repeat that over the 50 widened records; it re-runs the specific test the item asked
  for (the cell) and reads the chronic-pain-naming records. Any reader who wants the widened window
  classed by population would have to do that reading; it is not done here, and it is not claimed.
- The cell probe is a conjunction of index terms, not a semantic search. A record that measures
  retention against pain but never uses one of the probe's words would be invisible to it — the same
  limit the strict map stated, and the reason the probe uses MeSH *and* free text.
- Nothing here is clinical advice, and no patient-backed claim is made.

## Next action (set 2026-10-08)

Do **not** widen the item-24 search again: it was tried, it tripled the noise, and it pushed both of
the item's actual records (34403125, 36069812) below the reachable window while the retention cell
stayed empty. The honest output of item 24 is the negative map: a named, reproducible gap. The one
remaining step is to read the two subject-matter records (34403125, 36069812) in full — abstract
reading already finds them, so this is only worth doing with full-text access. If no access exists,
the item is complete as the negative map and should be marked so, not re-searched.

*Pinned by `tests/test_maternal_pain_wide.py` (offline): it re-checks that the queries printed above
are the script's, that the snapshot and this file agree on the totals and rows, and that the two
cell records and the two displaced records are the ones named.*
