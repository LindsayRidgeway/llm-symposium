#!/usr/bin/env python3
# Owner: Desi
"""The reject queue, and the sweep that tells the steward when a decision is owed.

Set down by the human on 2026-09-25, after he and Gemini spent 09-24 closing loopholes in the wake
rules. Desi had written the rule as "a reject is not a dead end — decide in that wake", which
collapses four distinct steps into one and invites exactly the loophole it was meant to close. The
real protocol, verbatim in intent:

  1. If an amigo can do the next to-do item, just do it.
  2. If it cannot, it puts the item on the reject queue — **and that does not count as work.**
  3. Every amigo reviews **every** item on the queue:
       - can do it -> do it, take it off the queue. **That counts as work.**
       - cannot    -> add a notation that it looked and cannot. **That does not count as work.**
  4. When all four have said they cannot, the item becomes a request for the human's judgement, and
     the request itself is marked. **That does not count as work.**
  5. The human left the delivery of that request to Desi's judgement, between (a) Desi sweeping
     periodically and notifying him, and (b) whichever amigo is fourth to reject notifying him.

**The choice made here: (a), and it is a script rather than a judgement.** Counting is the part of
this that must not be done by a language model — an amigo asked "am I the fourth?" will sometimes
say yes. This sweep does arithmetic on the file, and it rides Desi's existing wake clock instead of
adding one. Cost of (a): latency, up to the sweep interval. Cost of (b): every amigo has to count
correctly, and a missed count leaves an item silent forever, which is the failure this queue exists
to prevent.

Format — one block per item, at most:
    ## <short title>
    - raised: <YYYY-MM-DD> by <amigo>
    - blocked because: <one line, the reason it is not doable now>
    - reviewed: <amigo> <YYYY-MM-DD> cannot (<one line of reason>)
    - steward-requested: <YYYY-MM-DD>

Only a `reviewed:` line naming an amigo, a date **and a reason** counts as a review. "cannot" with no
reason is not a review and the sweep ignores it — a rubber stamp is how a queue of four real verdicts
turns into a queue of four shrugs.

Usage:
  python3 scripts/reject_queue_sweep.py --check        # what is ready, send nothing
  python3 scripts/reject_queue_sweep.py --mark         # stamp and print the note for the human
  python3 scripts/reject_queue_sweep.py --selftest     # fixtures; no file touched
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
QUEUE = REPO_ROOT / "channels" / "reject-queue.md"
AMIGOS = ("desi", "gemini", "claude", "tarik")

HEAD_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$")
REVIEW_RE = re.compile(r"^-\s*reviewed:\s*(?P<amigo>[A-Za-z]+)\s+(?P<day>\d{4}-\d\d-\d\d)\s+"
                       r"cannot\s*\((?P<reason>.+?)\)\s*$", re.I)
RAISED_RE = re.compile(r"^-\s*raised:\s*", re.I)
REQUEST_RE = re.compile(r"^-\s*steward-requested:\s*(?P<day>\d{4}-\d\d-\d\d)\s*$", re.I)


def parse(text):
    """Blocks in file order, with the reviews that actually count."""
    items, current, in_fence = [], None, False
    for line in text.splitlines():
        # A fenced block in this file is a *description* of the format, not an item. Counting the
        # example as a queued item was the second bug found by running the sweep on the real file.
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEAD_RE.match(line)
        if m:
            current = {"title": m.group("title"), "reviews": {}, "requested": None,
                       "raised": False}
            items.append(current)
            continue
        if current is None:
            continue
        r = REVIEW_RE.match(line)
        if r:
            amigo = r.group("amigo").lower()
            # A duplicate review is a later verdict, and a review by a non-amigo does not count.
            if amigo in AMIGOS:
                current["reviews"][amigo] = {"day": r.group("day"), "reason": r.group("reason")}
            continue
        if RAISED_RE.match(line):
            current["raised"] = True
            continue
        if REQUEST_RE.match(line):
            current["requested"] = line
    # A heading is an item only if it was actually raised. Without this, the queue file's own
    # section headings ("## Format", "## Queue") counted as three items — found the first time the
    # sweep ran against the real file.
    return [i for i in items if i["raised"]]


def ready(items):
    """Items all four have rejected, with no request to the human yet."""
    return [i for i in items
            if len(i["reviews"]) == len(AMIGOS) and i["requested"] is None]


def note(items, today=None):
    today = today or date.today().isoformat()
    lines = ["%d item(s) on the reject queue have now been looked at by all four of us and none of us "
             "can do them, so they need your judgement:" % len(items), ""]
    for i in items:
        reason = i["reviews"][AMIGOS[0]]["reason"] if AMIGOS[0] in i["reviews"] else ""
        lines.append("• %s — %s" % (i["title"], reason))
    lines += ["", "I have marked each one as asked, so you will not get this note twice about the "
                  "same item. Nothing needed from you today unless you want to rule on one."]
    return "\n".join(lines), today


def stamp(path, titles, today):
    """Mark the request in the file itself, so the note can never be sent twice."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    out, current = [], None
    for line in text.splitlines():
        m = HEAD_RE.match(line)
        current = m.group("title") if m else current
        out.append(line)
        if m and current in titles:
            out.append("- steward-requested: %s" % today)
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def selftest():
    fixture = """# Reject queue

## Item with one review
- raised: 2026-09-25 by desi
- blocked because: needs a credential nobody has
- reviewed: desi 2026-09-25 cannot (no access)

## Item with three reviews
- raised: 2026-09-25 by desi
- blocked because: x
- reviewed: desi 2026-09-25 cannot (a)
- reviewed: gemini 2026-09-25 cannot (b)
- reviewed: claude 2026-09-25 cannot (c)

## Item with four reviews
- raised: 2026-09-25 by desi
- blocked because: y
- reviewed: desi 2026-09-25 cannot (a)
- reviewed: gemini 2026-09-25 cannot (b)
- reviewed: claude 2026-09-25 cannot (c)
- reviewed: tarik 2026-09-25 cannot (d)

## Already requested
- raised: 2026-09-25 by desi
- blocked because: z
- reviewed: desi 2026-09-25 cannot (a)
- reviewed: gemini 2026-09-25 cannot (b)
- reviewed: claude 2026-09-25 cannot (c)
- reviewed: tarik 2026-09-25 cannot (d)
- steward-requested: 2026-09-25

## Four shrugs is not four verdicts
- raised: 2026-09-25 by desi
- blocked because: w
- reviewed: desi 2026-09-25 cannot
- reviewed: gemini 2026-09-25 cannot
- reviewed: claude 2026-09-25 cannot
- reviewed: tarik 2026-09-25 cannot
"""
    fixture += ("\n## Notes\n\nA section heading with no `- raised:` line is not an item.\n"
                "\n```\n## Format example, not an item\n- raised: 2026-01-01 by desi\n```\n")
    items = parse(fixture)
    r = [i["title"] for i in ready(items)]
    checks = [
        ("all five blocks parsed; the bare section heading is not one", len(items) == 5),
        ("only the four-review item is ready", r == ["Item with four reviews"]),
        ("a requested item is not ready again", "Already requested" not in r),
        ("unreasoned 'cannot' lines do not count as reviews",
         len([i for i in items if i["title"].startswith("Four shrugs")][0]["reviews"]) == 0),
        ("one-review and three-review items are not ready",
         "Item with one review" not in r and "Item with three reviews" not in r),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "q.md"
        f.write_text(fixture, encoding="utf-8")
        stamp(f, ["Item with four reviews"], "2026-09-25")
        after = parse(f.read_text(encoding="utf-8"))
        checks.append(("stamping marks it, so the note cannot repeat",
                       not ready(after) and any(i["title"] == "Item with four reviews" and i["requested"]
                                                for i in after)))
    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print("%s %s" % ("PASS" if ok else "FAIL", n))
    print("all checks passed" if not bad else "%d failed" % len(bad))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--mark", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--path", default=str(QUEUE))
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    p = Path(args.path)
    if not p.is_file():
        print("no reject queue at %s — nothing to sweep" % p)
        return 0
    items = parse(p.read_text(encoding="utf-8"))
    r = ready(items)
    print("%d item(s) on the queue, %d ready for the steward" % (len(items), len(r)))
    for i in r:
        print("  • %s" % i["title"])
    if r and args.mark:
        text, today = note(r)
        stamp(p, [i["title"] for i in r], today)
        print("---note-for-the-human---")
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
