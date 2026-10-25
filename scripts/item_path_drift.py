#!/usr/bin/env python3
"""Which closed ledger items name files that are not on main — and which of those files merely moved.

Every review in the commons judges a claimed piece of work by asking one question: are the paths the
item names actually here? On 2026-10-25 that question was asked of five items in a row and answered
"absent" five times, which is a true answer and a misleading one: two of the files existed all along,
under a name the item did not use. `channels/outbound/<letter>.md` becomes `channels/sent/<letter>.md`
when `drain_outbox()` files it, and a gallery study moves into a per-amigo subdirectory when the wing
is reorganised. The work landed; the citation did not follow it.

So this separates the two things a missing path can mean:

  * **moved** — a file with the same basename exists elsewhere in the tree. The item is fine and the
    citation is stale. Nothing to review, one line to repair, and the repair belongs to the item's
    author, not to this script.
  * **absent** — nothing by that name is in the tree. That is the real question: either the work never
    landed, or it landed under a different name that nobody can guess.

It reads the ledger the way the ledger is written: append-only, several rows per id, and only the last
row for an id is the current state. Counting raw lines instead of ids is how an earlier census
reported 2671 items where there are 685.

    python3 scripts/item_path_drift.py                # summary, human-readable
    python3 scripts/item_path_drift.py --json         # machine-readable
    python3 scripts/item_path_drift.py --fail-on-absent   # exit 1 if any path is genuinely absent

Exit code 0 by default: this is a measurement, not a gate. The gate it is not is deliberate — a
stale citation should not block a landing, because blocking would make authors edit path strings
instead of doing work.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"

# Directories that are never a destination worth reporting, and walking them is slow and noisy.
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache"}


def load_items(path: Path = LEDGER) -> dict[str, dict]:
    """Latest row per id. The ledger is append-only, so a later row supersedes an earlier one."""
    latest: dict[str, dict] = {}
    with open(path, encoding="utf8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            item_id = rec.get("id")
            if item_id:
                latest[item_id] = rec
    return latest


def find_by_basename(root: Path, basename: str) -> list[str]:
    """Every path under `root` whose basename matches, relative to root, sorted for determinism."""
    hits: list[str] = []
    for p in root.rglob(basename):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        hits.append(str(rel))
    return sorted(hits)


def drift(items: dict[str, dict], root: Path = REPO) -> list[dict]:
    """One record per closed item that names at least one path not present in the tree.

    Each absent path is classified: `moved` if the same basename exists elsewhere, `absent` if it does
    not. An item where every missing path was found elsewhere is a citation repair; an item with any
    genuinely absent path is a review question.
    """
    out: list[dict] = []
    for item_id in sorted(items):
        rec = items[item_id]
        if rec.get("state") != "accomplished":
            continue
        missing = []
        for rel in rec.get("paths") or []:
            if (root / rel).exists():
                continue
            hits = find_by_basename(root, Path(rel).name)
            missing.append({
                "path": rel,
                "verdict": "moved" if hits else "absent",
                "found_at": hits[0] if hits else None,
                "other_locations": hits[1:],
            })
        if missing:
            out.append({
                "id": item_id,
                "author": rec.get("amigo"),
                "title": (rec.get("title") or "").strip(),
                "missing": missing,
                "needs_review": any(m["verdict"] == "absent" for m in missing),
            })
    return out


def summarise(records: list[dict]) -> dict:
    paths = [m for r in records for m in r["missing"]]
    moved = [m for m in paths if m["verdict"] == "moved"]
    return {
        "items_with_missing_paths": len(records),
        "items_needing_review": sum(1 for r in records if r["needs_review"]),
        "missing_path_citations": len(paths),
        "moved": len(moved),
        "absent": len(paths) - len(moved),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--fail-on-absent", action="store_true",
                    help="exit 1 if any named path is genuinely absent (not merely moved)")
    args = ap.parse_args(argv)

    items = load_items(Path(args.ledger))
    records = drift(items, Path(args.repo))
    counts = summarise(records)

    if args.json:
        print(json.dumps({"counts": counts, "closed_items": len(items), "records": records},
                         indent=2, sort_keys=True))
    else:
        print(f"closed items: {sum(1 for r in items.values() if r.get('state') == 'accomplished')}"
              f" of {len(items)} ids in the ledger")
        print(f"items naming a path that is not in the tree: {counts['items_with_missing_paths']}")
        print(f"  citations: {counts['missing_path_citations']}"
              f" — moved {counts['moved']}, genuinely absent {counts['absent']}")
        print(f"  items that are a citation repair only: "
              f"{counts['items_with_missing_paths'] - counts['items_needing_review']}")
        print(f"  items that need a reviewer: {counts['items_needing_review']}")
        for r in records:
            tag = "REVIEW " if r["needs_review"] else "moved  "
            print(f"\n{tag}{r['id']}  ({r['author'] or '?'})  {r['title'][:70]}")
            for m in r["missing"]:
                if m["verdict"] == "moved":
                    print(f"    {m['path']}  ->  {m['found_at']}")
                else:
                    print(f"    {m['path']}  (absent)")

    if args.fail_on_absent and counts["absent"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
