#!/usr/bin/env python3
"""Filtered *second-population* arm for agenda item 32 (affective pain neuromodulation).

Written 2026-10-10 (Desi, clock wake). This is the item's own wake-takeable next action, step 3
of the note in `agenda/32-affective-pain-neuromodulation-evidence-map.md`:

    "(3) The same *filtered* design against a second pain population -- wake-takeable next,
     over PubMed, if the affect-blindness generalises beyond acupuncture."

What it reuses, and what it changes. The *filtered design* is the one in
`scripts/affective_pain_acupuncture_filtered.py`: instead of keeping the top-N matches by a
relevance ranking the reader cannot inspect, the query **names the measurement** (fMRI OR EEG OR
HRV OR autonomic ...), so every record returned is already measurement-rich and the count is a
census of that sub-literature rather than a sample of everything. That filter is imported
verbatim from the acupuncture arm, so the two arms cannot drift apart.

The one thing that changes is the population. The acupuncture arm is an *intervention* arm
(`acupuncture AND measurement AND PAIN`); this arm is a *population* arm. It asks the same
question of a second chronic-pain population with no intervention restriction, so the question
tested is "do measurement-rich studies of this population measure mood?" and not "do acupuncture
studies?".

Why fibromyalgia. It is the chronic-pain population in which the affective burden is least
optional: depression, anxiety and pain catastrophising are clinical comorbidities of the
diagnosis and feature in its own diagnostic literature. If the affect column is *still* missing
in the measurement-rich fibromyalgia corpus, the blindness §8 found in the acupuncture arm is a
property of how chronic pain is measured, not a quirk of one intervention's literature. A
population in which mood is already partly diagnostic is the hardest case for the finding and the
fairest test of it.

WHAT THIS IS NOT. The same keyword screen as every other arm, not a reading. A term in an
abstract is not an outcome; the flags store the sentence that set them and the human-primary
records that set a flag are hand-read in the evidence map before any claim rests on them.

Usage:
    python3 scripts/affective_pain_second_population_filtered.py            # fetch, write raw
    python3 scripts/affective_pain_second_population_filtered.py --no-fetch # re-tag offline
"""

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402
from affective_pain_acupuncture_filtered import MEASUREMENT  # noqa: E402  (same filter, one source)

RAW = ROOT / "research" / "affective-pain-neuromodulation-second-population-filtered-raw.json"

ARM = "fibromyalgia_filtered"

# The second pain population, defined by the condition and not by an intervention.
POPULATION = (
    '(fibromyalgia[tiab] OR fibromyalgia[MeSH Terms] OR "fibromyalgia syndrome"[tiab] '
    'OR fibromyalgias[tiab])'
)

QUERY = f"{POPULATION} AND {MEASUREMENT} AND humans[MeSH Terms]"

# A census needs a fetch ceiling as a safety valve, not as a plan. If the filtered query outgrows
# this, the run records `censored: true` and the map must say so.
FETCH_LIMIT = 2000
PAGE = 200


def fetch_all(pmids):
    out = []
    for i in range(0, len(pmids), PAGE):
        chunk = pmids[i:i + PAGE]
        for attempt in range(3):
            try:
                out.extend(aps.parse_records(aps.efetch(chunk)))
                break
            except Exception as exc:  # transient upstream; retry, then fail loudly
                if attempt == 2:
                    raise
                print(f"  efetch retry {attempt + 1} for chunk {i}: {exc}", file=sys.stderr)
                time.sleep(2 * (attempt + 1))
        time.sleep(0.4)
    return out


def build(snapshot_end):
    res = aps.esearch(QUERY, retmax=FETCH_LIMIT, date_from="2015-01-01", date_to=snapshot_end)
    pmids = res["pmids"]

    recs = fetch_all(pmids)
    for r in recs:
        r["arm"] = ARM
        r.update(aps.classify(r))
        r.update(aps.classify_subject(r))
        r["co_mention_sentence"] = aps.same_sentence_affective_and_biomarker(r)

    return {
        "generated": date.today().isoformat(),
        "source": "PubMed E-utilities (esearch + efetch), filtered second-population arm",
        "arms": {ARM: {
            "query": QUERY,
            "filter": MEASUREMENT,
            "population": POPULATION,
            "total_matching": res["count"],
            "fetched": len(pmids),
            "censored": res["count"] > len(pmids),
            "pmids": pmids,
            "query_translation": res["query_translation"],
        }},
        "records": recs,
        "tallies": aps.tally(recs),
    }


def retag(record):
    record["records"] = [dict(r, **aps.classify(r), **aps.classify_subject(r))
                         for r in record["records"]]
    record["tallies"] = aps.tally(record["records"])
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fetch", action="store_true", help="re-tag the stored record offline")
    ap.add_argument("--snapshot-end", default=date.today().isoformat(),
                    help="latest publication date included (YYYY-MM-DD)")
    args = ap.parse_args()

    record = retag(json.loads(RAW.read_text())) if args.no_fetch else build(args.snapshot_end)

    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(record, indent=1) + "\n")

    a = record["arms"][ARM]
    t = record["tallies"]
    print(f"wrote {RAW.relative_to(ROOT)}")
    print(f"  query: {a['total_matching']} matching, {a['fetched']} fetched"
          f"{'  (CENSORED)' if a['censored'] else '  (census)'}")
    print(f"  records            : {t['n_records']}")
    print(f"  review/protocol    : {t['n_review']}/{t['n_protocol']}")
    print(f"  animal-subject     : {t['n_animal_subject']}")
    print(f"  human primary      : {t['n_human_primary']}")
    print(f"  affective term     : {t['n_affective_outcome']}")
    print(f"  biomarker term     : {t['n_neural_or_autonomic_biomarker']}")
    print(f"  both               : {t['n_both_affective_and_biomarker']}")
    print(f"  neither            : {t['n_neither']}")
    hp_both = sorted(r["pmid"] for r in record["records"]
                     if r["is_human_primary"] and r["both_affective_and_biomarker"])
    print(f"  human-primary both : {len(hp_both)} -> {hp_both}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
