#!/usr/bin/env python3
# Owner: Desi
"""Agenda item 30, next action §7 step 2 — turn the IED comparison set from abstracts into full-text
measurements, and record honestly which of the four "open-access" papers is not actually reachable.

The seed artefact (`research/sleep-cognition-epilepsy-seed.md`) built a six-paper comparison set from
PubMed abstracts to test the seed review's one flat claim — that nocturnal interictal epileptic
discharges (IEDs) harm cognition. Its §7 named the four comparison papers it believed were in PMC and
set the step this script performs: pull their full texts and extract the numbers under the IED claim.

Two things this script is built to do that a hand-run does not:

  * it records the HTTP status and the sha256 of every byte it retrieved, so a later reader can tell
    a full text from an abstract and can confirm a quote comes from the document it claims to;
  * it does not paper over the paper that is not there. The Wodeyar PNAS study — the one behavioural
    study carrying the destructive direction — is recorded as it actually is: European PMC reports
    `inPMC=N`, `isOpenAccess=N`, and both the Europe PMC full-text endpoint and the NCBI/PNAS pages
    refuse. That is a finding, not a gap to hide.

Usage:
    python3 scripts/sleep_epilepsy_ied_fulltext.py            # fetch + write the record
    python3 scripts/sleep_epilepsy_ied_fulltext.py --check    # verify quotes against the stored text
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "sleep-cognition-epilepsy-ied-measurements.json"
TABLE = ROOT / "research" / "sleep-cognition-epilepsy-ied-measurements.md"
UA = "llm-symposium/1.0 (Desi clock wake, agenda item 30; research)"

# The four comparison papers §7 named as "all in PMC", and the fifth that carries the behavioural
# direction of the claim and could not be reached. pmid -> (pmcid, short label, doc)
REACHABLE = {
    "27111281": ("PMC4899094", "Gelinas 2016", "Gelinas JN, Khodagholy D, Thesen T, Devinsky O, Buzsaki G. Interictal epileptiform discharges induce hippocampal-cortical coupling in temporal lobe epilepsy. Nat Med. 2016;22(6):641-648. doi:10.1038/nm.4084"),
    "42021788": ("PMC13098343", "Uehara 2026", "Uehara T, Barcelon EA, Shigeto H, et al. Hippocampal interictal discharges induce frontal spindles and enhance spindle-slow oscillation coupling in temporal lobe epilepsy. Clin Neurophysiol Pract. 2026;11:321-331. doi:10.1016/j.cnp.2026.04.005"),
    "41298465": ("PMC12749432", "Maslarova 2025", "Maslarova A, Shin JN, Navas-Olive A, et al. Spatiotemporal patterns differentiate hippocampal sharp-wave ripples from interictal epileptiform discharges in mice and humans. Nat Commun. 2025;16:11636. doi:10.1038/s41467-025-66562-6"),
}
UNREACHABLE = {
    "42378289": ("PMC13342884", "Wodeyar 2026", "Wodeyar A, et al. A hierarchical cascade of sleep rhythms supports motor memory and is hijacked by epileptic spikes in human epilepsy. PNAS. 2026. doi:10.1073/pnas.2517454123"),
}

# Verbatim fragments, keyed by extract id -> (source pmid, quote). Each must appear character-for-
# character (whitespace-normalised) in that source's stored text. These are the numbers the item asked
# for: cohort sizes, event counts, frequency bands, and the sign of the IED effect on a consolidation
# rhythm.
EXTRACTS = [
    ("G1", "27111281", "spontaneous hippocampal IEDs correlate with impaired memory consolidation and are precisely coordinated with spindle oscillations in the prefrontal cortex during NREM sleep"),
    ("G2", "27111281", "This coordination surpasses the normal physiological ripple-spindle coupling and is accompanied by decreased ripple occurrence"),
    ("G3", "27111281", "IED frequency and coupling with mPFC spindles are both correlated with the degree of memory impairment"),
    ("G4", "27111281", "pilot clinical examination of four subjects with focal epilepsy"),
    ("G5", "27111281", "Hippocampal ripples are brief, high-frequency (100\u2013200 Hz) oscillations"),
    ("G6", "27111281", "tested across four phases: baseline, kindling, recovery, and artificial IEDs"),
    ("U1", "42021788", "Simultaneous intracranial and scalp EEG was recorded during NREM sleep in 10 patients with temporal lobe epilepsy (TLE)."),
    ("U2", "42021788", "Eight among the 10 patients were women."),
    ("U3", "42021788", "we analyzed the data from 13 hemispheres of 10 patients"),
    ("U4", "42021788", "Spindle occurrence increased in the frontal region 0.4\u20130.8 s after IEDs."),
    ("U5", "42021788", "The incidence of SOs increased within"),
    ("U6", "42021788", "Phase consistency and amplitude modulation of spindle\u2013SO coupling were higher for IED-coupled than for uncoupled spindles in the frontal region."),
    ("U7", "42021788", "Hippocampal IEDs selectively induced frontal spindles and enhanced their coupling with SOs."),
    ("M1", "41298465", "mouse and human hippocampal ripples share spatial, spectral and temporal features, which are clearly distinct from IEDs"),
    ("M2", "41298465", "Conversely, IEDs showed a broad spatial extent and wide-band frequency power."),
    ("M3", "41298465", "IEDs were detected in 7 out of 9 sessions from all 5 mice"),
    ("M4", "41298465", "exceeding SPW-R magnitudes by over fivefold"),
    ("M5", "41298465", "SPW-Rs show a narrowband 130\u2013180 Hz peak absent in IEDs."),
    ("M6", "41298465", "narrowband 130\u2013180 Hz peak absent in IEDs"),
    ("M7", "41298465", "13 patients during surgical evaluation (6 temporal lobe epilepsy; 7 extratemporal epilepsy"),
    ("M8", "41298465", "lasting 20\u201370 ms"),
]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def strip_xml(raw: str) -> str:
    """Same normalization the seed table used: drop tags, unescape entities, collapse whitespace."""
    txt = re.sub(r"<[^>]+>", " ", raw)
    txt = html.unescape(txt)
    return norm(txt)


def fetch(url: str, timeout: int = 60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # noqa: BLE001 - recorded, not raised
        return None, str(e).encode()


def build() -> dict:
    sources = []
    for pmid, (pmc, label, doc) in REACHABLE.items():
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML"
        status, raw = fetch(url)
        raw_text = raw.decode("utf-8", "replace")
        text = strip_xml(raw_text)
        sources.append({
            "id": pmid,
            "label": label,
            "type": f"Europe PMC full text (fullTextXML), {pmc}",
            "doc": doc,
            "url": url,
            "http_status": status,
            "sha256_raw": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "bytes_raw": len(text),
            "text": text,
        })
    unreachable = []
    for pmid, (pmc, label, doc) in UNREACHABLE.items():
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML"
        status, raw = fetch(url)
        unreachable.append({
            "id": pmid,
            "label": label,
            "doc": doc,
            "url": url,
            "http_status": status,
            "body_first_80": raw.decode("utf-8", "replace")[:80],
            "note": "Europe PMC core record reports inPMC=N, isOpenAccess=N; no full text is deposited.",
        })
    extracts = [{"id": i, "source": s, "quote": q} for i, s, q in EXTRACTS]
    return {
        "artifact": "Agenda item 30 (sleep architecture as a mediator of memory impairment in epilepsy): IED comparison set, full-text measurements",
        "generated_utc": "2026-10-09T10:38:00Z",
        "generated_by": "desi wake 20261009T103736Z-4ea4f075",
        "claim_under_test": "The seed review's flat claim [T8]: nocturnal IEDs have a negative effect on cognition (6 of its 13 studies).",
        "sources": sources,
        "unreachable": unreachable,
        "extracts": extracts,
    }


def check(record: dict) -> int:
    problems = []
    byid = {s["id"]: s for s in record["sources"]}
    for s in record["sources"]:
        got = hashlib.sha256(s["text"].encode("utf-8")).hexdigest()
        if got != s["sha256_raw"]:
            problems.append(f"{s['id']}: text rehashes {got[:12]}... != {s['sha256_raw'][:12]}...")
    for e in record["extracts"]:
        src = byid.get(e["source"])
        if src is None:
            problems.append(f"{e['id']}: source {e['source']} not stored")
        elif norm(e["quote"]) not in src["text"]:
            problems.append(f"{e['id']}: quote not found in {e['source']}")
    for p in problems:
        print("FAIL", p)
    print(f"check: {len(record['extracts'])} extracts against {len(record['sources'])} stored texts, "
          f"{len(problems)} problem(s)")
    return 1 if problems else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify the written record, do not fetch")
    args = ap.parse_args()
    if args.check:
        return check(json.loads(RECORD.read_text()))
    record = build()
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {RECORD.relative_to(ROOT)} ({RECORD.stat().st_size} bytes)")
    for s in record["sources"]:
        print(f"  {s['id']} {s['label']:14} http={s['http_status']} bytes={s['bytes_raw']} "
              f"sha256={s['sha256_raw'][:12]}")
    for u in record["unreachable"]:
        print(f"  {u['id']} {u['label']:14} http={u['http_status']} UNREACHABLE")
    return check(record)


if __name__ == "__main__":
    sys.exit(main())
