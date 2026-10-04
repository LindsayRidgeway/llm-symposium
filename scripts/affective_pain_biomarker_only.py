#!/usr/bin/env python3
"""Biomarker-only human-primary records in the filtered acupuncture arm — agenda item 32, §6 step (2).

Written 2026-10-04 (Desi, clock wake). §7 of
`research/affective-pain-neuromodulation-evidence-map.md` corrected §4 and hand-read the
five human-primary records that set *both* the affective and the biomarker flag. §6 step
(2) names the other half, left open by §7:

    "classify the 16 human-primary filtered-arm records that set the biomarker flag only
     (no affective outcome) — are they mechanistic neuroimaging with no clinical affective
     outcome, and does that hold across the arm? ... it is a table over records already on
     disk."

This script is the reproducible half. The 16 are *selected* mechanically from the stored
census (`is_human_primary` and biomarker flag set and affective flag clear). The category
of each is a **hand reading** of the abstract — a term in an abstract is not an outcome
(the §2 caveat) — but the hand verdicts are recorded here as data, keyed by PMID, so the
reading is auditable rather than asserted, and two parts are re-checked by machine so a
reader need not take the reading on trust:

  * the selection (which 16), re-derived from the raw JSON; and
  * a **widened** affectivity net (`quality of life`, `mental`, `sf-36`, `well-being`, …),
    which tests whether the item's own affective term list is simply missing vocabulary.
    If a record carries a patient-centred emotional/quality-of-life outcome phrased in
    words the list does not hold, the list cannot see it — and that is a defect in the
    screen, not a finding about the literature.

WHAT THIS IS NOT. A verdict here is a claim about what the *abstract* reports, not about
the study. Several of these trials measure patient-reported instruments (BPI, WOMAC,
SF-36) whose subscales are affective; the abstract names the instrument, not the subscale,
so the reading credits only what the text says.

Usage:
    python3 scripts/affective_pain_biomarker_only.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RAW = ROOT / "research" / "affective-pain-neuromodulation-acupuncture-filtered-raw.json"

# --- the widened net -------------------------------------------------------------------
# The item's AFFECTIVE_TERMS (scripts/affective_pain_search.py) are emotion words. This is
# the affect-adjacent, patient-centred vocabulary the same abstracts use instead, and which
# that list therefore cannot catch. Kept to outcomes a patient would recognise as "how I
# feel", not to function words like "function".
WIDENED_AFFECTIVE = [
    "quality of life", "health-related quality", "mental", "sf-36", "sf36",
    "well-being", "wellbeing",
]

_CAT_LABEL = {
    "M": "mechanistic — a brain or autonomic signal is the readout",
    "C": "clinical trial — a pain-intensity / function outcome; imaging or autonomic secondary",
    "R": "mapping / meta-analytic method paper — not a primary patient study",
    "X": "not an acupuncture-intervention study",
}

# Hand verdicts, keyed by PMID. `note` is the sentence of evidence the verdict rests on.
VERDICTS = {
    "27741200": dict(cat="C",
                     note="RCT; primary outcome is brain connectivity (fMRI), but prespecified "
                          "secondary outcomes include physical AND mental quality of life — a "
                          "patient-centred affective outcome the term list cannot see."),
    "29325883": dict(cat="M",
                     note="fMRI expectancy / placebo study, verum vs sham electroacupuncture in knee "
                          "OA; readout is pain experience + brain activity, no affective scale."),
    "30137262": dict(cat="M",
                     note="real vs imagined acupuncture in healthy subjects, fMRI + pain threshold; "
                          "mechanism, no patient affective outcome."),
    "31176295": dict(cat="M",
                     note="resting-state FC predicting response to real/sham acupuncture in cLBP; "
                          "predictive biomarker, readout is pain reduction."),
    "31521794": dict(cat="C",
                     note="randomised crossover dental-pain model (healthy men); pain intensity + "
                          "autonomic responses (EDA, HRV), no affective scale."),
    "31922698": dict(cat="M",
                     note="resting-state FC in nonacute sciatica; readout is connectivity + sciatica "
                          "duration, no affective scale."),
    "31964691": dict(cat="M",
                     note="fMRI neural marker for migraine without aura; readout is marker accuracy "
                          "+ headache frequency."),
    "32377180": dict(cat="M",
                     note="degree-centrality changes after contralateral vs ipsilateral needling in "
                          "chronic shoulder pain; readout is connectivity + function."),
    "33314799": dict(cat="C",
                     note="randomised neuroimaging trial, fibromyalgia, EA vs mock laser; outcome is "
                          "BPI pain severity + connectivity + insular GABA — BPI is named, its "
                          "affective subscale is not."),
    "35633164": dict(cat="R",
                     note="scalp-stimulation targets from large-scale meta-analyses + 10-20 EEG; a "
                          "mapping method, not a patient study."),
    "38897810": dict(cat="R",
                     note="scalp acupuncture targets derived from Neurosynth neuroimaging "
                          "meta-analyses; a mapping method, not a patient study."),
    "39089662": dict(cat="C",
                     note="chronic sciatica, acupuncture vs sham; outcomes are VAS leg pain + ODI + "
                          "rs-fMRI, no affective scale."),
    "40634927": dict(cat="C",
                     note="three-armed randomised fMRI trial, knee OA; outcomes are NRS + WOMAC + "
                          "imaging, no affective scale."),
    "41086064": dict(cat="M",
                     note="resting EEG before/during/after cheek acupuncture in chronic pain; "
                          "readout is brain oscillations, no affective scale."),
    "41830820": dict(cat="C",
                     note="AcuENDO sub-study, endometriosis; outcomes are daily pain ratings + EEG, "
                          "no affective scale; control group omitted."),
    "42309066": dict(cat="X",
                     note="corticospinal fMRI model for pain perception — not an acupuncture "
                          "intervention study; it entered via the filter's biomarker text, and "
                          "reports pain intensity, not affect."),
}


def biomarker_only(records):
    """The 16: human-primary records with the biomarker flag set and the affective flag clear."""
    return sorted(
        (r for r in records
         if r.get("is_human_primary")
         and r.get("neural_or_autonomic_biomarker")
         and not r.get("affective_outcome")),
        key=lambda r: r["pmid"],
    )


def widened_hits(record):
    """Widened affectivity terms the item's own affective list cannot match."""
    text = record.get("abstract_plain", "") or ""
    return [t for t in WIDENED_AFFECTIVE if re.search(r"\b" + re.escape(t), text, re.I)]


def load():
    return json.loads(RAW.read_text())


def main():
    raw = load()
    rows = biomarker_only(raw["records"])

    missing = [r["pmid"] for r in rows if r["pmid"] not in VERDICTS]
    if missing:
        print(f"ERROR: {len(missing)} biomarker-only records have no hand verdict: {missing}",
              file=sys.stderr)
        return 2

    print(f"biomarker-only human-primary records: {len(rows)}")
    by_cat = {}
    for r in rows:
        by_cat.setdefault(VERDICTS[r["pmid"]]["cat"], []).append(r["pmid"])
    for cat in ("M", "C", "R", "X"):
        pmids = by_cat.get(cat, [])
        print(f"  {cat} ({_CAT_LABEL[cat]}): {len(pmids)}  {pmids}")

    widened = [(r["pmid"], widened_hits(r)) for r in rows if widened_hits(r)]
    print(f"widened-net re-tags: {len(widened)}  {widened}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
