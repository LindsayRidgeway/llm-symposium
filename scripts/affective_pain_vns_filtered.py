#!/usr/bin/env python3
"""Filtered vagus-nerve-stimulation arm for agenda item 32 (affective pain neuromodulation).

Written 2026-10-07 (Desi, clock wake). This is step 3 of the item's own next action, set
out in `research/affective-pain-neuromodulation-evidence-map.md` §8:

    "(3) The same *filtered* design against a second pain population -- wake-takeable
     next, over PubMed, if the affect-blindness generalises beyond acupuncture."

Why VNS and not a second patient group. The item's research question names *two*
interventions -- acupuncture and vagus-nerve stimulation -- and asks whether they act
through a shared brainstem-limbic pathway. §7 ran the acupuncture arm as a filtered
census and found the corpus measures the brain and the pain but not the mood (§8). The
open question is whether that affect-blindness is a property of *acupuncture* studies or
of the pain-neuromodulation literature the item is about. The second intervention the item
itself names is the honest test of "beyond acupuncture", so this script runs the VNS arm
through the identical filter and classifier. (Read literally, step 3 says "a second pain
population"; VNS studies in chronic pain are a distinct population *and* the item's second
intervention, so the same run answers both readings. Recorded in §9, not hidden.)

WHAT THIS IS NOT. Same caveat as the acupuncture arm: it is the keyword screen of §2, not a
reading. Every flag stores the sentence that set it, and the human-primary records that set
both flags are hand-read in the map before a claim rests on them.

The measurement filter is imported from `affective_pain_acupuncture_filtered` so the two
arms cannot drift apart: a difference between them is a difference in the papers, not in
the query.

Usage:
    python3 scripts/affective_pain_vns_filtered.py              # fetch, write raw
    python3 scripts/affective_pain_vns_filtered.py --no-fetch   # re-tag offline
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

RAW = ROOT / "research" / "affective-pain-neuromodulation-vns-filtered-raw.json"

ARM = "vns_filtered"

# The identical filter step 2 of §6 named, imported so the two arms stay comparable.
MEASUREMENT = apf.MEASUREMENT

QUERY = f"{aps.ARMS['vns']} AND {MEASUREMENT} AND {aps.PAIN} AND humans[MeSH Terms]"

# A census needs a fetch ceiling as a safety valve, not as a plan.
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
        time.sleep(0.6)
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
        "source": "PubMed E-utilities (esearch + efetch), filtered VNS arm",
        "arms": {ARM: {
            "query": QUERY,
            "filter": MEASUREMENT,
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
