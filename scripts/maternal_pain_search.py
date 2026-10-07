#!/usr/bin/env python3
"""Reproducible PubMed search for agenda item 24 — maternal chronic pain and substance-use care.

The question the commons adopted on 2026-09-18 (agenda/24):

    Among pregnant and postpartum patients with a substance-use disorder, does
    undertreated chronic pain — or treatment constrained by stigma and relapse
    concern — reduce medication retention, increase recurrence or overdose risk,
    or impair maternal functioning? Which integrated pain and addiction
    treatments have evidence of improving both pain-related and substance-use
    outcomes?

The next action on that item is a *reproducible* search plus a classification of
the first 50 relevant records by population, intervention, and reported pain and
addiction outcomes. This script is the reproducible half. It sends the exact
query string below to NCBI E-utilities (free, no key), records the total count
and the search date, and pulls the record metadata for the top N. Nothing here
is ranked or scored by us: the sort is PubMed's own relevance order, and the
table that a reader builds from this is only ever "what PubMed returned on the
day it was asked".

Why the query looks the way it does — read this before changing it:

  * Every concept is fielded to [tiab] (title/abstract). That is deliberate. An
    all-fields search matches MeSH-only and "discussed in passing" records, and
    the disease-research program already measured what an unfielded hit means
    (research/queue.md: "any_field hits are overwhelmingly reviews and abstract
    collections"). A tighter query returns fewer rows; it also returns rows whose
    title or abstract actually says the thing.
  * The three concepts are ANDed: (pregnancy/postpartum) AND (chronic or
    persistent pain) AND (a substance-use disorder) AND (a treatment term). A
    record must name all four to appear, so the count is a *floor* on the real
    literature, not a ceiling — abstracts that use other words for the same
    things are missed, and that is stated in the artefact rather than hidden.
  * No date bound is applied, so the corpus can be read for its shape (when the
    work appears) rather than only its newest edge.

Usage:
    python3 scripts/maternal_pain_search.py            # default N = 50
    python3 scripts/maternal_pain_search.py --n 200    # wider metadata pull
    python3 scripts/maternal_pain_search.py --query broad --abstracts \
        --out research/maternal-chronic-pain-substance-use-broad-raw.json

The `broad` query (added 2026-10-07, the item's own next action) is the same four
concepts widened with MeSH headings and the phrasing the strict query misses, so
a reader can test whether the strict query's empty "retention against pain" cell
stays empty when the net is cast wider. `--abstracts` stores each record's
abstract in the snapshot so a classification can be checked against its source.
The strict query is unchanged; run it with no flags to reproduce the original map.

It writes research/maternal-chronic-pain-substance-use-raw.json (every field it
received, so a later run can re-derive the table without re-asking NCBI) and
prints the query, the count and the records to stdout.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.parse
import urllib.request

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# The search, verbatim. One string, printed in the artefact so any reader can
# paste it into pubmed.ncbi.nlm.nih.gov and get the same rows back.
QUERY = (
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


# The *widening* query, added 2026-10-07 as the item's own next action. The
# strict query above is a floor: it returns only a product whichever words a
# title or abstract actually happens to use. This one widens in the two ways the
# item named — it adds MeSH subject headings (indexer-applied, so a hit means the
# record is *about* the concept, not merely that it says the word), and it adds
# the phrasing the strict query misses ("opioid-exposed pregnancy", "analgesia",
# "medication retention" as a phrase, the generic "opioid use in pregnancy"). It
# is the SAME four concepts, widened — not a different question — and it is kept
# as a separate constant so the strict map's numbers keep meaning what they say.
QUERY_BROAD = (
    '(pregnancy[tiab] OR pregnant[tiab] OR postpartum[tiab] OR perinatal[tiab] '
    'OR maternal[tiab] OR "pregnant women"[tiab] OR "opioid-exposed pregnancy"[tiab] '
    'OR "opioid exposed pregnancy"[tiab] '
    'OR "pregnancy"[MeSH] OR "postpartum period"[MeSH] OR "pregnant women"[MeSH]) '
    'AND ("chronic pain"[tiab] OR "persistent pain"[tiab] OR "pain management"[tiab] '
    'OR analgesia[tiab] OR analgesia[MeSH] '
    'OR "chronic pain"[MeSH] OR "pain management"[MeSH]) '
    'AND ("substance use disorder"[tiab] OR "substance use disorders"[tiab] '
    'OR "opioid use disorder"[tiab] OR "opioid use disorders"[tiab] '
    'OR "opioid dependence"[tiab] OR "opioid misuse"[tiab] OR "substance misuse"[tiab] '
    'OR "substance-related disorders"[MeSH] OR "opioid-related disorders"[MeSH]) '
    'AND (treatment[tiab] OR "medication for opioid use disorder"[tiab] OR MOUD[tiab] '
    'OR buprenorphine[tiab] OR methadone[tiab] OR "treatment retention"[tiab] '
    'OR "medication retention"[tiab] OR "integrated care"[tiab] '
    'OR buprenorphine[MeSH] OR methadone[MeSH] OR "opioid substitution treatment"[tiab])'
)

# Named so a run, and a test, can ask for a query by name rather than by copy.
QUERIES = {"strict": QUERY, "broad": QUERY_BROAD}


def _get(url: str, params: dict) -> dict:
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": "llm-symposium/1.0"})
    with urllib.request.urlopen(req, timeout=45) as fh:
        return json.loads(fh.read().decode("utf-8"))


def _get_text(url: str, params: dict) -> str:
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": "llm-symposium/1.0"})
    with urllib.request.urlopen(req, timeout=60) as fh:
        return fh.read().decode("utf-8", "replace")


def fetch_abstracts(pmids: list) -> dict:
    """Return {pmid: abstract} via efetch MEDLINE text. Best-effort, never raises.

    The strict query was classified by hand from titles plus abstracts fetched
    one at a time. Re-doing that for a widened set needs the abstracts in the
    snapshot, so a later reader can check the classification against the same
    text. MEDLINE format is line-based: records separated by a blank line,
    fields tagged `AB  - ` with continuation lines indented six spaces.
    """
    if not pmids:
        return {}
    try:
        text = _get_text(f"{EUTILS}/efetch.fcgi", {
            "db": "pubmed", "id": ",".join(pmids),
            "rettype": "medline", "retmode": "text",
        })
    except Exception as exc:  # noqa: BLE001 — a network miss must not lose the run
        print(f"warning: abstract fetch failed ({exc}); snapshot keeps titles only",
              file=sys.stderr)
        return {}

    out, pmid, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith("PMID- "):
            if pmid is not None:
                out[pmid] = " ".join(buf).strip()
            pmid, buf = line[6:].strip(), []
        elif line.startswith("AB  - "):
            buf.append(line[6:].strip())
        elif pmid is not None and line.startswith("      "):
            buf.append(line.strip())
    if pmid is not None:
        out[pmid] = " ".join(buf).strip()
    return out


def run(n: int = 50, query: str = "strict", abstracts: bool = False) -> dict:
    today = dt.date.today().isoformat()
    term = QUERIES[query]

    search = _get(f"{EUTILS}/esearch.fcgi", {
        "db": "pubmed", "term": term, "retmode": "json",
        "retmax": str(n), "sort": "relevance",
    })
    res = search["esearchresult"]
    total = int(res["count"])
    ids = res.get("idlist", [])

    summary = {"result": {}}
    if ids:
        summary = _get(f"{EUTILS}/esummary.fcgi", {
            "db": "pubmed", "id": ",".join(ids), "retmode": "json",
        })

    abs_by_pmid = fetch_abstracts(ids) if abstracts else {}

    records = []
    for pmid in ids:
        r = summary.get("result", {}).get(pmid)
        if not r:
            continue
        rec = {
            "pmid": pmid,
            "title": r.get("title", ""),
            "journal": r.get("fulljournalname") or r.get("source", ""),
            "pubdate": r.get("pubdate", ""),
            "pubtypes": r.get("pubtype", []),
        }
        if abstracts:
            rec["abstract"] = abs_by_pmid.get(pmid, "")
        records.append(rec)

    return {
        "_what": ("Reproducible PubMed result for commons agenda item 24 "
                  "(maternal chronic pain and substance-use care). Raw metadata "
                  "as returned by NCBI E-utilities; no ranking of our own."),
        "retrieved": today,
        "query_name": query,
        "query": term,
        "total_matching": total,
        "returned": len(records),
        "sort": "relevance",
        "records": records,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=50,
                    help="how many records to pull metadata for (default 50)")
    ap.add_argument("--query", choices=sorted(QUERIES), default="strict",
                    help="which query to run: 'strict' (title/abstract, the original floor) "
                         "or 'broad' (adds MeSH and the missing phrasing)")
    ap.add_argument("--abstracts", action="store_true",
                    help="also fetch each record's abstract into the snapshot (needed to "
                         "check a classification against its source text)")
    ap.add_argument("--out", default="research/maternal-chronic-pain-substance-use-raw.json")
    args = ap.parse_args(argv)

    data = run(args.n, query=args.query, abstracts=args.abstracts)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"retrieved  : {data['retrieved']}")
    print(f"total match: {data['total_matching']}")
    print(f"returned   : {data['returned']} (sort={data['sort']})")
    print(f"wrote      : {args.out}")
    print()
    for i, r in enumerate(data["records"], 1):
        pts = ", ".join(r["pubtypes"])
        print(f"{i:2d}. PMID {r['pmid']}  [{r['pubdate']}]  {r['title']}")
        print(f"    {r['journal']}  |  {pts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
