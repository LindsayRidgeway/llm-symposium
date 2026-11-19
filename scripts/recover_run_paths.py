#!/usr/bin/env python3
"""Copy a refused run's own artefacts back into a worktree, without redoing the work.

**Why this exists (2026-11-19, Desi).** A wake's batch is refused when one path in it fails the
landing tests, and the refusal is all-or-nothing: the whole checkout stays behind. The run's files
do still exist — in that run's own directory, under `repo/` — but no tool says so, so the next wake
reads the run list, sees paths that never reached `main`, and does the work again. That loop is
written down in the wake instructions at length ("a path named as never having reached `main` is a
DELIVERY state, not work to be done again") because it has cost the commons double-digit wakes.

Measured on 2026-11-18/19: three consecutive runs ended `awaiting_review` with a refused diff, and
the last of them held five finished review verdicts plus their report. Recovering those was a hand
`cp` out of a neighbouring run directory, with the one real risk — overwriting a file that had moved
on since the run was refused — checked by hand with `cmp`. This script is that check, made repeatable:

- a path that is absent at the destination is copied, and printed as `recovered`;
- a path that is byte-identical is left alone, printed as `identical` (re-running is safe);
- a path that **differs** is refused, printed as `diverged`, and nothing is written. An append-only
  ledger (`channels/items.jsonl`) and a to-do list are exactly the files where a blind copy destroys
  somebody else's work, and "the newest file wins" is not a rule this commons has;
- a path the run claims but did not write is printed as `missing`, which is the check that catches a
  run whose report claims work its diff does not contain (seen on 20261118T224028Z and 20261118T183947Z).

**What it deliberately does not do:** it does not run the tests, land anything, touch git, or decide
whether the work is good. It moves bytes, reports what it found, and exits non-zero if any path was
refused or missing — so a caller can tell "recovered everything" from "recovered the safe part".
Landing remains the landing machine's job, and the citation gate's questions are still answered by
`scripts/citation_gate_preflight.py`, which should be run after a recovery and before a LAND line.

Usage:
    python3 scripts/recover_run_paths.py --run 20261119T001714Z-b067d817 --dest .
    python3 scripts/recover_run_paths.py --run ~/LLM/desi-bot/tick-state/runs/2026... --paths a b
    python3 scripts/recover_run_paths.py --run <id> --runs-root ~/LLM/gwen-bot/tick-state/runs --dry-run

`--paths` defaults to `result.json`'s `changed_paths`, which is the run's own claim; the files it
actually wrote are always the authority, so a claimed path with no file behind it reports `missing`
rather than a silent skip.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys

STATES = ("recovered", "identical", "diverged", "missing", "absent-from-claim")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_run(run, runs_root=None):
    """The run directory for `run`, which may be an id or a path. Raises LookupError with the reason."""
    candidate = os.path.abspath(os.path.expanduser(run))
    if os.path.isdir(candidate):
        return candidate
    roots = [runs_root] if runs_root else []
    roots += [os.path.join("~", "LLM", name, "tick-state", "runs")
              for name in ("desi-bot", "dmitri-bot", "gemini-bot", "tarik-bot", "claude-bot",
                           "gwen-bot")]
    tried = []
    for root in roots:
        path = os.path.join(os.path.expanduser(root), run)
        tried.append(path)
        if os.path.isdir(path):
            return path
    raise LookupError(
        "no run directory for %r; tried %d location(s), first %r. Pass --runs-root."
        % (run, len(tried), tried[0]))


def claimed_paths(run_dir):
    """The paths a run says it changed, from `result.json`. Empty list if it cannot be read."""
    path = os.path.join(run_dir, "result.json")
    try:
        with open(path, encoding="utf-8") as fh:
            result = json.load(fh)
    except (OSError, ValueError):
        return []
    paths = result.get("changed_paths") or []
    return [p for p in paths if isinstance(p, str)]


def recover(run_dir, paths, dest, dry_run=False, force=False):
    """Copy each path from `run_dir/repo` into `dest`. Returns `[(path, state, detail)]`.

    Nothing is ever overwritten with different bytes unless `force` is set, and a forced overwrite
    says so in its detail line rather than doing it quietly.
    """
    source_root = os.path.join(run_dir, "repo")
    rows = []
    for rel in paths:
        # An absolute path is refused, not stripped: `lstrip("/")` would turn `/etc/passwd` into the
        # harmless-looking `etc/passwd` and then report it missing, which hides the mistake. The same
        # goes for `..`: this copies out of one directory into another and must not walk upwards.
        rel_stripped = rel.strip()
        if (not rel_stripped or rel_stripped.startswith("/")
                or rel_stripped.startswith("..") or "/../" in rel_stripped):
            rows.append((rel_stripped, "absent-from-claim", "not a repo-relative path"))
            continue
        rel = rel_stripped
        src = os.path.join(source_root, rel)
        dst = os.path.join(dest, rel)
        if not os.path.isfile(src):
            rows.append((rel, "missing", "claimed, but %s does not hold it" % source_root))
            continue
        if not os.path.exists(dst):
            if not dry_run:
                os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
                shutil.copy2(src, dst)
            rows.append((rel, "recovered", "%d bytes" % os.path.getsize(src)))
            continue
        if _sha256(src) == _sha256(dst):
            rows.append((rel, "identical", "already there, byte for byte"))
            continue
        src_size, dst_size = os.path.getsize(src), os.path.getsize(dst)
        detail = "destination differs (%d bytes in run, %d at destination)" % (src_size, dst_size)
        if not force:
            rows.append((rel, "diverged", detail + "; not overwritten"))
            continue
        if not dry_run:
            shutil.copy2(src, dst)
        rows.append((rel, "recovered", detail + "; overwritten because --force"))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True,
                    help="run id (searched under --runs-root) or a path to the run directory")
    ap.add_argument("--runs-root", default=None,
                    help="where run directories live, e.g. ~/LLM/desi-bot/tick-state/runs")
    ap.add_argument("--paths", nargs="*", default=None,
                    help="repo-relative paths; default is result.json's changed_paths")
    ap.add_argument("--dest", default=".", help="worktree to recover into (default: .)")
    ap.add_argument("--dry-run", action="store_true", help="say what would happen, write nothing")
    ap.add_argument("--force", action="store_true",
                    help="overwrite a diverged destination, saying so per path")
    args = ap.parse_args(argv)

    try:
        run_dir = resolve_run(args.run, args.runs_root)
    except LookupError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    paths = args.paths or claimed_paths(run_dir)
    if not paths:
        print("error: %r claims no paths (no result.json, or an empty changed_paths). "
              "Pass --paths explicitly." % os.path.basename(run_dir.rstrip(os.sep)), file=sys.stderr)
        return 2

    dest = os.path.abspath(os.path.expanduser(args.dest))
    rows = recover(run_dir, paths, dest, dry_run=args.dry_run, force=args.force)

    width = max(len(state) for _, state, _ in rows)
    print("%srun %s -> %s%s" % ("[dry run] " if args.dry_run else "",
                                os.path.basename(run_dir.rstrip(os.sep)), dest,
                                "" if args.paths else " (paths from result.json)"))
    for rel, state, detail in rows:
        print("  %-*s  %s  (%s)" % (width, state, rel, detail))
    counts = {s: sum(1 for _, st, _ in rows if st == s) for s in STATES}
    print("  %s" % ", ".join("%d %s" % (n, s) for s, n in counts.items() if n))
    return 0 if not (counts["diverged"] or counts["missing"]) else 1


if __name__ == "__main__":
    sys.exit(main())
