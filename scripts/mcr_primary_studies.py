#!/usr/bin/env python3
"""Fetch the primary studies behind the eight key rows of the MCR colistin seed table.

Agenda item 23 (MCR Colistin Resistance Evidence Map). The seed review
(Joy et al., Public Health Challenges 2026;5(3):e70376, PMID 42750694) prints only four of the
nine harmonisation columns the item asks for: sector, country, denominator, numerator. The item's
next action is to recover the missing columns -- collection year, mcr variant, detection method,
sampling design -- from the primary papers behind the rows where they matter most: the six largest
by N (rows 1, 6, 13, 17a, 19, 28) and the two rows the seed prints inconsistently (17a, and the
byte-identical Spain/Portugal pair 17h/17i, which are sub-rows of the same primary paper).

This script fetches each primary paper's Europe PMC `core` record (title, journal, year, authors,
DOI, PMCID, abstract, publication types) and writes it verbatim to
`research/mcr-primary-studies-raw.json`. It does NOT classify the papers -- the four missing columns
are hand-read from the stored abstract and pinned separately, because "detection method" and
"sampling design" are judgements about text, not strings a lookup can return.

Query recorded for reproducibility: Europe PMC REST `search`, one `EXT_ID:<pmid>` request per paper,
`resultType=core`, `format=json`. The PMID set is the seed table's own reference numbers, mapped by
hand from `research/mcr-colistin-seed.json` (each row already carries its reference string and PMID).

Run: python3 scripts/mcr_primary_studies.py
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "mcr-primary-studies-raw.json"

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UA = "llm-symposium-mcr-evidence-map/1.0 (research; contact via github.com/LindsayRidgeway/llm-symposium)"

# The seed table's key rows -> primary study. `row` is the seed's own row label; `pmid` is the
# PMID printed in that row's reference string (research/mcr-colistin-seed.json). Row 17a and the
# anomalous pair 17h/17i share one primary paper (Ewers et al. 2022, the multi-country porcine
# study the review split into eleven sub-rows).
TARGETS = [
    {"row": "1",   "pmid": "26603172", "why": "largest N overall; multi-sector China (raw meat, livestock, human)"},
    {"row": "6",   "pmid": "28056227", "why": "largest livestock N in China; isolates AND faecal samples"},
    {"row": "13",  "pmid": "27855068", "why": "largest single-country N (Japan, healthy food-producing animals)"},
    {"row": "17a", "pmid": "36569100", "why": "row the seed prints inconsistently (709/6158=11.51%, not 10.42%)"},
    {"row": "17h/17i", "pmid": "36569100", "why": "byte-identical Spain/Portugal sub-rows; same primary paper"},
    {"row": "19",  "pmid": "36687643", "why": "large French livestock N (goats)"},
    {"row": "28",  "pmid": "28018876", "why": "largest human N (Canada, hospital isolates)"},
]


def fetch_core(pmid: str) -> dict:
    q = urllib.parse.urlencode(
        {"query": f"EXT_ID:{pmid}", "format": "json", "resultType": "core"}
    )
    req = urllib.request.Request(f"{EPMC}?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as fh:
        payload = json.load(fh)
    results = payload.get("resultList", {}).get("result", [])
    if not results:
        raise SystemExit(f"no Europe PMC record for PMID {pmid}")
    return results[0]


def main() -> int:
    fetched: dict[str, dict] = {}
    records = []
    for t in TARGETS:
        pmid = t["pmid"]
        if pmid not in fetched:
            fetched[pmid] = fetch_core(pmid)
        r = fetched[pmid]
        records.append(
            {
                "row": t["row"],
                "why": t["why"],
                "pmid": pmid,
                "doi": r.get("doi"),
                "pmcid": r.get("pmcid"),
                "title": r.get("title"),
                "authorString": r.get("authorString"),
                "journal": (r.get("journalInfo", {}) or {}).get("journal", {}).get("title"),
                "year": r.get("pubYear"),
                "pubType": r.get("pubTypeList", {}).get("pubType", []),
                "isOpenAccess": r.get("isOpenAccess"),
                "inEPMC": r.get("inEPMC"),
                "abstract": r.get("abstractText"),
            }
        )
    OUT.write_text(
        json.dumps(
            {
                "artifact": "mcr-primary-studies-raw",
                "agenda_item": 23,
                "source_api": EPMC,
                "result_type": "core",
                "note": (
                    "Verbatim Europe PMC core records for the primary papers behind the eight key "
                    "rows of research/mcr-colistin-seed.json. The four missing harmonisation "
                    "columns are hand-read from these abstracts and pinned in "
                    "tests/test_mcr_primary_studies.py, not extracted here."
                ),
                "records": records,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT} ({len(records)} row-targets, {len(fetched)} distinct papers)")
    for rec in records:
        print(f"  row {rec['row']:<7} PMID {rec['pmid']}  {rec['year']}  {rec['title'][:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
