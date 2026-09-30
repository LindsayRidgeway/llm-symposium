#!/usr/bin/env python3
"""Fetch full patent document text from Google Patents for a set of publication numbers.

Used by agenda item 27 to attach verbatim evidence (abstract + first claim) to each
patent row. Writes raw HTML bytes with sha256, and an extracted text field.

Usage: python3 scripts/draftkings_patent_text.py research/draftkings-patent-text-raw.json PUB1 PUB2 ...
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

UA = "llm-symposium-research/1.0 (public-records research; no API key)"


def fetch(url: str, timeout: int = 35) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, (e.read() if e.fp else b"")
    except Exception as e:  # noqa: BLE001
        return -1, str(e).encode()


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


TERMS = ["responsible", "problem gambl", "vulnerab", "propensity", "churn",
         "retention", "predict", "machine learning", "neural network",
         "personali", "recommend", "notification", "vip", "comp ", "loss"]


def extract(body: bytes) -> dict:
    txt = body.decode("utf-8", "ignore")
    flat = clean(txt).lower()
    out: dict = {"full_text_chars": len(flat)}
    out["term_counts"] = {t: flat.count(t) for t in TERMS}
    m = re.search(r'<meta name="description" content="([^"]*)"', txt)
    out["meta_description"] = html.unescape(m.group(1)) if m else None
    m = re.search(r'<meta name="DC\.title" content="([^"]*)"', txt)
    out["dc_title"] = html.unescape(m.group(1)) if m else None
    m = re.search(r'<abstract[^>]*>(.*?)</abstract>', txt, re.S)
    if not m:
        m = re.search(r'<section itemprop="abstract".*?>(.*?)</section>', txt, re.S)
    out["abstract"] = clean(m.group(1)) if m else None
    m = re.search(r'<section itemprop="claims".*?>(.*?)</section>', txt, re.S)
    if m:
        claims = re.findall(r'<div class="claim[^"]*"[^>]*>(.*?)</div>', m.group(1), re.S)
        out["claim_1"] = clean(claims[0]) if claims else None
        out["n_claims_parsed"] = len(claims)
    else:
        out["claim_1"] = None
    return out


def main() -> int:
    out_path = sys.argv[1]
    pubs = sys.argv[2:]
    doc = {"retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "user_agent": UA, "patents": {}}
    for pub in pubs:
        url = f"https://patents.google.com/patent/{pub}/en"
        status, body = fetch(url)
        rec = {"url": url, "http": status, "bytes": len(body),
               "sha256": hashlib.sha256(body).hexdigest()}
        rec.update(extract(body))
        doc["patents"][pub] = rec
        print(f'{status} {pub:>18}  {str(rec.get("dc_title"))[:70]}')
        time.sleep(1.0)
    with open(out_path, "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
