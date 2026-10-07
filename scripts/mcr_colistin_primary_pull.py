#!/usr/bin/env python3
"""Primary-study pull behind the eight MCR rows that matter most — agenda item 23.

Written 2026-10-07 (Desi, clock wake). This is the item's own next action, from
`research/mcr-colistin-seed.md` §5:

    "Pull the primary studies for the rows where the harmonisation variables matter most
     -- the six largest by N (rows 13, 17a, 28, 1, 6, 19) plus the two anomalous rows --
     and record year, variant, detection method and sampling design from each."

The seed supplies only 4 of the item's 9 harmonisation columns (sector, country, numerator,
denominator). Collection year, mcr variant, detection method, sampling design and host/sample
detail are absent, and they are exactly the ones the item's question turns on: a country doing
molecular surveillance on raw meat will out-report a country doing phenotypic screening on
clinical isolates for reasons that have nothing to do with resistance. So the confounders have
to be read off the primary papers, not the review.

WHAT THIS SCRIPT DOES, AND WHAT IT DOES NOT. It fetches the six primary records behind the
target rows and stores the raw PubMed record (title, year, journal, abstract, MeSH,
publication types). It does **not** extract the four columns — that is a hand-read, because a
term match is not an outcome and the whole point of the exercise is the reading. The extraction
is written up in `research/mcr-colistin-primary-studies.md`.

The two anomalous rows (17a Germany printed 10.42% where 709/6158 = 11.51%; 17h Spain and 17i
Portugal byte-identical at 28 isolates / 17 positive) share one reference, [39] Ewers et al.
2022, so that single record covers row 17a and both members of the anomaly.

Usage:
    python3 scripts/mcr_colistin_primary_pull.py            # fetch, write raw json
    python3 scripts/mcr_colistin_primary_pull.py --no-fetch  # re-read the stored file
"""

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402  (shared efetch/parse_records)

RAW = ROOT / "research" / "mcr-colistin-primary-raw.json"

# row -> (seed row label, country/sector, N, ref number, PMID). The six largest by N, plus the
# anomalous row 17a (already largest after 13) and its siblings; 17h/17i share the same source.
TARGETS = [
    {"seed_rows": ["13"],     "label": "Japan, livestock",   "n": 9306, "ref": 35, "pmid": "27855068"},
    {"seed_rows": ["17a"],    "label": "Germany, livestock", "n": 6158, "ref": 39, "pmid": "36569100"},
    {"seed_rows": ["28"],     "label": "Canada, human",      "n": 5571, "ref": 47, "pmid": "28018876"},
    {"seed_rows": ["1"],      "label": "China, mixed",       "n": 2649, "ref": 15, "pmid": "26603172"},
    {"seed_rows": ["6"],      "label": "China, livestock",   "n": 2330, "ref": 29, "pmid": "28056227"},
    {"seed_rows": ["19"],     "label": "France, livestock",  "n": 1701, "ref": 41, "pmid": "36687643"},
]


def fetch():
    out = {}
    for t in TARGETS:
        for attempt in range(3):
            try:
                recs = aps.parse_records(aps.efetch([t["pmid"]]))
                break
            except Exception as exc:  # transient upstream; retry, then fail loudly
                if attempt == 2:
                    raise
                print(f"  efetch retry {attempt + 1} for {t['pmid']}: {exc}", file=sys.stderr)
                time.sleep(2 * (attempt + 1))
        out[t["pmid"]] = recs[0] if recs else None
        time.sleep(0.4)
    return out


def build():
    recs = fetch()
    rows = []
    for t in TARGETS:
        rec = recs.get(t["pmid"])
        rows.append({
            "seed_rows": t["seed_rows"],
            "seed_label": t["label"],
            "seed_n": t["n"],
            "seed_ref": t["ref"],
            "pmid": t["pmid"],
            "found": rec is not None,
            "title": (rec or {}).get("title"),
            "year": (rec or {}).get("year"),
            "journal": (rec or {}).get("journal"),
            "publication_types": (rec or {}).get("publication_types"),
            "mesh": (rec or {}).get("mesh"),
            "abstract_plain": (rec or {}).get("abstract_plain"),
        })
    return {
        "generated": date.today().isoformat(),
        "source": "PubMed E-utilities (efetch, rettype=abstract)",
        "agenda_item": "23",
        "what": "primary records behind the seed's six largest-N rows and its anomalous rows",
        "targets": rows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fetch", action="store_true", help="re-read the stored file, no network")
    args = ap.parse_args()

    if args.no_fetch:
        rec = json.loads(RAW.read_text())
    else:
        rec = build()
        RAW.parent.mkdir(parents=True, exist_ok=True)
        RAW.write_text(json.dumps(rec, indent=1) + "\n")

    n_ok = sum(1 for r in rec["targets"] if r["found"])
    print(f"{RAW.relative_to(ROOT)}: {n_ok}/{len(rec['targets'])} target records present")
    for r in rec["targets"]:
        flag = "ok " if r["found"] else "MISSING"
        print(f"  [{flag}] row(s) {','.join(r['seed_rows']):>4}  PMID {r['pmid']}  "
              f"{r['year']}  {(r['title'] or '')[:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
