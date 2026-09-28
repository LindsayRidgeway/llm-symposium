#!/usr/bin/env python3
"""Fetch PubMed records for a query and write them to JSON, reproducibly.

Why this exists: several standing-agenda items (19, 21, 23, 24, 27-32) each open with the
same mechanical step -- "run a PubMed search and build an evidence table" -- and there was no
shared way to do it. `scripts/disease_screen.py` talks to Europe PMC for target/disease joins
and is the wrong tool for that: it answers "is this gene joined to this disease", not "give me
the records so a reader can see them". This tool does the second, and keeps the exact query so
the search can be re-run and checked.

It uses NCBI E-utilities (no API key required; a key only raises the rate limit), which is the
route the commons already uses for PubMed. No key, no email is stored here -- pass yours if you
want, but the tool works without.

Usage:
    python3 scripts/pubmed_fetch.py --query 'acupuncture[tiab] AND chronic pain[tiab]' \
        --out research/example.json --retmax 40
    python3 scripts/pubmed_fetch.py --query-file q.txt --out out.json

Output JSON:
    {"query": ..., "retrieved_utc": ..., "count": N, "records": [ {pmid,title,journal,year,
     pubtypes, mesh, abstract, authors}, ... ]}
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "llm-symposium-pubmed-fetch"


def _get(url: str, params: dict) -> bytes:
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": TOOL})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry any transport error, then raise
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("unreachable")


def esearch(query: str, retmax: int, sort: str = "relevance") -> list[str]:
    raw = _get(
        f"{EUTILS}/esearch.fcgi",
        {
            "db": "pubmed",
            "term": query,
            "retmax": retmax,
            "retmode": "json",
            "sort": sort,
            "tool": TOOL,
        },
    )
    data = json.loads(raw)
    return data["esearchresult"].get("idlist", [])


def _text(node) -> str:
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def efetch(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    time.sleep(0.4)  # NCBI: <=3 req/s without a key
    raw = _get(
        f"{EUTILS}/efetch.fcgi",
        {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "tool": TOOL},
    )
    root = ET.fromstring(raw)
    records = []
    for art in root.findall(".//PubmedArticle"):
        pmid = _text(art.find(".//MedlineCitation/PMID"))
        title = _text(art.find(".//Article/ArticleTitle"))
        journal = _text(art.find(".//Journal/Title")) or _text(art.find(".//Journal/ISOAbbreviation"))
        year = ""
        for path in (
            ".//JournalIssue/PubDate/Year",
            ".//JournalIssue/PubDate/MedlineDate",
            ".//ArticleDate/Year",
        ):
            year = _text(art.find(path))
            if year:
                break
        abstract = " ".join(
            _text(a)
            for a in art.findall(".//Article/Abstract/AbstractText")
            if _text(a)
        )
        pubtypes = [_text(p) for p in art.findall(".//PublicationTypeList/PublicationType")]
        mesh = [_text(m) for m in art.findall(".//MeshHeading/DescriptorName")]
        authors = []
        for a in art.findall(".//AuthorList/Author")[:6]:
            last = _text(a.find("LastName"))
            init = _text(a.find("Initials"))
            if last:
                authors.append(f"{last} {init}".strip())
        records.append(
            {
                "pmid": pmid,
                "title": title,
                "journal": journal,
                "year": year,
                "pubtypes": pubtypes,
                "mesh": mesh,
                "abstract": abstract,
                "authors": authors,
            }
        )
    return records


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--query", help="PubMed query string")
    ap.add_argument("--query-file", help="file containing the PubMed query")
    ap.add_argument("--out", required=True, help="output JSON path")
    ap.add_argument("--retmax", type=int, default=40)
    ap.add_argument("--sort", default="relevance", choices=["relevance", "pub_date"])
    args = ap.parse_args()

    query = args.query
    if args.query_file:
        with open(args.query_file) as fh:
            query = fh.read().strip()
    if not query:
        print("need --query or --query-file", file=sys.stderr)
        return 2

    ids = esearch(query, args.retmax, args.sort)
    records = efetch(ids)
    payload = {
        "query": query,
        "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(records),
        "records": records,
    }
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print(f"{len(records)} records -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
