#!/usr/bin/env python3
"""Confound arm for agenda item 32 (affective pain neuromodulation).

Written 2026-10-14 (Desi, clock wake). This is the step §9 named and §10 sharpened: run the
*same* filtered design over the **low-back-pain population restricted to acupuncture**, so
that population and intervention are held fixed at once and the 24%-vs-46% gap between §7 and
§9 can be attributed to one of them rather than left to two.

What it holds fixed, and against what. §7's acupuncture arm is

    acupuncture block  AND  MEASUREMENT  AND  PAIN          AND humans[MeSH Terms]

and §9's low-back-pain arm is

    low_back_pain block  AND  MEASUREMENT  AND  humans[MeSH Terms]

— identical except that §9 dropped the **intervention** block and §7's population is the
generic PAIN block rather than the named LBP one. This arm is the intersection:

    low_back_pain block  AND  acupuncture block  AND  MEASUREMENT  AND humans[MeSH Terms]

so a record here is in both §7's and §9's worlds: it is a low-back-pain study *and* an
acupuncture study, measured with the same filter. Every block is imported, none re-typed:
the acupuncture block is `aps.ARMS['acupuncture']`, the measurement filter is
`apf.MEASUREMENT` (the step-2 filter both §7 and §9 already share), the population block is
`asp.POPULATIONS['low_back_pain']` (§9's own), and the classifier is `aps.classify` /
`aps.classify_subject`. If any of those is edited, this arm changes with it -- there is no
second copy to drift.

WHAT THIS IS NOT. It is the same keyword screen as the other arms, not a reading. A term in
an abstract is not an outcome; every flag stores the sentence that set it.

Usage:
    python3 scripts/affective_pain_confound_arm.py              # fetch, write raw
    python3 scripts/affective_pain_confound_arm.py --no-fetch   # re-tag offline
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
import affective_pain_acupuncture_filtered as apf  # noqa: E402
import affective_pain_second_population as asp  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-confound-arm-raw.json"

ARM = "low_back_pain_acupuncture_filtered"
POPULATION = "low_back_pain"
POPULATION_BLOCK = asp.POPULATIONS[POPULATION]

# Both fixed: the population block (§9's) AND the intervention block (§7's) AND the same
# measurement filter AND humans. Only the *generic* PAIN block is absent, because the named
# population block stands in for it -- exactly as §9 replaced it.
QUERY = (f"{POPULATION_BLOCK} AND {aps.ARMS['acupuncture']} "
         f"AND {apf.MEASUREMENT} AND humans[MeSH Terms]")

FETCH_LIMIT = apf.FETCH_LIMIT
PAGE = 200


def fetch_all(pmids):
    out = []
    for i in range(0, len(pmids), PAGE):
        chunk = pmids[i:i + PAGE]
        for attempt in range(4):
            try:
                out.extend(aps.parse_records(aps.efetch(chunk)))
                break
            except Exception as exc:  # transient upstream (incl. HTTP 429); retry, then fail loud
                if attempt == 3:
                    raise
                print(f"  efetch retry {attempt + 1} for chunk {i}: {exc}", file=sys.stderr)
                time.sleep(3 * (attempt + 1))
        time.sleep(1.0)
    return out


def search(term, snapshot_end):
    for attempt in range(4):
        try:
            return aps.esearch(term, retmax=FETCH_LIMIT,
                               date_from="2015-01-01", date_to=snapshot_end)
        except Exception as exc:
            if attempt == 3:
                raise
            print(f"  esearch retry {attempt + 1}: {exc}", file=sys.stderr)
            time.sleep(3 * (attempt + 1))


def build(snapshot_end):
    res = search(QUERY, snapshot_end)
    pmids = res["pmids"]

    recs = fetch_all(pmids)
    for r in recs:
        r["arm"] = ARM
        r.update(aps.classify(r))
        r.update(aps.classify_subject(r))
        r["co_mention_sentence"] = aps.same_sentence_affective_and_biomarker(r)

    return {
        "generated": date.today().isoformat(),
        "source": "PubMed E-utilities (esearch + efetch), low-back-pain x acupuncture confound arm",
        "arms": {ARM: {
            "query": QUERY,
            "population": POPULATION,
            "population_block": POPULATION_BLOCK,
            "intervention_block": aps.ARMS["acupuncture"],
            "filter": apf.MEASUREMENT,
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
