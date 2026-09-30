#!/usr/bin/env python3
"""Fetch DraftKings patent records from Google Patents, for agenda item 27.

Agenda item 27's first source table (`research/gambling-algorithmic-exploitation.md`)
recorded U.S. patent records as *unreachable* (Google Patents XHR returned 503 on
2026-09-30T00:11Z). This script retries the same source with a declared user agent,
walks every result page, and writes both the raw bytes (with sha256) and a flat
record list so the patent evidence can be added to the item without re-fetching.

Usage:  python3 scripts/draftkings_patents.py [out.json]
Network is required. No API key.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

UA = "llm-symposium-research/1.0 (public-records research; no API key)"
BASE = "https://patents.google.com/xhr/query"

# Queries chosen to answer the item's own question: which patents disclose using
# predicted behaviour to decide promotions, retention, VIP treatment or risk?
QUERIES = {
    # Every patent assigned to DraftKings. The item asks for "publicly searchable
    # U.S. patent records" for the operator under audit.
    "assignee_DraftKings": 'q=assignee="DraftKings"',
    # Full-text sweep of the operator's name, which catches patents where
    # DraftKings is the applicant but not the recorded assignee.
    "fulltext_DraftKings": 'q="DraftKings"',
}


def fetch(url: str, timeout: int = 30) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:  # noqa: PERF203
        return e.code, e.read() if e.fp else b""
    except Exception as e:  # noqa: BLE001
        return -1, str(e).encode()


def query_url(q: str, page: int) -> str:
    inner = q + ("" if page == 0 else f"&page={page}")
    return f"{BASE}?url={urllib.parse.quote(inner, safe='')}"


def walk(q: str) -> tuple[list[dict], list[dict]]:
    """Return (patents, page_provenance) for one query."""
    patents: list[dict] = []
    prov: list[dict] = []
    page = 0
    total_pages = 1
    while page < total_pages:
        url = query_url(q, page)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        status, body = fetch(url)
        prov.append({
            "page": page, "url": url, "http": status,
            "retrieved_utc": ts, "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
        })
        if status != 200:
            break
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            break
        res = (data.get("results") or {})
        total_pages = int(res.get("total_num_pages") or 1)
        for cluster in res.get("cluster", []):
            for hit in cluster.get("result", []):
                p = hit.get("patent") or {}
                patents.append({
                    "publication_number": p.get("publication_number"),
                    "title": (p.get("title") or "").strip(),
                    "assignee": p.get("assignee"),
                    "inventor": p.get("inventor"),
                    "filing_date": p.get("filing_date"),
                    "priority_date": p.get("priority_date"),
                    "grant_date": p.get("grant_date"),
                    "publication_date": p.get("publication_date"),
                    "snippet": (p.get("snippet") or "").strip(),
                })
        page += 1
        time.sleep(1.0)  # be polite
    # de-duplicate on publication number, keep first
    seen: set[str] = set()
    uniq = []
    for p in patents:
        n = p["publication_number"]
        if n and n not in seen:
            seen.add(n)
            uniq.append(p)
    return uniq, prov


def main() -> int:
    out = sys.argv[1] if len(sys.argv) > 1 else "research/draftkings-patents-raw.json"
    doc = {
        "source": "Google Patents XHR query endpoint",
        "user_agent": UA,
        "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "queries": {},
    }
    for name, q in QUERIES.items():
        patents, prov = walk(q)
        doc["queries"][name] = {"query": q, "n_records": len(patents),
                                "pages": prov, "patents": patents}
        print(f"{name}: {len(patents)} unique patents over {len(prov)} page(s)")
    with open(out, "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
