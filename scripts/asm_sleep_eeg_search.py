#!/usr/bin/env python3
"""The antiseizure-medication x sleep-EEG corpus, for agenda item 30 step (3).

Written 2026-10-07 (Desi, clock wake). This is step 3 of the item's own next-action
list, set out in `research/sleep-cognition-epilepsy-seed.md` §7:

    "Search the antiseizure-medication x sleep-EEG literature as a separate corpus,
     since the seed is silent on it. Without this the item cannot answer its own
     question, whatever the sleep-cognition review says."

Why it matters. The item's source review (PMID 42748517) contains **zero** occurrences of
any antiseizure-medication term (`seed_asm_total = 0`, measured 2026-09-30). The item's
headline question -- how much of the memory deficit in epilepsy is attributable to the
*drugs* rather than to the disease or to sleep -- therefore cannot be answered from its
own seed. This script builds the missing corpus: the set of PubMed records at the
intersection of epilepsy, a *named* antiseizure drug, and a sleep-subject heading, and it
counts, with no hand-picking, how many of them actually measure a sleep-EEG quantity, a
memory/cognition outcome, and a contrast in drug exposure.

WHAT THIS IS. A keyword census of public abstracts. A term in an abstract is not a
measured outcome and not a study design; every flag stores the sentence that set it
(`evidence`), and no claim rests on a flag that a reader cannot check against the stored
record. It is *not* a reading of any paper.

Deliberate design choices, stated so a stranger can disagree with them:
  * The corpus requires the drug name in title/abstract *and* a sleep-meSH subject
    heading, so the intersection is indexed-as-sleep, not merely containing the word.
    The alternative arms (class terms instead of named drugs; sleep in [tiab] instead of
    meSH) are counted in the same run and reported beside the chosen one, so the choice
    of query is auditable rather than silent.
  * It does NOT reuse any other arm's records; it fetches its own, so every flag here is
    reproducible from this one file.

Usage:
    python3 scripts/asm_sleep_eeg_search.py             # fetch, write raw JSON
    python3 scripts/asm_sleep_eeg_search.py --no-fetch  # re-tag the stored record offline
"""

from __future__ import annotations

import argparse
import hashlib
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
RAW = ROOT / "research" / "asm-sleep-eeg-raw.json"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = "llm-symposium-desi/1.0 (https://github.com/LindsayRidgeway/llm-symposium)"
RETMAX = 1000
BATCH = 200

# ---- query arms -------------------------------------------------------------------

EPILEPSY = (
    '(epilepsy[tiab] OR epileptic[tiab] OR epilepsies[tiab] OR seizure[tiab] '
    'OR seizures[tiab] OR "epilepsy"[MeSH Terms])'
)

# Named drugs, not class terms. A class term ("antiepileptic") appears in the background
# of nearly every epilepsy paper, so it makes the intersection meaningless (measured
# 2026-10-07: class terms give 1,708 tiab hits against 1,063 for named drugs).
NAMED_DRUGS = (
    '(carbamazepine[tiab] OR valproate[tiab] OR "valproic acid"[tiab] OR '
    'levetiracetam[tiab] OR lamotrigine[tiab] OR phenytoin[tiab] OR topiramate[tiab] OR '
    'gabapentin[tiab] OR zonisamide[tiab] OR perampanel[tiab] OR lacosamide[tiab] OR '
    'brivaracetam[tiab] OR ethosuximide[tiab] OR phenobarbital[tiab] OR vigabatrin[tiab] OR '
    'tiagabine[tiab] OR oxcarbazepine[tiab] OR eslicarbazepine[tiab] OR pregabalin[tiab] OR '
    'clobazam[tiab] OR clonazepam[tiab] OR felbamate[tiab] OR stiripentol[tiab] OR '
    'rufinamide[tiab] OR cenobamate[tiab])'
)

CLASS_TERMS = (
    '(antiseizure[tiab] OR "anti-seizure"[tiab] OR antiepileptic[tiab] OR '
    '"anti-epileptic"[tiab] OR anticonvulsant[tiab])'
)

SLEEP_MESH = (
    '(sleep[MeSH Terms] OR polysomnography[MeSH Terms] OR "sleep wake disorders"[MeSH Terms])'
)

SLEEP_TIAB = (
    '(sleep[tiab] OR polysomnograph*[tiab] OR "sleep architecture"[tiab] OR "slow wave"[tiab] '
    'OR "slow waves"[tiab] OR spindle[tiab] OR spindles[tiab] OR "rem sleep"[tiab] '
    'OR "sleep eeg"[tiab] OR "nocturnal eeg"[tiab])'
)

# The chosen corpus: epilepsy AND a named drug AND an indexed-as-sleep subject heading.
CORPUS_QUERY = f"{EPILEPSY} AND {NAMED_DRUGS} AND {SLEEP_MESH}"

# Sensitivity arms -- counted, not fetched. They show what the query choice costs.
REFERENCE_ARMS = {
    "epilepsy_nameddrug_sleepmesh": CORPUS_QUERY,
    "epilepsy_nameddrug_sleeptiab": f"{EPILEPSY} AND {NAMED_DRUGS} AND {SLEEP_TIAB}",
    "epilepsy_classterm_sleeptiab": f"{EPILEPSY} AND {CLASS_TERMS} AND {SLEEP_TIAB}",
    "nameddrug_sleepmesh_no_epilepsy": f"{NAMED_DRUGS} AND {SLEEP_MESH}",
}

# ---- term lists for tagging -------------------------------------------------------
# A term ending in "-" is a prefix match; every other term is a whole-word match.

SLEEP_ARCH_TERMS = [  # objective sleep architecture / continuity
    "sleep architecture", "slow wave-", "slow-wave", "slow oscillation-", "sws",
    "nrem", "rem sleep", "spindle-", "sleep efficiency", "sleep latency",
    "total sleep time", "sleep stage-", "polysomnograph-", "psg",
    "wake after sleep onset", "waso", "sleep fragmentation", "sleep continuity",
    "cyclic alternating pattern", "k-complex", "sleep onset",
]
EEG_TERMS = [  # sleep EEG / epileptiform electrophysiology
    "eeg", "electroencephalogra-", "spindle-", "slow oscillation-", "interictal",
    "epileptiform", "paroxysmal", "spectral power", "power spectrum", "coherence",
    "polysomnograph-",
]
MEMORY_TERMS = [  # a memory / cognition outcome
    "memory", "cognition", "cognitive", "consolidation", "attention", "executive",
    "learning", "recall", "verbal memory", "working memory", "psychomotor",
    "neuropsycholog-", "intelligence",
]
# Design terms that indicate the study contrasts drug exposure rather than merely listing
# the drugs the patients happen to take. Deliberately inclusive; reported as a screen.
DRUG_CONTRAST_TERMS = [
    "withdrawal", "discontinu-", "initiat-", "add-on", "adjunctive", "monotherapy",
    "polytherapy", "dose", "dosage", "titrat-", "drug-naive", "drug naive", "switch",
    "randomi-", "before and after", "pretreatment", "post-treatment", "untreated",
    "treated with", "exposure", "pharmacokinetic",
]
# The spike-wave-activation-in-sleep (SWAS / ESES / CSWS) syndrome cluster. In these
# abstracts "slow-wave sleep" names the condition and "cognitive" is its prognosis, so a
# sleep-architecture + memory keyword hit here is usually the syndrome's own vocabulary,
# not a measured drug effect. Flagged so the census can subtract it and say how much of
# the intersection is really the drug-on-sleep question.
SWAS_TERMS = [
    "spike-wave activation in sleep", "spike wave activation in sleep",
    "spike-wave activation during sleep", "spike and wave activation in sleep",
    "continuous spike", "continuous spikes", "electrical status epilepticus",
    "status epilepticus during sleep", "status epilepticus in sleep", "eses", "csws",
    "spike-wave index", "spike wave index", "landau-kleffner", "electrical status",
    "spike-wave during sleep", "spike and wave during sleep", "slow sleep",
]
ASM_TERMS = [
    "antiseizure", "anti-seizure", "antiepileptic", "anti-epileptic", "anticonvulsant",
    "aed", "aeds", "asm", "carbamazepine", "valproate", "valproic acid",
    "levetiracetam", "lamotrigine", "phenytoin", "topiramate", "gabapentin",
    "zonisamide", "perampanel", "lacosamide", "brivaracetam", "ethosuximide",
    "phenobarbital", "vigabatrin", "tiagabine", "oxcarbazepine", "pregabalin",
    "clobazam", "clonazepam", "cenobamate",
]

TERM_LISTS = {
    "sleep_architecture": SLEEP_ARCH_TERMS,
    "sleep_eeg": EEG_TERMS,
    "memory_cognition": MEMORY_TERMS,
    "drug_contrast": DRUG_CONTRAST_TERMS,
    "asm_named": ASM_TERMS,
    "swas_eses": SWAS_TERMS,
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
RODENT_RE = re.compile(r"\b(rats?|mice|mouse|murine|gerbil)\b", re.I)


def term_patterns(terms):
    out = []
    for t in terms:
        body = re.escape(t[:-1]) if t.endswith("-") else re.escape(t) + r"\b"
        out.append((t, re.compile(r"\b" + body, re.I)))
    return out


PATTERNS = {k: term_patterns(v) for k, v in TERM_LISTS.items()}


def sentences(text):
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]


def first_sentence_with(text, kind):
    """First sentence matching any term of `kind`, plus the term that matched."""
    for s in sentences(text):
        for term, pat in PATTERNS[kind]:
            if pat.search(s):
                return {"term": term, "sentence": s}
    return None


def all_terms_in(text, kind):
    found = []
    for term, pat in PATTERNS[kind]:
        if pat.search(text):
            found.append(term)
    return found


# ---- transport --------------------------------------------------------------------

def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


def esearch(term, retmax=RETMAX):
    params = {"db": "pubmed", "retmode": "json", "retmax": str(retmax), "term": term}
    url = f"{EUTILS}/esearch.fcgi?" + urllib.parse.urlencode(params)
    data = json.loads(_get(url))["esearchresult"]
    return {
        "count": int(data["count"]),
        "pmids": data["idlist"],
        "query_translation": data.get("querytranslation", ""),
    }


def efetch(pmids):
    if not pmids:
        return ""
    params = {"db": "pubmed", "retmode": "xml", "rettype": "abstract", "id": ",".join(pmids)}
    return _get(f"{EUTILS}/efetch.fcgi?" + urllib.parse.urlencode(params))


def parse_records(xml_text):
    out = []
    if not xml_text.strip():
        return out
    root = ET.fromstring(xml_text)

    def txt(el, path):
        node = el.find(path)
        return node.text.strip() if node is not None and node.text else None

    for art in root.findall(".//PubmedArticle"):
        title_el = art.find(".//Article/ArticleTitle")
        title = "".join(title_el.itertext()).strip() if title_el is not None else ""
        parts = []
        for ab in art.findall(".//Abstract/AbstractText"):
            label = ab.get("Label")
            body = "".join(ab.itertext()).strip()
            parts.append(f"{label}: {body}" if label else body)
        out.append({
            "pmid": txt(art, ".//MedlineCitation/PMID"),
            "title": title,
            "journal": txt(art, ".//Journal/ISOAbbreviation") or txt(art, ".//Journal/Title") or "",
            "year": txt(art, ".//JournalIssue/PubDate/Year")
                    or txt(art, ".//JournalIssue/PubDate/MedlineDate") or "",
            "abstract_plain": " ".join(parts).strip(),
            "publication_types": [p.text.strip() for p in art.findall(".//PublicationTypeList/PublicationType") if p.text],
            "mesh": [m.text.strip() for m in art.findall(".//MeshHeadingList/MeshHeading/DescriptorName") if m.text],
        })
    return out


# ---- classification ---------------------------------------------------------------

def classify_subject(rec):
    """Review / protocol / animal / human-primary. `Humans[MeSH]` is not a human filter:
    rodent studies carry both flags (measured 2026-09-29 in the pain arm)."""
    ptypes = [p.lower() for p in rec.get("publication_types", [])]
    mesh = rec.get("mesh", [])
    title = rec.get("title", "")
    is_review = any("review" in p for p in ptypes) or "systematic review" in title.lower()
    is_protocol = any("protocol" in p for p in ptypes) or "protocol" in title.lower()
    is_animal = ("Animals" in mesh) or bool(RODENT_RE.search(title))
    return {
        "abstract_present": bool(rec.get("abstract_plain", "").strip()),
        "is_review": is_review,
        "is_protocol": is_protocol,
        "is_animal_subject": is_animal,
        "is_human_primary": not (is_review or is_protocol or is_animal),
    }


def classify(rec):
    text = f'{rec["title"]}. {rec["abstract_plain"]}'
    sleep_arch = first_sentence_with(text, "sleep_architecture")
    sleep_eeg = first_sentence_with(text, "sleep_eeg")
    mem = first_sentence_with(text, "memory_cognition")
    contrast = first_sentence_with(text, "drug_contrast")
    return {
        "asm_named_terms": all_terms_in(text, "asm_named"),
        "sleep_architecture": sleep_arch,
        "sleep_eeg": sleep_eeg,
        "memory_cognition": mem,
        "drug_contrast": contrast,
        "swas_eses": first_sentence_with(text, "swas_eses"),
        "has_sleep_measure": sleep_arch is not None or sleep_eeg is not None,
        "has_sleep_architecture": sleep_arch is not None,
        "has_memory_outcome": mem is not None,
        "has_drug_contrast": contrast is not None,
        "has_swas_eses": first_sentence_with(text, "swas_eses") is not None,
    }


def all_three(r):
    return r["has_sleep_measure"] and r["has_memory_outcome"] and r["has_drug_contrast"]


def tally(records):
    n = len(records)
    human = [r for r in records if r["is_human_primary"]]
    human_sleep = [r for r in human if r["has_sleep_architecture"]]
    human_sleep_mem = [r for r in human_sleep if r["has_memory_outcome"]]
    human_all3 = [r for r in human if all_three(r)]
    human_sa_mem_nonswas = [r for r in human_sleep_mem if not r["has_swas_eses"]]
    years = sorted(int(r["year"][:4]) for r in records if r["year"][:4].isdigit())
    return {
        "n_records": n,
        "n_abstract_missing": sum(1 for r in records if not r["abstract_present"]),
        "n_review": sum(1 for r in records if r["is_review"]),
        "n_protocol": sum(1 for r in records if r["is_protocol"]),
        "n_animal_subject": sum(1 for r in records if r["is_animal_subject"]),
        "n_human_primary": len(human),
        "n_any_sleep_measure": sum(1 for r in records if r["has_sleep_measure"]),
        "n_sleep_architecture": sum(1 for r in records if r["has_sleep_architecture"]),
        "n_memory_outcome": sum(1 for r in records if r["has_memory_outcome"]),
        "n_drug_contrast": sum(1 for r in records if r["has_drug_contrast"]),
        "n_all_three": sum(1 for r in records if all_three(r)),
        "n_human_sleep_architecture": len(human_sleep),
        "n_human_sleep_arch_and_memory": len(human_sleep_mem),
        "n_human_all_three": len(human_all3),
        "n_swas_eses_any": sum(1 for r in records if r["has_swas_eses"]),
        "n_human_swas_eses": sum(1 for r in human if r["has_swas_eses"]),
        "n_human_sleep_arch_and_memory_non_swas": len(human_sa_mem_nonswas),
        "pmids_human_sleep_arch_memory_non_swas": sorted(r["pmid"] for r in human_sa_mem_nonswas),
        "year_min": years[0] if years else None,
        "year_max": years[-1] if years else None,
        "pmids_human_all_three": sorted(r["pmid"] for r in human_all3),
        "pmids_sleep_arch_and_memory": sorted(r["pmid"] for r in human_sleep_mem),
    }


def build():
    corpus = esearch(CORPUS_QUERY)
    time.sleep(0.4)
    # One authoritative fetch, batched, with the sha256 of the exact bytes classified.
    records, batches = [], []
    for i in range(0, len(corpus["pmids"]), BATCH):
        chunk = corpus["pmids"][i:i + BATCH]
        xml = efetch(chunk)
        batches.append({
            "ids": chunk,
            "sha256": hashlib.sha256(xml.encode("utf-8")).hexdigest(),
            "bytes": len(xml.encode("utf-8")),
        })
        records.extend(parse_records(xml))
        time.sleep(0.4)

    for r in records:
        r.update(classify(r))
        r.update(classify_subject(r))

    ref = {}
    for name, term in REFERENCE_ARMS.items():
        ref[name] = {"query": term, "total_matching": esearch(term, retmax=0)["count"]}
        time.sleep(0.4)

    record = {
        "generated": date.today().isoformat(),
        "source": "PubMed E-utilities (esearch + efetch)",
        "corpus_query": CORPUS_QUERY,
        "corpus_total_matching": corpus["count"],
        "corpus_fetched": len(corpus["pmids"]),
        "query_translation": corpus["query_translation"],
        "batches": batches,
        "reference_arms": ref,
        "records": records,
        "tallies": tally(records),
    }
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fetch", action="store_true", help="re-tag the stored record offline")
    args = ap.parse_args()

    if args.no_fetch:
        record = json.loads(RAW.read_text())
        record["records"] = [dict(r, **classify(r), **classify_subject(r)) for r in record["records"]]
        record["tallies"] = tally(record["records"])
    else:
        record = build()

    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(record, indent=1) + "\n")
    t = record["tallies"]
    print(f"wrote {RAW.relative_to(ROOT)}")
    print(f"  corpus: {record['corpus_total_matching']} matching, {record['corpus_fetched']} fetched")
    print(f"  human primary: {t['n_human_primary']}; sleep-architecture: {t['n_human_sleep_architecture']}; "
          f"+memory: {t['n_human_sleep_arch_and_memory']}; all three: {t['n_human_all_three']}")


if __name__ == "__main__":
    main()
