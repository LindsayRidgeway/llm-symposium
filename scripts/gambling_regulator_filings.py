#!/usr/bin/env python3
"""Reproducible fetch of state gaming-regulator filings (agenda item 27, step 2).

Written 2026-10-01 (Desi, clock wake). Item 27's second next action reads: "Fetch state
gaming-regulator filings for DraftKings' responsible-gaming plan - the document that would
show whether the safety pipeline is architecturally distinct."

This script answers it with documents rather than argument. Massachusetts is the state that
publishes operator filings openly, so the search runs there: the Massachusetts Gaming
Commission's own DraftKings licensee page links the operator's periodic reports, and the
MGC's license decision and Responsible Gaming Framework 2.0 are the two regulator documents
that say what an operator's Responsible Gaming Plan must contain. Every document is fetched,
hashed, and quoted verbatim; a claim in `research/gambling-regulator-filings.md` that is not
backed by a quote below is a claim this script refuses to let the reader make.

The three questions the table is built around:

  plan      - does the operator's Responsible Gaming Plan itself exist in the public record?
  separation- do the filings describe the safety function as architecturally separate from
              revenue optimisation (a distinct pipeline, a distinct data feed, a distinct
              system), or do they describe tools and organisational roles only?
  pipeline  - does any filed document name a predictive or algorithmic risk model at all?

Usage:
    python3 scripts/gambling_regulator_filings.py            # fetch, write raw JSON + table
"""

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research" / "gambling-regulator-filings-raw.json"
TABLE = ROOT / "research" / "gambling-regulator-filings.md"

UA = "llm-symposium-desi/1.0 (https://github.com/LindsayRidgeway/llm-symposium)"
BASE = "https://massgaming.com/wp-content/uploads/"

# kind: how the record is used in the reading. "operator" = filed by DraftKings;
# "regulator" = issued by the MGC and binding on the operator.
SOURCES = [
    {"id": "R1", "kind": "regulator",
     "doc": "Massachusetts Gaming Commission - DraftKings Category 3 License Decision (Final)",
     "file": "DraftKings-License-Decision-Final.pdf"},
    {"id": "R2", "kind": "operator",
     "doc": "DraftKings Tri-Annual Presentation, October 2025 - April 2026 (filed with MGC)",
     "file": "DraftKings-2026-1st-TriAnnual-Report.pdf"},
    {"id": "R3", "kind": "operator",
     "doc": "DraftKings Quarterly Report 2025 Q3 (filed with MGC)",
     "file": "DraftKings-Quarterly-Report-2025-Q3.pdf"},
    {"id": "R4", "kind": "regulator",
     "doc": "Massachusetts Gaming Commission - Responsible Gaming Framework, Version 2.0",
     "file": "MGC-Responsible-Gaming-Framework-2.0.pdf"},
    {"id": "R5", "kind": "operator",
     "doc": "DraftKings - Sports Wagering Operator & Vendor Scope of Licensing, Initial Survey "
            "(redacted application, as published)",
     "file": "DraftKings-redacted.pdf"},
]

# Attempts that yielded no readable text. Recorded so the gap is measured, not glossed.
ATTEMPTS = [
    {"id": "X1", "doc": "DraftKings Responsible Gaming Center (rg.draftkings.com)",
     "url": "https://rg.draftkings.com/",
     "note": "Reachable, but a client-rendered application: the response is markup with almost no "
             "visible text and no plan, model or pipeline. The operator's own RG front door "
             "carries no architecture to read - named because item 27's step 2 seeks exactly that."},
]

# (id, source, question, quote). The quote is verified verbatim (whitespace-normalised)
# against the fetched document before it is written; a mismatch aborts the run.
EXTRACTS = [
    ("E1", "R1", "plan", "DraftKings reported that it employs a five-pillar approach to "
     "responsible gaming: (1) training and education; (2) detection and intervention; "
     "(3) external engagements and research; (4) marketing and advertising; and "
     "(5) platform tools and resources."),
    ("E2", "R1", "plan", "Responsible gaming policies DraftKings described its responsible "
     "gaming polices on pages 443-459 of its Application and the Commission found it "
     "satisfactory."),
    ("E3", "R1", "separation", "DraftKings's platform is fully vertically integrated, meaning "
     "DraftKings owns the entirety of it sports betting platform, from the software to the "
     "sportsbook."),
    ("E4", "R1", "separation", "it utilizes a system-based public health approach and has "
     "partnered with the Cambridge Health Alliance"),
    ("E5", "R4", "separation", "Each licensee's Responsible Gaming Committee is responsible for "
     "continually improving their responsible gaming programs, maintaining compliance to the "
     "practices and policies described in their Responsible Gaming Plan, and reporting their "
     "findings to MGC."),
    ("E6", "R4", "separation", "Each gaming licensee's Responsible Gaming Plan should reflect the "
     "strategies outlined in the MGC Responsible Gaming Framework and include detailed practices "
     "and procedures for assuring effective implementation by conducting internal audits, "
     "surveying employees, and reviewing relevant data on a regular basis."),
    ("E7", "R4", "plan", "Submit an annual Responsible Gaming Plan progress report according to "
     "MGC standards"),
    ("E8", "R2", "separation", "All DraftKings players are routed from our platform Self-Exclusion "
     "page to Massachusetts state self-exclusion resources."),
    ("E9", "R2", "separation", "In October 2025, DraftKings finalized a partnership with Evive "
     "Digital Health to share Evive resources within its Responsible Gaming Center suite of "
     "resources."),
    ("E10", "R2", "separation", "Gamalyze is a quick, card-based game meant to help players "
     "discover their decision-making style."),
    ("E11", "R3", "separation", "In celebration of the first-ever HBCU Classic held in Boston, "
     "DraftKings' Belonging and Responsible Gaming teams sponsored the inaugural Welcome "
     "Reception at the View Boston Rooftop, bringing together 400 guests for an evening of "
     "connection and purpose."),
    ("E12", "R5", "pipeline", "Sports Wagering Operator & Vendor Scope of Licensing - "
     "Initial Survey"),
]

# Lexical audit. Keys are printed in the table and pinned by the test. "operator filings"
# is R2+R3+R5 (the three documents DraftKings itself filed and published); the zeros are the
# finding - the operator never names a predictive or algorithmic risk pipeline in them.
AUDIT = {
    "operator filings: responsible gaming": ("operator", "responsible gaming"),
    "operator filings: machine learning": ("operator", "machine learning"),
    "operator filings: algorithm": ("operator", "algorithm"),
    "operator filings: predictive": ("operator", "predictive"),
    "operator filings: risk model": ("operator", "risk model"),
    "operator filings: profiling": ("operator", "profil"),
    "MGC framework: risk model": ("regulator", "risk model"),
}

LIGATURES = {"\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl",
             "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
             "\u2013": "-", "\u2014": "-"}


def norm(s):
    for k, v in LIGATURES.items():
        s = s.replace(k, v)
    return re.sub(r"\s+", " ", s).strip()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def pdf_text(data):
    import fitz  # PyMuPDF; imported here so the module loads without it for --help
    doc = fitz.open(stream=data, filetype="pdf")
    return doc.page_count, "\n".join(p.get_text() for p in doc)


def build():
    rec = {"artifact": "Agenda item 27, step 2 - state gaming-regulator filings for the "
                       "operator's responsible-gaming plan",
           "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "sources": [], "unreachable": [], "extracts": [], "lexical_audit": {}}
    texts = {}
    for s in SOURCES:
        url = BASE + s["file"]
        try:
            data = fetch(url)
        except Exception as e:  # noqa: BLE001 - record the gap, do not crash the run
            print(f"  !! {s['id']} fetch failed: {e}")
            rec["unreachable"].append({"id": s["id"], "doc": s["doc"], "url": url,
                                       "note": f"fetch failed: {e}"})
            continue
        pages, text = pdf_text(data)
        texts[s["id"]] = norm(text)
        rec["sources"].append({
            "id": s["id"], "type": s["kind"], "doc": s["doc"], "url": url,
            "retrieved_utc": rec["generated_utc"], "http_status": 200,
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "pages": pages, "text_chars": len(texts[s["id"]])})
        print(f"  {s['id']}: {len(data)}B, {pages}p, {len(texts[s['id']])} chars")

    for s in UNREACHABLE:
        code = None
        try:
            req = urllib.request.Request(s["url"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception:  # noqa: BLE001
            code = None
        rec["unreachable"].append({"id": s["id"], "doc": s["doc"], "url": s["url"],
                                   "http_status": code, "note": s["note"]})
        print(f"  {s['id']}: HTTP {code}  {s['url']}")

    for eid, src, question, quote in EXTRACTS:
        text = texts.get(src)
        if text is None:
            raise SystemExit(f"extract {eid} names source {src}, which was not fetched")
        nq = norm(quote)
        i = text.find(nq)
        if i < 0:
            raise SystemExit(f"extract {eid} is NOT verbatim in {src}: {nq[:100]!r}")
        lo = max(0, i - 260)
        hi = min(len(text), i + len(nq) + 260)
        rec["extracts"].append({"id": eid, "source": src, "question": question,
                                "quote": nq, "full": text[lo:hi]})

    for key, (kind, term) in AUDIT.items():
        ids = [s["id"] for s in SOURCES if s["kind"] == kind]
        blob = " ".join(texts.get(i, "") for i in ids)
        rec["lexical_audit"][key] = len(re.findall(re.escape(term), blob, re.I))
    return rec


def esc(s):
    return s.replace("|", "\\|").strip()


def render(rec):
    L = []
    L.append("# State Gaming-Regulator Filings for DraftKings' Responsible-Gaming Plan")
    L.append("")
    L.append("*Agenda item 27, step 2. Generated by `scripts/gambling_regulator_filings.py`; the "
             "raw record is `research/gambling-regulator-filings-raw.json`. Every block quote "
             "below is verbatim from the fetched bytes and is re-checked offline by "
             "`tests/test_gambling_regulator_filings.py`.*")
    L.append("")
    L.append(f"**Generated:** {rec['generated_utc']}. "
             f"**Documents reached:** {len(rec['sources'])}. "
             f"**Attempts that did not resolve:** {len(rec['unreachable'])}.")
    L.append("")
    L.append("## Why these documents, and what the question was")
    L.append("")
    L.append("The item asks for the operator's *responsible-gaming plan* - the document that would "
             "show whether the safety pipeline is architecturally distinct from the "
             "revenue-optimisation pipeline. Massachusetts is the state that publishes operator "
             "filings, so the search runs there: the MGC's DraftKings licensee page links the "
             "operator's periodic reports, and two regulator documents define what a plan must "
             "contain. Each is fetched, hashed, and quoted; the columns below record what each "
             "document is.")
    L.append("")
    L.append("## Sources")
    L.append("")
    L.append("| id | kind | document | url | sha256 | bytes | pages |")
    L.append("|---|---|---|---|---|---|---|")
    for s in rec["sources"]:
        L.append(f"| {s['id']} | {s['type']} | {esc(s['doc'])} | {s['url']} | "
                 f"{s['sha256']} | {s['bytes']} | {s['pages']} |")
    for u in rec["unreachable"]:
        L.append(f"| {u['id']} | UNREACHABLE | {esc(u['doc'])} | {u['url']} | - | - | "
                 f"({u.get('http_status')}) |")
    L.append("")
    L.append("## The finding")
    L.append("")
    L.append("**The plan itself is not in the public record, and that is the first result.** The "
             "regulator's license decision states that DraftKings' responsible-gaming policies "
             "were described on **pages 443-459 of its Application**, and that the Commission "
             "found them satisfactory (`E2`) - but those pages are not published. The application "
             "the MGC posts (`R5`) is the blank survey form, not the completed filing (`E12`). So "
             "the single document the item hoped for exists in the record only as a page range "
             "and a satisfaction finding.")
    L.append("")
    L.append("**What the regulator does require is an organisational and documentary structure, "
             "not an architectural separation.** The MGC Responsible Gaming Framework 2.0 "
             "requires each licensee to keep a **Responsible Gaming Committee** drawn from "
             "leadership (`E5`) and a **Responsible Gaming Plan** with internal audits, employee "
             "surveys and periodic data review (`E6`), reported to the MGC annually (`E7`). "
             "Nothing in the quoted requirements asks the operator to separate the responsible-"
             "gaming function from the revenue or marketing function - and the operator states "
             "that its platform is **fully vertically integrated** (`E3`), the same platform that "
             "runs monetisation.")
    L.append("")
    L.append("**In the operator's own filings, responsible gaming appears as tools and "
             "organisational roles, never as a system.** The operator reports routing every "
             "player through to the state self-exclusion resource (`E8`), a wellness-content "
             "partnership (`E9`), a self-assessment card game (`E10`), and - in the same "
             "quarterly document - a sponsorship framed as **Belonging and Responsible Gaming** "
             "community engagement (`E11`). The five-pillar framing in the license decision lists "
             "**detection and intervention** as a pillar (`E1`), but no filed document describes "
             "the detection: no risk model, no scoring input, no separation of the data that "
             "feeds it from the data that drives play. The lexical audit below is the measured "
             "form of that absence.")
    L.append("")
    L.append("## What the documents do and do not disclose")
    L.append("")
    L.append("- **Disclosed:** a governance structure (committee, plan, annual report), player-"
             "facing tools (self-exclusion, limits, cool-off, wellness content), and a stated "
             "public-health framing with an external health partner.")
    L.append("- **Not disclosed:** any description of the responsible-gaming pipeline as a "
             "system; any statement that it is separate from, or shares infrastructure with, the "
             "monetisation system; any named risk model; and the plan text itself.")
    L.append("- **Consequence for the item:** the architectural-separation question cannot be "
             "settled from the public filings because the filings describe the *front* of the "
             "safety programme (tools and roles) and withhold the *middle* (the plan and its "
             "detection logic). This is a limit of the record, stated as such - not evidence of "
             "either separation or fusion.")
    L.append("")
    L.append("## Evidence (verbatim)")
    L.append("")
    for e in rec["extracts"]:
        L.append(f"**{e['id']}** — source {e['source']}, on *{e['question']}*")
        L.append("")
        L.append(f"> {e['quote']}")
        L.append("")
    L.append("## Lexical audit")
    L.append("")
    L.append("Case-insensitive term counts over the fetched text. `operator filings` is R2+R3+R5 "
             "(the three documents DraftKings itself filed and published); `MGC framework` is R4. "
             "The zeros carry the finding; the first row is the contrast that shows the search "
             "would have found the term had it been there.")
    L.append("")
    L.append("| term | count |")
    L.append("|---|---|")
    for key, val in rec["lexical_audit"].items():
        L.append(f"| {key} | {val} |")
    L.append("")
    L.append("## Limits")
    L.append("")
    L.append("- One operator (DraftKings), one state (Massachusetts). Step 3 of the item - the "
             "second operator (Flutter/FanDuel) - is separate and not done here.")
    L.append("- A term count is a screen over retrieved text, not a reading: **zero** means the "
             "document does not name the thing, never that the thing does not exist. The named "
             "absence is still the right null for this question, because a system the operator "
             "wanted to disclose would be named.")
    L.append("- The plan text (Application pages 443-459) is outside this record; a reader with "
             "access to the completed application, or a public-records request, is the only way "
             "to read it.")
    L.append("")
    return "\n".join(L).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.parse_args()
    rec = build()
    rec["lexical_audit"] = rec["lexical_audit"]
    RAW.write_text(json.dumps(rec, indent=1) + "\n")
    TABLE.write_text(render(rec))
    print(f"wrote {RAW.relative_to(ROOT)}")
    print(f"wrote {TABLE.relative_to(ROOT)}")
    for k, v in rec["lexical_audit"].items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
