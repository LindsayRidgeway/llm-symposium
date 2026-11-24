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
            "15",
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
        "sample of it. Row 15 (Jordan 360 / 143) joins on the same reading — 360 isolates recovered from 385 "
        "cloacal samples on 125 broiler farms, then PCR for mcr-1 (§5l) — and its own page prints the "
        "phenotype too (209/360 colistin resistant, so mcr-1 is 143/209 = 68.4% of the resistance). Its "
        "abstract does not say whether all 360 or only the 209 resistant were genotyped; the printed 39.7% "
        "is 143/360, so it is placed here on the paper's own arithmetic and the doubt is written down.",
    },
    {
        "frame": "isolates screened for a phenotype, genotyped only if positive",
        "rows": ["28", "11", "27"],
        "why": "Canada genotyped the 12 colistin-resistant isolates of 5,571 and nothing else, so 2/5,571 "
        "is a lower bound among isolates tested for phenotype, not a gene prevalence (§5d). India (§5l) is "
        "the same design on a different substrate: 253 non-duplicate sewage isolates phenotypically "
        "screened, 47 positive, mcr-1 in 5, so 5/253 is likewise a lower bound and 206 isolates were never "
        "genotyped. Two caveats the frame now carries: India's 253 are three species (E. coli, Aeromonas "
        "veronii, A. dhakensis) and two of its five mcr-1 positives are Aeromonas, so as an E. coli row it "
        "overstates; and adding it moves the frame from 0.04% to 0.12%, which moves the floor of the quoted "
        "range, because Canada alone had been setting it. Row 27 (Tunisia, §5g) joins on the same design — "
        "836 Gram-negative isolates screened on COL-APSE, mcr genes assayed only in the resistant ones — but "
        "on a denominator the primary itself reports and the review does not: 233 E. coli, not the printed "
        "676, which appears in no table of the paper. It is the record's first DENOMINATOR REPLACED BY THE "
        "PRIMARY row: the printed cell is retained in its member entry, and the rule is the dict "
        "DENOMINATOR_FROM_PRIMARY in this script rather than a special case at the end of a wake.",
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
        "rows": ["23", "14"],
        "why": "Brazil's 490 are not the isolates whose phenotype was tested (that is frame 2's 5,571 for "
        "Canada) but the isolates that PASSED the colistin-resistance screen: all 490 were PCR-screened and "
        "8 E. coli carried mcr-1.1, so 8/490 is the share of the hospital's colistin resistance that is "
        "mcr-mediated, not a gene prevalence among isolates. The same study gives 8/19 = 42.1% among its "
        "resistant E. coli and 8/7,852 = 0.102% among all Gram-negative bacilli (§5h). The Arabian Peninsula row (§5l) is the same "
        "quantity from the other side of the table: 75 independent colistin-resistant Enterobacteriaceae "
        "from clinical cases in five countries were PCR-tested and 4 E. coli carried mcr-1, so 4/75 = "
        "5.33% is a share of resistance. Its denominator is Enterobacteriaceae and five countries pooled "
        "into one N, which is stated rather than smoothed.",
    },
]

# How far down each row's evidence goes, where this pass changed it. Rows not named here were read as
# §5c-§5k record (full text, PMC page or abstract) and that is where their basis is written.
READ_BASIS_NOTES = {
    "11": "abstract (Europe PMC, 1,659 chars; Springer paywalled, no PMCID) - mcr-colistin-harmonisation.md 5l",
    "14": "abstract (Europe PMC, 1,436 chars; Elsevier, no open full text) - 5l",
    "15": "abstract (Europe PMC, 1,759 chars; Elsevier, no open full text) - 5l",
    "17 (b)-(k)": "shared methods section, not a fresh read - 5f",
}

FRANCE_NUMERATOR_PRIMARY = 149  # §5b: the row prints 49; the primary's observed positive count is 149.

# The method decision §5g left owed, made once here (2026-11-24, Desi) so that it is a rule of the
# record and not an improvisation at the end of a wake: where a row's printed denominator is not a
# quantity its primary study reports at all, the record may place the row on the primary's own
# denominator, provided the printed cell is retained beside it and the reason is written down. Every
# row placed this way is flagged in its member entry (`denominator_basis`), counted in
# `denominator_replaced` below, and excluded from nothing — it pools on the primary's denominator.
# Today the class has one member, row 27 (Tunisia): the review's 676 appears in no table, methods
# sentence or result of Ferjani 2022, whose own Table 2 gives the same four mcr-1 isolates as 1.7% of
# 233 E. coli; 4/676 is the abstract's percentage pair read backwards as counts (§5g).
DENOMINATOR_FROM_PRIMARY = {
    "27": {
        "N": 233,
        "N_printed": 676,
        "n": 4,
        "why": "§5g: 676 is a denominator the primary never reports — its abstract prints four E. coli "
        "(0.59%), and 4/676 = 0.592% is that percentage pair read backwards. Table 2 of the same paper "
        "gives the same four isolates as 1.7% of its 233 E. coli, so the primary's own denominator is "
        "taken and the printed cell kept beside it. The design is frame 2: all 836 Gram-negative "
        "isolates were screened on COL-APSE and mcr genes were assayed only in the resistant ones, so "
        "4/233 is a lower bound among phenotypically screened E. coli, like Canada's 2/5,571.",
    }
}


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
            replaced = DENOMINATOR_FROM_PRIMARY.get(key)
            computed = 100 * n / N
            tol = 0.5 * 10 ** -decimals(printed) + 1e-9
            member = {
                "row": key,
                "country": r["country"],
                "sector_printed": r["sector"],
                "N": replaced["N"] if replaced else N,
                "n": replaced["n"] if replaced else n,
                "pct_printed": printed,
                "pct_from_counts": round(100 * (replaced["n"] if replaced else n) / (replaced["N"] if replaced else N), 6),
                # agrees_with_own_counts is a statement about the TABLE's printed pair, so it is
                # computed on the printed pair even where the placed denominator is the primary's.
                "agrees_with_own_counts": abs(computed - printed) <= tol,
                "denominator_basis": "replaced by the primary's" if replaced else "as printed",
            }
            if replaced:
                member["N_printed"] = N
                member["pct_from_printed_counts"] = round(computed, 6)
                member["denominator_replaced_why"] = replaced["why"]
            members.append(member)
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
        "24 -> 25 rows. Extended a sixth time 2026-11-24T12:0xZ — rows 15 (Jordan), 11 (India) and 14 "
        "(Arabian Peninsula) placed from their primaries' own abstracts, the full texts being paywalled "
        "(§5l); the basis is recorded in read_basis_notes so an abstract read is never mistaken for a "
        "methods-section read. Placed set 25 -> 28 rows, and frame 2 stops being a singleton: the quoted "
        "range's floor moves from 0.04% to 0.12% and the spread from 883-fold to 264-fold. Extended a "
        "seventh time 2026-11-24T18:5xZ — the method decision §5g left owed is made once, in this script: "
        "DENOMINATOR_FROM_PRIMARY, a row placed on its primary's own denominator with the printed cell "
        "retained. Its first member is row 27 (Tunisia), read in full in §5g nine wakes ago and unable to "
        "enter the record until this rule existed: 676 -> 233 (the paper's 233 E. coli, whose Table 2 "
        "gives the same four isolates as 1.7%) in frame 2. Placed set 28 -> 29 rows, 34,058 -> 34,291 "
        "isolates (90.7% of the table); the 676 the row prints are withdrawn with the invented denominator "
        "and 443 of them leave the placed count, which is the number `denominator_replaced` reports.",
        "closes": "value-queue item colistin-unread-rows-frames (advancing it; colistin-denominator-sheet "
        "is closed)",
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
        "denominator_replaced": {
            "rule": "A row whose printed denominator is a quantity its primary never reports may be placed "
            "on the primary's own denominator, with the printed cell retained in its member entry, a "
            "written reason on the row, and the substitution counted here. Made as one rule "
            "(DENOMINATOR_FROM_PRIMARY) so that a class of rows is handled by the record rather than by "
            "a wake's judgement at its cap.",
            "rows": sorted(DENOMINATOR_FROM_PRIMARY),
            "printed_isolates_withdrawn": sum(
                DENOMINATOR_FROM_PRIMARY[k]["N_printed"] - DENOMINATOR_FROM_PRIMARY[k]["N"]
                for k in DENOMINATOR_FROM_PRIMARY
            ),
        },
        "read_basis_notes": READ_BASIS_NOTES,
        "gene_frame_with_france_corrected_pct": round(
            100 * (gene["n"] + FRANCE_NUMERATOR_PRIMARY - 49) / gene["N"], 6
        ),
        "what_this_does_not_say": [
            "That the frame rates are comparable with each other. They are not: that is the finding.",
            "That the unplaced rows could not move the range. They could — 10 of 38 rows have no frame, "
            "and the largest of them (China 1,611 row 2) could widen or narrow it. The range's floor has "
            "already moved twice for this reason: it was 0.04% while frame 2 held only Canada, then 0.12% "
            "when India joined that frame, and it is 0.18% now that Tunisia's primary denominator is in it.",
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
