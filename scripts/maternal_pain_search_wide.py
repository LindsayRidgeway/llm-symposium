#!/usr/bin/env python3
"""The widened re-run of the item-24 PubMed search — the step the 2026-09-28 map set itself.

Agenda item 24 (maternal chronic pain and substance-use care) was mapped on 2026-09-28 with a
deliberately strict query: every concept fielded to title/abstract, four concepts ANDed
(`scripts/maternal_pain_search.py`). That map found 54 matching records and returned the top 50,
of which **2** sat in the item's actual subject (chronic pain *as the subject* in a pregnant or
postpartum patient) and **0** measured medication retention *against* a pain variable. It closed by
naming its own next action:

    Widen the search once — add MeSH terms and the phrasing the strict query misses
    ("opioid-exposed pregnancy", "analgesia", "medication retention") — and re-run the
    classification to test whether the retention-against-pain cell stays empty.

This script is that widened run, and it runs **two** queries, on purpose:

  * `WIDE_QUERY` — the strict query with the missed phrasing and MeSH index terms added, so the
    count moves from a title/abstract floor toward the real size of the literature the item is
    about. Its job is to show how much class B grows when the vocabulary widens.
  * `CELL_QUERY` — a query aimed straight at the one cell the map left empty: a perinatal/opioid
    population AND a pain concept AND a substance-use concept AND an explicit *retention/adherence*
    term. This is the honest test of the map's central negative claim. If a record measuring
    retention against pain exists and is reachable by the index, the cell query is the most likely
    way to surface it.

Neither query is a quality filter and neither is ranked by us: the order is PubMed's own relevance
order, and every result is printed so a reader can re-run the string by hand.

Usage:
    python3 scripts/maternal_pain_search_wide.py                 # default top N = 50 per query
    python3 scripts/maternal_pain_search_wide.py --n 100

Writes research/maternal-chronic-pain-substance-use-wide-raw.json (both result sets, with
abstracts, so the table can be re-derived without re-asking NCBI) and prints the rows.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# --- the widened query: strict query + missed phrasing + MeSH index terms ------------------------
# Group 1 (population) adds antenatal/prenatal, "opioid-exposed pregnancy", and the MeSH headings
#   for pregnancy and the postpartum period.
# Group 2 (pain) adds analgesia / analgesic / opioid-sparing / pain severity and the MeSH headings
#   for chronic pain, analgesia and pain management.
# Group 3 (substance use) adds "opioid-exposed" and the MeSH headings for opioid- and
#   substance-related disorders.
# Group 4 (treatment) adds bare retention/adherence, opioid-agonist phrasing, and the MeSH headings
#   for opioid substitution treatment, buprenorphine, methadone and medication adherence.
WIDE_QUERY = (
    '(pregnancy[tiab] OR pregnant[tiab] OR postpartum[tiab] OR perinatal[tiab] '
    'OR maternal[tiab] OR antenatal[tiab] OR prenatal[tiab] OR "pregnant women"[tiab] '
    'OR "opioid-exposed pregnancy"[tiab] '
    'OR "Pregnancy"[MeSH] OR "Pregnancy Complications"[MeSH] OR "Postpartum Period"[MeSH]) '
    'AND ("chronic pain"[tiab] OR "persistent pain"[tiab] OR "pain management"[tiab] '
    'OR analgesia[tiab] OR analgesic[tiab] OR "opioid-sparing"[tiab] OR "pain severity"[tiab] '
    'OR "Chronic Pain"[MeSH] OR "Analgesia"[MeSH] OR "Pain Management"[MeSH]) '
    'AND ("substance use disorder"[tiab] OR "substance use disorders"[tiab] '
    'OR "opioid use disorder"[tiab] OR "opioid use disorders"[tiab] '
    'OR "opioid dependence"[tiab] OR "opioid misuse"[tiab] OR "substance misuse"[tiab] '
    'OR "opioid-exposed"[tiab] '
    'OR "Opioid-Related Disorders"[MeSH] OR "Substance-Related Disorders"[MeSH]) '
    'AND (treatment[tiab] OR "medication for opioid use disorder"[tiab] OR MOUD[tiab] '
    'OR buprenorphine[tiab] OR methadone[tiab] OR "treatment retention"[tiab] '
    'OR "medication retention"[tiab] OR "integrated care"[tiab] OR retention[tiab] '
    'OR adherence[tiab] OR "opioid agonist"[tiab] OR "agonist therapy"[tiab] '
    'OR "Opioid Substitution Treatment"[MeSH] OR "Buprenorphine"[MeSH] OR "Methadone"[MeSH] '
    'OR "Medication Adherence"[MeSH])'
)

# --- the cell probe: does anything measure retention/adherence against a pain variable? ---------
CELL_QUERY = (
    '(pregnancy[tiab] OR pregnant[tiab] OR postpartum[tiab] OR perinatal[tiab] '
    'OR maternal[tiab] OR prenatal[tiab] OR "opioid-exposed pregnancy"[tiab] '
    'OR "Pregnancy"[MeSH] OR "Postpartum Period"[MeSH] OR "Pregnancy Complications"[MeSH]) '
    'AND ("chronic pain"[tiab] OR "persistent pain"[tiab] OR "pain management"[tiab] '
    'OR analgesia[tiab] OR "pain severity"[tiab] '
    'OR "Chronic Pain"[MeSH] OR "Analgesia"[MeSH] OR "Pain Management"[MeSH]) '
    'AND ("opioid use disorder"[tiab] OR "substance use disorder"[tiab] '
    'OR "opioid dependence"[tiab] OR "opioid misuse"[tiab] OR "substance misuse"[tiab] '
    'OR "Opioid-Related Disorders"[MeSH] OR "Substance-Related Disorders"[MeSH]) '
    'AND (retention[tiab] OR adherence[tiab] OR "treatment retention"[tiab] '
    'OR "medication retention"[tiab] OR "retention in care"[tiab] '
    'OR "Medication Adherence"[MeSH] OR "Retention in Care"[MeSH])'
)


def _get_json(url: str, params: dict) -> dict:
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": "llm-symposium/1.0"})
    with urllib.request.urlopen(req, timeout=60) as fh:
        return json.loads(fh.read().decode("utf-8"))


def _get_text(url: str, params: dict) -> str:
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": "llm-symposium/1.0"})
    with urllib.request.urlopen(req, timeout=60) as fh:
        return fh.read().decode("utf-8", "replace")


def _abstract(pubmed_article: ET.Element) -> str:
    parts = []
    for node in pubmed_article.iter("AbstractText"):
        label = node.get("Label")
        text = "".join(node.itertext()).strip()
        if not text:
            continue
        parts.append(f"{label}: {text}" if label else text)
    return " ".join(parts)


def _text(article: ET.Element, tag: str) -> str:
    node = article.find(f".//{tag}")
    return "".join(node.itertext()).strip() if node is not None else ""


def run_query(query: str, n: int) -> dict:
    search = _get_json(f"{EUTILS}/esearch.fcgi", {
        "db": "pubmed", "term": query, "retmode": "json",
        "retmax": str(n), "sort": "relevance",
    })["esearchresult"]
    total = int(search["count"])
    ids = search.get("idlist", [])

    records = []
    if ids:
        xml = _get_text(f"{EUTILS}/efetch.fcgi", {
            "db": "pubmed", "id": ",".join(ids), "retmode": "xml",
        })
        root = ET.fromstring(xml)
        for article in root.iter("PubmedArticle"):
            pmid = _text(article, "PMID")
            records.append({
                "pmid": pmid,
                "title": _text(article, "ArticleTitle"),
                "journal": _text(article, "Title"),
                "pubdate": _text(article, "PubDate"),
                "pubtypes": [t for t in (
                    "".join(x.itertext()).strip() for x in article.iter("PublicationType")) if t],
                "abstract": _abstract(article),
            })
    return {"query": query, "total_matching": total, "returned": len(records), "records": records}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=50,
                    help="records to pull per query (default 50)")
    ap.add_argument("--out",
                    default="research/maternal-chronic-pain-substance-use-wide-raw.json")
    args = ap.parse_args(argv)

    wide = run_query(WIDE_QUERY, args.n)
    cell = run_query(CELL_QUERY, args.n)

    data = {
        "_what": ("Widened re-run of the commons agenda item 24 PubMed search (maternal chronic "
                  "pain and substance-use care). Two queries: the strict search widened with MeSH "
                  "and missed phrasing, and a probe of the empty retention-against-pain cell. Raw "
                  "metadata and abstracts as returned by NCBI E-utilities; no ranking of our own."),
        "retrieved": dt.date.today().isoformat(),
        "sort": "relevance",
        "wide": wide,
        "cell": cell,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    for name, block in (("WIDE", wide), ("CELL", cell)):
        print(f"== {name} ==  total matching: {block['total_matching']}  "
              f"returned: {block['returned']}")
        for i, r in enumerate(block["records"], 1):
            print(f"{i:2d}. PMID {r['pmid']}  [{r['pubdate']}]  {r['title']}")
            print(f"    {r['journal']}  |  {'; '.join(r['pubtypes'])}")
        print()
    print(f"wrote: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
