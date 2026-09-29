#!/usr/bin/env python3
"""Reproducible PubMed search for agenda item 32 (affective pain neuromodulation).

Written 2026-09-29 (Desi, clock wake). Item 32 asks whether acupuncture and
vagus-nerve stimulation (VNS) improve the *affective* burden of chronic pain through a
shared brainstem-limbic pathway, distinguishable from any effect on nociceptive intensity.

Its first next action is a search plus a first evidence table. This script is the
reproducible half of that: it runs two dated PubMed queries (an acupuncture arm and a VNS
arm, both restricted to human studies in chronic/somatoform pain), stores every fetched
record verbatim, and tags each record with three keyword flags so the table can be built
and audited rather than asserted:

  affective      - the abstract uses affective/emotional outcome vocabulary
  biomarker      - the abstract names a neural or autonomic measurement
  intensity      - the abstract names a pain-intensity instrument

WHAT THIS IS NOT. Token presence in an abstract is a *screen*, not a reading. "Anxiety"
can appear only in an exclusion criterion; "fMRI" can appear only in a limitation.
So the record stores, for every flag it sets, the first sentence that set it, and the
markdown table prints those sentences. The counts are a lower bound on how many papers
report the thing, and a hypothesis about how many do not - not a verdict.

Usage:
    python3 scripts/affective_pain_search.py                 # fetch, write the raw record
    python3 scripts/affective_pain_search.py --no-fetch      # re-tag the stored record offline
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
RAW = ROOT / "research" / "affective-pain-neuromodulation-raw.json"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = "llm-symposium-desi/1.0 (https://github.com/LindsayRidgeway/llm-symposium)"
RETMAX = 80

PAIN = (
    '("chronic pain"[tiab] OR "chronic pain"[MeSH Terms] OR fibromyalgia[tiab] '
    'OR "somatoform"[tiab] OR "somatic symptom"[tiab] OR "persistent pain"[tiab] '
    'OR "chronic widespread pain"[tiab] OR "medically unexplained"[tiab])'
)

ARMS = {
    # arm A - needle/electroacupuncture
    "acupuncture": (
        '(acupuncture[tiab] OR electroacupuncture[tiab] OR "acupuncture therapy"[MeSH Terms])'
    ),
    # arm B - implanted and transcutaneous vagus-nerve stimulation
    "vns": (
        '("vagus nerve stimulation"[tiab] OR "vagal nerve stimulation"[tiab] '
        'OR "transcutaneous auricular vagus"[tiab] OR "transcutaneous vagus"[tiab] '
        'OR "auricular vagus"[tiab] OR "vagus nerve stimulation"[MeSH Terms])'
    ),
}

# Term lists. A term ending in "-" is a prefix match; every other term is matched
# as a whole word (so "vas" cannot fire on "vascular" and "pet" cannot fire on "carpet").
AFFECTIVE_TERMS = [
    "affective", "emotion-", "catastrophiz-", "anxiety", "anxious", "depress-",
    "mood", "unpleasantness", "distress", "fear", "anger", "negative affect",
    "pain-related emotion", "psychological",
]
BIOMARKER_TERMS = [
    "fmri", "functional magnetic resonance", "functional connectivity", "bold",
    "eeg", "electroencephalogra-", "event-related potential", "erp", "meg", "pet",
    "positron emission", "heart rate variability", "hrv",
    "skin conductance", "galvanic skin", "pupil", "pupillometry", "autonomic",
    "vagal tone", "insula", "amygdala", "anterior cingulate", "cingulate",
    "prefrontal", "brainstem", "locus coeruleus", "nucleus tractus",
    "nucleus of the solitary", "periaqueductal", "thalamus", "mu-opioid",
    "neural", "neuroimaging", "resting-state", "somatosensory",
]
INTENSITY_TERMS = [
    "pain intensity", "intensity of pain", "vas", "visual analog", "visual analogue",
    "numeric rating scale", "nrs", "pain severity", "pain score", "brief pain inventory",
    "mpq", "mcgill pain questionnaire", "pressure pain threshold", "von frey",
    "pain threshold", "numerical rating",
]

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def term_patterns(terms):
    out = []
    for t in terms:
        body = re.escape(t[:-1]) if t.endswith("-") else re.escape(t) + r"\b"
        out.append((t, re.compile(r"\b" + body, re.I)))
    return out


PATTERNS = {
    "affective": term_patterns(AFFECTIVE_TERMS),
    "biomarker": term_patterns(BIOMARKER_TERMS),
    "intensity": term_patterns(INTENSITY_TERMS),
}


def sentences(text):
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]


def first_sentence_with(text, kind):
    """First sentence matching any term of `kind`, plus the term that matched."""
    for s in sentences(text):
        for term, pat in PATTERNS[kind]:
            if pat.search(s):
                return {"term": term, "sentence": s}
    return None


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def esearch(term, retmax=RETMAX, date_from=None, date_to=None):
    params = {"db": "pubmed", "retmode": "json", "retmax": str(retmax), "term": term}
    if date_from and date_to:
        params.update({"datetype": "pdat", "mindate": date_from, "maxdate": date_to})
    url = f"{EUTILS}/esearch.fcgi?" + urllib.parse.urlencode(params)
    data = json.loads(_get(url))["esearchresult"]
    return {"count": int(data["count"]), "pmids": data["idlist"], "query_translation": data.get("querytranslation", "")}


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
    for art in root.findall(".//PubmedArticle"):
        def txt(path):
            el = art.find(path)
            return el.text.strip() if el is not None and el.text else None

        pmid = txt(".//MedlineCitation/PMID")
        title = "".join(art.find(".//Article/ArticleTitle").itertext()).strip() \
            if art.find(".//Article/ArticleTitle") is not None else ""
        journal = txt(".//Journal/ISOAbbreviation") or txt(".//Journal/Title") or ""
        year = txt(".//JournalIssue/PubDate/Year") or txt(".//JournalIssue/PubDate/MedlineDate") or ""
        parts = []
        for ab in art.findall(".//Abstract/AbstractText"):
            label = ab.get("Label")
            body = "".join(ab.itertext()).strip()
            parts.append(f"{label}: {body}" if label else body)
        abstract = " ".join(parts).strip()
        ptypes = [p.text.strip() for p in art.findall(".//PublicationTypeList/PublicationType") if p.text]
        mesh = [m.text.strip() for m in art.findall(".//MeshHeadingList/MeshHeading/DescriptorName") if m.text]
        out.append({
            "pmid": pmid, "title": title, "journal": journal, "year": year,
            "abstract_plain": abstract, "publication_types": ptypes, "mesh": mesh,
        })
    return out


RODENT_RE = re.compile(r"\b(rats?|mice|mouse|murine|gerbil)\b", re.I)


def classify_subject(rec):
    """What kind of paper is this? Needed because `humans[MeSH Terms]` is not a human filter.

    Measured 2026-09-29: rodent electroacupuncture studies in this set carry BOTH the
    'Humans' and the 'Animals' MeSH terms, so the humans filter passes them. The only
    honest way to report a human-evidence count is to subtract them, explicitly, here.
    """
    ptypes = [p.lower() for p in rec.get("publication_types", [])]
    mesh = rec.get("mesh", [])
    title = rec.get("title", "")
    is_review = any("review" in p for p in ptypes)
    is_protocol = any("protocol" in p for p in ptypes) or "protocol" in title.lower()
    is_animal = ("Animals" in mesh) or bool(RODENT_RE.search(title))
    return {
        "abstract_present": bool(rec.get("abstract_plain", "").strip()),
        "is_review": is_review,
        "is_protocol": is_protocol,
        "is_animal_subject": is_animal,
        # an original human study: not a review, not a protocol, not animal-flagged
        "is_human_primary": not (is_review or is_protocol or is_animal),
    }


def classify(rec):
    text = f'{rec["title"]}. {rec["abstract_plain"]}'
    aff = first_sentence_with(text, "affective")
    bio = first_sentence_with(text, "biomarker")
    inten = first_sentence_with(text, "intensity")
    return {
        "affective": aff, "biomarker": bio, "intensity": inten,
        "affective_outcome": aff is not None,
        "neural_or_autonomic_biomarker": bio is not None,
        "pain_intensity_instrument": inten is not None,
        "both_affective_and_biomarker": aff is not None and bio is not None,
    }


def same_sentence_affective_and_biomarker(rec):
    """Sharper proxy: one sentence carrying both an affective term and a biomarker term."""
    text = f'{rec["title"]}. {rec["abstract_plain"]}'
    for s in sentences(text):
        aff = any(p.search(s) for _, p in PATTERNS["affective"])
        bio = any(p.search(s) for _, p in PATTERNS["biomarker"])
        if aff and bio:
            return s
    return None


def build(snapshot_end):
    record = {
        "generated": date.today().isoformat(),
        "source": "PubMed E-utilities (esearch + efetch)",
        "arms": {}, "records": [],
    }
    all_recs = {}
    for arm, arm_query in ARMS.items():
        term = f"{arm_query} AND {PAIN} AND humans[MeSH Terms]"
        res = esearch(term, date_from="2015-01-01", date_to=snapshot_end)
        record["arms"][arm] = {
            "query": term, "total_matching": res["count"],
            "fetched": len(res["pmids"]), "pmids": res["pmids"],
            "query_translation": res["query_translation"],
        }
        time.sleep(0.4)
        recs = parse_records(efetch(res["pmids"]))
        time.sleep(0.4)
        for r in recs:
            r["arm"] = arm
            all_recs[r["pmid"]] = r
    for r in all_recs.values():
        r.update(classify(r))
        r.update(classify_subject(r))
        r["co_mention_sentence"] = same_sentence_affective_and_biomarker(r)
    record["records"] = list(all_recs.values())
    record["tallies"] = tally(record["records"])
    return record


def tally(records):
    n = len(records)
    both = [r for r in records if r["both_affective_and_biomarker"]]
    co = [r for r in records if r.get("co_mention_sentence")]
    neither = [r for r in records if not r["affective_outcome"] and not r["neural_or_autonomic_biomarker"]]
    no_aff = [r for r in records if not r["affective_outcome"]]
    no_bio = [r for r in records if not r["neural_or_autonomic_biomarker"]]
    return {
        "n_records": n,
        "n_affective_outcome": n - len(no_aff),
        "n_neural_or_autonomic_biomarker": n - len(no_bio),
        "n_both_affective_and_biomarker": len(both),
        "n_co_mention_same_sentence": len(co),
        "n_neither": len(neither),
        "n_no_affective_term": len(no_aff),
        "n_no_biomarker_term": len(no_bio),
        "n_review": sum(1 for r in records if r["is_review"]),
        "n_protocol": sum(1 for r in records if r["is_protocol"]),
        "n_animal_subject": sum(1 for r in records if r["is_animal_subject"]),
        "n_human_primary": sum(1 for r in records if r["is_human_primary"]),
        "n_abstract_missing": sum(1 for r in records if not r["abstract_present"]),
        "pmids_both": sorted(r["pmid"] for r in both),
        "pmids_co_mention": sorted(r["pmid"] for r in co),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fetch", action="store_true", help="re-tag the stored record offline")
    ap.add_argument("--snapshot-end", default=date.today().isoformat(),
                    help="latest publication date included (YYYY-MM-DD)")
    args = ap.parse_args()

    if args.no_fetch:
        record = json.loads(RAW.read_text())
        record["records"] = [dict(r, **classify(r), **classify_subject(r))
                             for r in record["records"]]
        record["tallies"] = tally(record["records"])
    else:
        record = build(args.snapshot_end)

    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(record, indent=1) + "\n")
    t = record["tallies"]
    print(f"wrote {RAW.relative_to(ROOT)}  ({t['n_records']} records)")
    for arm, a in record["arms"].items():
        print(f"  {arm}: {a['total_matching']} matching, {a['fetched']} fetched")
    print(f"  affective term: {t['n_affective_outcome']}/{t['n_records']}")
    print(f"  neural/autonomic biomarker term: {t['n_neural_or_autonomic_biomarker']}/{t['n_records']}")
    print(f"  both: {t['n_both_affective_and_biomarker']}  co-mention in one sentence: {t['n_co_mention_same_sentence']}")
    print(f"  neither: {t['n_neither']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
