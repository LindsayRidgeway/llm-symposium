#!/usr/bin/env python3
"""Verdicts the commons paid for and then threw away — named, and where possible recovered.

Why this exists (2026-11-10, Desi). A reading verdict survives in exactly one place: its mirror file in
`channels/ledger-verdicts/`. `channels/items.jsonl` is rebuilt by folding those mirrors in, so an
unfolded mirror is not a partial record — it is no record. On 2026-11-10 two of Gemini's mirrors were
found to be on no branch at all: the wake had written them, its report's LAND line named them, the
landing gate refused the run for an unrelated reason, and `replay` therefore had nothing to fold. Both
items it had read stayed in the never-read pile, so the queue paid for the same read twice.

Nothing detected that case. `python3 channels/item_ledger.py --reading-queue <amigo>` sees only the
mirrors that are already on disk, so a mirror that never landed is invisible to every queue in the
repository — invisible is worse than late, because nobody can even count it. This is the count.

The four states, because they are different facts and only the fourth needs a human:

* ON MAIN     the named mirror is in the checkout. Nothing to do.
* RECOVERABLE the mirror is absent from the checkout but its full text is inside that run's own
              `changes.patch` (the diff the lander refused). The reading was done and the bytes still
              exist. `--recover` writes them, verbatim, into `channels/ledger-verdicts/`. It does not
              fold them into items.jsonl: that is `item_ledger.py --collect`/`replay`'s job, and a
              transcript is not a fold.
* LOST        the mirror is absent from the checkout and its bytes are nowhere on this machine. The
              reading is gone. This is the one that must be reported, because the only honest repair
              is that the item returns to the reading queue rather than being counted as read.
* PATCHED-OTHER  a mirror of the same id landed under a different timestamp prefix (a later run
              re-mirrored the same verdict). Not a loss; said so that it is not read as one.

The scope is the run directories on this machine, not the git history: a mirror could also exist on a
review branch that this checkout cannot see. That limit is real and stated — `--recover` never
overwrites a file that already exists, so running this from a stale clone cannot destroy the better copy.

Usage:
    python3 scripts/lost_verdict_check.py                 # report, exit 0
    python3 scripts/lost_verdict_check.py --strict        # exit 1 if anything is LOST
    python3 scripts/lost_verdict_check.py --recover       # write RECOVERABLE mirrors into the checkout
    python3 scripts/lost_verdict_check.py --json
    python3 scripts/lost_verdict_check.py --bots-root /tmp/fixture
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_BOTS_ROOT = Path.home() / "LLM"
VERDICT_DIR = "channels/ledger-verdicts"

# A named mirror is either in a LAND line or in the prose beside it; both are the run claiming the
# file exists, which is exactly the claim this checks. Trailing punctuation is stripped by the regex.
VERDICT_PATH_RE = re.compile(re.escape(VERDICT_DIR) + r"/[A-Za-z0-9_.\-]+\.json")
MIRROR_STEM_RE = re.compile(r"^(\d{8}T\d{6}Z)-(.+)\.json$")


def verdict_paths_in(text: str) -> list[str]:
    """Every verdict-mirror path the text names, in first-seen order, without duplicates."""
    seen: list[str] = []
    for m in VERDICT_PATH_RE.finditer(text):
        if m.group(0) not in seen:
            seen.append(m.group(0))
    return seen


def new_files_in_patch(patch: str) -> dict[str, str]:
    """The files a unified diff *creates*, path -> full text.

    Only creations are returned, on purpose. A modified file's new content requires applying the hunk
    to a base that may no longer exist, and guessing at that is how a recovery silently becomes an
    invention. A new mirror file has no base, so its text is the hunk's `+` lines and nothing else.
    """
    out: dict[str, str] = {}
    path = None
    in_new = False
    body: list[str] = []
    in_hunk = False
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            if path is not None and in_new:
                out[path] = "\n".join(body) + ("\n" if body else "")
            path, in_new, body, in_hunk = None, False, [], False
            # `diff --git a/x b/x`; the b-side is what the file is called after the patch.
            parts = line.split(" b/", 1)
            if len(parts) == 2:
                path = parts[1].strip()
            continue
        if path is None:
            continue
        if line.startswith("new file mode"):
            in_new = True
            continue
        if line.startswith("@@"):
            in_hunk = True
            continue
        if in_new and in_hunk:
            if line.startswith("+"):
                body.append(line[1:])
            elif line.startswith("\\"):  # "\ No newline at end of file"
                continue
    if path is not None and in_new:
        out[path] = "\n".join(body) + ("\n" if body else "")
    return out


def mirror_item_id(path: str) -> str | None:
    """The item a mirror is about: its filename minus the stamp of the run that mirrored it.

    The remainder is the item id itself, and it is not always one stamp plus a hash — Codex mirrors
    are named `<stamp>-codex-<item>.json` — so the id is taken as everything after the first stamp
    rather than rebuilt from groups. Getting this wrong is not cosmetic: `PATCHED-OTHER` matches on
    the id, so a truncated id makes two different readings look like one.
    """
    m = MIRROR_STEM_RE.match(Path(path).name)
    return m.group(2) if m else None


def local_mirrors_landed(repo: Path) -> dict[str, str]:
    """item id -> mirror path, for every mirror already in the checkout (any timestamp prefix)."""
    d = repo / VERDICT_DIR
    out: dict[str, str] = {}
    if not d.is_dir():
        return out
    for p in sorted(d.glob("*.json")):
        item_id = mirror_item_id(p.name)
        if item_id:
            out.setdefault(item_id, f"{VERDICT_DIR}/{p.name}")
    return out


def scan(bots_root: Path = DEFAULT_BOTS_ROOT, repo: Path = REPO) -> list[dict]:
    """One row per (run, named mirror): where that mirror actually is."""
    landed_ids = local_mirrors_landed(repo)
    rows: list[dict] = []
    for bot_dir in sorted(bots_root.glob("*-bot")):
        runs_dir = bot_dir / "tick-state" / "runs"
        if not runs_dir.is_dir():
            continue
        for run_dir in sorted(runs_dir.iterdir()):
            report = run_dir / "report.txt"
            if not report.is_file():
                continue
            try:
                text = report.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            named = verdict_paths_in(text)
            if not named:
                continue
            patch_files: dict[str, str] | None = None
            for path in named:
                item_id = mirror_item_id(path)
                row = {
                    "amigo": bot_dir.name[:-4],
                    "run": run_dir.name,
                    "path": path,
                    "item_id": item_id,
                }
                target = repo / path
                if target.is_file():
                    row["state"] = "ON MAIN"
                else:
                    if patch_files is None:
                        patch = run_dir / "changes.patch"
                        patch_files = (
                            new_files_in_patch(patch.read_text(encoding="utf-8", errors="replace"))
                            if patch.is_file()
                            else {}
                        )
                    if path in patch_files and patch_files[path].strip():
                        row["state"] = "RECOVERABLE"
                        row["content"] = patch_files[path]
                        if item_id and item_id in landed_ids:
                            row["state"] = "PATCHED-OTHER"
                            row["on_main_as"] = landed_ids[item_id]
                    elif item_id and item_id in landed_ids:
                        row["state"] = "PATCHED-OTHER"
                        row["on_main_as"] = landed_ids[item_id]
                    else:
                        row["state"] = "LOST"
                rows.append(row)
    return rows


def recover(rows: list[dict], repo: Path = REPO) -> tuple[list[str], list[str]]:
    """Write RECOVERABLE mirrors into the checkout, never overwriting an existing file.

    One mirror per item id: if two refused runs each left a mirror for the same item, the later one
    is written and the earlier is reported as superseded. Two mirrors for one item id is not two
    verdicts — it is the same verdict written twice — and folding both would put two rows where the
    commons has one reading.

    Returns (written, superseded).
    """
    newest: dict[str, dict] = {}
    for row in rows:
        if row["state"] != "RECOVERABLE":
            continue
        key = row["item_id"] or row["path"]
        # The path's own timestamp prefix is the run's own stamp; the newer mirror wins.
        prev = newest.get(key)
        if prev is None or row["path"] > prev["path"]:
            newest[key] = row
    written: list[str] = []
    superseded: list[str] = []
    for row in rows:
        if row["state"] != "RECOVERABLE":
            continue
        key = row["item_id"] or row["path"]
        if newest[key] is not row:
            superseded.append(row["path"])
            continue
        target = repo / row["path"]
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(row["content"], encoding="utf-8")
        written.append(row["path"])
    return written, superseded


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bots-root", default=str(DEFAULT_BOTS_ROOT),
                    help="directory holding <amigo>-bot/tick-state/runs (default ~/LLM)")
    ap.add_argument("--repo", default=str(REPO), help="checkout to check against")
    ap.add_argument("--recover", action="store_true",
                    help="write mirrors whose text survives only in a run's changes.patch")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any mirror is LOST")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    bots_root = Path(args.bots_root).expanduser()
    repo = Path(args.repo).resolve()
    rows = scan(bots_root, repo)
    written, superseded = recover(rows, repo) if args.recover else ([], [])

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["state"]] = counts.get(row["state"], 0) + 1

    if args.json:
        print(json.dumps({"counts": counts, "recovered": written, "superseded": superseded,
                          "rows": [{k: v for k, v in r.items() if k != "content"} for r in rows]},
                         indent=1))
    else:
        print(f"lost_verdict_check: {len(rows)} verdict-mirror claim(s) named by a run's report, "
              f"checked against {repo}")
        for state in ("LOST", "RECOVERABLE", "PATCHED-OTHER", "ON MAIN"):
            if counts.get(state):
                print(f"  {state:<14} {counts[state]}")
        for state in ("LOST", "RECOVERABLE"):
            hits = [r for r in rows if r["state"] == state]
            if not hits:
                continue
            print(f"\n{state}:")
            for r in hits:
                print(f"  {r['amigo']}/{r['run']}  item {r['item_id']}  {r['path']}")
        if written:
            print(f"\nrecovered {len(written)} mirror(s) from a refused run's own diff:")
            for p in written:
                print(f"  {p}")
            if superseded:
                print(f"  {len(superseded)} older mirror(s) for the same item left alone "
                      f"(one verdict, written twice):")
                for p in superseded:
                    print(f"    {p}")
            print("  — now fold them: python3 channels/item_ledger.py --collect")
        if not rows:
            print("  no run report on this machine names a verdict mirror")
        print("\nNot checked: branches this checkout cannot see. A mirror that is on a review branch "
              "and not here will read as LOST or RECOVERABLE; --recover never overwrites.")

    if args.strict and counts.get("LOST"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
