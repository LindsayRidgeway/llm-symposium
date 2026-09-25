#!/usr/bin/env python3
"""Audit what the disease screen's two new rules change on the screens already on disk.

`scripts/disease_screen.py` grew two rules on 2026-09-20, and nobody has measured what they do
to the screens that already exist:

  * **Rule 1 — the density floor** (`FLOOR_STRICT = 1000`). A condition with fewer than this many
    title/abstract papers cannot carry an "unjoined" band: at that density almost every target
    looks unjoined for the trivial reason that few documents name the condition at all. The
    screen warns instead of concluding.
  * **Rule 2 — a join must carry its document** (`strict_hits` + `ambiguous_symbol`). A strict
    join whose symbol is three characters or fewer is a real token match that may be an ordinary
    word or another field's acronym (`AR` in "augmented reality", `KIT` in "mesh kit"). The rule
    fetches the documents and flags the row, so a reader is told to open the hit before a
    "prior work" verdict closes a lead.

This script answers, from the JSON artefact alone and with no network, three questions:

  1. Which screens sit below the floor — i.e. which verdicts rule 1 refuses to allow?
  2. How many "already published together" verdicts are token collisions, once rule 2 is applied?
  3. Which screens predate the rules and so cannot satisfy them at all — the rows that claim a
     join with no document behind it and no ambiguity flag?

It is a read-only measurement: it never runs a query. Writes `<screen>-rule-audit.md` next to the
screen and prints a summary. Usage:
    python3 scripts/screen_rule_audit.py research/*-screen.json
    python3 scripts/screen_rule_audit.py --json   # machine-readable to stdout only
"""
from __future__ import annotations

import glob
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Reuse the live constants so this audit cannot drift from the screen it audits.
_spec = importlib.util.spec_from_file_location("disease_screen", ROOT / "scripts/disease_screen.py")
ds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ds)
FLOOR_STRICT = ds.FLOOR_STRICT
AMBIGUOUS_MAX_LEN = ds.AMBIGUOUS_MAX_LEN


def corpus_strict(screen: dict) -> int | None:
    """Title/abstract paper count for the condition, under whichever key this vintage used."""
    for key in ("disease_papers_strict",):
        if isinstance(screen.get(key), int):
            return screen[key]
    return None


def audit_one(path: Path) -> dict:
    screen = json.loads(path.read_text())
    rows = screen.get("targets", []) or []
    real = [r for r in rows if not r.get("is_control")]
    joined = [r for r in real if (r.get("strict") or 0) > 0]

    def failed(r: dict) -> bool:
        """A count that came back negative is a query that did not answer, on either field."""
        return any(isinstance(r.get(k), int) and r[k] < 0 for k in ("strict", "any_field"))

    unanswered = [r for r in real if failed(r)]

    carries_hits = any("strict_hits" in r for r in rows)  # rule 2 adopted by this screen?
    carriers = [r for r in joined if r.get("strict_hits")]
    ambiguous = [r for r in joined if r.get("ambiguous_symbol")
                 or len(str(r.get("symbol", "")).strip()) <= AMBIGUOUS_MAX_LEN]

    strict_papers = corpus_strict(screen)
    below_floor = strict_papers is not None and 0 <= strict_papers < FLOOR_STRICT

    return {
        "file": path.name,
        "disease": screen.get("disease") or screen.get("condition_union"),
        "strict_papers": strict_papers,
        "floor": FLOOR_STRICT,
        "below_floor": below_floor,
        "n_targets": len(real),
        "n_controls": len(rows) - len(real),
        "rule2_adopted": carries_hits,
        "joined": len(joined),
        "joined_symbols": [r.get("symbol") for r in joined],
        "ambiguous_joins": len(ambiguous),
        "ambiguous_symbols": [r.get("symbol") for r in ambiguous],
        "joined_without_document": len(joined) - len(carriers) if carries_hits else len(joined),
        # Rows whose query never answered. A screen with these is a screen whose bands rest on
        # a denominator that includes searches that did not happen (see disease_screen.py,
        # 2026-09-23) — so the audit states them next to the rule they weaken.
        "unanswered": len(unanswered),
        "unanswered_symbols": [r.get("symbol") for r in unanswered],
        # Rule 2 as written still *counts* a collision; this is what it would be if it refused.
        "joined_if_collisions_refused": len(joined) - len(ambiguous),
    }


def audit_files(paths: list[Path]) -> list[dict]:
    return [audit_one(p) for p in sorted(paths)]


def _md_table(rows: list[dict]) -> str:
    head = ("| screen | condition | strict papers | floor | joined | collisions | joined if refused "
            "| carries documents |\n|---|---|---|---|---|---|---|---|\n")
    lines = []
    for a in rows:
        lines.append("| `%s` | %s | %s | %s | %d | %d | %d | %s |" % (
            a["file"], a["disease"], a["strict_papers"],
            "**below**" if a["below_floor"] else "ok",
            a["joined"], a["ambiguous_joins"], a["joined_if_collisions_refused"],
            "yes" if a["rule2_adopted"] else "**no — predates the rule**",
        ))
    return head + "\n".join(lines) + "\n"


def render_markdown(audits: list[dict]) -> str:
    below = [a for a in audits if a["below_floor"]]
    tot_joined = sum(a["joined"] for a in audits)
    tot_coll = sum(a["ambiguous_joins"] for a in audits)
    no_docs = [a for a in audits if not a["rule2_adopted"]]
    lines = [
        "# What the disease screen's two new rules change, measured on the screens we have",
        "",
        "Generated by `scripts/screen_rule_audit.py` from the `research/*-screen.json` artefacts "
        "on disk. Read-only, no network: it does not re-run any query, it only reads what the "
        "screens already recorded.",
        "",
        _md_table(audits),
        "## Rule 1 — the density floor",
        "",
    ]
    if below:
        for a in below:
            lines.append(
                "- **%s** (`%s`): %s title/abstract papers, below the %d floor. Its unjoined band "
                "is saturated, so any \"nothing here is unjoined\" reading of that screen is "
                "**warned against but not prevented** (see below)." % (
                    a["disease"], a["file"], a["strict_papers"], a["floor"]))
    else:
        lines.append("- No screen on disk is below the floor.")
    lines += [
        "",
        "## Rule 2 — a join must carry its document",
        "",
        "%d strict joins across these screens; %d of them (%s) are symbols of %d characters or "
        "fewer, so they are token collisions until a reader opens them." % (
            tot_joined, tot_coll, "%.0f%%" % (100.0 * tot_coll / tot_joined) if tot_joined else "n/a",
            AMBIGUOUS_MAX_LEN),
        "",
    ]
    for a in audits:
        if a["ambiguous_symbols"]:
            lines.append("- **%s**: %s" % (a["disease"], ", ".join(
                "`%s`" % s for s in a["ambiguous_symbols"])))
    lines += [
        "",
        "### The decision rule 2 leaves open",
        "",
        "The screen *counts* a collision as a join and only flags it (a warning). If it instead "
        "*refused* a flagged collision, the joined counts would move:",
        "",
    ]
    for a in audits:
        lines.append("- **%s**: %d → %d joined." % (
            a["disease"], a["joined"], a["joined_if_collisions_refused"]))
    lines += [
        "",
        "### What the flag does not mean",
        "",
        "Length is a heuristic, not a verdict. The flag is deliberately over-inclusive: it marks "
        "**every** symbol of three characters or fewer, because an ordinary word or another "
        "field's acronym is *possible* at that length, not because it is likely. `TNF`, `IL6` and "
        "`NGF` are rarely ordinary words; `CAT`, `HP`, `MET`, `F2`, `F10` and `C3` are. The flag "
        "says \"open the hit\", not \"this join is false\" — which is why the screen still counts "
        "the join, and why refusing it outright (the column above) would discard real ones too.",
        "",
        "## Screens that predate the rules",
        "",
    ]
    if no_docs:
        for a in no_docs:
            lines.append(
                "- **%s** (`%s`): %d joined rows, none carrying a `strict_hits` document and no "
                "`ambiguous_symbol` flag — the rule cannot be satisfied retroactively. These "
                "verdicts are the ones a reviewer should treat as unverified." % (
                    a["disease"], a["file"], a["joined_without_document"]))
    else:
        lines.append("- Every screen on disk carries its join documents.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    paths = [Path(a) for a in args] or sorted(
        (ROOT / "research").glob("*-screen.json"))
    if not paths:
        print("no screens found", file=sys.stderr)
        return 2
    audits = audit_files(paths)
    if "--json" in argv:
        print(json.dumps(audits, indent=2))
        return 0
    out = render_markdown(audits)
    dest = ROOT / "research" / "disease-screen-rule-audit.md"
    dest.write_text(out)
    print(out)
    print("wrote %s" % dest.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
