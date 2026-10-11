#!/usr/bin/env python3
"""Second-pain-population arm for agenda item 32 (affective pain neuromodulation).

Written 2026-10-11 (Dmitri, clock wake). This is step 3 of the item's own next action, set
out in `research/affective-pain-neuromodulation-evidence-map.md`:

    "(3) The same *filtered* design against a second pain population -- wake-takeable next,
     over PubMed, if the affect-blindness generalises beyond acupuncture."

WHY A SECOND POPULATION. Section 8 of the map sharpened the finding to "*the brain and the
pain, but not the mood*": of the 16 human-primary records in the filtered acupuncture census
that named a brain or autonomic measure but no affect term, 15 named no affect term at all.
That finding is measured inside a corpus whose pain block is *chronic pain, fibromyalgia,
somatoform / somatic symptom, persistent pain, chronic widespread pain, medically
unexplained*. Every population the claim rests on is a pain *without a known lesion* -- a
nociplastic-pain corpus. If the omission is a property of that population's literature
(say, the way nociplastic-pain trials are designed) rather than of acupuncture research in
general, the claim does not generalise and section 8's wording is one population too wide.

The test this file runs is not "a second intervention" -- the VNS filtered arm
(`scripts/affective_pain_vns_filtered.py`, 31 records, 20 human-primary) already tests
*beyond acupuncture on the same population*. This file holds the intervention and the
measurement filter fixed and swaps the **population**: **migraine** (and, in the strict
query below, only migraine) instead of the nociplastic-chronic-pain block.

WHY MIGRAINE. (1) It is a single, clinically distinct chronic-pain diagnosis with its own
literature, not a widening of the existing pain block. (2) It is the pain population in
which an affective comorbidity (anxiety, depression) is most established, so the test is
*not* stacked in advance: if acupuncture trials measure mood anywhere, migraine is where
they should. (3) The filtered query is a comparable size (see the run), so the two censuses
can be read side by side rather than one being a handful of papers.

WHAT IS HELD FIXED, so the comparison is a comparison. Same measurement filter (a brain or
autonomic measurement named in the title/abstract -- imported, not re-typed, from
`scripts/affective_pain_acupuncture_filtered.py`), same intervention block (imported, not
re-typed, from `scripts/affective_pain_search.py`), same `humans[MeSH Terms]` term, same
publication window start, same classifier, same subject classifier, same affect/index term
lists. The only thing that changes is the population block.

WHAT THIS IS NOT. It is the same keyword screen as the other arms, not a reading. A term in
an abstract is not an outcome; every flag stores the sentence that set it, and the
human-primary records that set both flags are hand-read in the evidence map before any claim
rests on them. The affect flags in particular are a *keyword* scan, so "names no affect term"
means those words are absent, not that no mood was measured.

Usage:
    python3 scripts/affective_pain_migraine_filtered.py              # fetch, write raw
    python3 scripts/affective_pain_migraine_filtered.py --no-fetch   # re-tag offline
"""

import argparse
import importlib.util
import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402


def _load_acupuncture_filter():
    """Import the acupuncture filtered arm to *reuse* its filter string, not re-type it.

    A re-typed filter would drift, and then the two censuses would no longer be countable
    against each other -- which is the only thing that makes this a test of generalisation.
    """
    spec = importlib.util.spec_from_file_location(
        "affective_pain_acupuncture_filter",
        ROOT / "scripts" / "affective_pain_acupuncture_filtered.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_ACUPUNCTURE = _load_acupuncture_filter()
MEASUREMENT = _ACUPUNCTURE.MEASUREMENT

RAW = ROOT / "research" / "affective-pain-neuromodulation-migraine-filtered-raw.json"

ARM = "acupuncture_migraine_filtered"

# The second pain population. Strict on purpose: `migraine[tiab]` or the MeSH heading,
# nothing else -- so a record here is a migraine study, and the arm cannot grow by
# absorbing tension-type or medication-overuse headache papers the way a bare `headache`
# term would. The chronic-pain block of `affective_pain_search.PAIN` is NOT added, so a
# record with both a migraine term and a "chronic pain" mention is still included, but a
# record with only a generic chronic-pain mention is not: the population is the selector.
POPULATION = '(migraine[tiab] OR "migraine disorders"[MeSH Terms])'

QUERY = f"{aps.ARMS['acupuncture']} AND {MEASUREMENT} AND {POPULATION} AND humans[MeSH Terms]"

# A census needs a fetch ceiling as a safety valve, not as a plan. If the filtered query
# ever outgrows this, the run records `censored: true` and the map must say so.
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
        "source": "PubMed E-utilities (esearch + efetch), filtered acupuncture+ migraine arm",
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
    hp_bio_only = sorted(r["pmid"] for r in record["records"]
                         if r["is_human_primary"] and r["neural_or_autonomic_biomarker"]
                         and not r["affective_outcome"])
    print(f"  human-primary both : {len(hp_both)} -> {hp_both}")
    print(f"  human-primary bio-only: {len(hp_bio_only)} -> {hp_bio_only}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
