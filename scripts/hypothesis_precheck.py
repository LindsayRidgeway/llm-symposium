#!/usr/bin/env python3
"""Pre-check a hypothesis before it is filed.

The commons keeps asserting before checking. This makes the check mechanical: given a
gene/protein and a disease, it reports

  1. how much literature mentions both (Europe PMC, no key), split into two scopes —
     anywhere at all, and in a title or abstract;
  2. what the aggregated evidence says about the pair (Open Targets, with a score);
  3. how many trials have already been registered for the disease (ClinicalTrials.gov v2);
  4. whether the pair is ALREADY PUBLISHED TOGETHER — which is the only question that
     decides whether an "undiscovered link" is actually undiscovered.

REPAIRED 2026-09-17 after a clock run caught it killing real hypotheses. The old verdict was
`both > 0` on a bare all-fields query: ONE incidental hit — a conference abstract, a
supplementary gene list, a review's table — and the result was "ALREADY PUBLISHED TOGETHER,
not a discovery". It was a false-negative generator, and false negatives here are expensive:
they kill the only output this program has. The repair does three things:

  * SCOPE, named. The all-fields number and the title/abstract number are reported
    separately, because they are different claims. "A document contains both strings" is
    not "a paper is about the pair".
  * THE EVIDENCE, listed. Every hit that would kill a hypothesis is fetched with its title
    and identifier, so the claim can be read instead of counted. A number that ends a line
    of work must be inspectable.
  * A GRADED VERDICT instead of a binary one — a handful of incidental co-mentions is a
    prompt to read, not a verdict.

Usage:
    python3 scripts/hypothesis_precheck.py IGFBP5 hypothyroidism
    python3 scripts/hypothesis_precheck.py --json IGFBP5 "Peyronie's disease"
    python3 scripts/hypothesis_precheck.py --selftest
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "llm-symposium-precheck/1.0 (public research; no key)"}
OT = "https://api.platform.opentargets.org/api/v4/graphql"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

# How many all-fields-only co-mentions still count as "incidental noise" rather than a join.
# Above this, the list is long enough that the pair has probably been discussed somewhere and
# the honest move is to read it, not to call it novel.
INCIDENTAL_MAX = 5


def _get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


def _graphql(query: str):
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(OT, data=body,
                                 headers={**UA, "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=45).read())["data"]


def europepmc(term: str) -> int:
    u = EPMC + "?format=json&pageSize=1&query=" + urllib.parse.quote(term)
    try:
        return int(json.loads(_get(u)).get("hitCount", 0))
    except Exception:
        return -1


def europepmc_hits(term: str, n: int = 5) -> list:
    """The evidence itself, so a verdict can be read rather than believed."""
    u = EPMC + "?format=json&pageSize=%d&resultType=core&query=" % n + urllib.parse.quote(term)
    try:
        d = json.loads(_get(u))
    except Exception:
        return []
    out = []
    for r in (d.get("resultList") or {}).get("result", []) or []:
        out.append({
            "title": (r.get("title") or "").strip()[:180],
            "id": r.get("pmid") or r.get("id") or "",
            "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title", "")[:70],
            "year": r.get("pubYear") or "",
            "source": r.get("source") or "",
        })
    return out


def trials(condition: str) -> int:
    u = ("https://clinicaltrials.gov/api/v2/studies?pageSize=1&countTotal=true&query.cond="
         + urllib.parse.quote(condition))
    try:
        return int(json.loads(_get(u)).get("totalCount", 0))
    except Exception:
        return -1


def ot_target(symbol: str):
    q = '{ search(queryString: "%s", entityNames: ["target"]) { hits { id name } } }' % symbol
    hits = (_graphql(q).get("search") or {}).get("hits") or []
    return (hits[0]["id"], hits[0]["name"]) if hits else (None, None)


def ot_disease(name: str):
    q = '{ search(queryString: "%s", entityNames: ["disease"]) { hits { id name } } }' % name
    hits = (_graphql(q).get("search") or {}).get("hits") or []
    return (hits[0]["id"], hits[0]["name"]) if hits else (None, None)


def ot_score(ensembl: str, efo: str):
    q = ('{ target(ensemblId: "%s") { associatedDiseases(page: {index: 0, size: 1}, '
         'BFilter: "%s") { rows { score } } } }') % (ensembl, efo)
    try:
        rows = ((_graphql(q).get("target") or {}).get("associatedDiseases") or {}).get("rows") or []
        return rows[0]["score"] if rows else None
    except Exception:
        return None


def check(symbol: str, disease: str, evidence: bool = True) -> dict:
    ens, ens_name = ot_target(symbol)
    efo, efo_name = ot_disease(disease)

    # TWO SCOPES. The all-fields query is what the old verdict used on its own; the
    # title/abstract query is closer to "a paper is about this pair".
    both_all = europepmc(f'"{symbol}" AND ("{disease}")')
    both_strict = europepmc(
        f'(TITLE:"{symbol}" OR ABSTRACT:"{symbol}") AND '
        f'(TITLE:"{disease}" OR ABSTRACT:"{disease}")')
    just_disease = europepmc(f'"{disease}"')
    n_trials = trials(disease)
    score = ot_score(ens, efo) if (ens and efo) else None

    # The verdict is graded, and it says which scope it is speaking about.
    if both_strict > 0:
        verdict = (f"ALREADY PUBLISHED TOGETHER — {both_strict} paper(s) name both in a title "
                   f"or abstract. Not a discovery; cite it as prior work.")
    elif both_all == 0:
        verdict = ("no document found containing both terms at all — a candidate, NOT a finding.")
    elif both_all <= INCIDENTAL_MAX:
        verdict = (f"only {both_all} document(s) contain both terms anywhere, and NONE in a title "
                   f"or abstract — READ THEM below before claiming novelty. A co-mention is not a study.")
    else:
        verdict = (f"{both_all} documents contain both terms but none in a title or abstract — "
                   f"long enough that the pair has been discussed somewhere. Read the list; do not "
                   f"call it novel on this number alone.")

    hits = europepmc_hits(f'"{symbol}" AND ("{disease}")') if (evidence and both_all > 0) else []
    return {
        "target_symbol": symbol,
        "target_resolved": ens_name,
        "ensembl_id": ens,
        "disease_query": disease,
        "disease_resolved": efo_name,
        "efo_id": efo,
        "documents_containing_both_any_field": both_all,
        "papers_naming_both_in_title_or_abstract": both_strict,
        "papers_joining_both": both_all,          # kept: older records reference this key
        "papers_on_disease": just_disease,
        "open_targets_score": score,
        "registered_trials_for_disease": n_trials,
        "already_linked_in_literature": both_strict > 0,
        "evidence": hits,
        "verdict": verdict,
    }


def selftest() -> int:
    """Two pairs with known answers, so the instrument can be seen to discriminate.

    SLC19A3 (thiamine transporter) against ME/CFS is the case that exposed the defect: the
    old tool called it published-together on one incidental mention. PDHA1 against the same
    disease is a pair the literature does discuss. A tool that cannot tell these apart is
    not measuring novelty.
    """
    print("Self-test: one pair the literature discusses, one it does not.\n")
    a = check("PDHA1", "chronic fatigue syndrome")
    b = check("SLC19A3", "chronic fatigue syndrome")
    for label, r in (("PDHA1 (expected: some literature)", a),
                     ("SLC19A3 (expected: none or incidental)", b)):
        print("  %-40s all-fields=%-5s title/abstract=%-4s" % (
            label, r["documents_containing_both_any_field"],
            r["papers_naming_both_in_title_or_abstract"]))
    discriminates = (a["documents_containing_both_any_field"] >
                     b["documents_containing_both_any_field"])
    print("\n  discriminates: %s" % ("yes" if discriminates else "NO — the counts do not separate them"))
    print("  (the two scopes are printed for both, which is the repair: a number that kills a")
    print("   hypothesis must say what it counted and where.)")
    return 0 if discriminates else 1


def main() -> int:
    args = [a for a in sys.argv[1:]]
    as_json = "--json" in args
    run_selftest = "--selftest" in args
    args = [a for a in args if a not in ("--json", "--selftest")]
    if run_selftest:
        return selftest()
    if len(args) != 2:
        print(__doc__)
        return 1
    r = check(args[0], args[1])
    if as_json:
        print(json.dumps(r, indent=2))
        return 0
    print(f"\nPRE-CHECK — {r['target_symbol']} × {r['disease_query']}\n" + "-" * 58)
    print(f"  target resolved          : {r['target_resolved']} ({r['ensembl_id']})")
    print(f"  disease resolved         : {r['disease_resolved']} ({r['efo_id']})")
    print(f"  papers on disease        : {r['papers_on_disease']:,}")
    print(f"  both terms, any field    : {r['documents_containing_both_any_field']:,}")
    print(f"  both in title/abstract   : {r['papers_naming_both_in_title_or_abstract']:,}   <-- decides novelty")
    print(f"  Open Targets score       : {r['open_targets_score']}")
    print(f"  registered trials        : {r['registered_trials_for_disease']:,}")
    print(f"\n  VERDICT: {r['verdict']}")
    if r.get("evidence"):
        print("\n  The documents that number is counting:")
        for h in r["evidence"]:
            print("    [%s %s] %s — %s" % (h["source"], h["id"], h["year"], h["title"]))
    print("\n  A zero here means nobody has PUBLISHED the link. It does not mean the link is")
    print("  true, or untested, or worth money. Discovery is not validation. State both.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
