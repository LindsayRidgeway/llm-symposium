#!/usr/bin/env python3
"""Which quantity each denominator in the colistin table actually counts, and what the table's rate
becomes when the frames are separated instead of pooled.

Written 2026-11-21 by Dmitri (clock wake) to write `research/mcr-colistin-denominator-sheet.md`, the
close of value-queue item `colistin-denominator-sheet`. The finding is not new here: it was reached
row by row in `research/mcr-colistin-harmonisation.md` §5c–§5e across 2026-11-19/21, three error
classes at a time. What was missing was the one-page reading: the frames, their rows, and a
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
        "rows": [
            "13",
            "6",
            "17 (a)",
            "17 (b)",
            "17 (c)",
            "17 (d)",
            "17 (e)",
            "17 (f)",
            "17 (g)",
            "17 (h)",
            "17 (i)",
            "17 (j)",
            "17 (k)",
            "19",
            "7",
            "12",
        ],
        "why": "each N is a count of bacterial isolates put through a molecular screen, so n/N is a gene "
        "prevalence among screened isolates. Row 19's printed numerator disagrees with its own primary "
        "by 100 (49 vs 149, §5b) — the frame is still this one, the cell is the error. Rows 17 (a)–17 (k) "
        "are the eleven country slices of one laboratory's stored porcine isolates, PCR-screened for "
        "mcr-1 and mcr-2 (§2a, §3, §5f); eight of them were placed on 2026-11-21 22:50Z from the shared "
        "methods section rather than from a fresh read. Row 7 (Bangladesh 1,200 / 305) is an isolate "
        "screen whose sampling unit is not the isolate: 20 MacConkey colonies picked at random per pooled "
        "faecal sample, on 20 broiler farms at three points in one flock cycle (§5j). Its 25.42% is the "
        "share of screened colonies, so it belongs to this frame by what N counts and carries a weight "
        "caveat the frame's pool does not escape — 1,200 colonies from 60 samples now count twenty times "
        "each in its 5.66%. Row 12 (Japan 684 / 90) joins on the same reading: the 684 are swine-pathogenic "
        "*E. coli* strains — diagnostic submissions from diseased pigs (diarrhoea or oedema disease) at "
        "23 Livestock Hygiene Service Centres, 1991-2014 — put through a PCR screen for mcr-1 (§5k). It is "
        "an isolate screen, but a serogroup-restricted subset: 684 of the 967 strains the collection holds, "
        "kept because they fall in four predominant serogroups, so it is 71% of its own source and not a "
        "sample of it.",
    },
    {
        "frame": "isolates screened for a phenotype, genotyped only if positive",
        "rows": ["28"],
        "why": "Canada genotyped the 12 colistin-resistant isolates of 5,571 and nothing else, so 2/5,571 "
        "is a lower bound among isolates tested for phenotype, not a gene prevalence (§5d).",
    },
    {
        "frame": "hosts (animals and humans enrolled)",
        "rows": ["21", "22"],
        "why": "the Portugal row's 227 are enrolled hosts and its 12 are positive hosts; the study's 17 "
        "isolates and the isolation medium's own colistin (3.5 µg/mL) are not in either number (§5e). "
        "Argentina's 140 are rectal swabs from pigs on six farms — animals sampled, not E. coli isolates "
        "(§5i), so 23/140 is host carriage. The frame therefore holds two host species and two sampling "
        "designs, and its 9.54% is a pool of those two rows only.",
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
    {
        "frame": "colistin-resistant isolates, genotyped for the gene",
        "rows": ["23"],
        "why": "Brazil's 490 are not the isolates whose phenotype was tested (that is frame 2's 5,571 for "
        "Canada) but the isolates that PASSED the colistin-resistance screen: all 490 were PCR-screened and "
        "8 E. coli carried mcr-1.1, so 8/490 is the share of the hospital's colistin resistance that is "
        "mcr-mediated, not a gene prevalence among isolates. The same study gives 8/19 = 42.1% among its "
        "resistant E. coli and 8/7,852 = 0.102% among all Gram-negative bacilli (§5h).",
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
        "extended_by": "Desi (clock wake 2026-11-21T22:50Z) — frame 1 extended from six rows to fourteen "
        "with the eight remaining Ewers country rows (17 b–g, j, k), placed from the shared methods "
        "section in research/mcr-colistin-harmonisation.md §5f; no cell re-read here. Extended again "
        "2026-11-23T16:56Z — row 23 (Brazil) placed in an eighth frame, 'colistin-resistant isolates, "
        "genotyped for the gene', because its N counts the isolates that passed the phenotype screen "
        "rather than the isolates screened; the row read is §5h. Extended a third time 2026-11-23T22:57Z — "
        "row 22 (Argentina) placed in the existing hosts frame, since its 140 are pigs swabbed rather "
        "than isolates; the row read is §5i, written at 19:4xZ, and this pass is the one-step "
        "regeneration that read left owed. Extended a fourth time 2026-11-24T07:00Z — row 7 "
        "(Bangladesh) placed in frame 1, the isolate screen, on a full read of its primary (Ahmed et "
        "al., Sci Rep 2020, PMC7596488); the read is §5j and the caveat it leaves on the frame's pool is "
        "stated there. Placed set 23 -> 24 rows. Extended a fifth time 2026-11-24T11:00Z — row 12 "
        "(Japan 684 / 90) placed in frame 1 on a full read of its primary (Kusumoto et al., Emerg "
        "Infect Dis 2016, PMC4918142), the read is §5k; its 684 are a serogroup-restricted subset of "
        "diagnostic submissions from diseased swine, which is stated rather than smoothed. Placed set "
        "24 -> 25 rows.",
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
            "bases": f"the {len(frames_out)} frame rates, not the {len(all_pct)} row rates",
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
            "That the frame rates are comparable with each other. They are not: that is the finding.",
            "That the unplaced rows could not move the range. They could — 14 of 38 rows have no frame, "
            "and the largest of them (China 1,611 row 2, Japan 684 row 12) could widen or narrow it; "
            "Tunisia 676 is now read and deliberately unplaced, per §5g.",
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
    print(f"pooled 7.0% replaced by {record['frame_count']} frame rates, {r['low_pct']:.4f}% to {r['high_pct']:.4f}% "
          f"({r['fold_spread']}x)")
    print(f"arithmetic failures among placed rows: {record['arithmetic_failures_among_placed_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
