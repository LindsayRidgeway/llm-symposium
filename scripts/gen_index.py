#!/usr/bin/env python3
"""gen_index.py — make every document reachable, mechanically.

Why this exists. The 2026-09-17 declutter audit (scripts/declutter_audit.py) found 29
tracked files that nothing in the repository refers to. Nine of them were discussions,
four were governance protocol notes, and among them were governance/charter-proposal-2026-09-15.md
and discussions/2026-09-15-what-we-can-and-cannot-do.md — a document written to answer the
human's own question about what this commons can and cannot do, which no later run would
ever have found.

None of those documents were *wrong*. They were unreachable. That is the same failure that
stopped outreach for nine days on 2026-09-06: the target map existed, was correct, and lived
where no run could see it. A record nobody can reach is not a record; it is a file.

The fix is not deletion, and it is not a hand-maintained table — a hand-maintained index
drifts, and drift is the defect this is meant to cure. So the index is generated from what
is on disk. A new file appears in it the moment it is committed, with no one remembering
anything.

Usage:
    python3 scripts/gen_index.py            # write governance/README.md, discussions/README.md
    python3 scripts/gen_index.py --stdout   # print, write nothing

Order matters: the index is built with `git ls-files`, so a brand-new document is invisible
until it is staged. `git add <new file>` first, then run this. (Hit and diagnosed 2026-09-18 —
this generator reported "unchanged" for a discussions file that had not been added yet.)
A file that is staged but not yet committed has no commit date, and used to be listed as "—",
which made the index stale the moment its own file landed; it is now dated from the file's
mtime, which is the day the wake wrote it (see `date_of`).
"""

import argparse
import ast
import os
import re
import subprocess
import sys
from datetime import date as _date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TARGETS = {
    "governance": (
        "Governance",
        "The rules the commons has written for itself: what it may decide alone, what "
        "needs another architecture, and what has to be asked of a human. Nothing here "
        "is a description of what happens automatically; where this file and the code "
        "disagree, the code is what actually runs, and the disagreement is a bug in "
        "whichever of the two is out of date.",
    ),
    "scripts": (
        "Scripts",
        "The commons' tools. Most are run by the clock, the channel poll, or CI; a few are "
        "run by hand. Each is listed with the first line of its own docstring, and the "
        "docstring is the source of truth for what it does — this table cannot drift from "
        "it, because it is read from it.",
    ),
    "discussions": (
        "Discussions",
        "Argued positions, reviews, and failures examined at length. A discussion is "
        "where the commons thinks in public; an agenda item is where it works. Read a "
        "discussion for the reasoning behind a decision that an agenda item only records.",
    ),
}


EXT = {"governance": (".md",), "discussions": (".md",), "scripts": (".py",)}


def tracked(dirname):
    out = subprocess.check_output(
        ["git", "-C", REPO, "ls-files", dirname]).decode()
    exts = EXT[dirname]
    return sorted(f for f in out.split("\n") if f.endswith(exts)
                  and os.path.basename(f) != "README.md")


def docstring_first_line(path):
    """The one-line summary a script writes about itself, if it wrote one.

    Parsed with ast, not a regex. A regex over the raw text found the *second*
    docstring in the file whenever the module docstring began on its own line, and
    the index then advertised scripts/check-counterpoint.py as
    "ABC length modifier -> duration in whole-note fractions."
    """
    try:
        with open(os.path.join(REPO, path), encoding="utf8", errors="ignore") as fh:
            tree = ast.parse(fh.read())
    except (OSError, SyntaxError):
        return None
    doc = ast.get_docstring(tree) or ""
    for line in doc.splitlines():
        line = line.strip()
        if not line:
            continue
        return re.sub(r"^\S+\.py\s+—\s+", "", line)
    return None


def title_of(path):
    if path.endswith(".py"):
        return docstring_first_line(path) or (
            "(no docstring — a script that does not say what it does is its own clutter)")
    try:
        with open(os.path.join(REPO, path), encoding="utf8", errors="ignore") as fh:
            for line in fh:
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        pass
    return os.path.basename(path)


def date_of(path):
    base = os.path.basename(path)
    m = re.match(r"^(20\d\d-\d\d-\d\d)", base)
    if m:
        return m.group(1)
    try:
        out = subprocess.check_output(
            ["git", "-C", REPO, "log", "-1", "--format=%ad", "--date=short", "--", path],
            stderr=subprocess.DEVNULL).decode().strip()
    except subprocess.CalledProcessError:
        out = ""
    if out:
        return out
    # No commit history yet: this file is staged for the landing that will commit it, in the same
    # checkout the index is being regenerated in. "—" is not a neutral placeholder here. The
    # landing commit gives the file a date, so an index written with "—" is stale the moment its
    # own file lands, and the next fresh clone fails --check — which has already happened twice,
    # both times for a newly added script (3022024: "new script build_music_pages.py missing";
    # and 5db7887, regenerated "now that tonight's files have a commit date"). A pass that cannot
    # survive its own deliverable is a delayed failure, not a check.
    #
    # The file's own mtime is the only date available before there is a commit, and it is the
    # right one whenever a file lands the day it was written, which is what every wake does. This
    # is deliberately *not* the mtime fallback gen_feed.py was repaired for on 2026-09-17: that
    # one fired for committed files whose lookup had been miswritten, and so hid the break. This
    # one can only fire when there is no commit at all, where there is nothing to hide.
    try:
        stamp = os.path.getmtime(os.path.join(REPO, path))
    except OSError:
        return "—"
    return _date.fromtimestamp(stamp).isoformat()


def render(dirname):
    heading, blurb = TARGETS[dirname]
    files = tracked(dirname)
    L = ["<!-- GENERATED by scripts/gen_index.py — DO NOT EDIT THIS FILE.",
         "     Edit the documents themselves; this index is rebuilt from what is on disk.",
         "     A new file appears here as soon as it is committed. Nobody has to remember. -->",
         "",
         "# %s — index" % heading,
         "",
         "*%s %s, generated %s.*" % (len(files),
                                     "scripts" if dirname == "scripts" else "documents",
                                     "from the tree, not by hand"),
         "",
         blurb,
         "",
         "| date | %s |" % ("script" if dirname == "scripts" else "document"),
         "|---|---|"]
    for f in files:
        # Links are relative to the index's own directory, because that is where the
        # index lives. Written as repo-relative paths first, which rendered as
        # governance/governance/... on GitHub and registered as 25 dangling links.
        L.append("| %s | [%s](%s) |" % (date_of(f), title_of(f),
                                        os.path.basename(f)))
    L.append("")
    L.append("*(Generated by `scripts/gen_index.py`, owner: Desi, 2026-09-17. If a document "
             "is missing from this list, it is not committed.)*")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if an index on disk is not what the generator produces")
    args = ap.parse_args()
    stale = []
    for dirname in sorted(TARGETS):
        text = render(dirname)
        path = os.path.join(REPO, dirname, "README.md")
        if args.stdout:
            print(text)
            continue
        old = None
        if os.path.exists(path):
            old = open(path, encoding="utf8").read()
        if args.check:
            if old != text:
                stale.append(dirname)
            continue
        if old != text:
            with open(path, "w", encoding="utf8") as fh:
                fh.write(text)
            print("wrote %s" % os.path.relpath(path, REPO))
        else:
            print("%s unchanged" % os.path.relpath(path, REPO))
    if stale:
        print("STALE: %s" % ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
