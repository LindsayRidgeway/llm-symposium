#!/usr/bin/env python3
"""Re-measure the source catalogue and report *what changed*, not what is true today.

Why this file exists (agenda item 17, rule 1). Item 17's finding is that source access is
not a property of a source but a relation between a source and a reader, and that the
failure it cares about is the *silent* one: a page that answered last month and 403s this
month, discovered only when a script quietly falls back on memory. `docs/works/fetchable-
sources.json` is a measurement, taken once (2026-09-16) — a snapshot. A snapshot cannot
detect drift, because nothing compares it to anything. This script is the comparison.

It reuses the catalogue and the probe from `measure_sources.py` on purpose: two lists
would drift from each other, which is the failure it is trying to catch.

What it prints, per source: the reachability state *relative to the recorded baseline* —
newly-blocked, cors-lost, newly-readable, still-blocked, unchanged — plus how many of the
commons' own scripts call that host, because a source that breaks and is used by six
scripts is not the same event as one nothing uses.

Exit code: 0 normally; 1 if a source **used by at least one script** regressed (became
blocked, or lost browser-readable CORS). `--strict` treats any regression as failure.
This is a maintenance probe and is deliberately NOT wired into the offline test gate —
it makes live network requests. The classification it uses is pinned offline by
`tests/test_source_reachability_drift.py`.

Usage:
    python3 scripts/source_reachability_drift.py                 # compare, print, exit 0/1
    python3 scripts/source_reachability_drift.py --write         # also write research/source-reachability-drift-<date>.json
    python3 scripts/source_reachability_drift.py --baseline X.json
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import measure_sources  # noqa: E402  (same directory, on purpose: one catalogue)

DEFAULT_BASELINE = os.path.join(REPO, "docs", "works", "fetchable-sources.json")

# Files that *are* the catalogue or its guards: counting them as "a script that uses the
# source" would make every source look used, which is the opposite of the point.
USAGE_EXCLUDE = {
    "measure_sources.py",
    "source_reachability_drift.py",
    "validate_fetchable_page.mjs",
}

REGRESSIONS = ("newly-blocked", "cors-lost")


def host_of(url: str) -> str:
    return url.split("//", 1)[-1].split("/", 1)[0]


def usage_counts(repo: str = REPO) -> dict:
    """How many of the commons' own source files name each host.

    A crude proxy, and said to be crude: it counts textual references in `scripts/` and
    `.github/scripts/`, so a commented-out URL counts too. Under-counting is the safe
    direction — this only decides whether a regression is *operationally* interesting.
    """
    counts: dict = {}
    for sub in ("scripts", os.path.join(".github", "scripts")):
        d = os.path.join(repo, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn in USAGE_EXCLUDE or not fn.endswith((".py", ".mjs", ".sh")):
                continue
            try:
                with open(os.path.join(d, fn), encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            for _name, _field, _holds, url, _key in measure_sources.SOURCES:
                h = host_of(url)
                if h in text:
                    counts[h] = counts.get(h, 0) + 1
    return counts


def diff_rows(baseline: dict, current: dict) -> list:
    """Classify each source's reachability *relative to the baseline*. Pure, no I/O.

    `baseline` and `current` are `{name: row}` maps of the measure_sources row shape
    (`http_status`, `cors`, `ok`, `browser_usable`). The returned rows are
    `{name, state, used_by, was, now, note}` sorted worst-first.
    """
    order = {"newly-blocked": 0, "cors-lost": 1, "still-blocked": 2, "removed": 3,
             "passes-a-key-wall": 4, "new": 5, "newly-readable": 6, "cors-gained": 7,
             "unchanged": 8}
    rows = []
    for name in sorted(set(baseline) | set(current)):
        b, c = baseline.get(name), current.get(name)
        if b is None:
            state = "new"
            was = "—"
        elif c is None:
            state = "removed"
            was = "recorded"
        else:
            was = "%s cors=%s" % (b.get("http_status"), b.get("cors"))
            bok, cok = bool(b.get("ok")), bool(c.get("ok"))
            bbrowser, cbrowser = bool(b.get("browser_usable")), bool(c.get("browser_usable"))
            if bok and not cok:
                state = "newly-blocked"
            elif not bok and cok:
                state = "newly-readable"
            elif bok and cok and bbrowser and not cbrowser:
                state = "cors-lost"
            elif bok and cok and not bbrowser and cbrowser:
                state = "cors-gained"
            elif not bok and not cok:
                state = "still-blocked"
            else:
                state = "unchanged"
        now = ("—" if c is None else "%s cors=%s%s" % (
            c.get("http_status"), c.get("cors"),
            (" " + c["error"]) if c.get("error") else ""))
        rows.append({"name": name, "state": state, "was": was, "now": now})
    rows.sort(key=lambda r: (order.get(r["state"], 9), r["name"]))
    return rows


def rows_to_map(rows: list) -> dict:
    return {r["name"]: r for r in rows}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--baseline", default=DEFAULT_BASELINE)
    ap.add_argument("--write", action="store_true",
                    help="write research/source-reachability-drift-<date>.json")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on any regression, not only on ones a script depends on")
    args = ap.parse_args()

    with open(args.baseline, encoding="utf-8") as f:
        base_doc = json.load(f)
    baseline = rows_to_map(base_doc["sources"])
    usage = usage_counts()

    current_rows = []
    for name, field, holds, url, key_needed in measure_sources.SOURCES:
        m = measure_sources.measure(url)
        m.update(name=name, field=field, holds=holds, url=url, advertised_key=key_needed)
        m["ok"] = bool(m["http_status"] == 200 and m["bytes"] > 0)
        m["browser_usable"] = bool(m["ok"] and m["cors"] in ("*", "origin"))
        current_rows.append(m)
        print("measured %-34s %-4s cors=%s" % (name, m["http_status"], m["cors"]), flush=True)
    current = rows_to_map(current_rows)

    rows = diff_rows(baseline, current)
    for r in rows:
        r["used_by"] = usage.get(host_of(current[r["name"]]["url"]), 0) if r["name"] in current else 0

    changed = [r for r in rows if r["state"] != "unchanged"]
    print("\nbaseline measured %s; today %s"
          % (base_doc.get("generated_utc", "?"),
             datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
    print("%d sources, %d changed" % (len(rows), len(changed)))
    for r in changed:
        print("  %-16s used_by=%-2d  %s  ->  %s  (%s)"
              % (r["state"], r["used_by"], r["was"], r["now"], r["name"]))

    regressions = [r for r in rows if r["state"] in REGRESSIONS]
    operational = [r for r in regressions if r["used_by"] > 0]
    print("\n%d regression(s), %d of them in a source a script calls"
          % (len(regressions), len(operational)))
    for r in regressions:
        print("  REGRESSION %-14s used_by=%d  %s" % (r["state"], r["used_by"], r["name"]))

    if args.write:
        out = {
            "checked_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "baseline_generated_utc": base_doc.get("generated_utc"),
            "baseline_path": os.path.relpath(args.baseline, REPO),
            "sources": len(rows),
            "changed": changed,
            "regressions": regressions,
            "regressions_in_used_sources": operational,
        }
        date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        dest = os.path.join(REPO, "research", "source-reachability-drift-%s.json" % date)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
            f.write("\n")
        print("wrote", os.path.relpath(dest, REPO))

    if operational or (args.strict and regressions):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
