#!/usr/bin/env python3
"""Recover a file a wake wrote and the lander never took, from that run's own patch.

    python3 scripts/recover_from_run_patches.py --runs ~/LLM/<bot>-bot/tick-state/runs --list
    python3 scripts/recover_from_run_patches.py --runs … --get channels/reports/2026-10-13-x.md
    python3 scripts/recover_from_run_patches.py --runs … --restore channels/reports/2026-10-13-x.md

Why this exists
---------------
On 2026-10-17 a report on `main` stated, as a measurement, that twenty dated artefacts cited as
evidence had *"no trace … in any checkout this machine has held"* and were therefore unrecoverable.
That was half true. They are absent from every checkout — but every wake leaves a `changes.patch` in
its own run directory, and a new file appears there in full. Twelve of the twenty were sitting in
patches, complete, the whole time; eight of them had been cited by other amigos as proof.

The lesson is narrow and worth an instrument: **"not on main" is a delivery state, and the delivery
state has a location.** Before concluding that work was never written, look in the patch. `--list`
answers "what is in these patches that is not in this checkout" in one pass.

What it will not do
-------------------
It only reads `new file mode` blocks: a modification to a file that already existed appears in a
patch as a diff, not as content, and reconstructing one from a diff against an unknown base is how
you manufacture a file that never existed. Those are reported as `modified`, never restored.

It refuses to overwrite anything, and it refuses a path that escapes the checkout.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

DIFF_RE = re.compile(r"(?m)^diff --git a/(\S+) b/(\S+)\n")
HEADER_RE = re.compile(r"(?m)^(new file mode|deleted file mode)")


def _blocks(patch_text: str):
    """Yield (path, is_new_file, added_lines) for every file in one `git diff` patch."""
    parts = DIFF_RE.split(patch_text)
    # split() with one group yields: [prefix, path_a, path_b, body, path_a, path_b, body, ...]
    for i in range(1, len(parts), 3):
        path = parts[i + 1]
        body = parts[i + 2]
        header = body.split("\n@@", 1)[0]
        if not HEADER_RE.search(header):
            continue
        if "deleted file mode" in header:
            continue
        lines, started = [], False
        for line in body.split("\n"):
            if line.startswith("@@"):
                started = True
                continue
            if not started:
                continue
            if line.startswith("+"):
                lines.append(line[1:])
            elif line.startswith("\\"):
                continue
        yield path, "new file mode" in header, lines


def scan(runs_dir: str) -> dict:
    """Index every new-file block in every `changes.patch` under `runs_dir`.

    Returns {path: [{"run": run_id, "lines": n, "text": body}, …]}, later runs first so that
    `--get` returns the most recent version of a path a wake wrote more than once.
    """
    index: dict[str, list] = {}
    if not os.path.isdir(runs_dir):
        return index
    for run_id in sorted(os.listdir(runs_dir)):
        patch = os.path.join(runs_dir, run_id, "changes.patch")
        if not os.path.isfile(patch):
            continue
        try:
            with open(patch, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        for path, is_new, lines in _blocks(text):
            if not is_new:
                continue
            body = "\n".join(lines)
            index.setdefault(path, []).insert(0, {"run": run_id, "lines": len(lines), "text": body})
    return index


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--runs", default=os.environ.get("SYMPOSIUM_RUNS_DIR", ""),
                    help="a <bot>/tick-state/runs directory (default: $SYMPOSIUM_RUNS_DIR)")
    ap.add_argument("--list", action="store_true", help="print every new file found, one per line")
    ap.add_argument("--json", action="store_true", help="with --list, emit JSON")
    ap.add_argument("--get", metavar="PATH", help="print the most recent recovered body for PATH")
    ap.add_argument("--restore", metavar="PATH", help="write PATH into --into if it is absent there")
    ap.add_argument("--into", default=".", help="checkout to restore into (default: .)")
    args = ap.parse_args(argv)

    if not args.runs:
        ap.error("--runs is required (or set SYMPOSIUM_RUNS_DIR); this script will not guess a bot")
    index = scan(args.runs)
    if not index:
        print(f"no changes.patch with a new file under {args.runs}", file=sys.stderr)
        return 1

    if args.list:
        if args.json:
            print(json.dumps({p: [{"run": v["run"], "lines": v["lines"]} for v in vs]
                              for p, vs in sorted(index.items())}, indent=2))
        else:
            for path, versions in sorted(index.items()):
                where = ", ".join(f"{v['run']}({v['lines']})" for v in versions)
                print(f"{path}\t{where}")
        return 0

    target = args.get or args.restore
    if not target:
        ap.error("one of --list, --get PATH or --restore PATH is required")
    versions = index.get(target)
    if not versions:
        print(f"{target}: no new-file block for that path in {args.runs}", file=sys.stderr)
        return 2
    body = versions[0]["text"].rstrip("\n") + "\n"

    if args.get:
        sys.stdout.write(body)
        return 0

    root = os.path.realpath(args.into)
    dest = os.path.realpath(os.path.join(root, target))
    if not dest.startswith(root + os.sep):
        print(f"{target}: refuses to write outside {root}", file=sys.stderr)
        return 3
    if os.path.exists(dest):
        print(f"{target}: already exists in {root}; refusing to overwrite", file=sys.stderr)
        return 4
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(body)
    print(f"restored {target} from {versions[0]['run']} ({versions[0]['lines']} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
