#!/usr/bin/env python3
"""The check counts the Works pages print to strangers, re-derived (Desi, 2026-11-27).

`docs/works/index.html` tells a reader "(81 checks)", "(50 checks)", "(60 checks)". Those numbers are
the page's own evidence that somebody looked. Nothing re-derived them, and two of them were wrong:

    validate_unreported_trials_page.mjs   index said 50, the harness runs 54
    validate_recalls_page.mjs            index said 60, the harness runs 94

Both understated, which is the safe direction and still false: a reader who trusts "60 checks" has
been told something about this repository that is not true, and a reader who distrusts it is right for
the wrong reason. The heat page went the other way in the same measurement — 57 checks, printed as 57,
because a previous hand count was right.

How a count is taken: lines in the harness's own output that begin `ok` or `PASS`. Uniform across the
thirteen `validate_*.mjs` harnesses, which print one line per assertion. It is a proxy: an assertion
printed inside a loop counts once per iteration, which is what a reader expects of "56 checks", and a
harness that prints nothing counts zero, which is a finding rather than a pass.

    python3 scripts/page_check_counts.py --write    # run every harness, record what it checks
    python3 scripts/page_check_counts.py --check    # compare the record with the pages and, where
                                                    # the harness runs offline, with the harness itself
    python3 scripts/page_check_counts.py --check --json

The live harnesses need the network, so a scheduled check cannot re-derive those numbers; it checks the
*page* against the record, and the record says when it was last derived and how. That is the honest
split: the number is re-derived on a machine with the network, and cannot drift afterwards without
`tests/test_page_check_counts.py` saying so by name.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INDEX = REPO / "docs" / "works" / "index.html"
RECORD = REPO / "tests" / "page-check-counts.json"
TESTS = REPO / "tests"
COUNT_LINE = re.compile(r"^\s*(?:ok|PASS)\b")
# The index wraps the file name in <code>, so the phrase is read from the tag-stripped text: a
# pattern that refused a `<` between the name and the number matched nothing at all, and "0 printed
# numbers agree" is exactly the kind of green that this file exists to prevent.
PRINTED = re.compile(r"(validate_[a-z_0-9]+\.mjs)\s*\((\d+) checks")
TAGS = re.compile(r"<[^>]+>")
TIMEOUT = 240


def printed(index: Path = INDEX) -> dict:
    """{harness: the number the Works index tells a reader it runs}."""
    try:
        html = index.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    return {m.group(1): int(m.group(2)) for m in PRINTED.finditer(TAGS.sub("", html))}


def harnesses() -> list:
    return sorted(TESTS.glob("validate_*.mjs"))


def runs_offline(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    return "HARNESS_REPLAY" in text or "await fetch(" not in text


def node():
    import shutil
    found = shutil.which("node")
    if found:
        return found
    for d in ("/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/opt/local/bin"):
        candidate = Path(d) / "node"
        if candidate.is_file():
            return str(candidate)
    return None


def run_count(path: Path, binary=None):
    """The number of check lines the harness prints, or None when it cannot run here."""
    binary = binary or node()
    if not binary:
        return None
    try:
        r = subprocess.run([binary, str(path)], capture_output=True, text=True,
                           cwd=str(REPO), timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    return sum(1 for line in (r.stdout or "").splitlines() if COUNT_LINE.match(line))


def derive() -> dict:
    out = {}
    for path in harnesses():
        n = run_count(path)
        if n is not None:
            out[path.name] = n
    return out


HARNESS_NAME = re.compile(r"validate_[a-z_0-9]+\.mjs")
ANY_CHECK_NUMBER = re.compile(r"(\d+)\s+checks")


def problems_in_pages(record: dict, pages_dir: Path) -> list:
    """Pages that print their own check count in each direction.

    The Works index is the obvious place a number is printed, and it was not the only one: with the
    index corrected, `docs/works/trials.html` still said "all 33 checks pass" — and the harness ran 34,
    because a check had been added to it that morning. Found 2026-11-27 by widening the question from
    "what does the index say" to "what does every page say".

    A page is checkable only when it names exactly one harness: with two names, "56 checks" cannot be
    attributed, and guessing would be worse than saying nothing.
    """
    if not isinstance(record, dict) or not isinstance(record.get("harnesses"), dict):
        return []
    counts = record["harnesses"]
    found = []
    for page in sorted(Path(pages_dir).glob("*.html")):
        text = TAGS.sub(" ", page.read_text(encoding="utf-8", errors="replace"))
        named = set(HARNESS_NAME.findall(text))
        if len(named) != 1:
            continue
        harness = named.pop()
        if harness not in counts:
            continue
        for m in ANY_CHECK_NUMBER.finditer(text):
            number = int(m.group(1))
            if number != counts[harness]:
                found.append("%s prints %d checks for %s, which runs %d"
                             % (page.name, number, harness, counts[harness]))
    return found


def problems(record: dict, said: dict, measured: dict | None = None) -> list:
    """Every way the printed numbers can be wrong. Pure: the three maps are arguments."""
    if not isinstance(record, dict) or not isinstance(record.get("harnesses"), dict):
        return ["no recorded counts: nothing to compare a page against"]
    counts = record["harnesses"]
    found = []
    for name, number in sorted(said.items()):
        if name not in counts:
            found.append("%s is printed on the Works index (%d checks) and never measured" % (name, number))
        elif counts[name] != number:
            found.append("%s: the page says %d checks, the harness runs %d"
                         % (name, number, counts[name]))
    if measured:
        for name, number in sorted(measured.items()):
            if name in counts and counts[name] != number:
                found.append("%s: recorded %d checks, runs %d now — re-record with --write"
                             % (name, counts[name], number))
            elif name not in counts:
                found.append("%s runs %d checks and is not in the record" % (name, number))
    return found


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="run the harnesses and record their counts")
    ap.add_argument("--check", action="store_true", help="compare the record with the pages")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.write:
        counts = derive()
        data = {
            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "method": "lines in the harness's own output beginning `ok` or `PASS`",
            "harnesses": counts,
        }
        RECORD.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print("recorded %d harness(es), %d checks in total" % (len(counts), sum(counts.values())))
        return 0

    record = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.is_file() else None
    measured = {p.name: n for p in harnesses() if runs_offline(p) and (n := run_count(p)) is not None}
    found = problems(record, printed(), measured) + problems_in_pages(record, INDEX.parent)
    if args.json:
        print(json.dumps({"problems": found, "measured_offline": measured}, indent=2))
    elif found:
        print("page_check_counts: %d problem(s)" % len(found))
        for line in found:
            print("  " + line)
    else:
        print("page_check_counts: %d printed number(s) agree with the harnesses"
              % len(printed()))
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
