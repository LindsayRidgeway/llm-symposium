#!/usr/bin/env python3
"""Agenda item 30, step (2): pull the four papers the seed names as open and turn
the abstract-level comparison set into measurements.

The seed (`research/sleep-cognition-epilepsy-seed.md` §7) lists four primary papers it
says "are all in PMC" and reachable as full text:

    42378289  PNAS 2026, Wodeyar et al.      PMC13342884
    41298465  Nat Commun 2025, Maslarova     PMC12749432
    42021788  Clin Neurophysiol Pract 2026,  PMC13098343
    27111281  Nat Med 2016, Gelinas          PMC4899094

This script fetches each via Europe PMC `fullTextXML` (keyless), records the HTTP status,
byte count and sha256 of the exact bytes retrieved, and pulls a short set of verbatim
extracts under the item's one contested claim (that nocturnal interictal discharges harm
cognition). It does NOT store the full text — only quotations and the hash receipt — so
the artefact respects the papers' licences while staying checkable.

Network is required. The output JSON is what the offline test pins.
Run:  python3 scripts/sleep_cognition_epilepsy_ied_fulltext.py
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "sleep-cognition-epilepsy-ied-fulltext-raw.json"

EPMC_FULLTEXT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML"
EPMC_CORE = (
    "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    "?query=EXT_ID:{pmid}&format=json&resultType=core"
)
NCBI_EFETCH = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    "?db=pmc&id={pmcid_n}&retmode=xml"
)

# pmc -> (pmid, journal, year, first author)
REACHABLE = {
    "PMC12749432": ("41298465", "Nature Communications", "2025", "Maslarova A"),
    "PMC13098343": ("42021788", "Clinical Neurophysiology Practice", "2026", "Uehara T"),
    "PMC4899094": ("27111281", "Nature Medicine", "2016", "Gelinas JN"),
}
UNREACHABLE_PMC = "PMC13342884"
UNREACHABLE_PMID = "42378289"
UNREACHABLE_N = "13342884"

# Verbatim extracts to pull, keyed by pmc. Each must appear character-for-character in
# the tag-stripped, whitespace-normalised full text or the script reports it MISSING.
EXTRACTS = {
    "PMC4899094": [
        "We show in a rat model of temporal lobe epilepsy that spontaneous hippocampal IEDs correlate with impaired memory consolidation and are precisely coordinated with spindle oscillations in the prefrontal cortex during NREM sleep.",
        "This coordination surpasses the normal physiological ripple-spindle coupling and is accompanied by decreased ripple occurrence.",
        "IED rate and IED-spindle coupling rate were strongly negatively correlated with performance, while cumulative seizure number yielded a more variable negative correlation.",
        "We confirm a similar correlation of temporofrontal IEDs with spindles over anatomically restricted cortical regions in a pilot clinical examination of four subjects with focal epilepsy.",
        "n = 47 sessions from four rats; 15,441 IEDs, 37,835 spindles",
    ],
    "PMC13098343": [
        "Hippocampal IED density ranged from 0.35 to 38.54/min and was above 5/min in 14 hemispheres.",
        "Ultimately, we analyzed the data from 13 hemispheres of 10 patients.",
        "Post hoc analyses revealed that spindle occurrence in the frontal region was significantly increased during the 0.4\u20130.8 s time bin following hippocampal IEDs, compared to the mean across all bins (rate ratio [RR] = 1.26, 95% confidence interval [CI] [1.18, 1.34], Z = 7.18, Bonferroni-corrected p < 0.001)",
        "temporal IED\u2013SO coupling strength showed a significant negative correlation with VIQ ( r = \u2212 0.86, 95% CI [\u22120.97, \u22120.47], Bonferroni-corrected p = 0.010)",
        "Notably, we observed no correlation between the densities of IEDs and spindles, suggesting that IED-induced spindles may not simply add to, but rather replace physiological spindles.",
        "this study does not directly address whether IED-induced spindles contribute to cognitive impairment in patients with TLE.",
    ],
    "PMC12749432": [
        "Here, we demonstrate that mouse and human hippocampal ripples share spatial, spectral and temporal features, which are clearly distinct from IEDs.",
        "IED peak frequencies were lower than SPW-Rs (54 \u00b1 11 Hz in the pyramidal layer).",
        "Ripple rates during NREM sleep before ripmap curation were 10.5 \u00b1 1.6 events/min on macrocontacts ( n = 10) and 6.6 \u00b1 2.2 events/min on microwires ( n = 8).",
        "without the 1/f correction, a narrowband high-frequency filter (130\u2013180 Hz) applied to the LFP may actually represent IEDs.",
        "a wide distribution of reported ripple incidences across sleep, from 0.35 to 30 ripples per minute",
        "For human IEDs, positive modulation was seen in 21 (29%) principal cells and 9 (17%) interneurons",
    ],
}


def fetch(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": "llm-symposium/1.0 (agenda item 30)"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:  # noqa: PERF203
        return e.code, e.read()


def normalise(xml: str) -> str:
    s = re.sub(r"<ref-list[ >].*?</ref-list>", "", xml, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def main() -> int:
    records = []
    missing_total = 0
    for pmc, (pmid, journal, year, author) in REACHABLE.items():
        status, body = fetch(EPMC_FULLTEXT.format(pmc=pmc))
        text = normalise(body.decode("utf-8", "replace"))
        extracts = []
        for i, q in enumerate(EXTRACTS[pmc], 1):
            present = q in text
            if not present:
                missing_total += 1
                print(f"MISSING  {pmc}  extract {i}: {q[:70]}...")
            extracts.append({"n": i, "text": q, "verbatim": present})
        rec = {
            "pmc": pmc,
            "pmid": pmid,
            "first_author": author,
            "journal": journal,
            "year": year,
            "source_url": EPMC_FULLTEXT.format(pmc=pmc),
            "http": status,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "extracts": extracts,
        }
        records.append(rec)
        print(f"{pmc}  HTTP {status}  {len(body)} bytes  {len(extracts)} extracts  "
              f"{sum(e['verbatim'] for e in extracts)}/{len(extracts)} verbatim")

    # The fourth paper — the one the seed lists as open — is recorded for what it is.
    core_status, core_body = fetch(EPMC_CORE.format(pmid=UNREACHABLE_PMID))
    core = json.loads(core_body.decode("utf-8", "replace"))["resultList"]["result"][0]
    ncbi_status, ncbi_body = fetch(NCBI_EFETCH.format(pmcid_n=UNREACHABLE_N))
    ncbi_raw = ncbi_body.decode("utf-8", "replace")
    note = "The publisher of this article does not allow downloading of the full text in XML form."
    unreachable = {
        "pmc": UNREACHABLE_PMC,
        "pmid": UNREACHABLE_PMID,
        "first_author": "Wodeyar A",
        "journal": "Proceedings of the National Academy of Sciences",
        "year": "2026",
        "title": core.get("title"),
        "isOpenAccess": core.get("isOpenAccess"),
        "inEPMC": core.get("inEPMC"),
        "inPMC": core.get("inPMC"),
        "europepmc_fulltext_http": fetch(EPMC_FULLTEXT.format(pmc=UNREACHABLE_PMC))[0],
        "europepmc_core_source": EPMC_CORE.format(pmid=UNREACHABLE_PMID),
        "europepmc_core_http": core_status,
        "ncbi_efetch_source": NCBI_EFETCH.format(pmcid_n=UNREACHABLE_N),
        "ncbi_efetch_http": ncbi_status,
        "ncbi_efetch_bytes": len(ncbi_body),
        "publisher_withholds_fulltext_note_present": note in ncbi_raw,
        "reachable_as_fulltext": False,
    }
    records.append(unreachable)
    print(f"{UNREACHABLE_PMC}  Europe PMC fullTextXML HTTP {unreachable['europepmc_fulltext_http']}  "
          f"isOpenAccess={core.get('isOpenAccess')}  inPMC={core.get('inPMC')}  "
          f"withhold-note-present={unreachable['publisher_withholds_fulltext_note_present']}")

    doc = {
        "artifact": "agenda item 30 step (2) — full-text measurements under the IED claim",
        "generated_from": "Europe PMC fullTextXML + NCBI E-utilities (keyless)",
        "note": "Full text is NOT stored (licence). Only short verbatim extracts and the sha256 "
                "of the retrieved bytes are kept, so a reader can re-fetch and confirm the quotes.",
        "papers": records,
    }
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 1 if missing_total else 0


if __name__ == "__main__":
    sys.exit(main())
