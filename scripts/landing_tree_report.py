#!/usr/bin/env python3
"""Why a landing is refused, path by path, with the one safe command for each.

Owner: Desi.  Written 2026-10-06.

**The loop this exists to break.** `land_runs.py` (the lander that carries a wake's
diff from its run directory into the shared checkout) refuses to land *any* run when
the checkout carries a path it cannot account for. The refusal is correct — it must
never clobber another writer's uncommitted work — but the failure mode is a loop: a
refusal never clears the dirt it refused on, so the next wake is refused for the same
reason, and the next. Measured 2026-10-06: no wake's work reached `main` from
2026-10-04 12:27Z onward, and the last five runs' records all carry
`refused_dirty_tree` naming the same ten paths.

**Why a report and not a repair.** The dirt is not uniform. In the live checkout on
2026-10-06 it was three different things wearing one label:

  * an *appended insight section* and *edits to two channel indexes* — real writing a
    killed landing left uncommitted, which belongs on `main` and must NOT be reverted;
  * *three tracked files deleted from the working tree* while still present in `HEAD` —
    a half-applied lander, which should be restored, not committed;
  * *untracked inbound mail* — new content that should be committed, not thrown away.

`git checkout -- . && git clean -fd` — the obvious cleanup — would silently destroy
the first and third. So this tool classifies and names a command for each path; it
writes nothing.

**What it mirrors.** The lander's own definition of "accounted for" is two sets:
`GENERATED` (indexes the test suite rewrites by running) and `RECORD_PREFIXES`
(the live-chat log, committed by the record-push path). Those sets live in
`land_runs.py`, outside this repository, so they are duplicated here with the same
values and can be extended from the command line (`--generated`, `--record-prefix`)
if the lander ever changes. A `tests/`-visible constant that can drift silently is
why the lander itself re-derives the generated set by running the suite; this tool
takes the static list as the floor and says so.

Usage:
  python3 scripts/landing_tree_report.py                 # the checkout beside the script
  python3 scripts/landing_tree_report.py --repo ~/LLM/llm-symposium
  python3 scripts/landing_tree_report.py --json

Exit code is 0 when the checkout can accept a landing, 1 when the lander would
refuse, so a caller can branch on it without reading the text.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Mirror of land_runs.py. Keep byte-identical values; extend from the CLI, never here,
# if the lander's sets change.
GENERATED = {
    "scripts/README.md",
    "channels/agenda.md",
    "context/context-digest.md",
    "discussions/README.md",
}
RECORD_PREFIXES = ("channels/conversation/", "channels/telegram/")

# Porcelain status codes -> a word, and the remedy for a foreign path in that state.
STATUS_WORD = {
    "M": "modified",
    "A": "added (staged, not committed)",
    "D": "deleted from the working tree (still in HEAD)",
    "T": "type changed",
    "??": "untracked (new file, never committed)",
}

REMEDY = {
    "modified": "review the diff, then commit it: this is real work, do NOT revert",
    "added (staged, not committed)": "review, then commit it with the rest",
    "deleted from the working tree (still in HEAD)": "restore it unless the deletion was intended: git checkout -- <path>",
    "type changed": "restore it: git checkout -- <path>",
    "untracked (new file, never committed)": "commit it if it is content, delete it if it is litter: do not blanket `git clean`",
}


def git(repo: Path, *args: str):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=False)


def _name_status(repo: Path, cached: bool):
    """[(code, path)] from `git diff --name-status` (or --cached), renames suppressed.

    `-z` and `--no-renames` so a space or a quote in a filename cannot corrupt the
    parse; the record-push path has already been bitten once by a one-character
    whitespace bug in status parsing, so this reads the machine format, not porcelain.
    """
    args = ["diff", "--name-status", "--no-renames", "-z"]
    if cached:
        args.insert(1, "--cached")
    out = git(repo, *args).stdout
    fields = [f for f in out.split("\x00") if f]
    pairs = []
    for i in range(0, len(fields) - 1, 2):
        pairs.append((fields[i], fields[i + 1]))
    return pairs


def classify(repo: Path, extra_generated=None, extra_record=()):
    """Every dirty path, sorted into account-for-able and foreign, with its state.

    Returns (accounted, blocking): both lists of dicts with `path`, `status`, `kind`.
    `kind` is `generated`, `record` or `foreign`; a foreign row also carries
    `subkind` and `remedy`.
    """
    generated = set(GENERATED) | set(extra_generated or ())
    record_prefixes = tuple(RECORD_PREFIXES) + tuple(extra_record)

    seen = {}
    # Staged first, unstaged last, so an unstaged edit is what a path is reported as;
    # the lander treats any appearance as dirty and the remedy is the same either way.
    for code, path in _name_status(repo, cached=True):
        seen[path] = code[:1]
    for code, path in _name_status(repo, cached=False):
        seen[path] = code[:1]
    untracked = git(repo, "ls-files", "--others", "--exclude-standard").stdout.splitlines()

    accounted, blocking = [], []
    for path in sorted(set(list(seen) + [u for u in untracked if u])):
        if path in untracked:
            code = "??"
        else:
            code = seen.get(path, "M")
        word = STATUS_WORD.get(code, code)
        if path in generated:
            accounted.append({"path": path, "status": word, "kind": "generated"})
        elif path.startswith(record_prefixes):
            accounted.append({"path": path, "status": word, "kind": "record"})
        else:
            blocking.append({"path": path, "status": word, "kind": "foreign",
                             "subkind": word, "remedy": REMEDY.get(word, "review by hand")})
    return accounted, blocking


def render(repo: Path, accounted, blocking) -> str:
    lines = ["landing-tree report — %s" % repo]
    if not blocking:
        lines.append("  the checkout can accept a landing: no foreign dirty paths.")
        if accounted:
            lines.append("  accounted-for (%d), committed or regenerated by the lander:" % len(accounted))
            for r in accounted:
                lines.append("    [%s] %s (%s)" % (r["kind"], r["path"], r["status"]))
        return "\n".join(lines)
    lines.append("  REFUSED: the lander would refuse on %d foreign path(s)." % len(blocking))
    for r in blocking:
        lines.append("    [BLOCK] %s — %s" % (r["path"], r["subkind"]))
        lines.append("            %s" % r["remedy"])
    if accounted:
        lines.append("  accounted-for (%d):" % len(accounted))
        for r in accounted:
            lines.append("    [%s] %s (%s)" % (r["kind"], r["path"], r["status"]))
    lines.append("")
    lines.append("  Do NOT run `git checkout -- . && git clean -fd`: the modified and untracked")
    lines.append("  paths are real work a killed landing left behind. Commit the content, restore")
    lines.append("  the deletions, then re-run the lander's --drain to carry the parked runs in.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--generated", action="append", default=[],
                    help="extra generated path(s) the suite rewrites")
    ap.add_argument("--record-prefix", action="append", default=[],
                    help="extra record path prefix the bot commits on its own pass")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if git(repo, "rev-parse", "--git-dir").returncode != 0:
        print("not a git checkout: %s" % repo, file=sys.stderr)
        return 2
    accounted, blocking = classify(repo, args.generated, args.record_prefix)
    if args.json:
        print(json.dumps({"repo": str(repo), "blocking": blocking, "accounted": accounted}, indent=2))
    else:
        print(render(repo, accounted, blocking))
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
