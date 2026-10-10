#!/usr/bin/env python3
"""Widened reproducible PubMed search for agenda item 24 — the one the item asked for next.

`scripts/maternal_pain_search.py` ran the *strict* query: four concepts, every term fielded to
title/abstract, nothing else. It returned 54 records and found that the specific hypothesis in the
adopted question — that undertreated chronic pain *reduces* medication retention — was **unmeasured**
in that window. The item's own next action was to widen the query **once** and re-run, to test whether
that cell stays empty when the search is loosened:

  * add the phrasing the strict query misses — "opioid-exposed pregnancy", plain "analgesia", and the
    general "retention" rather than only the compound "medication retention";
  * add the MeSH terms the terse query never used — the indexer's own vocabulary for the same four
    concepts, which is where a record lives when its abstract words differ from ours.

The widened query is a **floor too, but a looser one**: it trades precision for reach, so it will pull
in records that merely mention the words. The point is not the bigger number; it is whether the
**retention-against-pain** cell fills or stays empty when the net is loosened. Each concept is still
fielded (tiab) or MeSH-tagged — never bare — so the reader can still say what a hit means.

This script also runs the strict query on the same day and records both totals side by side, because
the comparison is the artefact: 54 → N is the price of loosening the net, and the classification below
says what the extra records bought.

It writes `research/maternal-chronic-pain-widened-raw.json`: both queries, both totals, the widened
record set with titles *and* abstracts, and a lexical screen (not the finding — the leads for it) that
flags each record for a pain term, a retention/engagement term and a medication-for-OUD term.

Usage:
    python3 scripts/maternal_pain_widened_search.py
    python3 scripts/maternal_pain_widened_search.py --n 200
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# --- The strict query, verbatim from scripts/maternal_pain_search.py (kept identical on purpose:
#     the comparison is only honest if this string is the one the first map printed). ---
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

# --- The widened query: same four concepts, each loosened once, by the two means the item named. ---
# population: + "opioid-exposed pregnancy" (the obstetric wording the strict query missed)
#             + MeSH "Pregnancy" / "Postpartum Period"
# pain:       + analgesia (the plain word), + MeSH "Chronic Pain" / "Analgesia"
# substance:  + MeSH "Opioid-Related Disorders"
# treatment:  + plain "retention", + MeSH "Opiate Substitution Treatment"
WIDENED_QUERY = (
    '(pregnancy[tiab] OR pregnant[tiab] OR postpartum[tiab] OR perinatal[tiab] '
    'OR maternal[tiab] OR "pregnant women"[tiab] '
    'OR "opioid-exposed pregnancy"[tiab] OR "opioid exposed pregnancy"[tiab] '
    'OR "Pregnancy"[MeSH Terms] OR "Postpartum Period"[MeSH Terms]) '
    'AND ("chronic pain"[tiab] OR "persistent pain"[tiab] OR "pain management"[tiab] '
    'OR analgesia[tiab] OR "Chronic Pain"[MeSH Terms] OR "Analgesia"[MeSH Terms]) '
    'AND ("substance use disorder"[tiab] OR "substance use disorders"[tiab] '
    'OR "opioid use disorder"[tiab] OR "opioid use disorders"[tiab] '
    'OR "opioid dependence"[tiab] OR "opioid misuse"[tiab] OR "substance misuse"[tiab] '
    'OR "Opioid-Related Disorders"[MeSH Terms]) '
    'AND (treatment[tiab] OR "medication for opioid use disorder"[tiab] OR MOUD[tiab] '
    'OR buprenorphine[tiab] OR methadone[tiab] OR "treatment retention"[tiab] '
    'OR "medication retention"[tiab] OR retention[tiab] OR "integrated care"[tiab] '
    'OR "Opiate Substitution Treatment"[MeSH Terms])'
)

# The lexical screen. These are NOT the finding; they nominate rows for a human to read, exactly the
# way research/queue.md insists a strict join is opened before it closes a lead.
CHRONIC_PAIN_RE = re.compile(
    r"\bchronic pain\b|\bpersistent pain\b|\bchronic pelvic pain\b|\blong[- ]term pain\b", re.I)
ACUTE_PAIN_RE = re.compile(
    r"\bcesarean\b|\bcaesarean\b|\blabou?r\b|\bdelivery\b|\bintrapartum\b|\bpostpartum analgesia\b"
    r"|\bperipartum\b|\bneuraxial\b|\bepidural\b", re.I)
PAIN_RE = re.compile(r"\bpain\b|\banalges\w*|\bopioid[- ]toleran\w*", re.I)
RETENTION_RE = re.compile(
    r"\bretention\b|\bretain\w*\b|\bcontinu\w* (?:of|in) (?:care|treatment|buprenorphine|methadone)"
    r"|\badherence\b|\bengagement\b|\bdiscontinu\w*", re.I)
MOUD_RE = re.compile(
    r"\bMOUD\b|\bbuprenorphine\b|\bmethadone\b|medication for opioid use disorder"
    r"|opioid agonist (?:therapy|treatment)|\bOAT\b|\bagonist therapy\b", re.I)


def _get(url: str, params: dict) -> dict:
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": "llm-symposium/1.0"})
    with urllib.request.urlopen(req, timeout=60) as fh:
        return json.loads(fh.read().decode("utf-8"))


def _count(term: str) -> int:
    d = _get(f"{EUTILS}/esearch.fcgi",
             {"db": "pubmed", "term": term, "retmode": "json", "retmax": "0"})
    return int(d["esearchresult"]["count"])


def _ids(term: str, n: int) -> tuple[int, list[str]]:
    d = _get(f"{EUTILS}/esearch.fcgi",
             {"db": "pubmed", "term": term, "retmode": "json",
              "retmax": str(n), "sort": "relevance"})
    res = d["esearchresult"]
    return int(res["count"]), res.get("idlist", [])


def _abstracts(pmids: list[str]) -> dict:
    """Return {pmid: {title, journal, pubdate, abstract}} via efetch XML."""
    if not pmids:
        return {}
    full = (f"{EUTILS}/efetch.fcgi?" +
            urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids),
                                    "retmode": "xml"}))
    req = urllib.request.Request(full, headers={"User-Agent": "llm-symposium/1.0"})
    with urllib.request.urlopen(req, timeout=120) as fh:
        root = ET.fromstring(fh.read())

    out = {}
    for art in root.iter("PubmedArticle"):
        pmid_el = art.find(".//PMID")
        if pmid_el is None:
            continue
        pmid = pmid_el.text
        title_el = art.find(".//ArticleTitle")
        title = "".join(title_el.itertext()) if title_el is not None else ""
        journal_el = art.find(".//Journal/Title")
        journal = journal_el.text if journal_el is not None else ""
        year = ""
        yd = art.find(".//JournalIssue/PubDate/Year")
        if yd is not None:
            year = yd.text
        else:
            md = art.find(".//JournalIssue/PubDate/MedlineDate")
            if md is not None:
                year = md.text
        parts = []
        for ab in art.iter("AbstractText"):
            label = ab.get("Label")
            txt = "".join(ab.itertext())
            parts.append(f"{label}: {txt}" if label else txt)
        out[pmid] = {"title": re.sub(r"\s+", " ", title).strip(),
                     "journal": journal or "", "pubdate": year or "",
                     "abstract": re.sub(r"\s+", " ", " ".join(parts)).strip()}
    return out


def _screen(rec: dict) -> dict:
    blob = (rec.get("title", "") + " " + rec.get("abstract", ""))
    return {
        "chronic_pain": bool(CHRONIC_PAIN_RE.search(blob)),
        "acute_pain": bool(ACUTE_PAIN_RE.search(blob)),
        "pain": bool(PAIN_RE.search(blob)),
        "retention": bool(RETENTION_RE.search(blob)),
        "moud": bool(MOUD_RE.search(blob)),
    }


def run(n: int = 200) -> dict:
    today = dt.date.today().isoformat()

    strict_total = _count(STRICT_QUERY)
    wide_total, ids = _ids(WIDENED_QUERY, n)
    meta = _abstracts(ids)

    records = []
    for pmid in ids:
        r = meta.get(pmid, {})
        rec = {"pmid": pmid, "title": r.get("title", ""), "journal": r.get("journal", ""),
               "pubdate": r.get("pubdate", ""), "abstract": r.get("abstract", "")}
        rec["screen"] = _screen(rec)
        records.append(rec)

    # The cell the item cares about: a record that names BOTH a retention/engagement term and a pain
    # term. The screen nominates; the map classifies. A chronic-pain retention record is the cell.
    retention_x_pain = [r["pmid"] for r in records if r["screen"]["retention"] and r["screen"]["pain"]]
    retention_x_chronic = [r["pmid"] for r in records
                           if r["screen"]["retention"] and r["screen"]["chronic_pain"]]

    return {
        "_what": ("Reproducible *widened* PubMed result for commons agenda item 24 "
                  "(maternal chronic pain and substance-use care). Both the strict and the widened "
                  "query, run the same day, plus the widened record set with abstracts and a lexical "
                  "screen. The screen nominates rows to read; it is not the classification."),
        "retrieved": today,
        "strict": {"query": STRICT_QUERY, "total_matching": strict_total},
        "widened": {"query": WIDENED_QUERY, "total_matching": wide_total, "sort": "relevance",
                    "returned": len(records)},
        "screen_counts": {
            "returned": len(records),
            "chronic_pain": sum(1 for r in records if r["screen"]["chronic_pain"]),
            "retention": sum(1 for r in records if r["screen"]["retention"]),
            "moud": sum(1 for r in records if r["screen"]["moud"]),
            "retention_x_pain": len(retention_x_pain),
            "retention_x_chronic_pain": len(retention_x_chronic),
        },
        "retention_x_pain_pmids": retention_x_pain,
        "retention_x_chronic_pain_pmids": retention_x_chronic,
        "records": records,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=200, help="widened records to pull (default 200)")
    ap.add_argument("--out", default="research/maternal-chronic-pain-widened-raw.json")
    args = ap.parse_args(argv)

    data = run(args.n)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"retrieved         : {data['retrieved']}")
    print(f"strict total      : {data['strict']['total_matching']}")
    print(f"widened total     : {data['widened']['total_matching']}")
    print(f"widened returned  : {data['widened']['returned']}")
    print(f"screen counts     : {data['screen_counts']}")
    print(f"wrote             : {args.out}")
    print()
    print("retention x pain (the cell under test):")
    for pmid in data["retention_x_pain_pmids"]:
        rec = next(r for r in data["records"] if r["pmid"] == pmid)
        tag = "CHRONIC" if rec["screen"]["chronic_pain"] else "acute/other"
        print(f"  {pmid}  [{tag}]  {rec['title'][:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
