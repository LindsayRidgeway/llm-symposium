#!/usr/bin/env python3
"""Agenda item 30, step (3): the antiseizure-medication x sleep-EEG corpus, as its own corpus.

Item 30's first-step source table found that its seed review — the newest systematic
review on sleep and cognition in adults with epilepsy (PMID 42748517) — never mentions
antiseizure medication: `antiseizure`, `anti-seizure`, `antiepileptic`, `anti-epileptic`,
`medication(s)`, `drug(s)`, `AED(s)` and four common drug names all occur zero times.
The item's own Next action therefore asks for the drug side to be searched as a corpus
of its own rather than as a corner of the sleep-cognition literature. That is what this
script does.

What it produces, and what it deliberately does not:

  * raw JSON — the exact bytes of each Europe PMC response, with HTTP status, byte count
    and sha256, plus every record's title/abstract as returned. The hash is the receipt:
    the offline test re-computes nothing over the network.
  * nothing is summarised here. The companion note
    (`research/sleep-cognition-epilepsy-drug-sleep-corpus.md`) does the reading, and each
    row in it cites a PMID that is in this file with a verbatim fragment.

The mechanical part (which named drug, which named sleep parameter, whether a memory or
cognition outcome is named at all) is computed here rather than by eye, so that a later
wake can disagree with the note and re-run this script to see whether the disagreement is
about the abstracts or about the reading.

Run:  python3 scripts/sleep_cognition_epilepsy_drug_corpus.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "sleep-cognition-epilepsy-drug-sleep-raw.json"
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

# Europe PMC search strings. Kept short and literal so a reader can paste one into the
# web UI and get the same hit count without this script.
DRUGS = (
    'levetiracetam OR lamotrigine OR valproate OR carbamazepine OR perampanel OR '
    'ethosuximide OR topiramate OR zonisamide OR lacosamide OR brivaracetam OR '
    'phenytoin OR gabapentin OR pregabalin OR clobazam OR phenobarbital'
)

QUERIES = [
    {
        "name": "drug_x_sleep_architecture",
        "why": "a named drug measured against a named sleep parameter — the drug side of the "
               "item's question, independent of whether cognition was measured",
        "query": f'(SRC:MED) AND ({DRUGS}) AND ("sleep architecture" OR polysomnography OR '
                 f'"slow wave sleep" OR "slow-wave sleep" OR "sleep spindles" OR '
                 f'"spindle" OR "sleep EEG")',
        "pageSize": 100,
    },
    {
        "name": "drug_x_sleep_x_memory",
        "why": "the mediating claim itself: a drug, a sleep/sleep-EEG parameter and a memory "
               "or cognition outcome named in the same record",
        "query": f'(SRC:MED) AND ({DRUGS}) AND (sleep) AND (memory OR cognition OR '
                 f'consolidation) AND ("sleep architecture" OR polysomnography OR '
                 f'"slow wave" OR "spindle")',
        "pageSize": 100,
    },
    {
        "name": "aed_class_review_sleep",
        "why": "the class-level reviews, which are where the field states what is believed "
               "about drug effects on sleep — the layer the seed review omits",
        "query": f'(SRC:MED) AND (antiseizure OR antiepileptic OR "anti-seizure") AND '
                 f'(sleep) AND (PUB_TYPE:"review" OR "systematic review") AND '
                 f'(polysomnography OR "sleep architecture" OR "slow wave" OR spindle)',
        "pageSize": 100,
    },
    {
        "name": "triad_in_abstract",
        "why": "the item's three terms forced into the abstract at once — sleep, a memory or "
               "cognition outcome, and a named or class-level antiseizure treatment. The "
               "first three queries sort by citation and therefore surface what the field "
               "cites; this one asks how many records anywhere in MEDLINE state the triad",
        "query": '(SRC:MED) AND (ABSTRACT:"sleep") AND (ABSTRACT:"memory" OR ABSTRACT:"cognition" '
                 'OR ABSTRACT:"consolidation") AND (ABSTRACT:"antiepileptic" OR '
                 'ABSTRACT:"antiseizure" OR ABSTRACT:"anti-seizure" OR ABSTRACT:"anticonvulsant" '
                 'OR ABSTRACT:"levetiracetam" OR ABSTRACT:"valproate" OR ABSTRACT:"lamotrigine" '
                 'OR ABSTRACT:"carbamazepine" OR ABSTRACT:"perampanel" OR ABSTRACT:"topiramate" '
                 'OR ABSTRACT:"zonisamide" OR ABSTRACT:"lacosamide" OR ABSTRACT:"brivaracetam" '
                 'OR ABSTRACT:"ethosuximide" OR ABSTRACT:"phenytoin" OR ABSTRACT:"gabapentin" '
                 'OR ABSTRACT:"pregabalin")',
        "pageSize": 100,
    },
]

# Named things the mechanical pass looks for. These are the item's own two halves:
# the drug, the sleep parameter, the memory outcome. A record that names none of a
# category is not evidence for that category, and the note says so instead of guessing.
DRUG_TERMS = [
    "levetiracetam", "lamotrigine", "valproate", "valproic acid", "carbamazepine",
    "perampanel", "ethosuximide", "topiramate", "zonisamide", "lacosamide",
    "brivaracetam", "phenytoin", "gabapentin", "pregabalin", "clobazam",
    "phenobarbital", "oxcarbazepine", "eslicarbazepine", "cenobamate", "vigabatrin",
    "tiagabine", "rufinamide", "felbamate", "stiripentol",
]
SLEEP_TERMS = [
    "slow wave", "slow-wave", "sws", "spindle", "rem sleep", "rem sleep",
    "sleep efficiency", "sleep latency", "sleep architecture", "polysomnograph",
    "nrem", "sleep stage", "k-complex", "delta power", "sleep eeg", "cyclic alternating",
]
CLASS_TERMS = [
    "antiepileptic", "anti-epileptic", "antiseizure", "anti-seizure", "asd", "aeds",
    "aed ", "aed,", "aed.", "anticonvulsant",
]
MEMORY_TERMS = [
    "memory", "cognition", "cognitive", "consolidation", "recall", "learning",
]


def _fetch(query: str, page_size: int) -> tuple[dict, dict]:
    params = {
        "query": query,
        "format": "json",
        "pageSize": str(page_size),
        "resultType": "core",
        "sort": "CITED desc",
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "llm-symposium/desi research"})
    for attempt in (1, 2, 3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                body = r.read()
                status = r.status
            break
        except Exception as exc:  # noqa: BLE001 - retried, then recorded as a gap
            if attempt == 3:
                return {"url": url, "http_status": None, "error": repr(exc)}, {}
            time.sleep(4)
    receipt = {
        "url": url,
        "http_status": status,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
    }
    return receipt, json.loads(body.decode("utf-8", "replace"))


def _hits(text: str, terms: list[str]) -> list[str]:
    low = (text or "").lower()
    return sorted({t for t in terms if t in low})


def main() -> int:
    artefact = {
        "artifact": "sleep-cognition-epilepsy-drug-sleep-raw",
        "generated_from": "scripts/sleep_cognition_epilepsy_drug_corpus.py",
        "note": (
            "Europe PMC search responses, verbatim. Each query's exact bytes are recorded "
            "with sha256; abstracts are stored, full texts are not. The companion note "
            "research/sleep-cognition-epilepsy-drug-sleep-corpus.md reads this file, and "
            "tests/test_sleep_drug_sleep_corpus.py pins the fragments it quotes."
        ),
        "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "queries": [],
    }
    for q in QUERIES:
        receipt, payload = _fetch(q["query"], q["pageSize"])
        entry = {
            "name": q["name"],
            "why": q["why"],
            "query": q["query"],
            "request": receipt,
            "hit_count": payload.get("hitCount"),
            "returned": 0,
            "records": [],
        }
        for rec in payload.get("resultList", {}).get("result", []):
            abstract = rec.get("abstractText") or ""
            blob = abstract + " " + (rec.get("title") or "")
            entry["records"].append({
                "pmid": rec.get("pmid"),
                "pmcid": rec.get("pmcid"),
                "doi": rec.get("doi"),
                "title": rec.get("title"),
                "journal": (rec.get("journalInfo") or {}).get("journal", {}).get("title")
                           or rec.get("journalTitle"),
                "pub_year": rec.get("pubYear"),
                "first_author": (rec.get("authorString") or "").split(",")[0],
                "pub_type": rec.get("pubTypeList", {}).get("pubType", []),
                "is_open_access": rec.get("isOpenAccess"),
                "has_abstract": bool(abstract),
                "abstract": abstract,
                "drug_terms": _hits(blob, DRUG_TERMS),
                "class_terms": _hits(blob, CLASS_TERMS),
                "sleep_terms": _hits(blob, SLEEP_TERMS),
                "memory_terms": _hits(blob, MEMORY_TERMS),
            })
        entry["returned"] = len(entry["records"])
        artefact["queries"].append(entry)
        print(f"{q['name']}: hitCount={entry['hit_count']} returned={entry['returned']} "
              f"http={receipt.get('http_status')}", file=sys.stderr)

    OUT.write_text(json.dumps(artefact, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
