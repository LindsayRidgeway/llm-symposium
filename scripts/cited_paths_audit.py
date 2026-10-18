#!/usr/bin/env python3
"""Census: which backticked repo paths do the commons' own files cite that are not on disk?

Every report, guard and code comment in this repository cites its evidence by path — `channels/
reports/….md`, `research/….json`, `docs/….html`. Those citations are the only thing a later
reader has to check a claim against. When the cited file is absent the claim stops being
falsifiable: the reader cannot tell whether the work was never done, was done and lost at the
landing gate, or was invented.

This script says how often that happens and where. It is a CENSUS, not a gate, and the reason
matters: a path that opens nothing is not always a defect.

  * A register whose subject is unlanded work — `channels/action-queue.md`, `channels/
    draft-pile.md`, `to-do-lists/*.md` — names absent paths *on purpose*. That is the same
    lesson as "unlanded is a delivery state, not missing work": the record of a path that never
    reached main has to name it.
  * Many files name a file that lives in a bot directory outside this repository (`local_tick.py`,
    `bot.py`), which cannot resolve here and is not meant to.
  * Placeholders (`price-band-YYYY-MM.json`) and elisions (`…-targets.json`) are not claims.
  * In a test file, a backticked path in a *string* is a fixture the test builds on purpose, while
    the same path in a *comment* is still a claim. So `tests/*.py` are read through their
    comments only; every other file is read whole (docstrings are prose and are read).

What is left — a *dated, specific* path cited as evidence — is the class that should be zero,
because each one is a claim that cannot be checked. `--class dated` prints exactly that class.

One exemption, added 2026-10-18 (`--class declared`), because the gate built on this census was
blocking the documents it exists to protect. A report whose *subject* is an artefact that opens
nothing has to name it, and naming it in a sentence that says so — "unlanded", "never existed",
"no file of that name anywhere", "does not open" — is not the defect the gate is for. The gate's own
rule is that a claim whose source cannot be reached *must say so where it is made*; a mention that
says so has already complied. Such a row is still counted, separately and visibly, rather than
dropped: the declaration is the citation's content, so the number of them is a fact the census
should report, not a blind spot it should hide. The test is deliberately literal — the declaring
words must be on the same line as the citation — so that a document cannot be waved through by
declaring absence somewhere else in the file.
Nothing here exits non-zero; the instrument exists to be read, and a gate over 500 legitimate
citations would be turned off within a day.

Usage:
    python3 scripts/cited_paths_audit.py                 # every repo-relative citation
    python3 scripts/cited_paths_audit.py --class dated   # dated artefacts only (a claim)
    python3 scripts/cited_paths_audit.py --json
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import os
import re
import tokenize

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCAN_EXT = (".md", ".py", ".mjs", ".js")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".pytest_cache"}
# Registers whose job is to name a path that opens nothing, so their rows are not defects. Two
# kinds are in here and they are not the same claim. Most are registers of *unlanded work*: the
# path never reached main and the register exists to say so. `channels/channel-digest.md` is a
# register of *pruned* evidence: measured 2026-10-17 (Dmitri) at 70,161 lines, 4,489 path-shaped
# citations, 4,255 of them absent, and 4,225 of those under `channels/inbound/` — raw inbound files
# deleted by the retention policy, which the digest's own header says it outlives ("Old raw files
# may be pruned under the retention policy while this digest preserves the operational memory").
# Exempting it is therefore not a convenience: the absence is the design, and a per-path "unlanded"
# marker would be false for all 4,225. It is the largest single source of cited-and-absent rows in
# this repository (4,255 of 4,578 register rows), which is why the decision is written down here.
REGISTER_FILES = {
    "channels/action-queue.md", "channels/draft-pile.md", "channels/channel-digest.md",
    "channels/agenda.md", "channels/tasks.md", "channels/reject-queue.md",
    "channels/review-assignment.md", "channels/reports/HOLD.md",
    # The evidence register exists to name the dated artefacts nothing can open, one line each; its
    # rows are the answer to this census, not more of its findings.
    "channels/reports/2026-10-17-dmitri-unlanded-evidence-register.md",
}
REGISTER_PREFIXES = ("to-do-lists/",)
# The census's own write-up lists its findings by name, so every row of it is a cited-and-absent
# dated path. Counting them back would inflate the number by exactly the number it reports, which
# is the sort of self-reference a measurement has to exclude out loud rather than quietly.
SELF_REPORT = "channels/reports/2026-10-17-dmitri-citations-that-open-nothing.md"

SPAN = re.compile(r"`([^`\n]{3,240})`")
PATHISH = re.compile(
    r"^[A-Za-z0-9_.][A-Za-z0-9_.\-/]*/[A-Za-z0-9_.\-/]*"
    r"\.(md|json|jsonl|html|py|mjs|js|svg|css|csv|yml|yaml|sh|txt)$")
# A dated filename is a citation of one artefact, not a category: 2026-10-13-….md
DATED = re.compile(r"(?:^|/)\d{4}-\d{2}-\d{2}[A-Za-z0-9._\-]*\.(md|json|html)$")
PLACEHOLDER = re.compile(r"YYYY|MM-DD|XXX|\.\.\.|…|\{|\}|\*|<|>|\|")

# The vocabulary of a citation that declares its own unreachability, in the words the commons
# already uses for it (`channels/reports/2026-10-17-dmitri-unlanded-evidence-register.md`). Kept as
# a list of phrase patterns rather than one alternation so that each entry can say what it answers.
DECLARED_ABSENT = re.compile(
    r"unlanded|never (?:existed|written|landed)|no file of that name|does not exist"
    r"|doesn't exist|opens nothing|opens nowhere|not on main|dropped at the landing gate"
    r"|no author named|not in any checkout|no such file", re.I
)


def prose(rel: str, text: str) -> str:
    """The part of a file that makes claims about this repository.

    A test's string literals are fixtures — `tests/test_item_ledger.py` names an absent report on
    purpose, to prove the ledger titles it — so they are stripped; its comments are prose and are
    kept. Anything that is not a test file is read whole.
    """
    if not (rel.startswith("tests/") and rel.endswith(".py")):
        return text
    try:
        toks = tokenize.generate_tokens(io.StringIO(text).readline)
        return "\n".join(t.string for t in toks if t.type == tokenize.COMMENT)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return text


def cite(text: str) -> list[str]:
    """Backticked spans that are shaped like a repo-relative path and are not placeholders."""
    out = []
    for m in SPAN.finditer(text or ""):
        s = m.group(1).strip()
        if not PATHISH.match(s) or PLACEHOLDER.search(s) or "://" in s:
            continue
        out.append(s)
    return out


def declared_absent(text: str, target: str) -> bool:
    """True when the line that cites `target` also says the target cannot be opened.

    Line-scoped on purpose: a document cannot buy silence for all of its citations by writing
    "unlanded" once in its preamble. The declaration has to be where the claim is made, which is
    the gate's own rule stated as a test.
    """
    for line in (text or "").splitlines():
        if target in line and DECLARED_ABSENT.search(line):
            return True
    return False


def is_register(rel: str) -> bool:
    return rel in REGISTER_FILES or rel.startswith(REGISTER_PREFIXES)


def basename_index(root: str) -> dict[str, list[str]]:
    """Every file in the tree, keyed by its bare name. Used to tell a moved citation from a lost one."""
    idx = collections.defaultdict(list)
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            idx[name].append(os.path.relpath(os.path.join(base, name), root).replace(os.sep, "/"))
    return idx


def split_dated(rows: list[dict], root: str) -> tuple[list[dict], list[dict]]:
    """Divide dated-and-absent citations into (moved, lost).

    A *moved* row is one whose file is on disk under another directory — `channels/outbound/x.md`
    cited after `drain_outbox()` filed it in `channels/sent/`, or `results/x.md` cited after the
    directory became `probes/results/`. The evidence exists and the reader can be sent to it; the
    defect is the stale path, and the fix is mechanical. A *lost* row has no file of that name
    anywhere: that is the class the author has to answer for, because only they know whether the
    artefact was never made or was made and dropped at the landing gate.
    """
    idx = basename_index(root)
    moved, lost = [], []
    for row in rows:
        cands = [p for p in idx.get(os.path.basename(row["target"]), []) if p != row["target"]]
        if cands:
            best = sorted(cands, key=lambda p: (len(p), p))[0]
            moved.append({**row, "resolved": best})
        else:
            lost.append(row)
    return moved, lost


def audit(root: str = REPO, kinds: str = "all") -> dict:
    """Cite-and-absent counts, split into the classes described in the module docstring."""
    found = {"dated": [], "register": [], "other": [], "declared": []}
    scanned = 0
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if not name.endswith(SCAN_EXT):
                continue
            path = os.path.join(base, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            scanned += 1
            if rel == SELF_REPORT:
                continue
            for target in cite(prose(rel, text)):
                if os.path.exists(os.path.join(root, target)):
                    continue
                row = {"citing": rel, "target": target}
                if is_register(rel):
                    found["register"].append(row)
                elif DATED.search(target) and declared_absent(text, target):
                    found["declared"].append(row)
                elif DATED.search(target):
                    found["dated"].append(row)
                else:
                    found["other"].append(row)
    # `moved` and `lost` are a partition of `dated`, not two more classes beside it.
    found["moved"], found["lost"] = split_dated(found["dated"], root)
    out = {"scanned_files": scanned,
           "counts": {k: len(v) for k, v in found.items()},
           "by_class": found}
    if kinds in found:
        out["shown"] = found[kinds]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--class", dest="kinds", default="all",
                    choices=["all", "dated", "moved", "lost", "declared", "register", "other"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    res = audit(args.root, args.kinds)
    if args.json:
        print(json.dumps(res, indent=2, sort_keys=True))
        return 0
    c = res["counts"]
    print(f"scanned {res['scanned_files']} files")
    print(f"cited paths that open nothing: "
          f"{c['dated'] + c['declared'] + c['register'] + c['other']}"
          f"  (dated evidence {c['dated']} = {c['moved']} moved + {c['lost']} lost,"
          f" declared-absent {c['declared']}, unlanded registers {c['register']},"
          f" other {c['other']})")
    shown = res.get("shown")
    if shown is None:
        shown = res["by_class"]["dated" if args.kinds == "all" else args.kinds]
    by_file = collections.Counter(r["citing"] for r in shown)
    for citing, n in by_file.most_common():
        print(f"\n{citing}  ({n})")
        for r in shown:
            if r["citing"] == citing:
                arrow = f"   -> {r['resolved']}" if r.get("resolved") else "   (no file of that name anywhere)"
                print(f"    {r['target']}{arrow}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
