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

# Curated extracts for the comparison table. Each is (id, source, question, start-anchor,
# end-anchor): the script captures the span between the two anchors on the whitespace-flattened
# document and stores it verbatim, failing loudly if either anchor is absent, so a quote in the
# markdown can never be invented or silently drift from the retrieved bytes. Added 2026-10-01.
KEY_EXTRACTS = [
    ("F1", "F1", "Does Flutter describe a responsible-gambling function, and is it owned separately from the commercial function?",
     "We have taken a principle-based approach to our responsible gambling strategy",
     "align on key strategic topics."),
    ("F2", "F1", "Where does the company say it uses machine learning and AI?",
     "We use machine learning, AI technologies, data science and similar technologies in our products, services and infrastructure",
     "developing new product features using AI."),
    ("F3", "F1", "Does the company disclose models that optimize marketing at the customer level?",
     "We use proprietary models and software tools to track",
     "optimize our marketing strategies as necessary."),
    ("F4", "F1", "Are rewards or loyalty benefits personalized from a player's own history?",
     "Players in the higher tiers are also entitled to participate in monthly poker challenges",
     "in the form of star coins."),
    ("F5", "F1", "Does the filing describe player-protection tooling, and who requires it?",
     "These changes have included, among other things, the introduction of financial vulnerability checks",
     "the design and offer of non-slots online gaming products."),
    ("F6", "F1", "How is the AI/ML risk framed in the risk factors?",
     # NB: the filing uses typographic quotes around “AI”; a straight-quote anchor never matches.
     "We use artificial intelligence (\u201cAI\u201d), machine learning and similar technologies in our business, which may present business,",
     "compliance, and reputational risks."),
    ("P1", "S2", "Does the privacy notice name inferences drawn from collected data?",
     "audio information (e.g., if you participate in a customer support call",
     "reasonably associated with you."),
    ("P2", "S2", "How is geolocation used, and for whom?",
     "We also collect non-precise geolocation data",
     "serve you ads that are relevant to you."),
    ("P3", "S2", "What does the notice list among the purposes of processing?",
     "3.1.1 providing you with our products and services",
     "protecting the integrity of FanDuel's contests."),
    ("P4", "S2", "Through which channels may the operator market to a user?",
     "We may use your information (both personal and non-personal information) to send you marketing",
     "and personal text messages."),
    ("P5", "S2", "Can a user opt out of interest-based advertising, and how?",
     "To learn more and to opt out of the collection of data on our website",
     "www.youronlinechoices.com"),
    ("P6", "S2", "How is precise geolocation used, and for what compliance purpose?",
     "in order to locate you so we may verify your location",
     "purposes of legal and regulatory compliance."),
]


def flat(text: str) -> str:
    """One-line, whitespace-collapsed view used for anchor search and stored quotes."""
    return re.sub(r"\s+", " ", text).strip()


def key_extracts(flat_f1: str, flat_s2: str) -> list[dict]:
    out = []
    texts = {"F1": flat_f1, "S2": flat_s2}
    for eid, sid, question, start, end in KEY_EXTRACTS:
        body = texts[sid]
        i = body.find(start)
        if i < 0:
            raise SystemExit(f"extract {eid}: start anchor not found in {sid}: {start!r}")
        j = body.find(end, i)
        if j < 0:
            raise SystemExit(f"extract {eid}: end anchor not found in {sid}: {end!r}")
        quote = body[i:j + len(end)]
        out.append({"id": eid, "source": sid, "question": question, "quote": quote})
    return out


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
    # (Corrected 2026-10-01: the earlier pass tested for "we collect"/"personal information we"
    # and, finding neither in a shell it had mis-read as client-rendered, filed the notice as a
    # measured gap. The notice body IS in the retrieved bytes; the detector was wrong, not the
    # fetch. The check now looks for a phrase the notice actually uses, and the notice is parsed.)
    privacy_url = "https://www.fanduel.com/privacy"
    pst, praw, phdrs = http_get(privacy_url)
    ptext = html_to_text(praw)
    pflat = flat(ptext)
    has_body = "personal information we collect" in ptext.lower()
    out["sources"].append({
        "id": "S2" if has_body else "X2",
        "type": "Privacy notice" if has_body else "Privacy notice (ATTEMPTED, NO EXTRACTABLE TEXT)",
        "doc": "FanDuel public privacy notice",
        "url": privacy_url, "http": pst, "size_bytes": len(praw),
        "content_type": phdrs.get("Content-Type", ""),
        "sha256": hashlib.sha256(praw).hexdigest(), "chars_text": len(ptext),
    })
    if has_body:
        out["lexical_audit_privacy"] = audit(ptext)
        out["extracts"] += extract(ptext, "S2")
    else:
        out["sources"][-1]["note"] = ("HTTP 200 but no notice text found in the retrieved bytes; "
                                      "no extract could be drawn from it.")

    f1_flat = flat(text)
    out["key_extracts"] = key_extracts(f1_flat, pflat if has_body else "")

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  source F1: {url}")
    print(f"  http={st} size={len(raw)} sha256={sha[:16]}… chars={len(text)}")
    print(f"  privacy has_body={has_body} http={pst} chars={len(ptext)}")
    print(f"  extracts: {len(out['extracts'])}  key_extracts: {len(out['key_extracts'])}")
    for k, v in out["lexical_audit"].items():
        if v:
            print(f"    10-K {k!r}: {v}")
    for k, v in out.get("lexical_audit_privacy", {}).items():
        if v:
            print(f"    priv {k!r}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
