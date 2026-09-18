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

Usage:
    python3 scripts/disease_screen.py ENDOMETRIOSIS targets.json --out research/endo-screen.json
    python3 scripts/disease_screen.py --density "vulvodynia" "interstitial cystitis"
    python3 scripts/disease_screen.py "pudendal neuralgia|pudendal nerve entrapment" targets.json
    python3 scripts/disease_screen.py "pudendal neuralgia|pudendal neuropathy" targets.json \\
        --control "morton's neuroma|interdigital neuroma" --out research/pudendal-screen.json
    python3 scripts/disease_screen.py --selftest

A disease argument may name several spellings separated by `|` (or be a list, when called as a
function). Screen the union: a single spelling can return a false zero, and a false zero here
becomes a discovery claim.

`--control` screens the *same* target list against a second condition deliberately chosen to have
a corpus of the same size, and reports which targets are unjoined for one but not the other. On a
thin condition the unjoined list is mostly a fact about the size of the literature, not about
nobody having had the idea — see `compare_to_control` and `research/pudendal-neuralgia.md`.
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


def disease_names(disease) -> list:
    """The names a condition is queried under, because the counts move with spelling.

    `SLC19A3 × ME/CFS` returned 0 documents under one spelling and 1 under the union of three
    (recorded 2026-09-18): a single-name query can produce a **false zero**, which in this
    program is fatal in the expensive direction — it invents an unjoined node that is not one.
    Pass a list, or a `|`-separated string, to screen the union of the spellings a condition is
    actually published under. See `research/pudendal-neuralgia.md` for the worked case.
    """
    if isinstance(disease, (list, tuple)):
        return [str(d).strip() for d in disease if str(d).strip()]
    return [p.strip() for p in str(disease).split("|") if p.strip()]


def _name_group(disease) -> str:
    """Europe PMC OR-group of the condition's spellings, for interpolation into a query.

    A single name is returned bare, so the query for a one-spelling condition is unchanged.
    """
    names = disease_names(disease)
    if len(names) == 1:
        return f'"{names[0]}"'
    return "(" + " OR ".join(f'"{n}"' for n in names) + ")"


def any_field(symbol: str, disease) -> int:
    return epmc(f'"{symbol}" AND {_name_group(disease)}')


def strict(symbol: str, disease) -> int:
    grp = _name_group(disease)
    return epmc(f'(TITLE:"{symbol}" OR ABSTRACT:"{symbol}") AND '
                f'(TITLE:{grp} OR ABSTRACT:{grp})')


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


def compare_to_control(disease_rows: list, control_rows: list) -> dict:
    """Which targets are unjoined *for this condition specifically*, not for its corpus size.

    A target list screened against a thin condition comes back with hundreds of "unjoined" nodes,
    and every one of them looks like a candidate. Most are not: the same list screened against a
    **control condition of the same corpus size** is just as empty. Pudendal neuralgia (430 strict
    papers) and Morton's neuroma (391) are such a pair — two mechanically comparable entrapment
    neuropathies, found 2026-09-18 to return almost the same unjoined list from the same 330
    targets. The bands below separate "nobody studies this gene in this disease" from "nobody
    studies this disease at all":

      unjoined_in_both                          no information about either condition
      joined_in_control_only                    studied for the neighbour, absent here
      mentioned_in_disease_studied_in_control   the strongest shape: talked about here, a
                                                mechanism over there, no study joining them
      joined_in_both / joined_in_disease_only   prior work — cite it

    A control is chosen for *size*, not for biology: matching on mechanism as well makes the
    comparison stronger but is not required for the correction, which is only about how many
    nodes an empty corpus produces by itself.
    """
    a = {r["symbol"]: r for r in disease_rows}
    b = {r["symbol"]: r for r in control_rows}
    shared = lambda pred: [r["symbol"] for sym, r in a.items()
                           if sym in b and pred(r, b[sym])]
    return {
        "unjoined_in_both": shared(
            lambda r, c: r["strict"] == 0 and r["any_field"] == 0
            and c["strict"] == 0 and c["any_field"] == 0),
        "joined_in_control_only": shared(lambda r, c: r["strict"] == 0 and c["strict"] > 0),
        "mentioned_in_disease_studied_in_control": shared(
            lambda r, c: r["strict"] == 0 and r["any_field"] > 0 and c["strict"] > 0),
        "joined_in_disease_only": shared(lambda r, c: r["strict"] > 0 and c["strict"] == 0),
        "joined_in_both": shared(lambda r, c: r["strict"] > 0 and c["strict"] > 0),
    }


def unjoined_fraction(rows: list) -> float:
    """Share of targets with no document containing both terms — the number a size-matched
    control is there to deflate. Not a score: a big value on a small corpus is arithmetic."""
    if not rows:
        return 0.0
    return round(sum(1 for r in rows if r["strict"] == 0 and r["any_field"] == 0) / len(rows), 3)


def run(disease: str, targets: list, use_ot: bool = True, control: str = None) -> dict:
    t0 = time.time()
    grp = _name_group(disease)
    dis_any = epmc(grp)
    dis_strict = epmc(f'(TITLE:{grp} OR ABSTRACT:{grp})')
    n_trials = trials(disease_names(disease)[0])
    efo, efo_name = ot_disease(disease_names(disease)[0]) if use_ot else (None, None)

    def one(t):
        sym = t["symbol"]
        a = any_field(sym, disease)
        s = strict(sym, disease)
        score = ot_score(sym, efo) if use_ot else None
        return {
            "category": t.get("category", ""),
            "symbol": sym,
            "any_field": a,
            "strict": s,
            "open_targets_score": score,
            "verdict": verdict(a, s),
        }

    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(one, targets))

    control_block = None
    if control:
        c = run(control, targets, use_ot=use_ot)
        control_block = {
            "disease": control,
            "disease_papers_any_field": c["disease_papers_any_field"],
            "disease_papers_strict": c["disease_papers_strict"],
            "registered_trials_for_disease": c["registered_trials_for_disease"],
            "unjoined": c["unjoined"],
            "unjoined_fraction": unjoined_fraction(c["targets"]),
            "compare": compare_to_control(rows, c["targets"]),
        }

    return {
        "disease": disease if isinstance(disease, str) else " | ".join(disease_names(disease)),
        "disease_names": disease_names(disease),
        "disease_resolved": efo_name,
        "efo_id": efo,
        "disease_papers_any_field": dis_any,
        "disease_papers_strict": dis_strict,
        "registered_trials_for_disease": n_trials,
        "note": ("any_field = Europe PMC hitCount for \"SYMBOL\" AND (\"disease\") — counts "
                 "mentions, not studies. strict = SYMBOL and disease both in a TITLE or ABSTRACT "
                 "— the number that decides novelty. Counts move with spelling; these are small "
                 "numbers, not exact ones. A zero means nobody has PUBLISHED the link; it does "
                 "not mean the link is true, untested, or valuable."),
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
        "unjoined_fraction": unjoined_fraction(rows),
        "control": control_block,
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
    control = None
    if "--control" in args:
        i = args.index("--control")
        control = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__)
        return 1
    disease, targets_path = args
    with open(targets_path) as fh:
        targets = json.load(fh)
    res = run(disease, targets, use_ot=use_ot, control=control)
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
    d_frac = res["unjoined_fraction"]
    print(f"\nunjoined share of this {res['n_targets']}-target list: {d_frac:.0%}")
    if res.get("control"):
        c = res["control"]
        cmpf = c["compare"]
        c_frac = c["unjoined_fraction"]
        print(f"  against the size-matched control '{c['disease']}' "
              f"(strict={c['disease_papers_strict']}, trials="
              f"{c['registered_trials_for_disease']}): {c_frac:.0%} unjoined "
              f"— a share of these targets is empty for any condition of this size.")
        if d_frac > c_frac:
            print(f"  excess over the control: {d_frac - c_frac:+.0%}. Only the excess is "
                  f"about {res['disease'].split('|')[0].strip()}.")
        for band in ("unjoined_in_both", "joined_in_control_only",
                     "mentioned_in_disease_studied_in_control", "joined_in_disease_only",
                     "joined_in_both"):
            print(f"  {band}: {', '.join(cmpf[band]) or '(none)'}")
    if out:
        print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
