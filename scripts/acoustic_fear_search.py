#!/usr/bin/env python3
"""Reproducible PubMed search for agenda item 21 (acoustic sleep stimulation and traumatic memory).

Written 2026-10-01 (Desi, clock wake). Item 21 asks a boundary question the commons cannot
answer by argument: closed-loop acoustic stimulation (CLAS) and targeted memory
reactivation (TMR) during slow-wave sleep are being studied as ways to *enhance* memory
consolidation, and that enhancement is treated as a uniform good. Traumatic and
conditioned fear memories consolidate in sleep too. So the question is whether the
acoustic-stimulation literature has ever tested its intervention against a *maladaptive*
memory - and if not, which boundary conditions (stimulation phase, autonomic state,
whether extinction preceded sleep) the two literatures have and have not measured on the
same subjects.

Its first next action is a search plus an evidence table. This script is the reproducible
half: it runs three dated PubMed queries over the intersection of (a) sleep, (b) fear /
emotional-memory vocabulary, and (c) one of three intervention arms - non-specific
acoustic stimulation, cued targeted memory reactivation, or neither (the boundary arm) -
stores every fetched record verbatim, and tags each record so the table can be built and
audited rather than asserted:

  protocol     - what was delivered: non-specific acoustic, cued TMR, or neither/boundary
  memory_type  - which maladaptive-memory vocabulary the paper actually uses
  sleep_phase  - whether the abstract names an oscillatory / staging measurement, and which
  autonomic    - whether it names an autonomic or physiological measure, and which
  fear_outcome - the direction the paper reports for the fear memory, from the sentence
                 that carries it (strengthen / reduce / neither / not stated)

WHAT THIS IS NOT. Token presence in an abstract is a *screen*, not a reading. "Amygdala"
can appear only in a limitation; "spindle" only in a future-work clause. So for every flag
the record stores the first sentence that set it, and the markdown table prints those
sentences next to the flag. The counts are a lower bound on how many papers report the
thing, and a hypothesis about how many do not - not a verdict. This table is a *map of
what was tested*, which is what item 21 needs; the mechanistic claim is not made here.

Usage:
    python3 scripts/acoustic_fear_search.py                 # fetch, write raw record + table
    python3 scripts/acoustic_fear_search.py --no-fetch      # re-tag the stored record offline
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
RAW = ROOT / "research" / "acoustic-sleep-fear-raw.json"
TABLE = ROOT / "research" / "acoustic-sleep-fear-evidence-table.md"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = "llm-symposium-desi/1.0 (https://github.com/LindsayRidgeway/llm-symposium)"
RETMAX = 120

# ---- shared domain filters -------------------------------------------------

# (b) the maladaptive-memory half. This is what makes the search about fear rather than
# about memory in general; every arm is ANDed with it.
FEAR = (
    '("fear conditioning"[tiab] OR "fear extinction"[tiab] OR "fear memory"[tiab] '
    'OR "fear memories"[tiab] OR "fear learning"[tiab] OR "fear recall"[tiab] '
    'OR "fear generalization"[tiab] OR "emotional memory"[tiab] OR "emotional memories"[tiab] '
    'OR "aversive memory"[tiab] OR "threat memory"[tiab] OR "threat conditioning"[tiab] '
    'OR "traumatic memory"[tiab] OR "traumatic memories"[tiab] OR trauma[tiab] '
    'OR "post-traumatic"[tiab] OR posttraumatic[tiab] OR "PTSD"[tiab] OR "intrusive memory"[tiab])'
)

# (a) the sleep half. Deliberately generous: an abstract can report a sleep experiment
# without saying "slow-wave sleep" in the sentence that carries the result.
SLEEP = (
    '("slow-wave sleep"[tiab] OR "slow wave sleep"[tiab] OR "slow oscillation"[tiab] '
    'OR "slow oscillations"[tiab] OR "slow-wave"[tiab] OR "slow wave"[tiab] '
    'OR "NREM"[tiab] OR "non-REM"[tiab] OR "sleep spindles"[tiab] OR "spindle"[tiab] '
    'OR "sleep"[MeSH Terms] OR sleep[tiab] OR nap[tiab])'
)

# (c) three intervention arms.
ARMS = {
    # arm A - stimulation delivered without regard to what was encoded
    "acoustic_non_specific": (
        '(acoustic[tiab] OR "acoustic stimulation"[MeSH Terms] OR "auditory stimulation"[tiab] '
        'OR "closed-loop"[tiab] OR "closed loop"[tiab] OR "pink noise"[tiab] '
        'OR "auditory closed-loop"[tiab] OR "phase-locked"[tiab] OR "0.75 Hz"[tiab] '
        'OR "1 Hz" [tiab] OR "slow oscillation stimulation"[tiab])'
    ),
    # arm B - stimulation cued to a specific prior learning episode
    "tmr_cued": (
        '("targeted memory reactivation"[tiab] OR "targeted reactivation"[tiab] '
        'OR "memory reactivation"[tiab] OR "cued reactivation"[tiab] OR "cueing"[tiab] '
        'OR "cued"[tiab] OR ("odor"[tiab] AND "sleep"[tiab]))'
    ),
    # arm C - the boundary: sleep and fear, with neither acoustic nor cued stimulation.
    # This arm is the one that shows what the two literatures measure *in common*.
    "boundary_no_stimulation": (
        '(consolidation[tiab] OR "reconsolidation"[tiab] OR "sleep-dependent"[tiab] '
        'OR "sleep dependent"[tiab] OR "overnight"[tiab] OR "sleep deprivation"[tiab])'
    ),
}

# ---- tag vocabularies ------------------------------------------------------
# A trailing "-" means prefix match; every other term is a whole word.

PROTOCOL_TERMS = {
    "acoustic_non_specific": [
        "acoustic stimulation", "auditory stimulation", "closed-loop", "closed loop",
        "pink noise", "phase-locked", "phase locked", "tACS", "acoustic",
    ],
    "tmr_cued": [
        "targeted memory reactivation", "targeted reactivation", "memory reactivation",
        "cued reactivation", "cueing", "cued", "odor", "odour", "sound cue", "tone",
        "olfactory",
    ],
}

MEMORY_TYPE_TERMS = [
    ("fear conditioning", ["fear conditioning", "conditioned fear", "fear learning",
                           "threat conditioning", "fear acquisition"]),
    ("fear extinction", ["fear extinction", "extinction learning", "extinction recall",
                         "extinction memory", "extinction retention"]),
    ("fear generalization", ["fear generalization", "generalized fear", "generalisation"]),
    ("reconsolidation", ["reconsolidation", "reconsolidat-"]),
    ("emotional memory", ["emotional memory", "emotional memories", "emotional episodic",
                          "emotional content", "arousing", "valence"]),
    ("trauma / PTSD", ["trauma", "traumatic", "PTSD", "post-traumatic", "posttraumatic",
                       "intrusive memory", "intrusions", "stress disorder"]),
    ("neutral / declarative (comparison)", ["declarative", "word pair", "word-pair",
                                            "paired associate", "neutral memory"]),
]

SLEEP_TERMS = [
    "slow-wave sleep", "slow wave sleep", "slow oscillation", "slow oscillations",
    "slow-wave", "SWS", "NREM", "non-REM", "spindle", "spindles",
    "up-state", "up state", "down-state", "down state", "phase", "polysomnograph-",
    "PSG", "EEG", "REM", "sleep stage", "N2", "N3",
]

AUTONOMIC_TERMS = [
    "skin conductance", "SCR", "galvanic skin", "EDA", "heart rate variability", "HRV",
    "heart rate", "pupil", "pupillometry", "cortisol", "startle", "blood pressure",
    "respiratory", "respiration", "vagal", "autonomic", "electrodermal", "EMG",
    "amygdala",
]

STRENGTHEN_TERMS = [
    "enhanc-", "increas-", "strengthen-", "reinforc-", "potentiat-", "persist-",
    "intrusi-", "spontaneously recover-", "renewal", "return of fear", "relapse",
    "maintain-", "preserv-", "resistan-",
]
REDUCE_TERMS = [
    "reduc-", "attenuat-", "diminish-", "extinguish-", "decreas-", "impair-",
    "disrupt-", "suppress-", "weaken-", "abolish-", "lower-", "inhibit-", "block-",
]

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def term_patterns(terms):
    out = []
    for t in terms:
        body = re.escape(t[:-1]) if t.endswith("-") else re.escape(t) + r"\b"
        out.append((t, re.compile(r"\b" + body, re.I)))
    return out


PROTOCOL_PATTERNS = {k: term_patterns(v) for k, v in PROTOCOL_TERMS.items()}
MEMORY_PATTERNS = [(name, term_patterns(terms)) for name, terms in MEMORY_TYPE_TERMS]
SLEEP_PATTERNS = term_patterns(SLEEP_TERMS)
AUTONOMIC_PATTERNS = term_patterns(AUTONOMIC_TERMS)
STRENGTHEN_PATTERNS = term_patterns(STRENGTHEN_TERMS)
REDUCE_PATTERNS = term_patterns(REDUCE_TERMS)

RODENT_RE = re.compile(r"\b(rats?|mice|mouse|murine|gerbil|rodents?)\b", re.I)


def sentences(text):
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]


def first_sentence_with(text, patterns):
    """First sentence matching any pattern, with the term that matched."""
    for s in sentences(text):
        for term, pat in patterns:
            if pat.search(s):
                return {"term": term, "sentence": s}
    return None


def first_sentence_with_any(text, pattern_groups):
    for s in sentences(text):
        for term, pat in pattern_groups:
            if pat.search(s):
                return {"term": term, "sentence": s}
    return None


def protocol_of(rec):
    """Which intervention, read off the title+abstract text (not off the arm)."""
    text = f'{rec["title"]}. {rec["abstract_plain"]}'
    hits = {}
    for kind, pats in PROTOCOL_PATTERNS.items():
        hit = first_sentence_with(text, pats)
        if hit:
            hits[kind] = hit
    if "acoustic_non_specific" in hits and "tmr_cued" in hits:
        kind = "acoustic+tmr"
    elif "acoustic_non_specific" in hits:
        kind = "acoustic_non_specific"
    elif "tmr_cued" in hits:
        kind = "tmr_cued"
    else:
        kind = "no_stimulation_boundary"
    return {"protocol": kind, "protocol_hits": hits}


def memory_type_of(text):
    for name, pats in MEMORY_PATTERNS:
        hit = first_sentence_with(text, pats)
        if hit:
            return {"memory_type": name, "memory_type_sentence": hit["sentence"],
                    "memory_type_term": hit["term"]}
    return {"memory_type": "none found", "memory_type_sentence": None, "memory_type_term": None}


def fear_outcome_of(rec):
    """Direction reported for the fear memory, from the sentence that carries the fear term."""
    text = f'{rec["title"]}. {rec["abstract_plain"]}'
    fear_pats = term_patterns(
        ["fear", "threat", "trauma", "traumatic", "PTSD", "aversive", "anxiety",
         "emotional memory", "intrusi-"]
    )
    for s in sentences(text):
        if not any(p.search(s) for _, p in fear_pats):
            continue
        strength = [t for t, p in STRENGTHEN_PATTERNS if p.search(s)]
        reduce = [t for t, p in REDUCE_PATTERNS if p.search(s)]
        if strength and reduce:
            direction = "both (ambiguous)"
        elif strength:
            direction = "strengthen/retain"
        elif reduce:
            direction = "reduce/extinguish"
        else:
            direction = "fear term present, direction unstated"
        return {"fear_outcome_direction": direction, "fear_outcome_sentence": s,
                "fear_strengthen_terms": strength, "fear_reduce_terms": reduce}
    return {"fear_outcome_direction": "no fear outcome sentence",
            "fear_outcome_sentence": None,
            "fear_strengthen_terms": [], "fear_reduce_terms": []}


def classify_subject(rec):
    """Human primary vs animal vs review vs protocol. `humans[MeSH]` is not a human filter:
    rodent studies in this literature carry both `Humans` and `Animals` MeSH terms."""
    ptypes = [p.lower() for p in rec.get("publication_types", [])]
    mesh = rec.get("mesh", [])
    title = rec.get("title", "")
    is_review = any("review" in p for p in ptypes) or any("meta-analysis" in p for p in ptypes)
    is_protocol = any("protocol" in p for p in ptypes) or "protocol" in title.lower()
    is_animal = ("Animals" in mesh) or bool(RODENT_RE.search(title))
    return {
        "abstract_present": bool(rec.get("abstract_plain", "").strip()),
        "is_review": is_review,
        "is_protocol": is_protocol,
        "is_animal_subject": is_animal,
        "is_human_primary": not (is_review or is_protocol or is_animal),
    }


# Title-level vocabulary. A title is the author's own claim about the paper, so these
# three flags are far more precise than the abstract screen and are what the "core set"
# below is built from. Deliberately conservative.
TITLE_SLEEP = re.compile(
    r"sleep|nap|nrem|non-?rem|slow[- ]wave|slow oscillation|spindle|nocturnal|overnight", re.I)
TITLE_FEAR = re.compile(
    r"fear|threat|trauma|ptsd|post-?traumatic|emotional memor|aversive|intrusi|extinction|"
    r"anxiety|reconsolidat", re.I)
TITLE_STIM = re.compile(
    r"acoustic|auditory|closed-?loop|pink noise|stimulat|reactivat|cue|odor|odour|tone|"
    r"targeted memory", re.I)


def title_flags(rec):
    t = rec.get("title", "")
    f = {"title_sleep": bool(TITLE_SLEEP.search(t)),
         "title_fear": bool(TITLE_FEAR.search(t)),
         "title_stim": bool(TITLE_STIM.search(t))}
    f["title_core"] = f["title_stim"] and (f["title_fear"] or f["title_sleep"])
    return f


def classify(rec):
    text = f'{rec["title"]}. {rec["abstract_plain"]}'
    sleep_hit = first_sentence_with(text, SLEEP_PATTERNS)
    auto_hit = first_sentence_with(text, AUTONOMIC_PATTERNS)
    out = {}
    out.update(protocol_of(rec))
    out.update(memory_type_of(text))
    out.update(classify_subject(rec))
    out.update(title_flags(rec))
    out.update(fear_outcome_of(rec))
    out["sleep_phase"] = sleep_hit
    out["sleep_phase_named"] = sleep_hit is not None
    out["autonomic"] = auto_hit
    out["autonomic_measured"] = auto_hit is not None
    return out


# ---- fetch -----------------------------------------------------------------


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
    return {"count": int(data["count"]), "pmids": data["idlist"],
            "query_translation": data.get("querytranslation", "")}


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

        title_el = art.find(".//Article/ArticleTitle")
        title = "".join(title_el.itertext()).strip() if title_el is not None else ""
        parts = []
        for ab in art.findall(".//Abstract/AbstractText"):
            label = ab.get("Label")
            body = "".join(ab.itertext()).strip()
            parts.append(f"{label}: {body}" if label else body)
        out.append({
            "pmid": txt(".//MedlineCitation/PMID"),
            "title": title,
            "journal": txt(".//Journal/ISOAbbreviation") or txt(".//Journal/Title") or "",
            "year": txt(".//JournalIssue/PubDate/Year")
                    or txt(".//JournalIssue/PubDate/MedlineDate") or "",
            "abstract_plain": " ".join(parts).strip(),
            "publication_types": [p.text.strip() for p in
                                  art.findall(".//PublicationTypeList/PublicationType") if p.text],
            "mesh": [m.text.strip() for m in
                     art.findall(".//MeshHeadingList/MeshHeading/DescriptorName") if m.text],
        })
    return out


def build(snapshot_end, date_from):
    record = {"generated": date.today().isoformat(),
              "source": "PubMed E-utilities (esearch + efetch)",
              "query_window": f"{date_from}..{snapshot_end}", "arms": {}, "records": []}
    all_recs = {}
    for arm, arm_query in ARMS.items():
        term = f"{arm_query} AND {SLEEP} AND {FEAR}"
        res = esearch(term, date_from=date_from, date_to=snapshot_end)
        record["arms"][arm] = {"query": term, "total_matching": res["count"],
                               "fetched": len(res["pmids"]), "pmids": res["pmids"],
                               "query_translation": res["query_translation"]}
        time.sleep(0.5)
        for r in parse_records(efetch(res["pmids"])):
            r["arms"] = sorted(set(all_recs.get(r["pmid"], {}).get("arms", []) + [arm]))
            all_recs[r["pmid"]] = r
        time.sleep(0.5)
    for r in all_recs.values():
        r.update(classify(r))
    record["records"] = sorted(all_recs.values(), key=lambda r: (r.get("year") or "", r["pmid"]))
    record["tallies"] = tally(record["records"])
    return record


def tally(records):
    from collections import Counter
    t = {
        "n_records": len(records),
        "n_abstract_missing": sum(1 for r in records if not r["abstract_present"]),
        "n_human_primary": sum(1 for r in records if r["is_human_primary"]),
        "n_animal_subject": sum(1 for r in records if r["is_animal_subject"]),
        "n_review": sum(1 for r in records if r["is_review"]),
        "n_protocol": sum(1 for r in records if r["is_protocol"]),
        "n_sleep_phase_named": sum(1 for r in records if r["sleep_phase_named"]),
        "n_autonomic_measured": sum(1 for r in records if r["autonomic_measured"]),
        "n_sleep_phase_and_autonomic": sum(
            1 for r in records if r["sleep_phase_named"] and r["autonomic_measured"]),
        "n_title_core": sum(1 for r in records if r["title_core"]),
        "n_title_core_human": sum(1 for r in records if r["title_core"] and r["is_human_primary"]),
        "by_protocol": dict(Counter(r["protocol"] for r in records)),
        "by_protocol_title_core": dict(Counter(r["protocol"] for r in records if r["title_core"])),
        "by_memory_type": dict(Counter(r["memory_type"] for r in records)),
        "by_direction": dict(Counter(r["fear_outcome_direction"] for r in records)),
        "pmids_sleep_phase_and_autonomic": sorted(
            r["pmid"] for r in records if r["sleep_phase_named"] and r["autonomic_measured"]),
    }
    return t


# ---- markdown ---------------------------------------------------------------


def esc(s):
    if not s:
        return ""
    return s.replace("|", "\\|").replace("\n", " ").strip()


def clip(s, n=260):
    s = esc(s)
    return s if len(s) <= n else s[: n - 1].rstrip() + "\u2026"


def row(r):
    proto = {
        "acoustic_non_specific": "acoustic (non-specific)",
        "tmr_cued": "TMR (cued)",
        "acoustic+tmr": "acoustic + TMR",
        "no_stimulation_boundary": "\u2014 (boundary)",
    }[r["protocol"]]
    sp = f"yes: {r['sleep_phase']['term']}" if r["sleep_phase_named"] else "no"
    au = f"yes: {r['autonomic']['term']}" if r["autonomic_measured"] else "no"
    return "| {pmid} | {year} | {journal} | {proto} | {mem} | {sp} | {au} | {dirn} |".format(
        pmid=r["pmid"], year=esc(r.get("year", "")), journal=esc(r.get("journal", "")),
        proto=proto, mem=esc(r["memory_type"]), sp=sp, au=au,
        dirn=esc(r["fear_outcome_direction"]))


HEADER = ("| PMID | Year | Journal | Protocol | Maladaptive-memory vocabulary | "
          "Sleep-phase measure | Autonomic measure | Fear-outcome direction |")
SEP = "|---|---|---|---|---|---|---|---|"

# Written by Desi, 2026-10-01, from the records this script fetched. Kept in the
# generator so the reading and the data it rests on cannot drift apart silently.
# Every claim below is checkable against the core-set table and the raw JSON.
READING = """## Reading (Desi, 2026-10-01)

The abstract screen is noisy - the `acoustic_non_specific` arm in particular drags in
tinnitus, hearing-loss and railway-noise epidemiology, where "acoustic", "trauma" and
"sleep" co-occur as topic words and nothing is stimulated to change a memory. The
**core set** below is the fix: records whose *title* names an intervention and also names
sleep or a fear/emotional memory. It is small and it is checkable.

Three things are true of that core set, and they answer item 21's question directly.

1. **The intervention that is deployed without regard to content has not been tested
   against a maladaptive memory in humans.** Closed-loop acoustic stimulation (pink noise
   or tone bursts phase-locked to the slow-oscillation up-state, with no cue tied to any
   learning episode) is a memory-*enhancement* literature: Ngo, Papalambros, Marshall and
   their descendants test neutral declarative material. Searching all three arms for a
   human study that pairs non-specific acoustic slow-wave stimulation with explicit
   fear-conditioning, fear-extinction or reconsolidation vocabulary returns **no human
   trial**. The single record of any species combining the two is a 2026 hypothesis paper.
   The dangerous experiment - dose the oscillation, encode a fear memory first, measure the
   fear afterwards - has not been run in people.

2. **The intervention that *has* been tested against fear is, by construction, the one
   that cannot be content-blind.** Every human fear-memory/sleep stimulation study in this
   set is targeted memory reactivation: an auditory or olfactory cue that was previously
   paired with the specific memory. `25348121` (CS exposure in SWS and fear extinction),
   `26071676` (extinction-associated tone in SWS vs wake), `35845468` (TMR in social
   anxiety), `39116885` (TMR with closed-loop slow-oscillation phase targeting in PTSD
   patients after EMDR), `39052838` (weakening aversive memories by reactivating positive
   interfering memories). So the safety question - *does stimulation strengthen trauma?* -
   has been asked almost entirely of an intervention that selects its target, and the
   literature's reassurance is about a different thing from the technology at risk.

3. **Where the boundary *has* been probed, direction depends on sleep stage and on what
   preceded sleep, not on stimulation per se.** the same cue delivered in NREM weakened
   fear in mice (`28401950`) while SWS reactivation enhanced emotional memory and REM
   reactivation impaired it in humans (`36909630`); reactivation after extinction training
   extinguished, reactivation without it renewed (`25669194`, an editorial framing exactly
   this fork). Phase and stage are the moderators. A protocol that stimulates the up-state
   of every slow oscillation, for everyone, is blind to both.

**The missing experiment, stated as item 21 asked.** The gap is not a mechanism; it is a
population and a control arm. Take a pre-registered human sample with a controlled fear
memory (differential conditioning the evening before), randomise to (A) slow-oscillation
up-phase acoustic stimulation without any memory cue, (B) sham, (C) the same acoustic
stimulation in a non-trauma-exposed sample, and measure next-morning extinction retention,
fear generalisation (SCR / pupillometry) and nocturnal autonomic state. Two records in
this set already measure the required *association* without stimulating: `39974936` and
`40902948` find slow-oscillation-spindle coupling tracks fear-extinction retention in
trauma-exposed individuals. That is the read-out a stimulation trial needs, and no one has
turned the stimulator on.
"""


def section(title, recs):
    if not recs:
        return f"### {title}\n\n_None in this set._\n"
    lines = [f"### {title} ({len(recs)})", "", HEADER, SEP]
    lines += [row(r) for r in recs]
    lines.append("")
    return "\n".join(lines)


def render(record):
    recs = record["records"]
    t = record["tallies"]
    L = []
    L.append("# Acoustic Sleep Stimulation and Traumatic Memory \u2014 PubMed Source Table")
    L.append("")
    L.append("*Agenda item 21 (adopted 2026-09-16). Generated by "
             "`scripts/acoustic_fear_search.py`; the raw records are in "
             "`research/acoustic-sleep-fear-raw.json`. Rebuild with "
             "`python3 scripts/acoustic_fear_search.py`.*")
    L.append("")
    L.append(f"**Search window:** {record['query_window']} (PubMed publication dates). "
             f"**Records fetched:** {t['n_records']}. "
             f"**Generated:** {record['generated']}.")
    L.append("")
    L.append("Every arm is the intersection of three clause sets: a **sleep** clause, a "
             "**fear / emotional-memory** clause, and one **intervention** clause. "
             "The three arms partition the literature the question lives in:")
    for arm, a in record["arms"].items():
        L.append(f"- `{arm}` \u2014 {a['total_matching']} matching, {a['fetched']} fetched")
    L.append("")
    L.append("## What this table is, and is not")
    L.append("")
    L.append("The flags are a **screen over abstracts**, not a reading of the papers. "
             "Each flag is set from the first sentence that carries it, and the sentences "
             "are printed below the tables so any flag can be checked or overruled. "
             "`no` means *the abstract does not say so*, never *the study did not do it*.")
    L.append("")
    L.append("## Counts")
    L.append("")
    L.append(f"- Records with an abstract: {t['n_records'] - t['n_abstract_missing']} / {t['n_records']} "
             f"({t['n_abstract_missing']} without)")
    L.append(f"- Human primary studies (not review, not protocol, not animal-flagged): "
             f"**{t['n_human_primary']}**; animal-subject: {t['n_animal_subject']}; "
             f"reviews/meta-analyses: {t['n_review']}; protocols: {t['n_protocol']}")
    L.append(f"- Abstracts naming a **sleep-phase / oscillatory measure**: {t['n_sleep_phase_named']}")
    L.append(f"- Abstracts naming an **autonomic measure**: {t['n_autonomic_measured']}")
    L.append(f"- Abstracts naming **both** (the state the question turns on): "
             f"**{t['n_sleep_phase_and_autonomic']}**")
    L.append(f"- Protocol read off the text: {t['by_protocol']}")
    L.append(f"- Maladaptive-memory vocabulary: {t['by_memory_type']}")
    L.append(f"- Fear-outcome direction: {t['by_direction']}")
    L.append(f"- **Title-level core set** (title names an intervention *and* sleep or a "
             f"fear/emotional memory): **{t['n_title_core']}** "
             f"({t['n_title_core_human']} human primary); by protocol read off the text: "
             f"{t['by_protocol_title_core']}")
    L.append("")
    L.append("## Core set (title-level, high precision)")
    L.append("")
    L.append("Below this point the tables are the full, noisy abstract screen. This section is "
             "the subset a reader can act on: records whose **title** names an intervention "
             "(`acoustic|auditory|closed-loop|stimulat|cue|odor|tone|targeted memory`) *and* "
             "sleep *or* a fear/emotional memory. Titles are the authors' own claims, so "
             "false positives here are rarer; the flags in the columns are still abstract "
             "screens.")
    L.append("")
    core = [r for r in recs if r["title_core"]]
    L.append(section("Core set", core))
    L.append(READING)
    L.append("## The table")
    L.append("")
    human = [r for r in recs if r["is_human_primary"]]
    animal = [r for r in recs if r["is_animal_subject"]]
    review = [r for r in recs if r["is_review"] or r["is_protocol"]]
    other = [r for r in recs if r not in human and r not in animal and r not in review]
    L.append(section("Human primary studies", human))
    L.append(section("Animal studies", animal))
    L.append(section("Reviews and protocols", review))
    L.append(section("Unclassified", other))
    L.append("## Sentences behind the flags")
    L.append("")
    L.append("For every human primary study, the sentence that set each flag. Where a flag "
             "is `no`, the sentence is absent \u2014 read that as *not stated in the abstract*.")
    L.append("")
    for r in human:
        L.append(f"**{r['pmid']}** \u2014 {esc(r['title'])}")
        if r["sleep_phase_named"]:
            L.append(f"  - _sleep-phase_: {clip(r['sleep_phase']['sentence'])}")
        if r["autonomic_measured"]:
            L.append(f"  - _autonomic_: {clip(r['autonomic']['sentence'])}")
        L.append(f"  - _memory type ({r['memory_type']})_: {clip(r['memory_type_sentence'])}")
        if r["fear_outcome_sentence"]:
            L.append(f"  - _fear outcome ({r['fear_outcome_direction']})_: "
                     f"{clip(r['fear_outcome_sentence'])}")
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fetch", action="store_true", help="re-tag the stored record offline")
    ap.add_argument("--snapshot-end", default=date.today().isoformat(),
                    help="latest publication date included (YYYY-MM-DD)")
    ap.add_argument("--date-from", default="2005-01-01")
    args = ap.parse_args()

    if args.no_fetch:
        record = json.loads(RAW.read_text())
        record["records"] = [dict(r, **classify(r)) for r in record["records"]]
    else:
        record = build(args.snapshot_end, args.date_from)

    record["tallies"] = tally(record["records"])
    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(record, indent=1) + "\n")
    TABLE.write_text(render(record))

    t = record["tallies"]
    print(f"wrote {RAW.relative_to(ROOT)}  ({t['n_records']} records)")
    print(f"wrote {TABLE.relative_to(ROOT)}")
    for arm, a in record["arms"].items():
        print(f"  {arm}: {a['total_matching']} matching, {a['fetched']} fetched")
    print(f"  human primary: {t['n_human_primary']}  animal: {t['n_animal_subject']}  "
          f"review: {t['n_review']}  protocol: {t['n_protocol']}")
    print(f"  sleep-phase named: {t['n_sleep_phase_named']}  autonomic: {t['n_autonomic_measured']}"
          f"  both: {t['n_sleep_phase_and_autonomic']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
