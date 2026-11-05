#!/usr/bin/env python3
"""What is staged versus what the outbound ledger can see.

Written 2026-11-05 (Desi) after a review of Dmitri's 22:40Z run turned up two facts
that no existing instrument reports:

  * 26 letter drafts sit in `channels/outreach/drafts/` and only 9 of them are named
    by a row in `channels/outreach/pipeline.json`.
  * three of the unnamed ones are the *same letter*, byte for byte
    (md5 58cc72cb316c6a4fdd602c06d02482a8), staged under three filenames, addressed
    to the same desk at the same institution.

Why that matters, and why `scripts/outreach_ledger_audit.py` cannot say it: the audit
subscribes to the ledger and walks every row, so a draft that no row points at is
invisible to it. Its "staged = 9" is a true count of *rows in the staged state*, and
it has been quoted since 2026-10-01 as if it counted the drafts folder. A draft the
ledger cannot see cannot be sent through a drain, cannot be retired, and cannot be
noticed as a duplicate — it is staged work that exists only as a file.

Two directions, because either alone is a half-truth:
  orphan  — a staged draft that no pipeline row names (nobody can act on it)
  missing — a pipeline row that names a draft that is not on disk (the ledger lies)
Duplicate content is reported separately and by hash, because two copies of one
letter are a live risk (send the same pitch twice and the "one contact per venue"
discipline in the letters themselves is broken) even when both copies are named.

Read-only. Nothing is deleted, moved or edited: this is a census, and the decision
about which copy of a letter survives belongs to the amigo who wrote it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = REPO_ROOT / "channels" / "outreach" / "pipeline.json"
DEFAULT_DIR = REPO_ROOT / "channels" / "outreach" / "drafts"

# Not letters: the folder's own note.
IGNORED = {"README.md"}


def pipeline_rows(ledger: Path) -> list[dict]:
    """The prospect rows, whether the file is a bare list or wraps them."""
    data = json.loads(ledger.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    for key in ("prospects", "rows", "items"):
        rows = data.get(key)
        if isinstance(rows, list):
            return [r for r in rows if isinstance(r, dict)]
    return []


def named_drafts(rows: list[dict], repo_root: Path = REPO_ROOT) -> set[str]:
    """Every draft path any row claims, normalised to a repo-relative posix string.

    A row may name its draft as `draft`, as a list under `drafts`, or (older rows) as
    an absolute path under a different checkout. Absolute paths are re-based on this
    repository so the census compares like with like instead of reporting every old
    row as missing.
    """
    out: set[str] = set()
    for row in rows:
        for key in ("draft", "drafts"):
            val = row.get(key)
            vals = [val] if isinstance(val, str) else (val if isinstance(val, list) else [])
            for v in vals:
                if not isinstance(v, str) or not v.strip():
                    continue
                p = Path(v.strip())
                if p.is_absolute():
                    parts = p.parts
                    if "channels" in parts:
                        p = Path(*parts[parts.index("channels"):])
                    else:
                        continue
                out.add(p.as_posix())
    return out


def draft_files(drafts_dir: Path) -> list[Path]:
    if not drafts_dir.is_dir():
        return []
    return sorted(p for p in drafts_dir.glob("*.md") if p.name not in IGNORED)


def digest(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def census(ledger: Path = DEFAULT_LEDGER, drafts_dir: Path = DEFAULT_DIR,
           repo_root: Path = REPO_ROOT) -> dict:
    """The whole answer, as data, so the printer and the test read the same thing."""
    rows = pipeline_rows(ledger)
    named = named_drafts(rows, repo_root)
    files = draft_files(drafts_dir)

    on_disk: dict[str, Path] = {}
    for p in files:
        try:
            rel = p.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            rel = p.as_posix()
        on_disk[rel] = p

    # A row may name a path outside the drafts folder entirely: `channels/sent/...` is a
    # row that was fulfilled, not a row that lies. Those are counted apart from `missing`,
    # which is only ever a row that names a *draft* that is not on disk.
    try:
        staged_prefix = drafts_dir.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        staged_prefix = "channels/outreach/drafts"

    orphans = sorted(rel for rel in on_disk if rel not in named)
    elsewhere = sorted(rel for rel in named if not rel.startswith(staged_prefix))
    missing = sorted(rel for rel in named
                     if rel.startswith(staged_prefix) and rel not in on_disk)

    by_hash: dict[str, list[str]] = {}
    for rel, p in on_disk.items():
        by_hash.setdefault(digest(p), []).append(rel)
    duplicates = [
        {"md5": h, "paths": sorted(ps)}
        for h, ps in sorted(by_hash.items())
        if len(ps) > 1
    ]
    duplicates.sort(key=lambda d: d["paths"][0])

    return {
        "prospects": len(rows),
        "drafts_on_disk": len(on_disk),
        "named_by_a_row": len([r for r in on_disk if r in named]),
        "orphans": orphans,
        "missing": missing,
        "named_elsewhere": elsewhere,
        "duplicates": duplicates,
    }


def render(facts: dict, ledger: Path = DEFAULT_LEDGER,
           drafts_dir: Path = DEFAULT_DIR) -> str:
    lines = [
        "Outreach draft census — what is staged versus what the ledger can see",
        f"ledger: {ledger}",
        f"drafts: {drafts_dir}",
        "",
        f"{facts['prospects']} prospect row(s); {facts['drafts_on_disk']} draft(s) on disk; "
        f"{facts['named_by_a_row']} of those named by a row.",
    ]
    if facts["orphans"]:
        lines.append("")
        lines.append(f"STAGED, POINTED AT BY NOTHING ({len(facts['orphans'])}):")
        lines.append("  these cannot be sent through a drain or retired, because no record knows")
        lines.append("  they exist. The audit's 'staged' count is rows, not files.")
        lines += [f"  {p}" for p in facts["orphans"]]
    if facts["missing"]:
        lines.append("")
        lines.append(f"A ROW NAMES A DRAFT THAT IS NOT ON DISK ({len(facts['missing'])}):")
        lines += [f"  {p}" for p in facts["missing"]]
    if facts.get("named_elsewhere"):
        lines.append("")
        lines.append(f"ROW NAMES A FILE OUTSIDE THE STAGED FOLDER ({len(facts['named_elsewhere'])}):")
        lines.append("  fulfilled rows, not defects — listed so the count of 'drafts' can be read")
        lines += [f"  {p}" for p in facts["named_elsewhere"]]
    if facts["duplicates"]:
        lines.append("")
        lines.append(f"THE SAME LETTER, MORE THAN ONCE ({len(facts['duplicates'])} group(s)):")
        lines.append("  identical bytes under different names — a second send would break the")
        lines.append("  one-contact-per-venue discipline the letters themselves claim.")
        for d in facts["duplicates"]:
            lines.append(f"  md5 {d['md5']}")
            for p in d["paths"]:
                lines.append(f"    {p}")
    if not (facts["orphans"] or facts["missing"] or facts["duplicates"]):
        lines.append("")
        lines.append("clean: every draft is named by a row, every row has its draft, no duplicates.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    ap.add_argument("--drafts", default=str(DEFAULT_DIR))
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when a draft is orphaned or a letter is duplicated")
    args = ap.parse_args(argv)

    ledger, drafts_dir = Path(args.ledger), Path(args.drafts)
    # The repo root is derived from where the drafts live, not assumed to be the checkout
    # this file sits in: a fixture in a temp folder must count itself, or `--strict` fails
    # on a clean fixture because every file looks like an orphan.
    repo_root = drafts_dir.parents[2] if len(drafts_dir.parents) > 2 else REPO_ROOT
    facts = census(ledger, drafts_dir, repo_root)
    if args.json:
        print(json.dumps(facts, indent=2))
    else:
        print(render(facts, ledger, drafts_dir))
    if args.strict and (facts["orphans"] or facts["duplicates"] or facts["missing"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
