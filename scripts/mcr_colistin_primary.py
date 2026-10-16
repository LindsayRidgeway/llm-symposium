#!/usr/bin/env python3
# Owner: Desi
"""Pull the primary studies behind the heaviest rows of the mcr-colistin seed table.

Why this exists (2026-10-11, agenda item 23, next action). The seed evidence table
`research/mcr-colistin-seed.md` is a faithful transcription of one review's own table, and its own
finding is that the review supplies only 4 of the 9 harmonisation columns the item asks for --
collection year, mcr variant, detection method and sampling design are all missing. Those four are
exactly the columns that decide whether the reported cross-sector pattern is biology or surveillance.
So the item's next action is to go to the primary studies and read the missing columns off them.

This script does the *retrieval* half and nothing else: for each target seed row (the heavy/anomalous
ones named on 2026-10-11, plus the food and environmental rows 18/20/21/25 added 2026-10-16) it names
the primary study by DOI, fetches the Europe PMC core record, and writes the raw metadata plus
abstract to `research/mcr-colistin-primary-raw.json`. The classification (variant, method, design,
window) is done by hand in `research/mcr-colistin-harmonisation.md`, because it is a reading task and
a wrong guess printed as data is worse than a blank cell.

Network: Europe PMC REST (no key). Full text is fetched only where Europe PMC serves it; where it
does not, the record is marked `fulltext: false` and the reason is left in the file.

CLI:
    python3 scripts/mcr_colistin_primary.py --write   # fetch and write the raw JSON
    python3 scripts/mcr_colistin_primary.py --show    # print what is on disk
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "research" / "mcr-colistin-primary-raw.json"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"

# The targets: the six largest rows by N in the seed table (13, 17a, 28, 1, 6, 19) plus the two
# rows the seed flags as not agreeing with themselves (17h Spain, 17i Portugal). Every row is
# mapped to the reference number the seed prints and to the DOI of that reference. `seed_n` and
# `seed_pos` are copied from the seed table so the raw file carries the claim it is testing.
TARGETS = [
    {"row": "13",  "country": "Japan",   "sector": "Livestock", "seed_n": 9306, "seed_pos": 39,
     "ref": "35", "doi": "10.1128/aac.02057-16"},
    {"row": "17a", "country": "Germany", "sector": "Livestock", "seed_n": 6158, "seed_pos": 709,
     "ref": "39", "doi": "10.3389/fmicb.2022.1076315"},
    {"row": "28",  "country": "Canada",  "sector": "Human",     "seed_n": 5571, "seed_pos": 2,
     "ref": "47", "doi": "10.9778/cmajo.20160080"},
    {"row": "1",   "country": "China",   "sector": "Raw meat, livestock, human", "seed_n": 2649,
     "seed_pos": 260, "ref": "15", "doi": "10.1016/S1473-3099(15)00424-7"},
    {"row": "6",   "country": "China",   "sector": "Livestock", "seed_n": 2330, "seed_pos": 54,
     "ref": "29", "doi": "10.1099/jmm.0.000425"},
    {"row": "19",  "country": "France",  "sector": "Livestock", "seed_n": 1701, "seed_pos": 49,
     "ref": "41", "doi": "10.3389/fmicb.2022.1023403"},
    {"row": "17h", "country": "Spain",   "sector": "Livestock", "seed_n": 28,   "seed_pos": 17,
     "ref": "39", "doi": "10.3389/fmicb.2022.1076315"},
    {"row": "17i", "country": "Portugal", "sector": "Livestock", "seed_n": 28,  "seed_pos": 17,
     "ref": "39", "doi": "10.3389/fmicb.2022.1076315"},
    # Added 2026-10-16: the seed's food and environmental rows. These four carry the sampling-frame
    # differences the item's question is really about (meat vs a picked animal cohort; a cohabiting
    # dog/human household vs a survey; farmland soil/water/manure vs clinical sampling), and they are
    # the next step named in research/mcr-colistin-harmonisation.md section 7.
    {"row": "18",  "country": "Multiple countries in Europe", "sector": "Meat",
     "seed_n": 128,  "seed_pos": 33, "ref": "40", "doi": "10.15436/JFST.1.4.5"},
    {"row": "20",  "country": "Italy", "sector": "Meat", "seed_n": 147, "seed_pos": 2,
     "ref": "22", "doi": "10.3390/microorganisms10091805"},
    {"row": "21",  "country": "Portugal", "sector": "Human and companion animal", "seed_n": 227,
     "seed_pos": 12, "ref": "42", "doi": "10.2807/1560-7917.ES.2022.27.44.2101144"},
    {"row": "25",  "country": "Algeria", "sector": "Soil, water, and manure", "seed_n": 103,
     "seed_pos": 8, "ref": "21", "doi": "10.1016/j.jgar.2019.10.001"},
]


def _get(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "llm-symposium/1.0 (mcr-colistin)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def core_record(doi: str) -> dict:
    """The Europe PMC core record for one DOI (first hit)."""
    q = urllib.parse.quote(f'DOI:"{doi}"')
    data = json.loads(_get(f"{EPMC}/search?query={q}&format=json&resultType=core"))
    hits = data.get("resultList", {}).get("result") or []
    if not hits:
        return {}
    r = hits[0]
    ji = r.get("journalInfo") or {}
    j = ji.get("journal") or {}
    return {
        "pmid": r.get("pmid"),
        "pmcid": r.get("pmcid"),
        "doi": r.get("doi"),
        "title": r.get("title"),
        "journal": j.get("title"),
        "year": r.get("pubYear") or ji.get("yearOfPublication"),
        "is_open_access": r.get("isOpenAccess"),
        "in_epmc": r.get("inEPMC"),
        "abstract": r.get("abstractText"),
    }


def fulltext(pmcid: str | None) -> tuple[str | None, bool]:
    """Full text XML where Europe PMC serves it; else (None, False)."""
    if not pmcid:
        return None, False
    try:
        raw = _get(f"{EPMC}/{pmcid}/fullTextXML")
    except Exception:
        return None, False
    text = raw.decode("utf-8", "replace")
    # A refused/absent record returns a tiny error envelope, not an article.
    if len(text) < 2000 or "<article" not in text:
        return None, False
    return text, True


def build(now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc)
    studies: dict[str, dict] = {}
    cache: dict[str, dict] = {}
    for t in TARGETS:
        doi = t["doi"]
        if doi not in cache:
            rec = core_record(doi)
            ft, ok = fulltext(rec.get("pmcid"))
            rec["fulltext"] = ok
            if ok:
                rec["fulltext_bytes"] = len(ft)
            cache[doi] = rec
        studies[f'{t["row"]} {t["country"]}'] = {
            "seed_row": t["row"],
            "country": t["country"],
            "sector": t["sector"],
            "seed_n": t["seed_n"],
            "seed_pos": t["seed_pos"],
            "seed_ref": t["ref"],
            **cache[doi],
        }
    return {
        "generated_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "Europe PMC REST (search resultType=core; fullTextXML where served)",
        "question": ("Agenda item 23, next action: read collection year, mcr variant, detection method "
                     "and sampling design off the primary studies behind the seed table's heaviest and "
                     "self-inconsistent rows."),
        "note": ("Retrieval only. The four missing columns are classified by hand in "
                 "research/mcr-colistin-harmonisation.md; this file carries the primary studies' own "
                 "metadata and abstracts so those classifications can be checked."),
        "studies": studies,
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true", help="fetch and write the raw JSON")
    g.add_argument("--show", action="store_true", help="print what is on disk")
    args = ap.parse_args(argv)

    if args.show:
        if not OUT.exists():
            print("no raw file on disk; run --write")
            return 1
        data = json.loads(OUT.read_text(encoding="utf-8"))
        print(f"generated {data['generated_utc']}: {len(data['studies'])} studies")
        for k, v in data["studies"].items():
            print(f"  {k:22s} {v.get('year')}  fulltext={v.get('fulltext')}  {str(v.get('title'))[:60]}")
        return 0

    data = build()
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} ({len(data['studies'])} studies)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
