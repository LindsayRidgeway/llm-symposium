#!/usr/bin/env python3
"""The seven denominators behind the colistin table's pooled 7.0%, and what a
recalculated range replaces it with.

Written 2026-11-21 (Desi, clock wake) for agenda item 23 and the value-queue item
"a one-page correction sheet for the colistin prevalence table". Companion prose:
`research/mcr-colistin-denominator-correction-sheet.md`. Inputs are already on disk and
nothing is re-fetched: the table transcription is `research/mcr-colistin-seed.json`
(Europe PMC JATS, 2026-09-29) and the read-back corrections are the ones recorded in
`research/mcr-colistin-harmonisation.md` §5d/§5e.

The point of the script is that every number in the sheet can be recomputed from two
files, so a reader does not have to trust the prose:

  * the seven denominator FRAMES the read portion of the table is counted in;
  * the per-row alternative counts each primary study offers for the rows we have read;
  * five POOLS, including the review's own single 7.0%, so the range is a range over
    stated rules rather than a mood;
  * the size split, which is the finding: the heavy rows and the light rows pool to
    figures a factor of 3.6 apart.

Usage:
    python3 scripts/mcr_colistin_denominator_frames.py            # print a summary
    python3 scripts/mcr_colistin_denominator_frames.py --write    # write the record JSON
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "research" / "mcr-colistin-seed.json"
RECORD = ROOT / "research" / "mcr-colistin-denominator-frames.json"

# ---------------------------------------------------------------------------
# The seven frames. Rows are seed-row labels. A row can sit in two frames when the
# study really counts two things; row 21 does, and that overlap is the point of frame 3.
# ---------------------------------------------------------------------------
FRAMES = [
    {
        "id": 1,
        "frame": "isolates screened for the gene",
        "rows": ["13", "6", "17 (a)", "17 (h)", "17 (i)", "19"],
        "note": (
            "The frame the review's own table note claims for the whole column: "
            "(n/N) x 100 for 'isolates carrying any mcr gene variant'. Row 19 is only "
            "half in it: its N counts animal observations (1,561 breeding animals + 140 "
            "fattening observations from 50 kids) while its n counts mcr-1-positive "
            "isolates, so it is frame 1's numerator over frame 3's denominator."
        ),
    },
    {
        "id": 2,
        "frame": "isolates screened for a phenotype, genotyped only if positive",
        "rows": ["28", "21"],
        "note": (
            "Row 28 screened 5,571 isolates for colistin resistance (MIC >= 4) and ran "
            "mcr-1 PCR on the 12 that were resistant, so its N is a phenotype screen and "
            "its n a genotype find. Row 21 is the same order at the host level."
        ),
    },
    {
        "id": 3,
        "frame": "hosts (animals and humans enrolled), not isolates",
        "rows": ["21"],
        "note": (
            "227 is 102 animals + 125 humans in 80 households; the 12 are positive hosts, "
            "and the study reports 17 mcr-1 isolates across repeated timepoints. Same study, "
            "three possible rates."
        ),
    },
    {
        "id": 4,
        "frame": "samples or products, not isolates",
        "rows": ["18", "5"],
        "note": (
            "Row 18's 128 are retail poultry products bought in Switzerland and southern "
            "Germany; row 5's 1,112 are duck-farm samples. Neither is a count of isolates."
        ),
    },
    {
        "id": 5,
        "frame": "one recovered isolate per positive sample",
        "rows": ["20"],
        "note": (
            "570 retail meat samples were collected; 147 yielded E. coli and one isolate "
            "per positive sample was kept. The 147 is therefore neither the samples nor "
            "the isolates present in them."
        ),
    },
    {
        "id": 6,
        "frame": "colistin-selected mixed-species isolates",
        "rows": ["25"],
        "note": (
            "103 isolates (52 soil, 31 water, 20 manure) recovered from 40 environmental "
            "samples at 8 sites after colistin-containing selective culture. Because the "
            "medium selects the phenotype, an mcr-carrying but colistin-susceptible isolate "
            "could not have been recovered at all."
        ),
    },
    {
        "id": 7,
        "frame": "a sum across sampling frames",
        "rows": ["1"],
        "note": (
            "2,649 = 523 raw-meat isolates + 804 animal isolates + 1,322 inpatient "
            "isolates, three different populations added into one N and one n."
        ),
    },
]

# ---------------------------------------------------------------------------
# Per-row alternatives: every figure below is the primary study's own count as recorded
# in research/mcr-colistin-harmonisation.md §2, §5b and §5e. The first entry per row is
# the table's printed cell; the rest are the other frames the same study offers.
# label -> (numerator, denominator, what the denominator counts)
# ---------------------------------------------------------------------------
ALTERNATIVES = {
    "13": [
        (39, 9306, "isolates gene-screened (printed)"),
    ],
    "17 (a)": [
        (709, 6158, "any-mcr isolates (printed numerator; printed % is the study-wide rate)"),
    ],
    "28": [
        (2, 5571, "isolates phenotype-screened (printed)"),
        (2, 12, "colistin-resistant isolates genotyped"),
    ],
    "1": [
        (260, 2649, "three frames summed (printed)"),
        (78, 523, "raw-meat frame"),
        (166, 804, "animal frame"),
        (16, 1322, "inpatient frame"),
    ],
    "6": [
        (54, 2330, "isolates gene-screened (printed)"),
    ],
    "19": [
        (49, 1701, "printed numerator"),
        (149, 1701, "mcr-1-positive isolates (primary: 65 + 84)"),
    ],
    "17 (h)": [
        (17, 28, "any-mcr isolates, 16 mcr-1 + 1 mcr-2 (printed)"),
    ],
    "17 (i)": [
        (17, 28, "any-mcr isolates, 17 mcr-1 + 0 (printed)"),
    ],
    "18": [
        (33, 128, "PCR-positive cultures per product (printed)"),
        (12, 128, "pure-culture mcr-1 recoveries"),
    ],
    "20": [
        (2, 147, "colistin non-wild-type isolates (printed)"),
        (3, 147, "mcr-1 isolates, the primary's own gene figure"),
        (3, 570, "mcr-positive retail meat samples"),
    ],
    "21": [
        (12, 227, "positive hosts (printed)"),
        (17, 227, "mcr-1 isolates across repeated timepoints"),
    ],
    "25": [
        (8, 103, "colistin-selected isolates (printed)"),
        (8, 40, "positive environmental samples"),
    ],
}

# Rows whose printed numerator the primary study contradicts on its own gene count.
# Used by the "gene-corrected" pool. Row 17 (a) is not here: its numerator is right and
# its percentage is wrong, which changes no count and so moves no pool.
GENE_CORRECTED = {"19": 149, "20": 3}

# Rows whose printed denominator is not a count of isolates screened for the gene, and so
# cannot sit in the pool the review's own table note describes. Dropped by "isolates_only".
NON_ISOLATE_DENOMINATORS = ["18", "21", "25", "1"]


def pct(n: int, N: int) -> float:
    return 100.0 * n / N


def _rows() -> dict:
    seed = json.loads(SEED.read_text())
    return {r["sl"]: r for r in seed["rows"]}, seed["rows"]


def derive() -> dict:
    by_label, ordered = _rows()
    total_N = sum(r["n_isolates"] for r in ordered)
    total_n = sum(r["mcr_positive"] for r in ordered)

    # Pool 1 — the review's own figure: every printed cell, added.
    as_printed = {"numerator": total_n, "denominator": total_N, "pct": pct(total_n, total_N)}

    # Pool 2 — same 38 rows, numerator replaced by the primary's gene count where read.
    n2 = 0
    for r in ordered:
        n2 += GENE_CORRECTED.get(r["sl"], r["mcr_positive"])
    gene_corrected = {"numerator": n2, "denominator": total_N, "pct": pct(n2, total_N)}

    # Pool 3 — restricted to rows whose N is a count of isolates screened for the gene.
    N3 = sum(r["n_isolates"] for r in ordered if r["sl"] not in NON_ISOLATE_DENOMINATORS)
    n3 = sum(
        GENE_CORRECTED.get(r["sl"], r["mcr_positive"])
        for r in ordered
        if r["sl"] not in NON_ISOLATE_DENOMINATORS
    )
    isolates_only = {"numerator": n3, "denominator": N3, "pct": pct(n3, N3)}

    # Pool 4/5 — the twelve rows somebody has actually read back, as printed and corrected.
    read = [lbl for lbl in ALTERNATIVES]
    missing = [lbl for lbl in read if lbl not in by_label]
    if missing:
        raise SystemExit(f"seed table has no row labelled {missing}")
    Nr = sum(by_label[l]["n_isolates"] for l in read)
    nr = sum(by_label[l]["mcr_positive"] for l in read)
    nr2 = sum(GENE_CORRECTED.get(l, by_label[l]["mcr_positive"]) for l in read)
    read_twelve = {"rows": len(read), "numerator": nr, "denominator": Nr, "pct": pct(nr, Nr)}
    read_twelve_corrected = {"rows": len(read), "numerator": nr2, "denominator": Nr,
                             "pct": pct(nr2, Nr)}

    # The twenty-six rows nobody has read back, and the weight each side carries.
    unread_twenty_six = {
        "rows": len(ordered) - len(read),
        "numerator": total_n - nr,
        "denominator": total_N - Nr,
        "pct": pct(total_n - nr, total_N - Nr),
    }
    size_split = {
        "read_twelve_share_of_N": 100.0 * Nr / total_N,
        "ratio_read_to_unread": read_twelve["pct"] / unread_twenty_six["pct"],
    }

    # Per-row spreads: how far one row's rate moves between the frames its own study offers.
    per_row = []
    for lbl, alts in ALTERNATIVES.items():
        rates = [pct(n, N) for n, N, _ in alts]
        per_row.append({
            "row": lbl,
            "country": by_label[lbl]["country"],
            "sector": by_label[lbl]["sector"],
            "printed_pct": by_label[lbl]["prevalence_pct_reported"],
            "frames": [
                {"numerator": n, "denominator": N, "counts": what, "pct": pct(n, N)}
                for n, N, what in alts
            ],
            "spread_x": (max(rates) / min(rates)) if min(rates) > 0 else None,
        })

    spreads = sorted(
        (r["spread_x"], r["row"]) for r in per_row if r["spread_x"] and r["spread_x"] > 1.0
    )
    moved = [r for r in per_row if r["spread_x"] and r["spread_x"] > 1.0]

    pool_pcts = [as_printed["pct"], gene_corrected["pct"], isolates_only["pct"],
                 read_twelve["pct"], read_twelve_corrected["pct"]]

    return {
        "artifact": "The seven denominators behind the colistin table's pooled 7.0%, and the "
                    "range that replaces it",
        "written": "2026-11-21",
        "written_by": "Desi (clock wake 20261121T144924Z-5987a5f0)",
        "agenda_item": 23,
        "companion_prose": "research/mcr-colistin-denominator-correction-sheet.md",
        "generated_by": "scripts/mcr_colistin_denominator_frames.py --write",
        "inputs": {
            "table_transcription": "research/mcr-colistin-seed.json",
            "read_back_record": "research/mcr-colistin-harmonisation.md (§5d, §5e)",
            "arithmetic_audit": "research/mcr-colistin-table-arithmetic.json",
        },
        "note": "Nothing is re-fetched here. These are counts already on disk, re-pooled.",
        "frame_count": len(FRAMES),
        "frames": FRAMES,
        "pools": {
            "as_printed": as_printed,
            "gene_corrected": gene_corrected,
            "isolates_only": isolates_only,
            "read_twelve_as_printed": read_twelve,
            "read_twelve_gene_corrected": read_twelve_corrected,
            "unread_twenty_six": unread_twenty_six,
        },
        "recalculated_range_pct": [min(pool_pcts), max(pool_pcts)],
        "size_split": size_split,
        "per_row_frames": per_row,
        "rows_whose_rate_moves_between_frames": len(moved),
        "widest_spread": {"row": spreads[-1][1], "factor": spreads[-1][0]},
        "narrowest_spread": {"row": spreads[0][1], "factor": spreads[0][0]},
        "gene_corrected_rows": GENE_CORRECTED,
        "non_isolate_denominator_rows": NON_ISOLATE_DENOMINATORS,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    d = derive()
    if args.write:
        RECORD.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
        print(f"wrote {RECORD.relative_to(ROOT)}")

    p = d["pools"]
    print(f"frames: {d['frame_count']}")
    for k in ("as_printed", "gene_corrected", "isolates_only",
              "read_twelve_as_printed", "read_twelve_gene_corrected", "unread_twenty_six"):
        v = p[k]
        print(f"  {k:26} {v['numerator']:>5} / {v['denominator']:>6} = {v['pct']:6.4f}%")
    lo, hi = d["recalculated_range_pct"]
    print(f"range: {lo:.2f}% - {hi:.2f}%")
    print(f"read twelve carry {d['size_split']['read_twelve_share_of_N']:.2f}% of N; "
          f"read:unread rate ratio {d['size_split']['ratio_read_to_unread']:.2f}x")
    print(f"rows that move between frames: {d['rows_whose_rate_moves_between_frames']}; "
          f"widest {d['widest_spread']['row']} at {d['widest_spread']['factor']:.1f}x, "
          f"narrowest {d['narrowest_spread']['row']} at {d['narrowest_spread']['factor']:.2f}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
