#!/usr/bin/env python3
"""Widened PubMed search for agenda item 24 — maternal chronic pain and substance-use care.

This is the *second* step on the item, not a rebuild of the first. The first step
(`scripts/maternal_pain_search.py`, run 2026-09-28 by Desi) fielded every concept to
title/abstract with a strict four-way AND and returned a floor of 54 records; it named
its own next action:

    "Widen the search once — add MeSH terms and the phrasing that the strict query
     misses ('opioid-exposed pregnancy', 'analgesia', 'medication retention') — and
     re-run the classification to test whether the retention-against-pain cell stays
     empty."

That is what this script does. It runs three queries against the same free NCBI
E-utilities endpoint and writes them all to one JSON:

  * ``strict``  — the original query, re-run here so the two counts sit side by side
                  on the same day. If PubMed's index moved between 09-28 and now, the
                  reader sees it rather than having to infer it.
  * ``wide``    — the strict concepts, but each one *widened*: MeSH headings added, and
                  the phrasings the strict query missed ("opioid-exposed pregnancy",
                  "analgesia", "buprenorphine in pregnancy", bare "retention"). This is
                  a floor too, but a higher one; the point is to see how much of the
                  literature the strict query was hiding.
  * ``cell``    — a *targeted probe* for the single hypothesis the item is about: a
                  record in a pregnant/perinatal population that carries BOTH a
                  medication-retention outcome AND a pain measure. This is the cell
                  that stayed empty in the first pass. It is deliberately built from
                  the two concepts alone (no "treatment" arm, no fielding), so it
                  reaches abstracts the strict conjunction cannot.

For every query it pulls record metadata (esummary) and abstracts (efetch), so the
classification below can be audited offline without re-asking NCBI.

Usage:
    python3 scripts/maternal_pain_search_wide.py             # defaults: strict 200, wide 400, cell 200
    python3 scripts/maternal_pain_search_wide.py --wide 600

Writes research/maternal-chronic-pain-substance-use-wide.json and prints a summary.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = {"User-Agent": "llm-symposium/1.0"}

# --- Query 1: the strict query, verbatim from scripts/maternal_pain_search.py --------
STRICT_QUERY = (
    '(pregnancy[tiab] OR pregnant[tiab] OR postpartum[tiab] OR perinatal[tiab] '
    'OR maternal[tiab] OR "pregnant women"[tiab]) '
    'AND ("chronic pain"[tiab] OR "persistent pain"[tiab] OR "pain management"[tiab]) '
    'AND ("substance use disorder"[tiab] OR "substance use disorders"[tiab] '
    'OR "opioid use disorder"[tiab] OR "opioid use disorders"[tiab] '
    'OR "opioid dependence"[tiab] OR "opioid misuse"[tiab] OR "substance misuse"[tiab]) '
    'AND (treatment[tiab] OR "medication for opioid use disorder"[tiab] OR MOUD[tiab] '
    'OR buprenorphine[tiab] OR methadone[tiab] OR "treatment retention"[tiab] '
    'OR "medication retention"[tiab] OR "integrated care"[tiab])'
)

# --- Query 2: the widened query ------------------------------------------------------
# Each strict concept is widened in two ways: (a) a MeSH heading is ORed in, so records
# the indexer tagged but whose abstract uses other words are reached; (b) the phrasings
# the strict query missed are ORed in ("opioid-exposed pregnancy", "analgesia",
# "prenatal opioid exposure", "buprenorphine in pregnancy", the bare "retention").
WIDE_QUERY = (
    # population: pregnancy / postpartum / the newborn-as-proxy-of-the-pregnancy
    '(pregnancy[MeSH] OR "pregnant women"[MeSH] OR "postpartum period"[MeSH] OR perinatal[MeSH] '
    'OR pregnancy[tiab] OR pregnant[tiab] OR postpartum[tiab] OR perinatal[tiab] OR maternal[tiab] '
    'OR "opioid-exposed pregnancy"[tiab] OR "opioid exposed pregnancy"[tiab] '
    'OR "prenatal opioid exposure"[tiab] OR "opioid-exposed"[tiab] OR "neonatal abstinence"[tiab]) '
    # pain: chronic/persistent, plus the analgesia/pain-management phrasings
    'AND ("chronic pain"[MeSH] OR "pain management"[MeSH] OR analgesia[MeSH] '
    'OR "chronic pain"[tiab] OR "persistent pain"[tiab] OR "pain management"[tiab] '
    'OR analgesia[tiab] OR "analgesic"[tiab] OR "pain"[tiab]) '
    # substance use disorder: OUD/SUD MeSH headings plus the missed abbreviations
    'AND ("opioid-related disorders"[MeSH] OR "substance-related disorders"[MeSH] '
    'OR "substance use disorder"[tiab] OR "substance use disorders"[tiab] '
    'OR "opioid use disorder"[tiab] OR "opioid use disorders"[tiab] OR OUD[tiab] '
    'OR "opioid dependence"[tiab] OR "opioid misuse"[tiab] OR "substance misuse"[tiab] '
    'OR "medication for opioid use disorder"[tiab] OR MOUD[tiab] OR buprenorphine[tiab]) '
    # treatment / retention: the strict set plus the bare retention terms and analgesia
    'AND (treatment[tiab] OR "treatment retention"[tiab] OR "medication retention"[tiab] '
    'OR retention[tiab] OR buprenorphine[tiab] OR methadone[tiab] '
    'OR "integrated care"[tiab] OR analgesia[tiab] OR "pain management"[tiab] '
    'OR "opioid reduction"[tiab] OR "opioid tapering"[tiab])'
)

# --- Query 3: the targeted cell probe -------------------------------------------------
# The item's actual hypothesis is narrow: does undertreated chronic pain reduce medication
# retention, in a pregnant/postpartum patient? Query 3 asks PubMed for exactly that cell
# and nothing else — no "treatment" arm, no [tiab] fielding on the core concepts — so it
# reaches records that the conjunction above cannot. If the cell is truly empty, this
# query should return very few records and none of them should carry both outcomes.
CELL_QUERY = (
    '(pregnancy OR pregnant OR postpartum OR perinatal OR maternal) '
    'AND ("chronic pain" OR "persistent pain") '
    'AND ("opioid use disorder" OR "substance use disorder" OR OUD OR buprenorphine OR methadone) '
    'AND (retention OR "treatment retention" OR "medication retention" OR adherence OR "treatment engagement")'
)


def _get(url: str, params: dict) -> dict:
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as fh:
        return json.loads(fh.read().decode("utf-8"))


def _esearch(query: str, n: int) -> tuple[int, list[str]]:
    s = _get(f"{EUTILS}/esearch.fcgi", {
        "db": "pubmed", "term": query, "retmode": "json",
        "retmax": str(n), "sort": "relevance",
    })
    r = s["esearchresult"]
    return int(r["count"]), r.get("idlist", [])


def _esummary(ids: list[str]) -> dict:
    if not ids:
        return {}
    out: dict = {}
    for i in range(0, len(ids), 200):
        chunk = ids[i:i + 200]
        s = _get(f"{EUTILS}/esummary.fcgi", {
            "db": "pubmed", "id": ",".join(chunk), "retmode": "json",
        })
        out.update(s.get("result", {}))
        time.sleep(0.34)
    return out


def _efetch_abstracts(ids: list[str]) -> dict[str, str]:
    """Return pmid -> abstract text, fetched in batches. Free; no key."""
    out: dict[str, str] = {}
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        params = urllib.parse.urlencode({
            "db": "pubmed", "id": ",".join(chunk), "retmode": "xml",
        })
        req = urllib.request.Request(f"{EUTILS}/efetch.fcgi?{params}", headers=UA)
        with urllib.request.urlopen(req, timeout=90) as fh:
            xml = fh.read()
        root = ET.fromstring(xml)
        for art in root.iter("PubmedArticle"):
            pmid_el = art.find(".//PMID")
            if pmid_el is None or not pmid_el.text:
                continue
            pmid = pmid_el.text.strip()
            parts = []
            for ab in art.iter("AbstractText"):
                label = ab.get("Label")
                txt = "".join(ab.itertext()).strip()
                parts.append(f"{label}: {txt}" if label else txt)
            out[pmid] = " ".join(parts)
        time.sleep(0.34)
    return out


def _records(ids: list[str], summary: dict, abstracts: dict[str, str]) -> list[dict]:
    recs = []
    for pmid in ids:
        r = summary.get(pmid)
        if not r:
            continue
        recs.append({
            "pmid": pmid,
            "title": r.get("title", ""),
            "journal": r.get("fulljournalname") or r.get("source", ""),
            "pubdate": r.get("pubdate", ""),
            "pubtypes": r.get("pubtype", []),
            "abstract": abstracts.get(pmid, ""),
        })
    return recs


def _block(query: str, n: int) -> dict:
    count, ids = _esearch(query, n)
    summary = _esummary(ids)
    abstracts = _efetch_abstracts(ids)
    return {
        "query": query,
        "total_matching": count,
        "returned": len(ids),
        "records": _records(ids, summary, abstracts),
    }


def run(strict_n: int, wide_n: int, cell_n: int) -> dict:
    today = dt.date.today().isoformat()
    blocks = {
        "strict": _block(STRICT_QUERY, strict_n),
        "wide": _block(WIDE_QUERY, wide_n),
        "cell": _block(CELL_QUERY, cell_n),
    }
    return {
        "_what": ("Widened PubMed result for commons agenda item 24 (maternal chronic pain "
                  "and substance-use care). Three queries on one day: the strict re-run, a "
                  "MeSH/phrase-widened run, and a targeted probe for the retention-against-"
                  "pain cell. Raw metadata and abstracts as returned by NCBI; no ranking of our own."),
        "retrieved": today,
        "blocks": blocks,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", type=int, default=200)
    ap.add_argument("--wide", type=int, default=400)
    ap.add_argument("--cell", type=int, default=200)
    ap.add_argument("--out", default="research/maternal-chronic-pain-substance-use-wide.json")
    args = ap.parse_args(argv)

    data = run(args.strict, args.wide, args.cell)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"retrieved : {data['retrieved']}")
    for name, blk in data["blocks"].items():
        print(f"{name:6s}   : total={blk['total_matching']:>6d}  returned={blk['returned']}")
    print(f"wrote     : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
