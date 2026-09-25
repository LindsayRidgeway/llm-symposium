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

**3. A null control (`"control": true`).** A row marked `"control": true` is a string that names
nothing — it exists to be scored, and it is excluded from every count and band. If nonsense strings
come back "unjoined" at the same rate as the real targets, the unjoined band is measuring the
condition's literature density and not the absence of a link, and the screen says so in
`control_check`. The list a run screens should always carry two or three. (Suggested by the
2026-09-20 09:32 run, which put three nonsense strings in a 222-target list and left them
unexplained; the check is here so the next reader does not have to notice them.)

A target list is data, not code: pass a JSON file of `[{"category": "...", "symbol": "..."}, ...]`.
Choosing the targets is a judgement and stays with whoever runs the screen; the screen only
measures how much literature already joins each one. This is the "candidate-generation so the
queue feeds itself" half of agenda item 7, made mechanical.

Two defects, found by two clock runs on 2026-09-19, one more found on 2026-09-23, and what the
screen now does about each:

**1. Names, not just symbols (`names`), and disease forms (`--forms`).** A symbol-only query
against a thin disease returned 39 of 41 targets as "no title/abstract join", which is a
*false-gap generator*, not a finding: the literature writes "nerve growth factor", not "NGF". A
target entry may carry `"names": ["nerve growth factor", ...]`, `--forms` may add disease
spellings, and the screen reports the *maximum* join over (symbol|names) × (disease|forms), the
pair that produced it, and a `naming_sensitive` flag on any row whose number came from something
other than the plain symbol.

**2. A join must carry the document that produced it (`strict_hits`).** The screen invents
*presences* as well as absences: against pudendal neuralgia the only two "already published
together" hits were the symbol `AR` in a paper about **augmented reality** (PMID 38560457) and
`KIT` in a paper whose abstract says **"kit"** — a mesh kit, not the receptor. Both are real
token matches and both are wrong, so a token-boundary guard does not fix this and the count
alone cannot: *no count can tell "a paper about the pair" from a coincidence of English.* So
every strict join now fetches its top documents (title, PMID, year) into the artefact, and any
symbol of three characters or fewer is flagged `ambiguous_symbol` — the reader is told to open
the hit before a "prior work" verdict is allowed to close a lead.

**3. A failed count (-1) is not a row, and it is not a zero.** Europe PMC drops a request now and
then; the failure is recorded as -1 so it can never be read as a real 0. Until 2026-09-23 the -1
was handled at the *verdict* and then forgotten at the *summary*: such a row vanished from every
band, so the unjoined band shrank and `control_check` divided by rows it had never scored. Both
are the optimistic direction — a saturated condition reads as separable. Measured on
`research/vulvodynia-screen.json` as it then stood: 44 of 128 rows carried a failed count (23 with
no strict join but an unknown any-field, 21 with a failed strict query), the null-control rate was
17/128 = 13% where the same screen's prose recorded 45/128 = 35% from a clean run, and **3 rows
(`P2RY12`, `MGLL`, `SORT1`) printed "unjoined — a candidate, NOT a finding" on a strict query that
had failed outright** — a failed search dressed as a promising lead, the one error this program
exists to avoid. So: a row is *scored* only if both counts are real; unscored rows are kept out of
every band and named in `failed_queries`; the control check divides by what it actually scored; and
`verdict(0, -1)` now says QUERY FAILED instead of offering a candidate.

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

# Below this many title/abstract papers naming the condition, the "unjoined" band saturates:
# almost every target looks unjoined for the trivial reason that few documents mention the
# condition at all. Measured on 2026-09-19 — the same 128 targets against five conditions gave
# 95 unjoined at 221 strict papers (pudendal neuralgia) and 0 unjoined at 16,558 (fibromyalgia).
# A thin corpus is *worse* ground for this screen, not better, and the queue's premise is fixed.
FLOOR_STRICT = 1000

# Symbols this short are matched as ordinary words and other people's acronyms: `AR` in
# "AR guidance" (augmented reality), `KIT` in "mesh kit". The match is real; the meaning is not
# the gene. Nothing here is proof of anything — it is a warning to read before concluding.
AMBIGUOUS_MAX_LEN = 3

_epmc_cache: dict = {}
_ot_cache: dict = {}


def _get(url: str, timeout: int = 30, tries: int = 4) -> bytes:
    """Fetch with a short retry.

    Europe PMC intermittently answers a burst of queries with a body carrying no hitCount, or
    drops the connection. Without a retry that becomes a failure — and before 2026-09-23 it
    became a silent ZERO, i.e. a failed search dressed as a promising lead, the one error this
    program cannot afford. Retry so a transient miss is a retry, not a result.
    """
    last: Exception | None = None
    for i in range(tries):
        try:
            time.sleep(0.35)  # space requests out; Europe PMC fails a parallel burst
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=timeout).read()
        except Exception as e:  # noqa: BLE001 — every transport error here is retryable
            last = e
            if i < tries - 1:
                time.sleep(1.0 * (i + 1))
    assert last is not None
    raise last


def epmc(term: str) -> int:
    """Europe PMC hitCount, cached. -1 means the query failed (kept distinct from a real 0)."""
    if term in _epmc_cache:
        return _epmc_cache[term]
    u = EPMC + "?format=json&pageSize=1&query=" + urllib.parse.quote(term)
    try:
        body = json.loads(_get(u))
        # A response that parses but carries no hitCount is a FAILURE, not a zero. Reading it as
        # 0 hands the screen a false "unjoined" — a failed search dressed as a promising lead,
        # which is the one error this program cannot afford (it kills the only output). Found
        # 2026-09-23: a transient empty response recorded vulvodynia's own any-field count as 0
        # against 1045 strict papers.
        if "hitCount" not in body:
            n = -1
        else:
            n = int(body["hitCount"])
    except Exception:
        n = -1
    _epmc_cache[term] = n
    return n


def epmc_hits(term: str, size: int = 3) -> list:
    """The actual documents behind a count, so a join can be read instead of believed.

    A hitCount cannot distinguish a paper about a pair from a coincidence of English (see the
    module docstring: `AR` = augmented reality). These are the top `size` documents for the
    query, title and ID only, for a human or a later run to open. Empty on failure, never None.
    """
    u = (EPMC + "?format=json&pageSize=%d&resultType=core&query=" % size
         + urllib.parse.quote(term))
    try:
        res = json.loads(_get(u)).get("resultList", {}).get("result", []) or []
    except Exception:
        return []
    out = []
    for r in res:
        out.append({
            "pmid": r.get("pmid") or r.get("id") or "",
            "title": (r.get("title") or "").strip(),
            "year": str(r.get("pubYear") or ""),
        })
    return out


def any_query(symbol: str, disease: str) -> str:
    return f'"{symbol}" AND ("{disease}")'


def strict_query(symbol: str, disease: str) -> str:
    return (f'(TITLE:"{symbol}" OR ABSTRACT:"{symbol}") AND '
            f'(TITLE:"{disease}" OR ABSTRACT:"{disease}")')


def any_field(symbol: str, disease: str) -> int:
    return epmc(any_query(symbol, disease))


def strict(symbol: str, disease: str) -> int:
    return epmc(strict_query(symbol, disease))


def trials(condition: str) -> int:
    u = ("https://clinicaltrials.gov/api/v2/studies?pageSize=1&countTotal=true&query.cond="
         + urllib.parse.quote(condition))
    try:
        body = json.loads(_get(u))
        # Same rule as epmc(): a missing count is a failure (-1), never a real zero.
        return int(body["totalCount"]) if "totalCount" in body else -1
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


def ambiguous(symbol: str) -> bool:
    """Short symbols collide with ordinary words and other fields' acronyms. Not a verdict."""
    return len(symbol.strip()) <= AMBIGUOUS_MAX_LEN


def scored(r: dict) -> bool:
    """True only if BOTH counts are real. A -1 is a failed search, not a zero.

    A row with one -1 was silently dropped from every band before 2026-09-23, which shrank the
    unjoined band and let `control_check` divide by rows it had never scored — the optimistic
    error, on the band the program's whole output rests on. Such rows are excluded and named.
    """
    return r["strict"] >= 0 and r["any_field"] >= 0


def failed_scopes(r: dict) -> list:
    """Which of the row's two counts came back -1, for `failed_queries`."""
    return [k for k in ("strict", "any_field") if r[k] < 0]


def verdict(any_n: int, strict_n: int, ambiguous_symbol: bool = False) -> str:
    # Either count failing makes the pair unreadable. `any_n == 0, strict_n == -1` used to fall
    # through to "unjoined — a candidate, NOT a finding": a failed strict query printed as a
    # promising lead. Found 2026-09-23 on P2RY12, MGLL and SORT1 in the vulvodynia screen.
    if any_n < 0 or strict_n < 0:
        return "QUERY FAILED — re-run this pair; do not read the number"
    if strict_n > 0:
        if ambiguous_symbol:
            return ("already published together (title/abstract) — DO NOT CLOSE YET: the symbol "
                    "is short and may be an ordinary word or another field's acronym; open "
                    "strict_hits and confirm the gene")
        return "already published together (title/abstract) — prior work, cite it"
    if any_n == 0:
        return "unjoined — no document contains both; a candidate, NOT a finding"
    if any_n <= INCIDENTAL_MAX:
        return f"incidental only ({any_n}) — read them before claiming novelty"
    return f"discussed ({any_n} any-field, 0 strict) — read the list; not novel on this number"


def is_control(t: dict) -> bool:
    """A target that is a string naming nothing, scored to prove the screen is measuring.

    Marked explicitly (`"control": true`) rather than by category, because the self-test below
    uses category labels like "control/joined" for a different purpose.
    """
    return t.get("control") is True


def control_check(control_rows: list, rows: list) -> str | None:
    """What the null controls scored, next to what the real targets scored.

    A zero from a screen is only informative if a string that cannot exist also scores zero for
    a different reason. When both come back unjoined at the same rate, the band is a property of
    the corpus, and this line is the instrument saying so in its own artefact.
    """
    if not control_rows:
        return None
    # Only scorable rows. A control whose query failed is not a control that scored something:
    # reading its -1 as "scored other than unjoined" raised the alarm against the instrument
    # instead of against the run, and inflating the denominator did the same for the real rows.
    ctrl_ok = [r for r in control_rows if scored(r)]
    n_failed = len(control_rows) - len(ctrl_ok)
    tail = ("" if not n_failed else
            f" ({n_failed} control quer{'y' if n_failed == 1 else 'ies'} failed with no count; "
            f"it is not evidence either way — re-run it.)")
    if not ctrl_ok:
        return (f"none of the {len(control_rows)} strings that name nothing could be scored "
                f"(their queries failed), so this run has no null and no band to compare against. "
                f"Re-run before reading any count here.")
    n = len(ctrl_ok)
    ctrl_zero = sum(1 for r in ctrl_ok if r["strict"] == 0 and r["any_field"] == 0)
    if ctrl_zero < n:
        bad = ", ".join(r["symbol"] for r in ctrl_ok
                        if not (r["strict"] == 0 and r["any_field"] == 0))
        return (f"{n - ctrl_zero} of {n} strings that name nothing scored something other than "
                f"'unjoined' ({bad}) — the matching is not behaving as a plain string search. "
                f"Treat every number in this screen as suspect until that is explained.{tail}")
    rows_ok = [r for r in rows if scored(r)]
    unscored = len(rows) - len(rows_ok)
    # The fraction is over what was scored, and it says how much was not: a rate computed over
    # rows whose queries failed is the optimistic direction of error this line exists to prevent.
    us = ("" if not unscored else
          f" ({unscored} of {len(rows)} real targets could not be scored and are NOT in that "
          f"fraction; see `failed_queries`.)")
    if not rows_ok:
        return (f"{ctrl_zero} of {n} nonsense strings scored 'unjoined', and no real target "
                f"could be scored at all.{us}{tail}")
    real_zero = sum(1 for r in rows_ok if r["strict"] == 0 and r["any_field"] == 0)
    rate = 100.0 * real_zero / len(rows_ok)
    if real_zero == 0:
        return (f"{ctrl_zero} of {n} strings that name nothing scored 'unjoined', and no scorable "
                f"real target did — here the band separates a gene from a string that names "
                f"nothing.{us}{tail}")
    if rate >= 25.0:
        return (f"{ctrl_zero} of {n} strings that name nothing scored 'unjoined', and so did "
                f"{real_zero} of {len(rows_ok)} scorable real targets ({rate:.0f}%). A string "
                f"that names nothing scores exactly like a gene, so at this density the unjoined "
                f"band measures the condition's literature, not the absence of a link.{us}{tail}")
    return (f"{ctrl_zero} of {n} strings that name nothing scored 'unjoined', and so did "
            f"{real_zero} of {len(rows_ok)} scorable real targets ({rate:.0f}%). The two are "
            f"separable at this density, but the band is not free of noise either — read every "
            f"row before treating a zero as a gap.{us}{tail}")


def floor_warning(strict_papers: int) -> str | None:
    """Say when the corpus is too thin for the screen's zero to mean anything."""
    if 0 <= strict_papers < FLOOR_STRICT:
        return (f"only {strict_papers} title/abstract papers name this condition, below the "
                f"{FLOOR_STRICT} floor. At this density the unjoined band saturates: most targets "
                f"look unjoined for the trivial reason that few documents mention the condition at "
                f"all. A zero here is a property of the corpus, not evidence of an undiscovered "
                f"link — work this condition by reading the whole corpus, or screen a "
                f"well-populated sibling and check whether the link reaches this one.")
    return None


def run(disease: str, targets: list, use_ot: bool = True, forms: list = None) -> dict:
    t0 = time.time()
    forms = [disease] + [f for f in (forms or []) if f and f != disease]
    is_ctl = [is_control(t) for t in targets]
    controls = [t for t, c in zip(targets, is_ctl) if c]
    real = [t for t, c in zip(targets, is_ctl) if not c]
    dis_any = max(epmc(f'"{f}"') for f in forms)
    dis_strict = max(epmc(f'(TITLE:"{f}" OR ABSTRACT:"{f}")') for f in forms)
    n_trials = trials(disease)
    efo, efo_name = ot_disease(disease) if use_ot else (None, None)

    def one(t):
        sym = t["symbol"]
        # A target is a symbol AND the names a paper would actually use for it.
        names = [sym] + [n for n in t.get("names", []) if n]
        best = None  # (both counts real, strict, any_field, name, disease form)
        for name in names:
            for form in forms:
                s, a = strict(name, form), any_field(name, form)
                # A candidate whose counts BOTH came back is preferred over one that failed:
                # ranking on (strict, any_field) alone let a failed any-field (-1) ride on a
                # higher strict count and overwrite a real number with a -1.
                cand = (s >= 0 and a >= 0, s, a, name, form)
                if best is None or cand[:3] > best[:3]:
                    best = cand
        _, s, a, name, form = best
        # What the plain symbol-only query would have reported, kept so a reader can see the
        # difference a name makes rather than trusting the maximum on its own.
        sym_s, sym_a = strict(sym, disease), any_field(sym, disease)
        ambiguous_symbol = ambiguous(sym)
        score = ot_score(sym, efo) if use_ot else None
        ctl = is_control(t)
        fs = [k for k, v in (("strict", s), ("any_field", a)) if v < 0]
        return {
            "category": t.get("category", ""),
            "symbol": sym,
            "is_control": is_control(t),
            "any_field": a,
            "strict": s,
            "symbol_only_strict": sym_s,
            "symbol_only_any_field": sym_a,
            "matched_name": name,
            "matched_disease_form": form,
            # Which of this row's two counts failed (-1). A scored row has an empty list.
            "failed_scopes": fs,
            "naming_sensitive": (name != sym or form != disease),
            "ambiguous_symbol": ambiguous_symbol,
            # A join is only evidence if you can open it. Empty unless strict > 0.
            "strict_hits": epmc_hits(strict_query(name, form)) if s > 0 else [],
            "open_targets_score": score,
            "verdict": ("null control — a string that names nothing; it is here to be scored and "
                        "is excluded from every count" if ctl
                        else verdict(a, s, ambiguous_symbol)),
        }

    # 8 parallel workers trips Europe PMC's rate limit on a burst (observed 2026-09-23: 54 of
    # 128 rows came back as failures). 3 keeps the run inside the limit; a missed request is
    # retried in _get() rather than being read as a zero.
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        rows = list(ex.map(one, targets))

    # The bands are claims about biology, so a string that names nothing stays out of them and
    # is reported on its own. It has already done its work by being scored at the same time.
    ctrl_rows = [r for r in rows if r["is_control"]]
    real_rows = [r for r in rows if not r["is_control"]]
    # Bands are claims about the biology, so only rows with BOTH counts real may enter them.
    # An unscored row (a -1) is a failed search, not a zero: letting one drop silently out of
    # the bands is how the unjoined band shrinks and a saturated condition reads as separable.
    scored_rows = [r for r in real_rows if scored(r)]
    failed_rows = [r for r in real_rows if not scored(r)]
    false_gaps = [r["symbol"] for r in scored_rows
                  if r["naming_sensitive"] and r["symbol_only_strict"] == 0 and r["strict"] > 0]
    return {
        "disease": disease,
        "disease_resolved": efo_name,
        "efo_id": efo,
        "disease_papers_any_field": dis_any,
        "disease_papers_strict": dis_strict,
        "registered_trials_for_disease": n_trials,
        "disease_forms_searched": forms,
        "note": ("any_field = Europe PMC hitCount for \"SYMBOL\" AND (\"disease\") — counts "
                 "mentions, not studies. strict = SYMBOL and disease both in a TITLE or ABSTRACT "
                 "— the number that decides novelty. Counts move with spelling; these are small "
                 "numbers, not exact ones. A zero means nobody has PUBLISHED the link; it does "
                 "not mean the link is true, untested, or valuable. Where a target carries "
                 "`names`, any_field/strict are the maximum over the symbol and every name, so a "
                 "row is only 'unjoined' if it is unjoined under every spelling supplied. Every "
                 "strict join carries its `strict_hits` — open them; the count cannot tell a "
                 "paper about the pair from a coincidence of English. A row marked "
                 "`\"control\": true` is a string that names nothing: it is scored, kept out of "
                 "every count and band, and reported in `controls` with a `control_check` line, "
                 "so the reader can see whether the unjoined band separates a gene from noise. "
                 "`strict` or `any_field` of -1 means that query FAILED: the row is not a zero, "
                 "is excluded from every band, and is listed in `failed_queries`; compare "
                 "`n_scored` with `n_targets` before calling a band complete."),
        "n_targets": len(real_rows),
        "n_controls": len(ctrl_rows),
        # How much of the list this screen actually measured, said plainly. Before 2026-09-23
        # the artefact printed `n_targets` alone, so a run with 44 failed rows read as a
        # complete screen of 128.
        "n_scored": len(scored_rows),
        "n_failed": len(failed_rows),
        "failed_queries": [{"symbol": r["symbol"], "failed_scopes": r["failed_scopes"],
                            "any_field": r["any_field"], "strict": r["strict"]}
                           for r in failed_rows],
        "failed_queries_note": (None if not failed_rows else
                                f"{len(failed_rows)} of {len(real_rows)} real targets carry a "
                                f"failed count (-1, listed in `failed_queries` with the scope "
                                f"that failed) and are excluded from every band below: a failed "
                                f"search is not a zero, and it is not an absence of a link. "
                                f"Re-run those rows before quoting the bands as complete."),
        # Every band where strict == 0 is candidate territory, and the three bands are
        # different claims. The summary used to print only the first two, which hid the one
        # that matters most on a dense disease — nodes co-mentioned but never studied.
        "unjoined": [r["symbol"] for r in scored_rows
                     if r["strict"] == 0 and r["any_field"] == 0],
        "incidental_any_field_only": [r["symbol"] for r in scored_rows
                                      if r["strict"] == 0 and 0 < r["any_field"] <= INCIDENTAL_MAX],
        "no_title_abstract_join": [r["symbol"] for r in scored_rows if r["strict"] == 0],
        "no_strict_join_but_discussed": [r["symbol"] for r in scored_rows
                                         if r["strict"] == 0 and r["any_field"] > INCIDENTAL_MAX],
        "joined_in_title_or_abstract": [r["symbol"] for r in scored_rows if r["strict"] > 0],
        # The rows a symbol-only screen would have called unjoined but which are joined under a
        # name the literature actually uses. This is the false-gap count, and it belongs in the
        # artefact: the whole defect is that a false gap is indistinguishable from a real one.
        "false_gaps_repaired_by_names": false_gaps,
        # The rows a short symbol would have closed as "prior work" without anyone reading them.
        "ambiguous_joins_to_read": [r["symbol"] for r in scored_rows
                                    if r["strict"] > 0 and r["ambiguous_symbol"]],
        "density_floor": FLOOR_STRICT,
        "density_warning": floor_warning(dis_strict),
        # The null controls, and what they scored next to the real targets.
        "control_check": control_check(ctrl_rows, real_rows),
        "controls": [{"symbol": r["symbol"], "any_field": r["any_field"], "strict": r["strict"],
                      "verdict": r["verdict"]} for r in ctrl_rows],
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

    Since 2026-09-19 each row also carries a `band`: a condition below FLOOR_STRICT is not
    "better ground" for this screen, it is ground the screen cannot measure, and a zero there
    is an artefact of the corpus rather than a discovery. Thin and dense are both disqualifying.
    """
    rows = []
    for c in conditions:
        strict_n = epmc(f'(TITLE:"{c}" OR ABSTRACT:"{c}")')
        any_n = epmc(f'"{c}"')
        rows.append({
            "condition": c,
            "any_field": any_n,
            "strict": strict_n,
            "trials": trials(c),
            "band": ("query failed — no count; re-run before reading this condition"
                     if (strict_n < 0 or any_n < 0) else
                     "below floor — the unjoined band saturates; work by reading, not by screen"
                     if strict_n < FLOOR_STRICT else "screenable"),
        })
    rows.sort(key=lambda r: r["strict"])
    return rows


def selftest() -> int:
    """Two known pairs inside the screen: one joined, one not. A screen that cannot separate
    them is not measuring novelty. A third row is a string that names nothing: it must score
    zero like an unjoined gene, must stay out of the counts, and the control line must say so.
    """
    dis = "chronic fatigue syndrome"
    a = {"symbol": "PDHA1", "category": "control/joined"}
    b = {"symbol": "SLC19A3", "category": "control/unjoined"}
    z = {"symbol": "XQZWKJ", "category": "null control", "control": True}
    res = run(dis, [a, b, z], use_ot=False)
    ra, rb = res["targets"][0], res["targets"][1]
    print("Self-test: one pair the literature discusses, one it does not, one string that "
          "names nothing.\n")
    for label, r in (("PDHA1 (expected: discussed)", ra),
                     ("SLC19A3 (expected: unjoined/incidental)", rb),
                     ("XQZWKJ (null control, excluded)", res["targets"][2])):
        print("  %-40s any_field=%-5s strict=%-4s  %s" % (
            label, r["any_field"], r["strict"], r["verdict"]))
    print("\n  control check: %s" % res["control_check"])
    ok = ra["any_field"] > rb["any_field"]
    ok = ok and res["n_targets"] == 2 and res["n_controls"] == 1
    ok = ok and "names nothing" in (res["control_check"] or "")
    ok = ok and res["targets"][2]["verdict"].startswith("null control")
    ok = ok and "XQZWKJ" not in res["no_title_abstract_join"]
    ok = ok and "XQZWKJ" not in res["unjoined"]
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
    forms = None
    if "--forms" in args:
        i = args.index("--forms")
        forms = [x.strip() for x in args[i + 1].split(",") if x.strip()]
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
        print("%-44s %-9s %-9s %-7s %s" % ("condition", "any_field", "strict", "trials", "band"))
        for r in rows:
            print("%-44s %-9s %-9s %-7s %s" % (r["condition"], r["any_field"], r["strict"],
                                               r["trials"], r["band"]))
        print("\nstrict = papers naming the condition in a title or abstract. A large number "
              "means the ground is worked; a number below the floor means the ground is too "
              "thin for this screen's zero to carry information. Both disqualify.")
        return 0
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
    print(f"{disease}: {res['n_scored']} of {res['n_targets']} targets scored in "
          f"{res['seconds']}s; "
          f"disease papers any_field={res['disease_papers_any_field']}, "
          f"strict={res['disease_papers_strict']}, trials={res['registered_trials_for_disease']}\n")
    if res["n_failed"]:
        print(f"{res['n_failed']} real targets carry a FAILED count (-1) and are excluded from "
              f"every band: {', '.join(r['symbol'] for r in res['failed_queries'])}\n")
    print("%-10s %-8s %-8s %s" % ("symbol", "any", "strict", "verdict"))
    for r in sorted(res["targets"], key=lambda r: (r["strict"], r["any_field"])):
        print("%-10s %-8s %-8s %s" % (r["symbol"] + ("*" if r.get("is_control") else ""),
                                      r["any_field"], r["strict"], r["verdict"]))
    if res.get("controls"):
        print("\n* = null control (a string that names nothing; excluded from every count)")
    if res.get("control_check"):
        print(f"control check: {res['control_check']}")
    if res["density_warning"]:
        print(f"\ndensity warning: {res['density_warning']}")
    if res["disease_forms_searched"] and len(res["disease_forms_searched"]) > 1:
        print(f"\ndisease forms searched: {', '.join(res['disease_forms_searched'])}")
    fg = res["false_gaps_repaired_by_names"]
    if fg:
        print(f"\nrows a symbol-only query would have called unjoined, but which are joined under a "
              f"name the literature uses ({len(fg)}): {', '.join(fg)}")
    for sym in res["ambiguous_joins_to_read"]:
        hits = next(r["strict_hits"] for r in res["targets"] if r["symbol"] == sym)
        print(f"\n'{sym}' is short enough to be an ordinary word or another field's acronym. "
              f"Open these before closing the lead:")
        for h in hits:
            print(f"  PMID {h['pmid']} ({h['year']}): {h['title']}")
    print(f"\nno title/abstract join (all bands), over {res['n_scored']} scored rows: "
          f"{', '.join(res['no_title_abstract_join']) or '(none)'}")
    print(f"  of those, fully unjoined (0/0): {', '.join(res['unjoined']) or '(none)'}")
    print(f"  of those, incidental only (1-5): {', '.join(res['incidental_any_field_only']) or '(none)'}")
    print(f"  of those, co-mentioned but never studied: "
          f"{', '.join(res['no_strict_join_but_discussed']) or '(none)'}")
    if out:
        print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
