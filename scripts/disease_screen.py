#!/usr/bin/env python3
"""Screen many candidate targets against one disease, mechanically, before filing anything.

The disease program's rule 3 is "check before filing". The single-pair check
(`scripts/hypothesis_precheck.py TARGET DISEASE`) does that for a pair someone already has in
mind. This does the step before it: given a *list* of plausible targets for one condition, it
reports, for every pair, the same two scopes the single-pair pre-check reports —

  * any_field — documents containing both terms anywhere (counts mentions, not studies);
  * strict    — documents naming both in a TITLE or ABSTRACT (closer to "a paper is about the
                pair", and the number that decides novelty);

plus the Open Targets aggregated score for the pair and the number of registered trials for the
condition. The output is a JSON screen, so a later run can read the counts instead of re-running
the searches, and so a negative result ("nothing here is unjoined") is recorded rather than
forgotten — which is the failure mode this program exists to avoid.

A target list is data, not code: pass a JSON file of `[{"category": "...", "symbol": "..."}, ...]`.
Choosing the targets is a judgement and stays with whoever runs the screen; the screen only
measures how much literature already joins each one. This is the "candidate-generation so the
queue feeds itself" half of agenda item 7, made mechanical.

**Names, not just symbols (`names`), and disease forms (`--forms`).** Added 2026-09-18 after the
pudendal-neuralgia screen: a symbol-only query against a thin disease returned 39 of 41 targets as
"no title/abstract join", which is a *false-gap generator*, not a finding. The literature writes
"nerve growth factor", not "NGF"; "substance P", not "TAC1"; "endothelial nitric oxide synthase", not
"NOS3". A target entry may now carry `"names": ["nerve growth factor", ...]`, and `--forms` may add
disease spellings; the screen reports the *maximum* join over (symbol|names) × (disease|forms), the
pair that produced it, and a `naming_sensitive` flag on any row whose number came from something
other than the plain symbol. The default query is unchanged when neither is supplied.

Usage:
    python3 scripts/disease_screen.py ENDOMETRIOSIS targets.json --out research/endo-screen.json
    python3 scripts/disease_screen.py "pudendal neuralgia" targets.json --forms "pudendal nerve,pudendal neuropathy"
    python3 scripts/disease_screen.py --density "vulvodynia" "interstitial cystitis"
    python3 scripts/disease_screen.py --selftest
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "llm-symposium-screen/1.0 (public research; no key)"}
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OT = "https://api.platform.opentargets.org/api/v4/graphql"
INCIDENTAL_MAX = 5  # above this many any-field-only co-mentions, the pair has been discussed

_epmc_cache: dict = {}
_ot_cache: dict = {}


def _get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


def epmc(term: str) -> int:
    """Europe PMC hitCount, cached. -1 means the query failed (kept distinct from a real 0)."""
    if term in _epmc_cache:
        return _epmc_cache[term]
    u = EPMC + "?format=json&pageSize=1&query=" + urllib.parse.quote(term)
    try:
        n = int(json.loads(_get(u)).get("hitCount", 0))
    except Exception:
        n = -1
    _epmc_cache[term] = n
    return n


def any_field(symbol: str, disease: str) -> int:
    return epmc(f'"{symbol}" AND ("{disease}")')


def strict(symbol: str, disease: str) -> int:
    return epmc(f'(TITLE:"{symbol}" OR ABSTRACT:"{symbol}") AND '
                f'(TITLE:"{disease}" OR ABSTRACT:"{disease}")')


def trials(condition: str) -> int:
    u = ("https://clinicaltrials.gov/api/v2/studies?pageSize=1&countTotal=true&query.cond="
         + urllib.parse.quote(condition))
    try:
        return int(json.loads(_get(u)).get("totalCount", 0))
    except Exception:
        return -1


def _graphql(query: str):
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(OT, data=body,
                                 headers={**UA, "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=45).read())["data"]


def ot_disease(name: str):
    if "disease:" + name in _ot_cache:
        return _ot_cache["disease:" + name]
    q = '{ search(queryString: "%s", entityNames: ["disease"]) { hits { id name } } }' % name
    try:
        hits = (_graphql(q).get("search") or {}).get("hits") or []
        out = (hits[0]["id"], hits[0]["name"]) if hits else (None, None)
    except Exception:
        out = (None, None)
    _ot_cache["disease:" + name] = out
    return out


def ot_target(symbol: str):
    if "target:" + symbol in _ot_cache:
        return _ot_cache["target:" + symbol]
    q = '{ search(queryString: "%s", entityNames: ["target"]) { hits { id name } } }' % symbol
    try:
        hits = (_graphql(q).get("search") or {}).get("hits") or []
        out = (hits[0]["id"], hits[0]["name"]) if hits else (None, None)
    except Exception:
        out = (None, None)
    _ot_cache["target:" + symbol] = out
    return out


def ot_score(symbol: str, efo: str):
    ens, _ = ot_target(symbol)
    if not (ens and efo):
        return None
    q = ('{ target(ensemblId: "%s") { associatedDiseases(page: {index: 0, size: 1}, '
         'BFilter: "%s") { rows { score } } } }') % (ens, efo)
    try:
        rows = ((_graphql(q).get("target") or {}).get("associatedDiseases") or {}).get("rows") or []
        return rows[0]["score"] if rows else None
    except Exception:
        return None


def verdict(any_n: int, strict_n: int) -> str:
    if any_n < 0:
        return "QUERY FAILED — re-run this pair; do not read the number"
    if strict_n > 0:
        return "already published together (title/abstract) — prior work, cite it"
    if any_n == 0:
        return "unjoined — no document contains both; a candidate, NOT a finding"
    if any_n <= INCIDENTAL_MAX:
        return f"incidental only ({any_n}) — read them before claiming novelty"
    return f"discussed ({any_n} any-field, 0 strict) — read the list; not novel on this number"


def run(disease: str, targets: list, use_ot: bool = True, forms: list = None) -> dict:
    t0 = time.time()
    forms = [disease] + [f for f in (forms or []) if f and f != disease]
    dis_any = max(epmc(f'"{f}"') for f in forms)
    dis_strict = max(epmc(f'(TITLE:"{f}" OR ABSTRACT:"{f}")') for f in forms)
    n_trials = trials(disease)
    efo, efo_name = ot_disease(disease) if use_ot else (None, None)

    def one(t):
        sym = t["symbol"]
        # A target is a symbol AND the names a paper would actually use for it.
        names = [sym] + [n for n in t.get("names", []) if n]
        best = None  # (strict, any_field, name, disease form)
        for name in names:
            for form in forms:
                cand = (strict(name, form), any_field(name, form), name, form)
                if best is None or cand[:2] > best[:2]:
                    best = cand
        s, a, name, form = best
        # What the plain symbol-only query would have reported, kept so a reader can see the
        # difference a name makes rather than trusting the maximum on its own.
        sym_s, sym_a = strict(sym, disease), any_field(sym, disease)
        score = ot_score(sym, efo) if use_ot else None
        return {
            "category": t.get("category", ""),
            "symbol": sym,
            "any_field": a,
            "strict": s,
            "symbol_only_strict": sym_s,
            "symbol_only_any_field": sym_a,
            "matched_name": name,
            "matched_disease_form": form,
            "naming_sensitive": (name != sym or form != disease),
            "open_targets_score": score,
            "verdict": verdict(a, s),
        }

    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(one, targets))

    return {
        "disease": disease,
        "disease_forms_searched": forms,
        "disease_resolved": efo_name,
        "efo_id": efo,
        "disease_papers_any_field": dis_any,
        "disease_papers_strict": dis_strict,
        "registered_trials_for_disease": n_trials,
        "note": ("any_field = Europe PMC hitCount for \"SYMBOL\" AND (\"disease\") — counts "
                 "mentions, not studies. strict = SYMBOL and disease both in a TITLE or ABSTRACT "
                 "— the number that decides novelty. Counts move with spelling; these are small "
                 "numbers, not exact ones. A zero means nobody has PUBLISHED the link; it does "
                 "not mean the link is true, untested, or valuable. Where a target carries "
                 "`names`, any_field/strict are the maximum over the symbol and every name, so a "
                 "row is only 'unjoined' if it is unjoined under every spelling supplied."),
        "n_targets": len(targets),
        # Every band where strict == 0 is candidate territory, and the three bands are
        # different claims. The summary used to print only the first two, which hid the one
        # that matters most on a dense disease — nodes co-mentioned but never studied.
        "unjoined": [r["symbol"] for r in rows if r["strict"] == 0 and r["any_field"] == 0],
        "incidental_any_field_only": [r["symbol"] for r in rows
                                      if r["strict"] == 0 and 0 < r["any_field"] <= INCIDENTAL_MAX],
        "no_title_abstract_join": [r["symbol"] for r in rows if r["strict"] == 0],
        "no_strict_join_but_discussed": [r["symbol"] for r in rows
                                         if r["strict"] == 0 and r["any_field"] > INCIDENTAL_MAX],
        "joined_in_title_or_abstract": [r["symbol"] for r in rows if r["strict"] > 0],
        # The rows a symbol-only screen would have called unjoined but which are joined under a
        # name the literature actually uses. This is the false-gap count, and it belongs in the
        # artefact: the whole defect is that a false gap is indistinguishable from a real one.
        "false_gaps_repaired_by_names": [r["symbol"] for r in rows
                                         if r["naming_sensitive"] and r["symbol_only_strict"] == 0
                                         and r["strict"] > 0],
        "seconds": round(time.time() - t0, 1),
        "targets": rows,
    }


def density(conditions: list) -> list:
    """How worked-over is a condition, before anyone picks targets for it.

    The queue's own rule says a condition is only worth screening if its literature is thin,
    and that the check should happen *before* the condition is queued. It was not done for
    endometriosis, which turned out to be ~3.7x larger than ME/CFS and joined to 203 of 229
    plausible targets. This is that check, made mechanical: two Europe PMC counts and a trial
    count per condition, so a queue entry can carry its own measurement instead of a hunch
    about funding. A densely-joined condition is a negative control, not a candidate.
    """
    rows = []
    for c in conditions:
        rows.append({
            "condition": c,
            "any_field": epmc(f'"{c}"'),
            "strict": epmc(f'(TITLE:"{c}" OR ABSTRACT:"{c}")'),
            "trials": trials(c),
        })
    rows.sort(key=lambda r: r["strict"])
    return rows


def selftest() -> int:
    """Two known pairs inside the screen: one joined, one not. A screen that cannot separate
    them is not measuring novelty."""
    dis = "chronic fatigue syndrome"
    a = {"symbol": "PDHA1", "category": "control/joined"}
    b = {"symbol": "SLC19A3", "category": "control/unjoined"}
    ra, rb = run(dis, [a, b], use_ot=False)["targets"]
    print("Self-test: one pair the literature discusses, one it does not.\n")
    for label, r in (("PDHA1 (expected: discussed)", ra),
                     ("SLC19A3 (expected: unjoined/incidental)", rb)):
        print("  %-40s any_field=%-5s strict=%-4s  %s" % (
            label, r["any_field"], r["strict"], r["verdict"]))
    ok = ra["any_field"] > rb["any_field"]
    print("\n  discriminates: %s" % ("yes" if ok else "NO — the counts do not separate them"))
    return 0 if ok else 1


def main() -> int:
    args = [a for a in sys.argv[1:]]
    if "--selftest" in args:
        return selftest()
    use_ot = "--no-ot" not in args
    args = [a for a in args if a != "--no-ot"]
    out = None
    if "--out" in args:
        i = args.index("--out")
        out = args[i + 1]
        del args[i:i + 2]
    if "--density" in args:
        args = [a for a in args if a != "--density"]
        if not args:
            print(__doc__)
            return 1
        rows = density(args)
        if out:
            with open(out, "w") as fh:
                json.dump({"conditions": rows}, fh, indent=1)
                fh.write("\n")
        print("%-44s %-9s %-9s %s" % ("condition", "any_field", "strict", "trials"))
        for r in rows:
            print("%-44s %-9s %-9s %s" % (r["condition"], r["any_field"], r["strict"], r["trials"]))
        print("\nstrict = papers naming the condition in a title or abstract. A large number "
              "means the ground is worked; go elsewhere for a joined-literature discovery.")
        return 0
    if "--forms" in args:
        i = args.index("--forms")
        forms = [x.strip() for x in args[i + 1].split(",") if x.strip()]
        del args[i:i + 2]
    else:
        forms = None
    if len(args) != 2:
        print(__doc__)
        return 1
    disease, targets_path = args
    with open(targets_path) as fh:
        targets = json.load(fh)
    res = run(disease, targets, use_ot=use_ot, forms=forms)
    if out:
        with open(out, "w") as fh:
            json.dump(res, fh, indent=1)
            fh.write("\n")
    print(f"{disease}: {res['n_targets']} targets in {res['seconds']}s; "
          f"disease papers any_field={res['disease_papers_any_field']}, "
          f"strict={res['disease_papers_strict']}, trials={res['registered_trials_for_disease']}\n")
    print("%-10s %-8s %-8s %s" % ("symbol", "any", "strict", "verdict"))
    for r in sorted(res["targets"], key=lambda r: (r["strict"], r["any_field"])):
        print("%-10s %-8s %-8s %s" % (r["symbol"], r["any_field"], r["strict"], r["verdict"]))
    print(f"\nno title/abstract join (all bands): {', '.join(res['no_title_abstract_join']) or '(none)'}")
    print(f"  of those, fully unjoined (0/0): {', '.join(res['unjoined']) or '(none)'}")
    print(f"  of those, incidental only (1-5): {', '.join(res['incidental_any_field_only']) or '(none)'}")
    print(f"  of those, co-mentioned but never studied: "
          f"{', '.join(res['no_strict_join_but_discussed']) or '(none)'}")
    if res["disease_forms_searched"] and len(res["disease_forms_searched"]) > 1:
        print(f"\ndisease forms searched: {', '.join(res['disease_forms_searched'])}")
    fg = res["false_gaps_repaired_by_names"]
    if fg:
        print(f"\nrows a symbol-only query would have called unjoined, but which are joined under a "
              f"name the literature uses ({len(fg)}): {', '.join(fg)}")
    if out:
        print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
