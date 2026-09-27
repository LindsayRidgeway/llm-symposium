#!/usr/bin/env python3
"""Measure whether candidate 03 of the works queue ("a claim and its source, side by side")
has a data path at all.

The candidate needs three things, and the queue file says none has been demonstrated:

  1. a source of PRIMARY DOCUMENTS (the paper a circulated claim rests on), reachable
     without an account;
  2. a way to read what the document ITSELF says, sentence by sentence;
  3. a way to show what the document does NOT establish, honestly, without taking a side.

This script measures (1) and (2) and demonstrates (3). It makes live keyless requests to
Europe PMC and Crossref only. Every request is printed on the result so any number here can
be re-derived by hand. No key, no account.

Run:  python3 scripts/measure_claim_source_path.py [--json out.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
UA = "llm-symposium-desi/1.0 (data-path verification; desi.s.amigo@gmail.com)"

# Claim subjects, chosen because they are the fear-driven end of the agenda: things a person
# is forwarded about, not things a researcher argues about. None of them is a position.
TOPICS = [
    "microplastics",
    "ultra-processed food",
    "titanium dioxide",
    "artificial sweetener",
    "seed oil",
    "PFAS",
]

PAGE = 25  # records read per topic

requests_log: list[str] = []


def get(url: str, timeout: int = 40) -> tuple[int, bytes]:
    requests_log.append(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # network, timeout, DNS
        return 0, str(e).encode()


def epmc_search(query: str, page_size: int = PAGE, result_type: str = "core") -> dict:
    params = {
        "query": query,
        "format": "json",
        "pageSize": page_size,
        "resultType": result_type,
    }
    url = f"{EPMC}/search?" + urllib.parse.urlencode(params)
    status, body = get(url)
    if status != 200:
        return {"_status": status, "_error": body[:200].decode("utf-8", "replace"), "_url": url}
    return json.loads(body)


def epmc_fulltext(pmcid: str) -> tuple[int, bytes, str]:
    """The article endpoint takes the PMCID as a SINGLE path segment.

    The documented-looking `/{source}/{id}/fullTextXML` form returns 404 for every record in
    this sample (23 of 23), which reads exactly like "this paper has no full text" — the
    failure the tool this measures must never make. Kept in the note as a measured trap.
    """
    url = f"{EPMC}/{pmcid}/fullTextXML"
    status, body = get(url)
    return status, body, url


def sentences(xml: str) -> list[str]:
    text = re.sub(r"<[^>]+>", " ", xml)
    text = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 30]


def section_titles(xml: str) -> list[str]:
    return [re.sub(r"<[^>]+>", "", m).strip() for m in re.findall(r"<title>(.*?)</title>", xml, re.S)]


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 30]


def _tag(node) -> str:
    return node.tag.split("}")[-1]


def body_sentences(xml_text: str) -> list[tuple[str, str]]:
    """Sentences from the article's own body paragraphs, each tagged with its section heading.

    This exists because the first pass — every word of the XML, reference list included — picked
    up a retraction notice, a reference-list title and a news quote and ranked them as the
    paper's own statement. Dropping <ref-list>, <back> and captions is the whole difference.
    """
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    out: list[tuple[str, str]] = []

    def walk(node, sec: str):
        for child in node:
            t = _tag(child)
            if t == "p":
                for s in split_sentences("".join(child.itertext())):
                    out.append((sec, s))
            elif t == "sec":
                name = sec
                for tt in child:
                    if _tag(tt) == "title":
                        name = "".join(tt.itertext()).strip()
                walk(child, name)
            elif t in ("ref-list", "back", "table-wrap", "fig"):
                continue
            else:
                walk(child, sec)

    for body in root.iter():
        if _tag(body) == "body":
            walk(body, "")
    return out


def article_type(xml_text: str) -> str:
    m = re.search(r'<article[^>]*article-type="([^"]+)"', xml_text)
    return m.group(1) if m else ""


STOP = set("a an the of to in for and or on with by is are was were be been it its this that "
           "as at from not no does do did than then there their they we you i".split())


def toks(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP}


def best_sentence(claim: str, sents: list[str]) -> tuple[str, float]:
    """Closest sentence in the document to the claim, by shared-content-word overlap.
    This is the whole of the 'what does the source actually say' step: no model, no judgement,
    just the document's own words ranked against the claim's words."""
    c = toks(claim)
    if not c or not sents:
        return "", 0.0
    best, score = "", 0.0
    for s in sents:
        t = toks(s)
        if not t:
            continue
        j = len(c & t) / len(c | t)
        if j > score:
            best, score = s, j
    return best, round(score, 4)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    ap.add_argument("--fulltext-per-topic", type=int, default=4)
    args = ap.parse_args()

    out: dict = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "topics": {},
        "coverage": {},
        "notes": [],
    }

    tot_read = tot_inepmc = tot_oa = 0
    ft_tried = ft_ok = ft_with_limits = 0

    for topic in TOPICS:
        res = epmc_search(f'"{topic}"')
        if "_status" in res:
            out["topics"][topic] = {"error": res}
            continue
        hits = res.get("resultList", {}).get("result", [])
        hit_count = res.get("hitCount")
        rec = {
            "query": f'"{topic}"',
            "hit_count": hit_count,
            "read": len(hits),
            "in_epmc": sum(1 for h in hits if h.get("inEPMC") == "Y"),
            "open_access_flag": sum(1 for h in hits if h.get("isOpenAccess") == "Y"),
            "with_abstract": sum(1 for h in hits if h.get("abstractText")),
            "fulltext": [],
        }
        tot_read += len(hits)
        tot_inepmc += rec["in_epmc"]
        tot_oa += rec["open_access_flag"]

        tried = 0
        for h in hits:
            if h.get("inEPMC") != "Y" or tried >= args.fulltext_per_topic:
                continue
            pmcid = h.get("pmcid") or ""
            if not pmcid:
                continue
            tried += 1
            status, body, url = epmc_fulltext(pmcid)
            xml = body.decode("utf-8", "replace") if status == 200 else ""
            sents = sentences(xml) if xml else []
            titles = section_titles(xml) if xml else []
            lim = [t for t in titles if re.search(r"limit", t, re.I)]
            bsent = body_sentences(xml) if xml else []
            item = {
                "pmcid": h.get("pmcid"),
                "doi": h.get("doi"),
                "year": h.get("pubYear"),
                "journal": (h.get("journalInfo") or {}).get("journal", {}).get("title"),
                "title": (h.get("title") or "")[:160],
                "fulltext_http": status,
                "bytes": len(body),
                "article_type": article_type(xml) if xml else "",
                "sentences": len(sents),
                "body_sentences": len(bsent),
                "has_limitations_section": bool(lim),
                "limitations_titles": lim,
                "pub_types": [
                    p.get("name") if isinstance(p, dict) else p
                    for p in ((h.get("pubTypeList") or {}).get("pubType") or [])
                ],
                "url": url,
            }
            # demonstration of step 3 for the first readable paper of the first topic
            claim = f"{topic} is harmful to human health"
            if sents:
                s, sc = best_sentence(claim, sents)
                item["demo_claim"] = claim
                item["demo_best_sentence"] = s[:400]
                item["demo_overlap"] = sc
            if bsent:
                sec, s2 = max(bsent, key=lambda p: best_sentence(claim, [p[1]])[1])
                sc2 = best_sentence(claim, [s2])[1]
                item["demo_body_section"] = sec
                item["demo_body_sentence"] = s2[:400]
                item["demo_body_overlap"] = sc2
            rec["fulltext"].append(item)
            ft_tried += 1
            if status == 200 and sents:
                ft_ok += 1
            if lim:
                ft_with_limits += 1

        out["topics"][topic] = rec
        print(f"{topic:24s} hits={hit_count:<8} read={len(hits):<3} "
              f"inEPMC={rec['in_epmc']:<3} OA_flag={rec['open_access_flag']:<3} "
              f"fulltext_tried={tried}")

    # --- the three-way coverage question asked directly of the index -----------------
    cov = {}
    for q in ['"microplastics"',
              '"microplastics" AND OPEN_ACCESS:Y',
              '"microplastics" AND IN_EPMC:Y',
              '"microplastics" AND HAS_FT:Y',
              '"microplastics" AND HAS_ABSTRACT:Y']:
        r = epmc_search(q, page_size=1, result_type="idlist")
        cov[q] = r.get("hitCount")
    out["coverage"] = cov
    print("\ncoverage (hitCount, pageSize=1):")
    for k, v in cov.items():
        print(f"  {k:45s} {v}")

    # --- the paywalled case, named explicitly ---------------------------------------
    pay = {}
    for doi in ["10.1016/j.chemosphere.2024.143587",   # black-plastic-kitchen-utensils scare
                "10.1016/S0140-6736(98)01085-X"]:      # Wakefield 1998, retracted
        r = epmc_search(f'DOI:"{doi}"', page_size=1, result_type="core")
        hits = (r.get("resultList", {}) or {}).get("result", [])
        pay[doi] = {
            "hit": bool(hits),
            "inEPMC": hits[0].get("inEPMC") if hits else None,
            "isOpenAccess": hits[0].get("isOpenAccess") if hits else None,
            "pmcid": hits[0].get("pmcid") if hits else None,
        }
        print(f"\nDOI {doi}: {pay[doi]}")
    out["paywalled_probe"] = pay

    out["totals"] = {
        "records_read": tot_read,
        "in_epmc": tot_inepmc,
        "open_access_flag": tot_oa,
        "fulltext_attempted": ft_tried,
        "fulltext_readable": ft_ok,
        "fulltext_with_limitations_section": ft_with_limits,
    }
    types: dict = {}
    for t in out["topics"].values():
        for f in t.get("fulltext", []):
            if f.get("fulltext_http") == 200:
                k = f.get("article_type") or "?"
                types[k] = types.get(k, 0) + 1
    out["totals"]["readable_by_article_type"] = types
    print("\nreadable full texts by article-type:", json.dumps(types))
    print("totals:", json.dumps(out["totals"], indent=2))
    out["requests"] = requests_log

    if args.json:
        with open(args.json, "w") as f:
            json.dump(out, f, indent=1)
        print(f"\nwrote {args.json} ({len(requests_log)} requests logged)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
