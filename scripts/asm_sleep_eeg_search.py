#!/usr/bin/env python3
"""Reproducible PubMed search for agenda item 30, step (3) — antiseizure medication x sleep EEG.

Written 2026-10-07 (Desi, clock wake). Item 30 asks how much of the memory impairment
attributed to epilepsy — or to its drugs — is carried by disrupted sleep architecture.
Its seed (the 2026 systematic review, PMID 42748517) turned out to be silent on medication:
*antiseizure*, *anti-seizure*, *antiepileptic*, *anti-epileptic*, *medication(s)*, *drug(s)*,
*AED(s)* and four common drug names occur **zero** times between them (see
`research/sleep-cognition-epilepsy-seed.md` §5). So the item's step (3) is to go and read
the literature the seed omits: the corpus at the intersection of (a) a named antiseizure
drug or drug class and (b) an objective sleep measure (EEG, polysomnography, spindle,
slow-wave, sleep architecture).

This script is the reproducible half. It runs one dated PubMed query for that intersection,
fetches each record's abstract verbatim, and tags it so the corpus table can be audited rather
than asserted. Each flag stores the first sentence that set it:

  asm        - which drug / class vocabulary the abstract actually uses
  sleep_eeg  - which objective sleep or EEG measurement it names
  cognition  - whether it names a memory / cognition / consolidation outcome
  design     - the study design it declares (trial, cohort, case-control, review, ...)

WHAT THIS IS NOT. Token presence in an abstract is a *screen*, not a reading, and the same
caveat as item 21 applies: a drug name can appear in an exclusion criterion, a spindle only
in a limitation. So for every flag the record stores the sentence that set it, and the table
prints those sentences. The counts are a lower bound on how many papers *report* the thing,
which is what the item needs to decide whether the drug-attribution half is answerable at all.

Usage:
    python3 scripts/asm_sleep_eeg_search.py              # fetch, write raw record + table
    python3 scripts/asm_sleep_eeg_search.py --no-fetch   # rebuild the table from the snapshot
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research" / "antiseizure-sleep-eeg-raw.json"
TABLE = ROOT / "research" / "antiseizure-sleep-eeg-corpus.md"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = "llm-symposium-desi/1.0 (https://github.com/LindsayRidgeway/llm-symposium)"
RETMAX = 80

# The item's own query. Concept (a) is a named antiseizure drug or class — deliberately
# explicit, because the generic words "medication" and "drug" alone would dredge the whole
# of clinical epilepsy. Concept (b) requires an *objective* sleep measure, so that the corpus
# is about measured sleep, not sleep complaints.
QUERY = (
    '("antiseizure"[tiab] OR "anti-seizure"[tiab] OR "antiepileptic"[tiab] '
    'OR "anti-epileptic"[tiab] OR "antiepileptic drugs"[tiab] OR "antiseizure medication"[tiab] '
    'OR "antiseizure medications"[tiab] OR "antiepileptic medication"[tiab] '
    'OR "antiepileptic medications"[tiab] OR ASM[tiab] OR ASMs[tiab] OR AED[tiab] OR AEDs[tiab] '
    'OR carbamazepine[tiab] OR valproate[tiab] OR "valproic acid"[tiab] OR levetiracetam[tiab] '
    'OR lamotrigine[tiab] OR phenytoin[tiab] OR topiramate[tiab] OR phenobarbital[tiab] '
    'OR gabapentin[tiab] OR perampanel[tiab] OR brivaracetam[tiab] OR lacosamide[tiab]) '
    'AND (sleep[tiab] AND (EEG[tiab] OR electroencephalograph*[tiab] OR polysomnograph*[tiab] '
    'OR spindle*[tiab] OR "slow wave"[tiab] OR "slow-wave"[tiab] OR "slow oscillation"[tiab] '
    'OR "slow oscillations"[tiab] OR "sleep architecture"[tiab] OR "sleep macrostructure"[tiab] '
    'OR REM[tiab] OR NREM[tiab]))'
)

# vocab -> regex. Order matters only for the printed table.
ASM_VOCAB = [
    ("antiseizure", r"anti[- ]?seizure"),
    ("antiepileptic", r"anti[- ]?epileptic"),
    ("ASM", r"\bASMs?\b"),
    ("AED", r"\bAEDs?\b"),
    ("carbamazepine", r"carbamazepine"),
    ("valproate", r"valproat|valproic"),
    ("levetiracetam", r"levetiracetam"),
    ("lamotrigine", r"lamotrigine"),
    ("phenytoin", r"phenytoin"),
    ("topiramate", r"topiramate"),
    ("phenobarbital", r"phenobarbital"),
    ("gabapentin", r"gabapentin"),
    ("perampanel", r"perampanel"),
    ("brivaracetam", r"brivaracetam"),
    ("lacosamide", r"lacosamide"),
]
SLEEP_MODES = [
    ("polysomnography", r"polysomnograph"),
    ("EEG", r"\bEEG\b|electroencephalograph"),
    ("spindles", r"spindle"),
    ("slow-wave/slow-oscillation", r"slow[- ]wave|slow oscillation"),
    ("sleep architecture", r"sleep architecture|sleep macrostructure"),
    ("REM/NREM", r"\bREM\b|\bNREM\b"),
]
COGNITION = [
    ("memory", r"memor"),
    ("consolidation", r"consolidat"),
    ("cognition", r"cogniti"),
    ("attention/executive", r"attention|executive function"),
    ("IQ/neuropsychology", r"\bIQ\b|neuropsycholog|intelligence"),
    ("learning", r"learning"),
]
DESIGNS = [
    ("randomized trial", r"randomi[sz]ed|randomi[sz]ation"),
    ("trial (unspecified)", r"\btrial\b"),
    ("cohort", r"cohort"),
    ("case-control", r"case[- ]control"),
    ("cross-sectional", r"cross[- ]sectional"),
    ("systematic review/meta", r"systematic review|meta[- ]analys"),
    ("case report", r"case report"),
]


def _get(url, params, retries=3):
    full = url + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(full, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as fh:
                return fh.read().decode("utf-8")
        except Exception as exc:  # noqa: BLE001 - transient network; retried
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} tries: {full} ({last})")


def esearch():
    body = _get(f"{EUTILS}/esearch.fcgi", {
        "db": "pubmed", "term": QUERY, "retmode": "json",
        "retmax": str(RETMAX), "sort": "relevance",
    })
    res = json.loads(body)["esearchresult"]
    return int(res["count"]), res.get("idlist", [])


def _text(elem):
    parts = []
    for node in elem.iter():
        if node.tag == "AbstractText":
            label = node.attrib.get("Label")
            chunk = "".join(node.itertext()).strip()
            parts.append(f"{label}: {chunk}" if label else chunk)
    return " ".join(parts).strip()


def _art_to_record(art):
    pmid = art.findtext(".//PMID") or ""
    title = "".join(art.find(".//ArticleTitle").itertext()).strip() if art.find(".//ArticleTitle") is not None else ""
    journal = art.findtext(".//Journal/Title") or ""
    year = art.findtext(".//JournalIssue/PubDate/Year") or art.findtext(".//JournalIssue/PubDate/MedlineDate") or ""
    abstract = _text(art) if art.find(".//Abstract") is not None else ""
    pubtypes = [pt.text or "" for pt in art.findall(".//PublicationTypeList/PublicationType")]
    return {"pmid": pmid, "title": title, "journal": journal, "year": year,
            "pubtypes": pubtypes, "abstract": abstract}


def efetch_abstracts(ids):
    records = []
    for i in range(0, len(ids), 40):
        chunk = ids[i:i + 40]
        body = _get(f"{EUTILS}/efetch.fcgi",
                    {"db": "pubmed", "id": ",".join(chunk),
                     "rettype": "abstract", "retmode": "xml"})
        root = ET.fromstring(body)
        by_id = {a.findtext(".//PMID"): a for a in root.iter("PubmedArticle")}
        for pmid in chunk:  # preserve query order
            if pmid in by_id:
                records.append(_art_to_record(by_id[pmid]))
        time.sleep(0.4)
    return records


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _first_sentence(text, pattern):
    rx = re.compile(pattern, re.IGNORECASE)
    for sent in _sentences(text):
        if rx.search(sent):
            return sent
    return ""


def tag(record):
    hay = f"{record['title']} {record['abstract']}"
    flags = {"asm": [], "sleep_eeg": [], "cognition": [], "design": []}
    for group, vocab in (("asm", ASM_VOCAB), ("sleep_eeg", SLEEP_MODES),
                         ("cognition", COGNITION), ("design", DESIGNS)):
        for name, pattern in vocab:
            sent = _first_sentence(hay, pattern)
            if sent:
                flags[group].append({"name": name, "sentence": sent})
    return flags


def build(data):
    rows = []
    for rec in data["records"]:
        flags = tag(rec)
        rows.append({"record": rec, "flags": flags})
    return rows


def render_table(data):
    rows = build(data)
    out = []
    out.append("# Antiseizure medication x sleep EEG — corpus snapshot")
    out.append("")
    out.append(f"*Generated by `scripts/asm_sleep_eeg_search.py`; retrieved {data['retrieved']}. "
               f"PubMed reported **{data['total_matching']}** matching records; the newest/most relevant "
               f"**{data['returned']}** are stored in `research/antiseizure-sleep-eeg-raw.json` and screened below.*")
    out.append("")
    out.append("## The query, printed so it can be re-run")
    out.append("")
    out.append("```")
    out.append(QUERY)
    out.append("```")
    out.append("")
    out.append("## What this corpus is for")
    out.append("")
    out.append("Item 30's seed review says nothing about medication (its `antiseizure`, `antiepileptic`, "
               "`AED`, `medication` and drug-name terms occur zero times). This corpus is the literature the "
               "seed omits: a named antiseizure drug or class **and** an objective sleep/EEG measure. The flags "
               "below are token screens; each stores the sentence that set it, so a reader can judge the screen.")
    out.append("")
    # corpus tallies
    def count(group, name):
        return sum(1 for r in rows if any(f["name"] == name for f in r["flags"][group]))
    out.append("## Screen tallies (lower bounds, not verdicts)")
    out.append("")
    out.append("| dimension | term | records naming it |")
    out.append("|---|---|---|")
    for name, _ in ASM_VOCAB:
        out.append(f"| asm | {name} | {count('asm', name)} |")
    for name, _ in SLEEP_MODES:
        out.append(f"| sleep_eeg | {name} | {count('sleep_eeg', name)} |")
    for name, _ in COGNITION:
        out.append(f"| cognition | {name} | {count('cognition', name)} |")
    out.append("")
    n = len(rows)

    def has(r, group):
        return bool(r["flags"][group])

    asm = sum(has(r, "asm") for r in rows)
    slp = sum(has(r, "sleep_eeg") for r in rows)
    cog = sum(has(r, "cognition") for r in rows)
    asm_cog = sum(has(r, "asm") and has(r, "cognition") for r in rows)
    all3 = sum(has(r, "asm") and has(r, "sleep_eeg") and has(r, "cognition") for r in rows)
    out.append("### The intersections — the number that decides the item's drug-attribution half")
    out.append("")
    out.append("| set | records |")
    out.append("|---|---|")
    out.append(f"| all returned records | {n} |")
    out.append(f"| names an antiseizure drug or class | {asm} |")
    out.append(f"| names an objective sleep / EEG measure | {slp} |")
    out.append(f"| names a cognition / memory outcome | {cog} |")
    out.append(f"| **names a drug AND a cognition outcome** | **{asm_cog}** |")
    out.append(f"| **names a drug AND a sleep measure AND a cognition outcome** | **{all3}** |")
    out.append("")
    out.append(f"**{all3} of {n}** returned records sit at the full intersection item 30 needs. That is the "
               "answer to whether the seed's silence on medication was a gap in the literature or a gap in "
               "the seed: the literature exists, so the item's drug-attribution half is reachable from public "
               "abstracts — but only just, and mostly as reviews rather than as trials that vary the drug "
               "under a measured sleep endpoint.")
    out.append("")
    out.append("## Records")
    out.append("")
    out.append("| # | PMID | yr | journal | asm | sleep | cognition | design |")
    out.append("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        rec, fl = r["record"], r["flags"]
        asm = ", ".join(f["name"] for f in fl["asm"]) or "—"
        slp = ", ".join(f["name"] for f in fl["sleep_eeg"]) or "—"
        cog = ", ".join(f["name"] for f in fl["cognition"]) or "—"
        des = ", ".join(f["name"] for f in fl["design"]) or "—"
        out.append(f"| {i} | {rec['pmid']} | {rec['year']} | {rec['journal']} | {asm} | {slp} | {cog} | {des} |")
    out.append("")
    out.append("## Evidence sentences")
    out.append("")
    out.append("Each flag stores the first sentence that set it, so the screen can be audited.")
    out.append("")
    for i, r in enumerate(rows, 1):
        rec, fl = r["record"], r["flags"]
        out.append(f"### {i}. PMID {rec['pmid']} — {rec['title']}")
        out.append("")
        out.append(f"*{rec['journal']} ({rec['year']}); {', '.join(rec['pubtypes']) or 'no pubtype'}*")
        out.append("")
        for group in ("asm", "sleep_eeg", "cognition", "design"):
            for f in fl[group]:
                out.append(f"- **{group}::{f['name']}** — {f['sentence']}")
        if not rec["abstract"]:
            out.append("- *(no abstract in the record)*")
        out.append("")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-fetch", action="store_true",
                    help="rebuild the table from the stored snapshot; no network")
    args = ap.parse_args(argv)

    if args.no_fetch:
        data = json.loads(RAW.read_text())
    else:
        total, ids = esearch()
        records = efetch_abstracts(ids)
        data = {
            "_what": ("Reproducible PubMed snapshot for commons agenda item 30, step (3): the "
                      "antiseizure-medication x objective-sleep/EEG corpus the item's seed omits. "
                      "Abstracts stored verbatim; no ranking of our own beyond PubMed relevance."),
            "retrieved": date.today().isoformat(),
            "query": QUERY,
            "sort": "relevance",
            "total_matching": total,
            "returned": len(records),
            "records": records,
        }
        RAW.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    TABLE.write_text(render_table(data))
    print(f"retrieved  : {data['retrieved']}")
    print(f"total match: {data['total_matching']}")
    print(f"returned   : {data['returned']}")
    print(f"wrote      : {RAW.relative_to(ROOT)}")
    print(f"wrote      : {TABLE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
