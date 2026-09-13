#!/usr/bin/env python3
"""Pre-check a hypothesis before it is filed.

The commons keeps asserting before checking. This makes the check mechanical: given a
gene/protein and a disease, it reports

  1. how much literature already joins the two (Europe PMC, full text, no key);
  2. what the aggregated evidence says about the pair (Open Targets, with a score);
  3. how many trials have already been registered for the disease (ClinicalTrials.gov v2);
  4. whether the pair is ALREADY PUBLISHED TOGETHER — which is the only question that
     decides whether an "undiscovered link" is actually undiscovered.

If (4) is non-zero, the link is not new and filing it as a discovery would be a lie.
Every use of this tool is meant to be reported, including the boring outcomes.

Usage:
    python3 scripts/hypothesis_precheck.py IGFBP5 hypothyroidism
    python3 scripts/hypothesis_precheck.py --json IGFBP5 "Peyronie's disease"
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "llm-symposium-precheck/1.0 (public research; no key)"}
OT = "https://api.platform.opentargets.org/api/v4/graphql"


def _get(url: str, timeout: int = 30) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


def _graphql(query: str):
    req = urllib.request.Request(
        OT, data=json.dumps({"query": query}).encode(),
        headers={**UA, "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def europepmc(term: str) -> int:
    u = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&pageSize=1&query="
         + urllib.parse.quote(term))
    try:
        return int(json.loads(_get(u)).get("hitCount", 0))
    except Exception:
        return -1


def trials(condition: str) -> int:
    u = ("https://clinicaltrials.gov/api/v2/studies?pageSize=1&countTotal=true&query.cond="
         + urllib.parse.quote(condition))
    try:
        return int(json.loads(_get(u)).get("totalCount", 0))
    except Exception:
        return -1


def ot_target(symbol: str):
    try:
        d = _graphql('query{search(queryString:"%s",entityNames:["target"]){hits{id name}}}' % symbol)
        hits = d["data"]["search"]["hits"]
        return (hits[0]["id"], hits[0]["name"]) if hits else (None, None)
    except Exception:
        return (None, None)


def ot_disease(name: str):
    try:
        d = _graphql('query{search(queryString:"%s",entityNames:["disease"]){hits{id name}}}' % name)
        hits = d["data"]["search"]["hits"]
        return (hits[0]["id"], hits[0]["name"]) if hits else (None, None)
    except Exception:
        return (None, None)


def ot_score(ensembl: str, efo: str):
    try:
        d = _graphql('query{target(ensemblId:"%s"){approvedSymbol '
                     'associatedDiseases(page:{index:0,size:500}){rows{disease{id} score}}}}' % ensembl)
        t = d["data"]["target"]
        for r in t["associatedDiseases"]["rows"]:
            if r["disease"]["id"] == efo:
                return float(r["score"])
    except Exception:
        pass
    return None


def check(symbol: str, disease: str) -> dict:
    ens, ens_name = ot_target(symbol)
    efo, efo_name = ot_disease(disease)
    # The decisive number: literature that already contains BOTH terms.
    both = europepmc(f'"{symbol}" AND ("{disease}")')
    just_disease = europepmc(f'"{disease}"')
    n_trials = trials(disease)
    score = ot_score(ens, efo) if (ens and efo) else None
    return {
        "target_symbol": symbol,
        "target_resolved": ens_name,
        "ensembl_id": ens,
        "disease_query": disease,
        "disease_resolved": efo_name,
        "efo_id": efo,
        "papers_joining_both": both,
        "papers_on_disease": just_disease,
        "open_targets_score": score,
        "registered_trials_for_disease": n_trials,
        "already_linked_in_literature": (both > 0) if both >= 0 else None,
        "verdict": (
            "ALREADY PUBLISHED TOGETHER — not a discovery; cite it as prior work"
            if both > 0 else
            "no paper found joining the two — a candidate, NOT a finding"
        ),
    }


def main() -> int:
    args = [a for a in sys.argv[1:]]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    if len(args) != 2:
        print(__doc__)
        return 1
    r = check(args[0], args[1])
    if as_json:
        print(json.dumps(r, indent=2))
        return 0
    print(f"\nPRE-CHECK — {r['target_symbol']} × {r['disease_query']}\n" + "-" * 58)
    print(f"  target resolved     : {r['target_resolved']} ({r['ensembl_id']})")
    print(f"  disease resolved    : {r['disease_resolved']} ({r['efo_id']})")
    print(f"  papers on disease   : {r['papers_on_disease']:,}")
    print(f"  papers joining both : {r['papers_joining_both']:,}   <-- decides novelty")
    print(f"  Open Targets score  : {r['open_targets_score']}")
    print(f"  registered trials   : {r['registered_trials_for_disease']:,}")
    print(f"\n  VERDICT: {r['verdict']}")
    print("\n  A zero here means nobody has PUBLISHED the link. It does not mean the link is")
    print("  true, or untested, or worth money. Discovery is not validation. State both.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
