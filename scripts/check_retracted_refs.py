#!/usr/bin/env python3
"""Does a paper's reference list still stand on work that has been retracted?

Companion tool to Works entry 8 ("Has this paper been retracted?"), for a whole
reference list rather than a single DOI.. The question a reader
actually has about a guideline is not "is it retracted" but "does it rest on anything that
was". This script answers that for one document, and prints every request it made.

Method, in three steps, each one on the page too:

  1. RESOLVE  — OpenAlex (`api.openalex.org/works/doi:<doi>`): the work, and its
     `referenced_works` list. OpenAlex is used because it hands back the whole reference
     list as machine-readable IDs, which most publishers do not deposit in Crossref.
  2. FLAG    — OpenAlex again, in batches of 100 ids, filtered `is_retracted: true`. The
     flag is OpenAlex's, and it is derived from retraction notices deposited with Crossref
     and (lately) the Retraction Watch data; it is not our judgement and not a finding.
  3. CONFIRM — Crossref (`api.crossref.org/works/<doi>`), asked *separately* and by DOI,
     whether the flagged record itself carries a retraction update (`updated-by` /
     `update-to`, type `retraction`). This matters: a flag nobody can re-derive is an
     assertion, and the page shows the notice so a reader can go read it.

Two numbers this script measures rather than assumes, because both would otherwise be
invisible and would make a zero look like an answer:

  * REFERENCES THAT DO NOT RESOLVE. OpenAlex `referenced_works` can name an id that has
    since been merged into another work; a batch ask then returns fewer records than ids.
    The shortfall is printed as `unresolved`, and it is a hole in the check, not a pass.
  * FLAGS THAT CROSSREF DOES NOT CONFIRM. Printed as `unconfirmed`, and listed with what
    Crossref said instead, so an over-flag is visible rather than credited.

Honest scope, stated here because the page must state it too: a retracted reference is not
a wrong conclusion. Retractions include honest error, plagiarism in a review, duplicate
publication, publisher error, and retraction-and-republication with the result unchanged.
This tool points at the reference and hands over the notice. It does not judge the
guideline, and it cannot see an error that was never retracted — which is most of them.

Usage:
  python3 scripts/check_retracted_refs.py 10.1093/eurheartj/ehy339     # one document
  python3 scripts/check_retracted_refs.py --selftest                   # prove the flag fires
  python3 scripts/check_retracted_refs.py --examples --out FILE        # the shipped sample
  python3 scripts/check_retracted_refs.py --json <doi>                 # machine-readable
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

OA = "https://api.openalex.org/works"
CR = "https://api.crossref.org/works/"
MAILTO = "desi.s.amigo@gmail.com"
UA = ("Mozilla/5.0 (LLM Symposium, works entry 7 retraction check; "
      "mailto:%s; +https://lindsayridgeway.github.io/llm-symposium/)" % MAILTO)
BATCH = 100          # ids per OpenAlex OR-filter ask (their filter cap; 200 would be refused)
PAUSE = 0.35         # seconds between asks: this is someone else's server
CONFIRM_LIMIT = 40   # Crossref asks per document, capped so one run cannot hammer them

# The detector has to be shown to fire. These four are retracted, one of them notoriously,
# and one of them was retracted *and republished with the result intact*, which is the case
# a reader most needs to see distinguished from the others.
SELFTEST = [
    ("10.1016/S0140-6736(97)11096-0", "Wakefield et al. 1998, the paper that started the MMR scare"),
    ("10.1056/NEJMoa1200303", "PREDIMED: retracted 2018, then republished with the conclusion intact"),
    ("10.1016/S0140-6736(20)31180-6", "Mehra et al. 2020, the Surgisphere hydroxychloroquine paper"),
    ("10.1016/S0140-6736(11)61590-0", "SCIPIO (cardiac stem cells), retracted 2019"),
]

# The shipped sample. NOT a survey and not a prevalence estimate: eight documents chosen
# because they are public, widely used, and have long machine-readable reference lists.
EXAMPLES = [
    ("10.1093/eurheartj/ehy339", "2018 ESC/ESH Guidelines for the management of arterial hypertension"),
    ("10.1161/CIR.0000000000000625", "2018 AHA/ACC cholesterol guideline"),
    ("10.1093/eurheartj/eht151", "2013 ESH/ESC Guidelines for the management of arterial hypertension"),
    ("10.2337/dc14-S014", "Standards of Medical Care in Diabetes — 2014"),
    ("10.1161/CIR.0b013e3182742cf6", "2013 ACCF/AHA Guideline for the Management of ST-Elevation MI"),
    ("10.1016/j.kint.2021.05.021", "KDIGO 2021 Clinical Practice Guideline for Glomerular Diseases"),
    ("10.1210/jc.2016-2573", "Endocrine Society: Pediatric Obesity — Assessment, Treatment, Prevention"),
    ("10.1161/HYP.0000000000000065", "2017 ACC/AHA hypertension guideline"),
]

_log = []


def _get(url: str, timeout: int = 60, attempts: int = 3):
    """One polite anonymous GET. No key, no credential: if it needed one, that is the answer."""
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                _log.append(url)
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:                                    # noqa: BLE001 - reported as-is
            last = e
            time.sleep(1.0 + 2.0 * i)
    _log.append(url + "   [FAILED: %s]" % last)
    raise RuntimeError("request failed: %s  (%s)" % (last, url))


def openalex_work(doi: str) -> dict:
    sel = "id,doi,title,publication_year,is_retracted,referenced_works,referenced_works_count"
    url = "%s/doi:%s?select=%s&mailto=%s" % (OA, urllib.parse.quote(doi), sel, MAILTO)
    return _get(url)


def flag_batch(ids: list[str]) -> tuple[list[dict], int]:
    """Ask which of these ids are flagged retracted. Returns (flagged, resolved_count)."""
    filt = "openalex_id:" + "|".join(ids) + ",is_retracted:true"
    url = "%s?filter=%s&per-page=200&select=id,doi,title,publication_year,is_retracted&mailto=%s" % (
        OA, urllib.parse.quote(filt, safe=":|,"), MAILTO)
    d = _get(url)
    return d.get("results", []), int(d.get("meta", {}).get("count", 0))


def resolve_batch(ids: list[str]) -> int:
    """How many of these ids still exist as records at all (merged ids vanish)."""
    filt = "openalex_id:" + "|".join(ids)
    url = "%s?filter=%s&per-page=1&select=id&mailto=%s" % (
        OA, urllib.parse.quote(filt, safe=":|,"), MAILTO)
    return int(_get(url).get("meta", {}).get("count", 0))


def crossref_update(doi: str) -> dict:
    """Ask Crossref, independently, what updates this DOI's record carries."""
    try:
        m = _get(CR + urllib.parse.quote(doi), timeout=45)["message"]
    except Exception as e:                                        # noqa: BLE001
        return {"checked": True, "error": str(e)[:120]}
    out = {"checked": True, "crossref_type": m.get("type"),
           "crossref_title": (m.get("title") or [""])[0][:200],
           "updated_by": [{"type": u.get("type"), "doi": (u.get("DOI") or "").lower()}
                          for u in (m.get("updated-by") or [])],
           "update_to": [{"type": u.get("type"), "doi": (u.get("DOI") or "").lower()}
                         for u in (m.get("update-to") or [])]}
    retractions, seen = [], set()
    for u in out["updated_by"] + out["update_to"]:
        if u["type"] in ("retraction", "partial_retraction", "withdrawal") and u["doi"] not in seen:
            seen.add(u["doi"])
            retractions.append(u)
    out["retraction_notices"] = retractions
    out["confirms_retraction"] = bool(retractions)
    return out


def check(doi: str, limit_refs: int | None = None, confirm: bool = True) -> dict:
    work = openalex_work(doi)
    ref_ids = [u.rsplit("/", 1)[-1] for u in (work.get("referenced_works") or [])]
    if limit_refs:
        ref_ids = ref_ids[:limit_refs]

    flagged, resolved, requests_made = [], 0, 0
    for i in range(0, len(ref_ids), BATCH):
        chunk = ref_ids[i:i + BATCH]
        hits, _ = flag_batch(chunk)
        requests_made += 1
        flagged += hits
        time.sleep(PAUSE)
        # count what is still resolvable so an unresolvable id is not silently a "not retracted"
        resolved += resolve_batch(chunk)
        requests_made += 1
        time.sleep(PAUSE)

    for f in flagged:
        f["doi"] = (f.get("doi") or "").replace("https://doi.org/", "")
    if confirm:
        for f in flagged[:CONFIRM_LIMIT]:
            if f["doi"]:
                f["crossref"] = crossref_update(f["doi"])
                time.sleep(PAUSE)

    confirmed = sum(1 for f in flagged if (f.get("crossref") or {}).get("confirms_retraction"))
    checked = sum(1 for f in flagged if (f.get("crossref") or {}).get("checked"))
    return {
        "doi": (work.get("doi") or "").replace("https://doi.org/", ""),
        "title": work.get("title"),
        "publication_year": work.get("publication_year"),
        "this_document_is_flagged_retracted": bool(work.get("is_retracted")),
        "references_listed": len(ref_ids),
        "references_resolved": resolved,
        "references_unresolved": len(ref_ids) - resolved,
        "reference_requests": requests_made,
        "flagged_retracted": flagged,
        "flagged_count": len(flagged),
        "crossref_checked": checked,
        "crossref_confirmed": confirmed,
        "crossref_unconfirmed": checked - confirmed,
    }


def show(r: dict) -> None:
    print("\n%s" % (r["title"] or "(no title)"))
    print("  doi %s (%s)   this document flagged retracted: %s" %
          (r["doi"], r["publication_year"], r["this_document_is_flagged_retracted"]))
    print("  references listed %d | resolvable %d | UNRESOLVED %d  <- a hole in the check, not a pass"
          % (r["references_listed"], r["references_resolved"], r["references_unresolved"]))
    print("  references flagged retracted: %d  (Crossref confirms %d of the %d checked, does not confirm %d)"
          % (r["flagged_count"], r["crossref_confirmed"], r["crossref_checked"], r["crossref_unconfirmed"]))
    for f in r["flagged_retracted"]:
        cr = f.get("crossref") or {}
        notices = ", ".join(n["doi"] for n in (cr.get("retraction_notices") or [])) or "none found"
        print("    - %s  %s\n        %s\n        retraction notice(s) at Crossref: %s"
              % (f.get("publication_year"), f.get("doi"), (f.get("title") or "")[:110], notices))


def selftest() -> int:
    """The flag has to be shown to fire, or a zero on a real document means nothing."""
    print("Detector self-test: four works that are retracted, asked the same way a reference is.")
    fired = 0
    for doi, why in SELFTEST:
        try:
            w = openalex_work(doi)
            ok = bool(w.get("is_retracted"))
            fired += ok
            print("  %-6s %s\n         %s" % ("FIRED" if ok else "MISSED", why, doi))
        except Exception as e:                                    # noqa: BLE001
            print("  %-6s %s (%s)" % ("ERROR", why, str(e)[:80]))
        time.sleep(PAUSE)
    print("  %d of %d fired." % (fired, len(SELFTEST)))
    return 0 if fired == len(SELFTEST) else 1


def build_examples(out_path: str) -> int:
    docs = []
    for doi, label in EXAMPLES:
        try:
            r = check(doi)
        except Exception as e:                                    # noqa: BLE001
            print("  ! %s failed: %s" % (doi, str(e)[:120]), file=sys.stderr)
            continue
        r["label"] = label
        docs.append(r)
        show(r)
    fired = []
    for doi, why in SELFTEST:
        try:
            w = openalex_work(doi)
            fired.append({"doi": doi, "why": why, "title": w.get("title"),
                          "publication_year": w.get("publication_year"),
                          "flagged_retracted": bool(w.get("is_retracted"))})
        except Exception as e:                                    # noqa: BLE001
            fired.append({"doi": doi, "why": why, "error": str(e)[:120]})
        time.sleep(PAUSE)

    doc = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "method": ("OpenAlex referenced_works -> OpenAlex is_retracted in batches of %d -> "
                   "Crossref updated-by/update-to, asked separately by DOI. Every count here "
                   "was measured, not written down." % BATCH),
        "detector_selftest": fired,
        "selftest_all_fired": all(f.get("flagged_retracted") for f in fired),
        "documents": docs,
        "counts": {
            "documents": len(docs),
            "references_listed": sum(d["references_listed"] for d in docs),
            "references_resolved": sum(d["references_resolved"] for d in docs),
            "references_unresolved": sum(d["references_unresolved"] for d in docs),
            "flagged_retracted": sum(d["flagged_count"] for d in docs),
            "documents_with_at_least_one": sum(1 for d in docs if d["flagged_count"]),
            "crossref_checked": sum(d["crossref_checked"] for d in docs),
            "crossref_confirmed": sum(d["crossref_confirmed"] for d in docs),
        },
        "requests_made": len(_log),
    }
    if out_path:
        with open(out_path, "w") as fh:
            json.dump(doc, fh, indent=2, sort_keys=False)
            fh.write("\n")
        print("\nwrote %s  (%d documents, %d requests)" % (out_path, len(docs), len(_log)))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dois", nargs="*", help="DOI(s) of the document whose reference list to check")
    ap.add_argument("--selftest", action="store_true", help="verify the retraction flag still fires")
    ap.add_argument("--examples", action="store_true", help="re-measure the shipped sample")
    ap.add_argument("--out", default="", help="write the JSON here (with --examples)")
    ap.add_argument("--json", action="store_true", help="print raw JSON instead of a summary")
    ap.add_argument("--no-confirm", action="store_true", help="skip the Crossref cross-check")
    ap.add_argument("--limit-refs", type=int, default=None, help="check only the first N references")
    ap.add_argument("--show-requests", action="store_true", help="print every URL requested")
    a = ap.parse_args()

    code = 0
    if a.selftest:
        code = selftest()
    elif a.examples:
        code = build_examples(a.out)
    elif a.dois:
        out = []
        for doi in a.dois:
            try:
                r = check(doi, limit_refs=a.limit_refs, confirm=not a.no_confirm)
            except Exception as e:                                # noqa: BLE001
                print("! %s: %s" % (doi, str(e)[:160]), file=sys.stderr)
                code = 1
                continue
            out.append(r)
            show(r)
        if a.json:
            print(json.dumps(out, indent=2))
    else:
        ap.print_help()
        print("\nStart with:  python3 scripts/check_retracted_refs.py --selftest", file=sys.stderr)
        return 2

    if a.show_requests:
        print("\nEvery request made this run (%d):" % len(_log))
        for u in _log:
            print("  " + u)
    else:
        print("\n(%d requests made this run; --show-requests prints the URLs)" % len(_log))
    return code


if __name__ == "__main__":
    sys.exit(main())
