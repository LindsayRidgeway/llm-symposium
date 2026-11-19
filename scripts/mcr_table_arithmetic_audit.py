#!/usr/bin/env python3
"""Audit the seed table's own arithmetic, row by row, and say which convention it uses.

Written 2026-11-19 by Desi (clock wake) after the letter to the review's corresponding author
(`channels/sent/2026-11-19-ferdous-colistin-row-17a-percentage.md`) offered the author a
"row-by-row reconciliation ... which is mostly the same work applied 28 times". This is the
arithmetic half of that promise, and it is the half that needs no network: every figure is
already in `research/mcr-colistin-seed.json`, transcribed from the review's Table 1.

What it answers, in order:

  1. Which rounding convention the table uses. Rows that discriminate between rounding and
     truncation are named; the convention is inferred from them rather than assumed.
  2. Which rows violate their own printed counts under that convention, and by how much.
  3. Where a violating cell's value comes from instead: tested against the pooled rate of its
     own sector, the pooled rate of the whole table, and — where the primary study's own
     study-wide rate is recorded on disk — that study's overall figure.
  4. What the table sums to, and how far the printed percentages move the pooled figures.

It writes `research/mcr-colistin-table-arithmetic.json`. It does NOT re-fetch the review, and it
makes no claim about prevalence in any population: the review's own footnote says its rows are
not comparable, and this file is arithmetic only.

    python3 scripts/mcr_table_arithmetic_audit.py --write
    python3 scripts/mcr_table_arithmetic_audit.py --show
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "research" / "mcr-colistin-seed.json"
PRIMARY = ROOT / "research" / "mcr-colistin-primary-raw.json"
OUT = ROOT / "research" / "mcr-colistin-table-arithmetic.json"

# The study-wide rate of the one primary whose Table 1 is transcribed in this repository. Ewers et
# al. 2022 (PMC9780603): 7,614 isolates, 793 mcr-1 positive. Kept here as constants because the
# figure is read from the primary's text, not recomputable from the review.
EWERS_STUDY_WIDE = {"isolates": 7614, "mcr1_positive": 793, "subrows": "17 (a)–17 (k)"}


def decimals(printed: float) -> int:
    """How many decimal places the review printed. Its table is not column-aligned in precision."""
    text = repr(float(printed))
    return len(text.split(".")[1]) if "." in text else 0


def exact_pct(n: int, N: int) -> float:
    return 100.0 * n / N


def half_width(dp: int) -> float:
    """The largest error a correctly rounded value can carry at this printed precision."""
    return 0.5 * 10 ** -dp


def audit_rows(rows: list[dict]) -> dict:
    checked = []
    for row in rows:
        n, N, printed = row["mcr_positive"], row["n_isolates"], float(row["prevalence_pct_reported"])
        exact = exact_pct(n, N)
        dp = decimals(printed)
        err = printed - exact
        tolerance = half_width(dp) + 1e-9
        rounded_ok = abs(err) <= tolerance
        truncated_ok = abs(printed - math.floor(exact * 10**dp) / 10**dp) < 1e-9
        # A row "discriminates" when rounding and truncation disagree about it, so the row tells us
        # which convention the table actually uses.
        discriminates = rounded_ok != truncated_ok
        checked.append(
            {
                "row": row["sl"],
                "country": row["country"],
                "sector": row["sector"],
                "N": N,
                "n": n,
                "printed_pct": printed,
                "exact_pct": round(exact, 6),
                "decimals_printed": dp,
                "error_pp": round(err, 6),
                "consistent_with_rounding": rounded_ok,
                "consistent_with_truncation": truncated_ok,
                "discriminates_convention": discriminates,
            }
        )
    return {"rows": checked}


def convention_evidence(checked: list[dict]) -> dict:
    """Pick the convention the table uses from the rows that can tell the two apart."""
    discriminators = [r for r in checked if r["discriminates_convention"]]
    return {
        "rows_that_discriminate": [
            {
                "row": r["row"],
                "country": r["country"],
                "exact_pct": r["exact_pct"],
                "printed_pct": r["printed_pct"],
                "reads_as": "rounding" if r["consistent_with_rounding"] else "truncation",
            }
            for r in discriminators
        ],
        "convention_inferred": (
            "rounding"
            if discriminators and all(r["consistent_with_rounding"] for r in discriminators)
            else "mixed or undetermined"
        ),
        "note": (
            "Rows where the two conventions agree (e.g. 8.8235 printed as 8.8) carry no evidence "
            "either way; only these rows do."
        ),
    }


def pools(checked: list[dict]) -> dict:
    by_sector: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for r in checked:
        bucket = by_sector[r["sector"]]
        bucket[0] += 1
        bucket[1] += r["N"]
        bucket[2] += r["n"]
    total_N = sum(b[1] for b in by_sector.values())
    total_n = sum(b[2] for b in by_sector.values())
    sectors = {}
    for name, (count, N, n) in sorted(by_sector.items(), key=lambda kv: -kv[1][1]):
        sectors[name] = {
            "rows": count,
            "sum_N": N,
            "sum_n": n,
            "pooled_pct_from_counts": round(exact_pct(n, N), 4),
        }
    return {
        "rows": len(checked),
        "sum_N": total_N,
        "sum_n": total_n,
        "pooled_pct_from_counts": round(exact_pct(total_n, total_N), 4),
        "by_sector": sectors,
    }


def attribution(checked: list[dict], pool_totals: dict) -> dict:
    """For every row that fails its own counts, test where the printed value came from."""
    findings = []
    for r in checked:
        if r["consistent_with_rounding"]:
            continue
        dp = r["decimals_printed"]
        tol = half_width(dp) + 1e-9
        sector_pool = pool_totals["by_sector"][r["sector"]]["pooled_pct_from_counts"]
        candidates = {
            "own sector pool (this table's counts)": sector_pool,
            "whole-table pool (this table's counts)": pool_totals["pooled_pct_from_counts"],
            "Ewers et al. study-wide mcr-1 rate": exact_pct(
                EWERS_STUDY_WIDE["mcr1_positive"], EWERS_STUDY_WIDE["isolates"]
            ),
        }
        matches = [
            {"candidate": name, "pct": round(value, 4), "matches_printed": abs(value - r["printed_pct"]) <= tol}
            for name, value in candidates.items()
        ]
        findings.append(
            {
                "row": r["row"],
                "country": r["country"],
                "printed_pct": r["printed_pct"],
                "exact_pct": r["exact_pct"],
                "error_pp": r["error_pp"],
                "is_largest_row_by_N": r["N"] == max(c["N"] for c in checked),
                "candidate_sources": matches,
            }
        )

    # The reverse test, which is what the letter to the author asked: is the study-wide rate pasted
    # into any other row? A row "carries" it if its printed value matches it to its own precision.
    carries_study_wide = [
        {
            "row": r["row"],
            "country": r["country"],
            "printed_pct": r["printed_pct"],
            "exact_pct": r["exact_pct"],
            "consistent_with_counts": r["consistent_with_rounding"],
        }
        for r in checked
        if abs(
            exact_pct(EWERS_STUDY_WIDE["mcr1_positive"], EWERS_STUDY_WIDE["isolates"]) - r["printed_pct"]
        )
        <= half_width(r["decimals_printed"]) + 1e-9
    ]
    return {"rows_failing_own_counts": findings, "rows_printing_the_study_wide_rate": carries_study_wide}


def printed_vs_counts_pooled(checked: list[dict], sector: str) -> dict:
    """What a reader gets who multiplies each printed percentage by its N, versus the counts."""
    rows = [r for r in checked if r["sector"] == sector]
    N = sum(r["N"] for r in rows)
    from_printed = sum(r["N"] * r["printed_pct"] for r in rows) / N
    from_counts = exact_pct(sum(r["n"] for r in rows), N)
    gap = from_printed - from_counts
    bad = [r for r in rows if not r["consistent_with_rounding"]]
    attributed = sum(r["N"] * (r["printed_pct"] - r["exact_pct"]) for r in bad) / N
    return {
        "sector": sector,
        "rows": len(rows),
        "sum_N": N,
        "pooled_from_counts_pct": round(from_counts, 4),
        "pooled_from_printed_pcts": round(from_printed, 4),
        "gap_pp": round(gap, 4),
        "gap_attributed_to_failing_rows_pp": round(attributed, 4),
    }


def build() -> dict:
    seed = json.loads(SEED.read_text())
    audited = audit_rows(seed["rows"])
    checked = audited["rows"]
    pool_totals = pools(checked)
    failing = [r for r in checked if not r["consistent_with_rounding"]]
    return {
        "artifact": "MCR colistin review Table 1 — arithmetic audit of every row against its own counts",
        "written": "2026-11-19",
        "written_by": "Desi (clock wake)",
        "source_table": {
            "review": seed["seed"]["title"],
            "citation": "Joy FU, Mouree TZ, Das M, Kabir A. Public Health Challenges 2026;5(3):e70376",
            "transcribed_in": "research/mcr-colistin-seed.json",
            "retrieved": seed["seed"]["retrieved"],
            "retrieved_from": seed["seed"]["retrieved_from"],
            "table_note_a": "Prevalence = (n/N) x 100, 'the percentage of isolates carrying any mcr gene variant'",
        },
        "rule": (
            "A row is consistent if its printed percentage is the correct rounding of 100*n/N at "
            "the number of decimals it printed. The rounding convention is not assumed: it is read "
            "off the rows that discriminate between rounding and truncation."
        ),
        "convention": convention_evidence(checked),
        "row_count": len(checked),
        "rows_failing_own_counts": len(failing),
        "failing_rows": [r["row"] + " " + r["country"] for r in failing],
        "pools": pool_totals,
        "attribution": attribution(checked, pool_totals),
        "printed_percentages_vs_counts": [printed_vs_counts_pooled(checked, s) for s in ("Livestock", "Human")],
        "rows": checked,
    }


def show(payload: dict) -> None:
    print(f"rows audited: {payload['row_count']}  failing own counts: {payload['rows_failing_own_counts']}")
    conv = payload["convention"]
    print(f"rounding convention: {conv['convention_inferred']} (from {len(conv['rows_that_discriminate'])} discriminating row(s))")
    for f in payload["attribution"]["rows_failing_own_counts"]:
        print(f"  FAIL {f['row']} {f['country']}: printed {f['printed_pct']} vs exact {f['exact_pct']} ({f['error_pp']:+.2f} pp)")
        for c in f["candidate_sources"]:
            print(f"       {c['candidate']}: {c['pct']}  match={c['matches_printed']}")
    p = payload["pools"]
    print(f"sum N = {p['sum_N']:,}   sum n = {p['sum_n']:,}   pooled = {p['pooled_pct_from_counts']:.2f}%")
    for s in payload["printed_percentages_vs_counts"]:
        print(f"  {s['sector']}: from counts {s['pooled_from_counts_pct']:.2f}% | from printed pcts {s['pooled_from_printed_pcts']:.2f}% | gap {s['gap_pp']:+.3f} pp (failing rows account for {s['gap_attributed_to_failing_rows_pp']:+.3f})")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help=f"write {OUT.relative_to(ROOT)}")
    ap.add_argument("--show", action="store_true", help="print the summary")
    args = ap.parse_args()
    payload = build()
    if args.write:
        OUT.write_text(json.dumps(payload, indent=1) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")
    if args.show or not args.write:
        show(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
