#!/usr/bin/env python3
"""Second-population arm for agenda item 32 (affective pain neuromodulation).

Written 2026-10-08 (Dmitri, clock wake). This is step 3 of the item's own next action, set
out in `research/affective-pain-neuromodulation-evidence-map.md`:

    "The same *filtered* design against a second pain population -- wake-takeable next,
     over PubMed, if the affect-blindness generalises beyond acupuncture."

What "the same filtered design" means here, stated so a reader can audit the choice.
`scripts/affective_pain_acupuncture_filtered.py` (step 2) built its census from:

    acupuncture block  AND  MEASUREMENT  AND  pain block  AND  humans[MeSH Terms]

where MEASUREMENT is a query that *names* a brain or autonomic measurement (fMRI, EEG,
HRV, autonomic, insula, amygdala, brainstem, ...). §8 of the map found that census is not
blind to pain (12 of its 16 biomarker-only records name a pain instrument) but is blind to
mood (15 of 16 name no affect term) -- *the brain and the pain, but not the mood*.

Step 3 asks whether that blindness survives a change of population. Two readings of "second
pain population" are possible, and the choice is recorded rather than hidden:

  (A) swap the pain block for a *named* condition, keeping the measurement filter; or
  (B) drop the intervention block and keep the original pain block.

This script takes reading (A) and names the population **chronic low back pain**: the most
common chronic pain condition, and clinically distinct from the fibromyalgia / somatoform
cluster that carries every both-flag record in the original two arms. Reading (B) -- the
whole chronic-pain measurement literature with the acupuncture block removed -- was measured
at 2,200 matches and is recorded in the map as the larger, unbounded alternative, not run
here. The measurement filter is imported unchanged from the step-2 script, so there is no
second copy of it to drift; if that filter is edited, this arm changes with it.

WHAT THIS IS NOT. It is the same keyword screen as the other arms, not a reading. A term in
an abstract is not an outcome; every flag stores the sentence that set it.

Usage:
    python3 scripts/affective_pain_second_population.py              # fetch, write raw
    python3 scripts/affective_pain_second_population.py --no-fetch   # re-tag offline
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
import affective_pain_acupuncture_filtered as af  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-second-population-raw.json"

# The population blocks this arm can census. Only one is run by default; each is a pain
# population *named by the paper*, in the same tiab style as the original pain block.
POPULATIONS = {
    "low_back_pain": (
        '("chronic low back pain"[tiab] OR "persistent low back pain"[tiab] '
        'OR "non-specific low back pain"[tiab] OR "nonspecific low back pain"[tiab])'
    ),
}

ARM = "low_back_pain_filtered"
# The measurement filter is the step-2 one, imported, not re-typed. The population block is
# the only thing that differs from the acupuncture arm.
QUERY = f"{POPULATIONS['low_back_pain']} AND {af.MEASUREMENT} AND humans[MeSH Terms]"

# A census needs a fetch ceiling as a safety valve, not as a plan.
FETCH_LIMIT = 2000
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


def build(snapshot_end, population):
    term = f"{POPULATIONS[population]} AND {af.MEASUREMENT} AND humans[MeSH Terms]"
    res = search(term, snapshot_end)
    pmids = res["pmids"]

    recs = fetch_all(pmids)
    for r in recs:
        r["arm"] = ARM
        r.update(aps.classify(r))
        r.update(aps.classify_subject(r))
        r["co_mention_sentence"] = aps.same_sentence_affective_and_biomarker(r)

    return {
        "generated": date.today().isoformat(),
        "source": "PubMed E-utilities (esearch + efetch), second-population filtered arm",
        "arms": {ARM: {
            "query": term,
            "population": population,
            "population_block": POPULATIONS[population],
            "filter": af.MEASUREMENT,
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
    ap.add_argument("--population", default="low_back_pain", choices=list(POPULATIONS))
    ap.add_argument("--snapshot-end", default=date.today().isoformat(),
                    help="latest publication date included (YYYY-MM-DD)")
    args = ap.parse_args()

    record = retag(json.loads(RAW.read_text())) if args.no_fetch else build(args.snapshot_end, args.population)

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
