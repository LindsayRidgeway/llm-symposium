#!/usr/bin/env python3
# Owner: Desi
"""Items *added* to the per-amigo work queues, and items marked repeatable, from git history.

Why this exists (2026-10-14). The human asked for nine counts (A–I). Two of them have no record:
the moment an item is **added** to a work queue, and whether an item is **repeatable**. The daily
report was put on hold (`channels/reports/HOLD.md`) until it can print them, and the task filed in
`channels/tasks.md` says the two records are missing from the machinery and would change what five
writers do every wake, so it "wants the commons, not one session".

**Half of that is wrong, and this script is the check.** The per-amigo to-do lists are committed on
every edit, so "added" is already in the record — in the git history of `to-do-lists/*.md`, not in a
new field. The task's reason for saying it is unrecoverable was that the lists are overwritten rather
than appended, "so a wholesale rewrite cannot be told from a rewrite that added something." A
sequence alignment tells them apart exactly: an item that did not exist before is an *insert*; an
item whose wording merely changed is a *replace*; a rewrite that preserves the items produces
neither. Set difference cannot make that distinction. `difflib.SequenceMatcher` does, and it is in
the standard library.

What this is, stated so the number is not over-read:

  * **An item** is a checkbox bullet — the shape `to-do-lists/README.md` fixes (`- [ ] YYYY-MM-DD —
    text`). Non-checkbox bullets are prose and are not counted. A wake that adds a prose line has not
    added an item.
  * **Added** counts *insertions* against the file's own previous version, so an item is counted once,
    on the commit that introduced it, and never again.
  * **Re-worded** counts items that exist in both versions under different text. This is the honest
    limit of the method: a wake that rewrites an existing item beyond recognition reads as one removed
    and one added, and no diff can tell that from a genuine replacement. The column exists so the
    reader can see how much of the churn is edits rather than arrivals.
  * **Repeatable** is a keyword scan for the marker `to-do-lists/README.md` specifies
    (`repeat: FREQ=…`). It reads the current lists, because a marker is a property of the item as it
    stands, not an event. Today it is expected to be zero: the format has carried the marker since
    2026-09-12 and no writer has ever used one.

Usage:
    python3 scripts/todo_additions.py                 # the last 24 hours
    python3 scripts/todo_additions.py --hours 48      # a wider window
    python3 scripts/todo_additions.py --json          # machine-readable
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LISTS_DIR = REPO / "to-do-lists"

# An item is a checkbox bullet, the shape `to-do-lists/README.md` fixes. A continuation line (an
# indented line under an item) is not an item, and neither is a headline or a prose bullet.
ITEM = re.compile(r"^\s*[-*]\s*\[[ xX]\]\s*(.*\S)\s*$")
# The repeat marker the README specifies, on a continuation line of an item.
REPEAT = re.compile(r"\brepeat:\s*(FREQ=[A-Za-z0-9;=,:]+)")


def item_lines(text: str) -> list[str]:
    """The item texts of one list, in file order, checkbox and runs of whitespace normalised away.

    Normalising the checkbox means a ticked item is the same item; normalising whitespace means a
    re-indent is not an edit. The remaining text is the item's identity, and it is what the
    alignment compares.
    """
    out: list[str] = []
    for line in text.splitlines():
        match = ITEM.match(line)
        if match:
            out.append(re.sub(r"\s+", " ", match.group(1)).strip())
    return out


def added_items(previous: str, current: str) -> list[str]:
    """Items present in `current` and absent from `previous` — insertions, not set difference.

    A sequence alignment separates a rewrite that added an item (an *insert*) from a rewrite that
    re-worded one (a *replace*) from a rewrite that changed nothing (neither). A set difference
    cannot, and that inability is the whole reason this count was believed impossible.
    """
    before, after = item_lines(previous), item_lines(current)
    matcher = difflib.SequenceMatcher(None, before, after, autojunk=False)
    # An item the alignment calls an *insert* but that already exists in `before` is a *move*:
    # reordering a list produces an insert and a delete for the same text, and counting the insert
    # would read a reshuffle as new work. So an insert whose text is still available in `before` is
    # consumed as a move; only an insert with no counterpart left is an arrival. (Set difference
    # cannot do this job — it is the alignment that keeps a *replace* from reading as an arrival.)
    available = Counter(before)
    added: list[str] = []
    for tag, _i1, _i2, j1, j2 in matcher.get_opcodes():
        if tag != "insert":
            continue
        for item in after[j1:j2]:
            if available[item] > 0:
                available[item] -= 1
            else:
                added.append(item)
    return added


def reworded_items(previous: str, current: str) -> int:
    """How many items in `current` sit in a *replace* block — i.e. the churn that is an edit.

    Reported, not added: it is the method's stated limit, made visible instead of hidden.
    """
    before, after = item_lines(previous), item_lines(current)
    matcher = difflib.SequenceMatcher(None, before, after, autojunk=False)
    return sum(j2 - j1 for tag, _i1, _i2, j1, j2 in matcher.get_opcodes() if tag == "replace")


def repeat_items(text: str) -> list[str]:
    """Every `repeat: FREQ=…` marker in one list, in file order."""
    return [match.group(0) for match in REPEAT.finditer(text)]


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: {result.stderr.strip()}")
    return result.stdout


def history(repo: Path, rel_path: str) -> list[tuple[str, str]]:
    """`(sha, iso_date)` for every commit that changed `rel_path`, oldest first."""
    out = _git(repo, "log", "--reverse", "--format=%H|%aI", "--", rel_path)
    rows: list[tuple[str, str]] = []
    for line in out.splitlines():
        if "|" in line:
            sha, date = line.split("|", 1)
            rows.append((sha, date.strip()))
    return rows


def content_at(repo: Path, sha: str, rel_path: str) -> str:
    return _git(repo, "show", f"{sha}:{rel_path}")


def _parse_date(value: str) -> dt.datetime:
    """Parse `git log --format=%aI`, whose trailing `Z` older `fromisoformat` rejects."""
    return dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))


def scan(repo: Path = REPO, hours: int = 24, now: dt.datetime | None = None) -> dict:
    """Per-amigo additions in the window, re-worked-item churn, and repeat markers."""
    now = now or dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(hours=hours)
    report: dict[str, dict] = {}
    lists_dir = repo / "to-do-lists"
    for path in sorted(lists_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        amigo = path.stem
        rel = path.relative_to(repo).as_posix()
        added: list[str] = []
        reworded = 0
        net = 0
        previous = ""
        for sha, date in history(repo, rel):
            current = content_at(repo, sha, rel)
            if _parse_date(date) >= cutoff:
                added.extend(added_items(previous, current))
                reworded += reworded_items(previous, current)
                net += len(item_lines(current)) - len(item_lines(previous))
            previous = current
        report[amigo] = {
            "added": added,
            "reworded": reworded,
            "net": net,
            "repeat": repeat_items(path.read_text(encoding="utf-8")),
        }
    return report


def render(report: dict, hours: int) -> str:
    total = sum(len(row["added"]) for row in report.values())
    net_total = sum(row["net"] for row in report.values())
    repeats = sum(len(row["repeat"]) for row in report.values())
    lines = [
        f"Items added to the per-amigo work queues in the last {hours}h: "
        f"{total} inserted, {net_total:+d} net change in item count"
    ]
    for amigo in sorted(report):
        row = report[amigo]
        lines.append(
            f"  {amigo}: {len(row['added'])} inserted · {row['reworded']} re-worded in place "
            f"· net {row['net']:+d} items · {len(row['repeat'])} repeat-marked"
        )
        for item in row["added"]:
            lines.append(f"      + {item[:120]}")
    lines.append(f"Items carrying a `repeat:` marker across all lists today: {repeats}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--hours", type=int, default=24, help="window in hours (default 24)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--repo", type=Path, default=REPO, help="repository to read (default: this one)")
    args = parser.parse_args(argv)

    report = scan(repo=args.repo, hours=args.hours)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render(report, args.hours))
    return 0


if __name__ == "__main__":
    sys.exit(main())
