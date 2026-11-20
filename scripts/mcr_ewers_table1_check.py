#!/usr/bin/env python3
"""Read back the eleven Ewers-country rows (seed 17a-17k) to Ewers et al. Table 1.

Class B of the MCR colistin review's error audit: a printed cell can be arithmetically
consistent with its own n and N and still disagree with the study it cites (row 19 is the
known case). Class A (scripts/mcr_table_arithmetic_audit.py) cannot see that. This script
does the only thing that can: it parses the primary's own table and compares it, row by
row, with what the review printed.

The primary is Ewers et al., Front Microbiol 2022;13:1076315 (PMID 36569100, PMC9780603).
Its Table 1 is served as JATS XML by Europe PMC:

    curl -sS -o ewers.xml \\
      https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9780603/fullTextXML

Usage:
    python3 scripts/mcr_ewers_table1_check.py --xml ewers.xml --write
    python3 scripts/mcr_ewers_table1_check.py --xml ewers.xml --show

The XML is not vendored in this repository (225 KB of publisher markup); the record it
produces carries the sha256 of the bytes it was parsed from, so a later reader can tell
whether they are looking at the same retrieval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "research" / "mcr-colistin-seed.json"
OUT = ROOT / "research" / "mcr-ewers-table1.json"

# The 2010-2017 arm of Table 1 is the one the review's eleven sub-rows are drawn from.
# Country name as printed in the primary -> seed row label and country as printed in the seed.
COUNTRY_TO_SEED_ROW = {
    "Germany": ("17 (a)", "Germany"),
    "The Netherlands": ("17 (b)", "The Netherlands"),
    "Denmark": ("17 (c)", "Denmark"),
    "Switzerland": ("17 (d)", "Switzerland"),
    "Belgium": ("17 (e)", "Belgium"),
    "Poland": ("17 (f)", "Poland"),
    "Austria": ("17 (g)", "Austria"),
    "Spain": ("17 (h)", "Spain"),
    "Portugal": ("17 (i)", "Portugal"),
    "Italy": ("17 (j)", "Italy"),
    "Hungary": ("17 (k)", "Hungary"),
}


def strip_tags(chunk: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", chunk)).strip()


def to_int(cell: str):
    cell = cell.replace(",", "").replace("*", "").strip()
    if cell in {"", "-", "–", "NA", "n"}:
        return None
    try:
        return int(cell)
    except ValueError:
        return None


def to_float(cell: str):
    cell = cell.replace("<", "").strip()
    try:
        return float(cell)
    except ValueError:
        return None


def parse_table1(xml_text: str):
    """Return (rows, table_label, caption) for Table 1 of the Ewers paper."""
    tables = re.findall(r"<table-wrap[^>]*>.*?</table-wrap>", xml_text, re.S)
    target = None
    for t in tables:
        cap = re.search(r"<caption>(.*?)</caption>", t, re.S)
        if cap and "Frequency of mcr-1 and mcr-2" in strip_tags(cap.group(1)):
            target = t
            break
    if target is None:
        raise SystemExit("Table 1 not found in the XML supplied")

    label = re.search(r"<label>(.*?)</label>", target, re.S)
    caption = re.search(r"<caption>(.*?)</caption>", target, re.S)
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", target, re.S):
        cells = [strip_tags(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
        if not cells:
            continue
        rows.append(cells)
    return rows, strip_tags(label.group(1)) if label else "", strip_tags(caption.group(1)) if caption else ""


def build_record(rows, label, caption, xml_bytes: bytes):
    # Row layout (verified against the printed table):
    # 0 Country | 1 isolates 2010-17 | 2 mcr-1 n | 3 mcr-1 % | 4 mcr-2 n | 5 mcr-2 %
    # 6 isolates 2018-20 | 7 colistin-non-S n | 8 mcr-1 n (2018-20) | 9 % col-non-S
    # 10 % all | 11 mcr-2 n (2018-20)
    by_country = {}
    for cells in rows:
        if len(cells) < 12:
            continue
        by_country[cells[0]] = cells

    seed = json.loads(SEED.read_text())
    seed_rows = {r.get("sl"): r for r in seed["rows"]}

    checks = []
    for country, (seed_label, seed_country) in COUNTRY_TO_SEED_ROW.items():
        cells = by_country.get(country)
        if cells is None:
            checks.append({"seed_row": seed_label, "country": seed_country,
                           "status": "country not found in primary table"})
            continue
        n = to_int(cells[1])
        mcr1 = to_int(cells[2])
        mcr1_pct = to_float(cells[3])
        mcr2 = to_int(cells[4])
        any_n = (mcr1 or 0) + (mcr2 or 0)
        any_pct = round(100.0 * any_n / n, 6) if n else None

        row = seed_rows.get(seed_label)
        rec = {
            "seed_row": seed_label,
            "country": seed_country,
            "primary": {
                "isolates_2010_2017": n,
                "mcr1_n": mcr1,
                "mcr1_pct_printed": mcr1_pct,
                "mcr2_n": mcr2,
                "any_mcr_n": any_n,
                "any_mcr_pct_computed": any_pct,
                "isolates_2018_2020": to_int(cells[6]),
            },
        }
        if row is None:
            rec["status"] = "seed row not found in research/mcr-colistin-seed.json"
            checks.append(rec)
            continue
        rec["seed"] = {"N": row.get("n_isolates"), "n": row.get("mcr_positive"),
                       "pct_printed": row.get("prevalence_pct_reported")}
        agree = (row.get("n_isolates") == n) and (row.get("mcr_positive") == any_n)
        rec["n_agrees"] = row.get("n_isolates") == n
        rec["any_mcr_agrees"] = row.get("mcr_positive") == any_n
        printed = row.get("prevalence_pct_reported")
        if printed is None or not row.get("n_isolates"):
            rec["pct_agrees_with_own_counts"] = None
        else:
            # Judge the printed percentage at the number of decimals it printed: 9/102 = 8.8235
            # is correctly printed as 8.8, and calling that a mismatch would be the mirror of the
            # error this audit exists to find.
            decimals = len(str(printed).split(".")[1]) if "." in str(printed) else 0
            correct = round(100.0 * row["mcr_positive"] / row["n_isolates"], decimals)
            rec["pct_printed_at_decimals"] = correct
            rec["pct_agrees_with_own_counts"] = abs(correct - float(printed)) < 1e-9
        # For the review's own cell (17a) the printed percentage is judged in §2b, not here:
        # it is the study-wide mcr-1 rate, a class-B disagreement, not an arithmetic slip.
        rec["status"] = "agrees" if agree else "DISAGREES"
        checks.append(rec)

    # Block arithmetic: do the eleven sub-rows sum to the primary's total, and where does the
    # remainder go?
    total_cells = by_country.get("Total")
    other_cells = by_country.get("Other countries**")
    seed_block = [r for lab, r in seed_rows.items() if str(lab).startswith("17")]
    block = {
        "seed_rows_labelled_17": len(seed_block),
        "seed_N_sum": sum(r.get("n_isolates") or 0 for r in seed_block),
        "seed_n_sum": sum(r.get("mcr_positive") or 0 for r in seed_block),
        "primary_total_isolates": to_int(total_cells[1]) if total_cells else None,
        "primary_total_mcr1": to_int(total_cells[2]) if total_cells else None,
        "primary_total_mcr2": to_int(total_cells[4]) if total_cells else None,
        "primary_other_countries_isolates": to_int(other_cells[1]) if other_cells else None,
        "primary_other_countries_mcr1": to_int(other_cells[2]) if other_cells else None,
        "primary_other_countries_mcr2": to_int(other_cells[4]) if other_cells else None,
    }
    block["primary_total_any_mcr"] = (
        (block["primary_total_mcr1"] or 0) + (block["primary_total_mcr2"] or 0)
        if total_cells else None
    )
    block["seed_positives_equal_primary_any_mcr"] = block["seed_n_sum"] == block["primary_total_any_mcr"]
    block["unrepresented_isolates"] = (
        block["primary_total_isolates"] - block["seed_N_sum"]
        if block["primary_total_isolates"] is not None else None
    )
    block["primary_pooled_any_mcr_pct"] = (
        round(100.0 * block["primary_total_any_mcr"] / block["primary_total_isolates"], 4)
        if block["primary_total_isolates"] else None
    )
    block["seed_pooled_any_mcr_pct"] = (
        round(100.0 * block["seed_n_sum"] / block["seed_N_sum"], 4) if block["seed_N_sum"] else None
    )

    return {
        "artifact": "Ewers et al. Table 1 read back against the review's rows 17a-17k (class-B check)",
        "written": "2026-11-20",
        "written_by": "Desi (clock wake)",
        "primary": {
            "citation": "Ewers C, et al. Occurrence of mcr-1 and mcr-2 colistin resistance genes in porcine "
                        "Escherichia coli isolates (2010-2020) and genomic characterization of mcr-2-positive "
                        "E. coli. Front Microbiol 2022;13:1076315.",
            "pmid": "36569100",
            "pmcid": "PMC9780603",
            "doi": "10.3389/fmicb.2022.1076315",
            "retrieved_from": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9780603/fullTextXML",
            "retrieved_utc": "2026-11-19T20:31Z",
            "bytes": len(xml_bytes),
            "sha256": hashlib.sha256(xml_bytes).hexdigest(),
            "table_label": label,
            "caption": caption,
        },
        "method": "Parse `<table-wrap>` for the caption 'Frequency of mcr-1 and mcr-2'; read the 2010-2017 "
                  "arm; compare isolates with the seed's N and (mcr-1 + mcr-2) with the seed's n. The review's "
                  "own column definition is 'isolates carrying any mcr gene variant', so mcr-1 + mcr-2 is the "
                  "number its cells should hold.",
        "note_on_refetch": "A refetch on 2026-11-20 timed out (55 s, 0 bytes) from the same endpoint; the bytes "
                          "parsed here are the 2026-11-19 retrieval. The sha256 is recorded so a later reader can "
                          "tell whether their copy is the same one.",
        "rows": checks,
        "block_arithmetic": block,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", required=True, help="path to the Europe PMC JATS XML for PMC9780603")
    ap.add_argument("--write", action="store_true", help="write research/mcr-ewers-table1.json")
    ap.add_argument("--show", action="store_true", help="print the record")
    args = ap.parse_args()

    xml_bytes = Path(args.xml).read_bytes()
    rows, label, caption = parse_table1(xml_bytes.decode("utf-8"))
    record = build_record(rows, label, caption, xml_bytes)

    if args.write:
        OUT.write_text(json.dumps(record, indent=1) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")
    if args.show or not args.write:
        print(json.dumps(record, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
