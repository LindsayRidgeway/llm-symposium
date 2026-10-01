#!/usr/bin/env python3
"""Agenda item 27, step (c) — the second operator.

Retrieves Flutter Entertainment plc's latest Form 10-K from SEC EDGAR and runs the
same lexical audit and verbatim-extract pass that was applied to DraftKings in
`research/gambling-algorithmic-exploitation.md`, so the two can be compared.

Outputs (paths are relative to the repo root):
  research/flutter-fanduel-sec-raw.json   sources, sha256 of retrieved bytes,
                                          lexical counts, verbatim extracts

Free and keyless: EDGAR submissions JSON + the filing's primary .htm, over HTTPS,
with a declared User-Agent (SEC requires one). Rebuild:

  python3 scripts/flutter_sec_extract.py
"""
from __future__ import annotations

import gzip
import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "desi-amigo research desi.s.amigo@gmail.com"
CIK10 = "0001635327"  # Flutter Entertainment plc
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "flutter-fanduel-sec-raw.json"

# Terms whose presence the item's question turns on. The first block is the same
# audit applied to DraftKings, so the counts are directly comparable; the second
# block is the monetization/AI vocabulary.
AUDIT_TERMS = [
    "responsible gaming", "responsible gambling", "problem gaming",
    "problem gambling", "self-exclusion", "self exclusion", "deposit limit",
    "reality check", "affordability", "safer gambling", "player safety",
    "machine learning", "artificial intelligence", "personaliz", "personaliz",
    "vip", "algorithm", "predictive model", "risk model", "retention",
    "reactivation", "monetization", "monetisation", "player protection",
]
EXTRACT_TERMS = [
    "responsible gaming", "responsible gambling", "problem gambling",
    "problem gaming", "self-exclusion", "machine learning",
    "artificial intelligence", "personaliz", "vip", "algorithm",
    "player protection", "safer gambling", "retention",
    # second pass: the responsible-gaming *pipeline* vocabulary
    "affordab", "vulnerab", "at-risk", "at risk", "harm", "predict",
    "propensity", "deposit limit", "play well",
]


def http_get(url: str) -> tuple[int, bytes, dict]:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Encoding": "gzip",
        "Accept": "text/html,application/json,*/*",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return r.status, raw, dict(r.headers)


def html_to_text(raw: bytes) -> str:
    s = raw.decode("utf-8", "replace")
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?is)<br\s*/?>", "\n", s)
    s = re.sub(r"(?is)</(p|div|tr|li|h[1-6])>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def sentences(text: str) -> list[str]:
    # Split on sentence enders followed by whitespace + capital, whitespace-normalized.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'])", text)
    return [re.sub(r"\s+", " ", p).strip() for p in parts if p.strip()]


def audit(text: str) -> dict:
    low = text.lower()
    return {t: low.count(t) for t in AUDIT_TERMS}


def extract(text: str, sid: str) -> list[dict]:
    out = []
    seen = set()
    for s in sentences(text):
        ls = s.lower()
        hits = sorted({t for t in EXTRACT_TERMS if t in ls})
        if hits and s not in seen:
            seen.add(s)
            out.append({"source": sid, "terms": hits, "text": s})
    return out


def main() -> int:
    out = {
        "artifact": "Agenda item 27 step (c): second-operator (Flutter/FanDuel) SEC extract",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": [],
        "lexical_audit": {},
        "extracts": [],
    }

    # 1. Submissions index -> latest 10-K
    _, sub_raw, _ = http_get(f"https://data.sec.gov/submissions/CIK{CIK10}.json")
    sub = json.loads(sub_raw)
    rec = sub["filings"]["recent"]
    idx = next(i for i, f in enumerate(rec["form"]) if f == "10-K")
    acc = rec["accessionNumber"][idx].replace("-", "")
    doc = rec["primaryDocument"][idx]
    filed = rec["filingDate"][idx]
    period = rec["reportDate"][idx]
    url = f"https://www.sec.gov/Archives/edgar/data/{int(CIK10)}/{acc}/{doc}"

    st, raw, hdrs = http_get(url)
    sha = hashlib.sha256(raw).hexdigest()
    text = html_to_text(raw)

    out["sources"].append({
        "id": "F1", "type": "SEC filing (Form 10-K)",
        "doc": f"Flutter Entertainment plc Annual Report on Form 10-K, period {period}, filed {filed}",
        "accession": rec["accessionNumber"][idx], "url": url,
        "http": st, "size_bytes": len(raw),
        "content_type": hdrs.get("Content-Type", ""),
        "sha256": sha, "chars_text": len(text),
    })
    out["lexical_audit"] = audit(text)
    out["extracts"] = extract(text, "F1")

    # 2. Second document of the two-document design: FanDuel's public privacy notice.
    # The URL answers 200 but serves a client-rendered shell — the notice text is not in the
    # retrieved bytes, so it cannot be extracted offline. Recorded as a measured gap, not papered over.
    privacy_url = "https://www.fanduel.com/privacy"
    pst, praw, phdrs = http_get(privacy_url)
    ptext = html_to_text(praw)
    has_body = any(t in ptext.lower() for t in ("we collect", "personal information we", "categories of personal information"))
    out["sources"].append({
        "id": "X2", "type": "Privacy notice (ATTEMPTED, NO EXTRACTABLE TEXT)",
        "doc": "FanDuel public privacy notice",
        "url": privacy_url, "http": pst, "size_bytes": len(praw),
        "content_type": phdrs.get("Content-Type", ""),
        "sha256": hashlib.sha256(praw).hexdigest(),
        "note": "HTTP 200 but the notice body is client-rendered; the retrieved bytes carry only "
                "navigation labels, no privacy text, so no extract could be drawn from it.",
    })

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  source F1: {url}")
    print(f"  http={st} size={len(raw)} sha256={sha[:16]}… chars={len(text)}")
    print(f"  extracts: {len(out['extracts'])}")
    for k, v in out["lexical_audit"].items():
        if v:
            print(f"    {k!r}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
