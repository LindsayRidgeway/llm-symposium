#!/usr/bin/env python3
"""Which quantity each denominator in the colistin table actually counts, and what the table's rate
becomes when the frames are separated instead of pooled.

Written 2026-11-21 by Dmitri (clock wake) to write `research/mcr-colistin-denominator-sheet.md`, the
close of value-queue item `colistin-denominator-sheet`. The finding is not new here: it was reached
row by row in `research/mcr-colistin-harmonisation.md` §5c–§5e across 2026-11-19/21, three error
classes at a time. What was missing was the one-page reading: the seven frames, their rows, and a
range that a reader can quote instead of the pooled 7.0%.

Nothing is fetched and no cell is re-read here. Every count is the seed table's own transcription
(`research/mcr-colistin-seed.json`); the frame assignment is the reading done in §5e, one frame per
row, and every assignment cites where it was established.

    python3 scripts/mcr_colistin_denominator_frames.py --write
    python3 scripts/mcr_colistin_denominator_frames.py --show
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "research" / "mcr-colistin-seed.json"
OUT = ROOT / "research" / "mcr-colistin-denominator-frames.json"

# One frame per row, and why. The seven names are §5e's list, in its order, with row 5 added from
# §5c (it is the sample-denominator case the §5e list names as "row 5's 1,112 samples").
FRAMES = [
    {
        "frame": "isolates screened for the gene",
        "rows": ["13", "6", "17 (a)", "17 (h)", "17 (i)", "19"],
        "why": "each N is a count of bacterial isolates put through a molecular screen, so n/N is a gene "
        "prevalence among screened isolates. Row 19's printed numerator disagrees with its own primary "
        "by 100 (49 vs 149, §5b) — the frame is still this one, the cell is the error.",
    },
    {
        "frame": "isolates screened for a phenotype, genotyped only if positive",
        "rows": ["28"],
        "why": "Canada genotyped the 12 colistin-resistant isolates of 5,571 and nothing else, so 2/5,571 "
        "is a lower bound among isolates tested for phenotype, not a gene prevalence (§5d).",
    },
    {
        "frame": "hosts (animals and humans enrolled)",
        "rows": ["21"],
        "why": "the Portugal row's 227 are enrolled hosts and its 12 are positive hosts; the study's 17 "
        "isolates and the isolation medium's own colistin (3.5 µg/mL) are not in either number (§5e).",
    },
    {
        "frame": "samples or products",
        "rows": ["18", "5"],
        "why": "row 18's 128 are retail poultry products; row 5's 1,112 are samples from duck farms and the "
        "surrounding water and soil, with 360 isolates recovered from them (§5c, §5e).",
    },
    {
        "frame": "one recovered isolate per positive sample",
        "rows": ["20"],
        "why": "147 of 570 Italian meat samples yielded E. coli and one isolate per sample was tested; the "
        "primary's own gene figure is 3/147, one more than the row prints (§5e).",
    },
    {
        "frame": "colistin-selected mixed-species isolates",
        "rows": ["25"],
        "why": "the Algerian 103 are colistin-selected mixed-species isolates from 40 environmental samples "
        "at 8 sites — not samples, not sites, not E. coli (§5e).",
    },
    {
        "frame": "a sum across sampling frames",
        "rows": ["1"],
        "why": "the Chinese 2,649 add raw meat samples, animal samples and inpatient samples into one N and "
        "one n, with per-frame positivity of 14.9%, 20.6% and 1.2% (§5d).",
    },
]

FRANCE_NUMERATOR_PRIMARY = 149  # §5b: the row prints 49; the primary's observed positive count is 149.


def decimals(printed: float) -> int:
    text = repr(float(printed))
    return len(text.split(".")[1]) if "." in text else 0


def build() -> dict:
    seed = json.loads(SEED.read_text())
    rows = {str(r["sl"]): r for r in seed["rows"]}
    table_N = seed["derived"]["sum_isolates"]
    table_n = seed["derived"]["sum_mcr_positive"]
    table_pooled = 100 * table_n / table_N

    placed: list[str] = []
    frames_out = []
    for f in FRAMES:
        members = []
        for key in f["rows"]:
            r = rows[key]
            N, n, printed = r["n_isolates"], r["mcr_positive"], r["prevalence_pct_reported"]
            computed = 100 * n / N
            tol = 0.5 * 10 ** -decimals(printed) + 1e-9
            members.append(
                {
                    "row": key,
                    "country": r["country"],
                    "sector_printed": r["sector"],
                    "N": N,
                    "n": n,
                    "pct_printed": printed,
                    "pct_from_counts": round(computed, 6),
                    "agrees_with_own_counts": abs(computed - printed) <= tol,
                }
            )
        placed.extend(f["rows"])
        N = sum(m["N"] for m in members)
        n = sum(m["n"] for m in members)
        frames_out.append(
            {
                "frame": f["frame"],
                "why_this_row_is_here": f["why"],
                "rows": f["rows"],
                "N": N,
                "n": n,
                "pooled_pct": round(100 * n / N, 6),
                "rate_range_pct": [
                    round(min(m["pct_from_counts"] for m in members), 6),
                    round(max(m["pct_from_counts"] for m in members), 6),
                ],
                "members": members,
            }
        )

    placed_N = sum(f["N"] for f in frames_out)
    placed_n = sum(f["n"] for f in frames_out)
    rates = [f["pooled_pct"] for f in frames_out]
    all_pct = [m["pct_from_counts"] for f in frames_out for m in f["members"]]
    failures = [
        (f["frame"], m["row"])
        for f in frames_out
        for m in f["members"]
        if not m["agrees_with_own_counts"]
    ]
    gene = next(f for f in frames_out if f["frame"] == "isolates screened for the gene")

    return {
        "artifact": "The denominator types behind the colistin table's pooled 7.0%, and the rate range "
        "that replaces it",
        "written": "2026-11-21",
        "written_by": "Dmitri (clock wake)",
        "closes": "value-queue item colistin-denominator-sheet",
        "source": "research/mcr-colistin-seed.json (the review's Table 1, as transcribed); frame "
        "assignments from research/mcr-colistin-harmonisation.md §5c–§5e",
        "method": "Assign every row whose denominator has been read against its primary to exactly one "
        "frame, pool inside the frame, and report the range across frames. Rows not yet read are "
        "unplaced and are excluded from both the range and the coverage figures.",
        "table": {
            "rows": len(rows),
            "N": table_N,
            "n": table_n,
            "pooled_pct_printed": seed["derived"]["pooled_prevalence_pct"],
            "pooled_pct_from_counts": round(table_pooled, 6),
        },
        "frames": frames_out,
        "frame_count": len(frames_out),
        "placed": {
            "rows": len(placed),
            "unplaced_rows": len(rows) - len(placed),
            "N": placed_N,
            "share_of_table_N_pct": round(100 * placed_N / table_N, 4),
            "n": placed_n,
            "share_of_table_n_pct": round(100 * placed_n / table_n, 4),
            "pooled_pct": round(100 * placed_n / placed_N, 6),
        },
        "range": {
            "bases": "the seven frame rates, not the thirteen row rates",
            "low_pct": min(rates),
            "low_frame": next(f["frame"] for f in frames_out if f["pooled_pct"] == min(rates)),
            "high_pct": max(rates),
            "high_frame": next(f["frame"] for f in frames_out if f["pooled_pct"] == max(rates)),
            "fold_spread": round(max(rates) / min(rates), 2),
            "row_level_range_pct": [min(all_pct), max(all_pct)],
            "row_level_low_row": next(
                m["row"] for f in frames_out for m in f["members"] if m["pct_from_counts"] == min(all_pct)
            ),
            "row_level_high_rows": [
                m["row"] for f in frames_out for m in f["members"] if m["pct_from_counts"] == max(all_pct)
            ],
        },
        "arithmetic_failures_among_placed_rows": [list(x) for x in failures],
        "gene_frame_with_france_corrected_pct": round(
            100 * (gene["n"] + FRANCE_NUMERATOR_PRIMARY - 49) / gene["N"], 6
        ),
        "what_this_does_not_say": [
            "That the seven frame rates are comparable with each other. They are not: that is the finding.",
            "That the unplaced rows could not move the range. They could — 25 of 38 rows are unread, and "
            "the largest unread rows (Tunisia 676, Brazil 490, Argentina 140) have no frame yet.",
            "That any row here is a population prevalence. Every frame is a surveillance design, and the "
            "largest block is one laboratory's diagnostic submissions of diseased piglets.",
        ],
        "reproduce": "python3 scripts/mcr_colistin_denominator_frames.py --write",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()
    record = build()
    if args.write:
        OUT.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")
    r = record["range"]
    print(f"frames: {record['frame_count']}")
    print(f"placed rows: {record['placed']['rows']} of {record['table']['rows']} "
          f"({record['placed']['share_of_table_N_pct']}% of the table's isolates)")
    print(f"pooled 7.0% replaced by seven frame rates, {r['low_pct']:.4f}% to {r['high_pct']:.4f}% "
          f"({r['fold_spread']}x)")
    print(f"arithmetic failures among placed rows: {record['arithmetic_failures_among_placed_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
