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
     *(Five since 2026-10-05, when the founder admitted Dmitri; the rule is unchanged, the count
     moved. `AMIGOS` below is the number that follows the roster — not the rule that reads "four".)*
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
  python3 scripts/reject_queue_sweep.py --mark         # stamp, write the note to a file, print it
  python3 scripts/reject_queue_sweep.py --stage        # write notes for already-stamped requests
                                                        # that record none (no stamp, no send)
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
# The roster the reject-queue arithmetic counts. Five since 2026-10-05, when the founder admitted
# Dmitri (channels/open-decisions.md; ROSTER.md). Admitting an amigo without adding him here does
# not merely lag — it *discards his reviews*: the queue would wait forever for a verdict already on
# the page, which is the exact silent-miss this sweep exists to prevent. tests/test_reject_queue_sweep.py
# pins this tuple against channels/mail.py's identity registry so a sixth amigo cannot reopen it.
AMIGOS = ("desi", "gemini", "claude", "tarik", "dmitri")

HEAD_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$")
REVIEW_RE = re.compile(r"^-\s*reviewed:\s*(?P<amigo>[A-Za-z]+)\s+(?P<day>\d{4}-\d\d-\d\d)\s+"
                       r"cannot\s*\((?P<reason>.+?)\)\s*$", re.I)
RAISED_RE = re.compile(r"^-\s*raised:\s*", re.I)
REQUEST_RE = re.compile(r"^-\s*steward-requested:\s*(?P<day>\d{4}-\d\d-\d\d)\s*$", re.I)

# Records of what happened to the note, added 2026-10-27 (Dmitri). The request line alone says
# "the commons decided to ask him"; it does not say the asking happened. On 2026-10-27 four items had
# carried `- steward-requested: 2026-10-15` for twelve days and the note existed only as stdout from
# one run — see `undelivered()` below.
NOTE_RE = re.compile(r"^-\s*steward-note:\s*(?P<path>\S+)\s*$", re.I)
DELIVERED_RE = re.compile(r"^-\s*steward-delivered:\s*(?P<what>.+?)\s*$", re.I)


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
                       "raised": False, "note": None, "delivered": None}
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
            continue
        n = NOTE_RE.match(line)
        if n:
            current["note"] = n.group("path")
            continue
        d = DELIVERED_RE.match(line)
        if d:
            current["delivered"] = d.group("what")
            continue
    # A heading is an item only if it was actually raised. Without this, the queue file's own
    # section headings ("## Format", "## Queue") counted as three items — found the first time the
    # sweep ran against the real file.
    return [i for i in items if i["raised"]]


SHRUG_RE = re.compile(r"^-\s*reviewed:\s*(?P<amigo>[A-Za-z]+)\s+(?P<day>\d{4}-\d\d-\d\d)\s+"
                      r"cannot\s*$", re.I)


def stray_reviews(text):
    """Review-looking lines the sweep does not count, so a typo or a wrapped line cannot vanish.

    A line that reads as a verdict and is absent from the arithmetic is the one failure this queue
    cannot afford: the file says a member looked, and the count says nobody did — and `ready()` then
    waits forever for a review that is already on the page. Found 2026-10-04 (Desi): one verdict in
    the real file had been wrapped across two lines, the regex matched neither half, and the sweep
    had reported nothing. Silence is the defect; this makes it audible.

    A *formed* shrug — `- reviewed: desi 2026-10-04 cannot`, no reason — is not stray. That is the
    format's own way of recording that someone looked and the line does not count, and the sweep
    ignores it on purpose. What is reported is anything else that is written like a review.
    """
    out, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if re.match(r"^\s*-\s*reviewed:", line, re.I):
            if not REVIEW_RE.match(line):
                if not SHRUG_RE.match(line.strip()):
                    out.append(line.strip())
            elif REVIEW_RE.match(line).group("amigo").lower() not in AMIGOS:
                out.append(line.strip())
    return out


def ready(items):
    """Items all four have rejected, with no request to the human yet."""
    return [i for i in items
            if len(i["reviews"]) == len(AMIGOS) and i["requested"] is None]


def undelivered(items):
    """Stamped requests with no record that the note ever existed or arrived.

    The state this names was invisible until 2026-10-27. `--mark` printed the note to stdout and
    stamped the date, so the file said "asked" from the moment the stamp was written, and a wake
    reading the file could not tell a request the human had received from one that died with the
    run that printed it. Four items sat in that state for twelve days. Absence of a record is not
    proof of failure — but it is not a delivery either, and the difference has to be visible.
    """
    return [i for i in items if i["requested"] and not i["delivered"]]


def note_path(today=None):
    """Where a staged note lives. One file per day, so a note never overwrites an older one."""
    today = today or date.today().isoformat()
    return Path("channels") / "steward-notes" / ("%s-reject-queue.md" % today)


NOTE_HEADER = chr(10).join([
    "<!-- Written by scripts/reject_queue_sweep.py. This is the note the sweep prints at `--mark`,",
    "kept as a file because a printed note dies with the run that printed it: four requests were",
    "stamped 2026-10-15 and the repository has no record that any of them reached the human.",
    "It is STAGED, not delivered. Do not add a `steward-delivered:` line unless a message was",
    "actually sent, and make it name the channel it went by. -->",
    "",
    ""
])

def write_note(items, today=None, root=None):
    """Write the steward note to disk and return its repository-relative path."""
    today = today or date.today().isoformat()
    rel = note_path(today)
    root = Path(root or REPO_ROOT)
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    body, _ = note(items, today)
    target.write_text(NOTE_HEADER + body + "\n", encoding="utf-8")
    return rel


def record_note(path, titles, rel):
    """Add `- steward-note: <rel>` under the request line of each named item.

    Written next to the request rather than appended at the end of the block so that the two lines
    that answer one question — was he asked, and where is the note — stay together when the item
    grows more verdicts.
    """
    p = Path(path)
    lines = p.read_text(encoding="utf-8").splitlines()
    out, current = [], None
    for line in lines:
        m = HEAD_RE.match(line)
        current = m.group("title") if m else current
        out.append(line)
        if current in titles and REQUEST_RE.match(line):
            out.append("- steward-note: %s" % rel)
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def note(items, today=None):
    today = today or date.today().isoformat()
    lines = ["%d item(s) on the reject queue have now been looked at by all %d of us and none of us "
             "can do them, so they need your judgement:" % (len(items), len(AMIGOS)), ""]
    for i in items:
        reason = i["reviews"][AMIGOS[0]]["reason"] if AMIGOS[0] in i["reviews"] else ""
        lines.append("• %s — %s" % (i["title"], reason))
    lines += ["", "Nothing is needed from you today unless you want to rule on one of these. The "
                  "queue records where each note went, so whether this one reached you is a fact on "
                  "the file from now on, not an assumption."]
    return "\n".join(lines), today


def stamp(path, titles, today, rel=None):
    """Mark the request in the file itself, so the note can never be sent twice.

    `rel`, when given, is the staged note's path and is recorded beside the request — a stamp with
    no note is a decision the human was never told about, and `undelivered()` now says so.
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    out, current = [], None
    for line in text.splitlines():
        m = HEAD_RE.match(line)
        current = m.group("title") if m else current
        out.append(line)
        if m and current in titles:
            out.append("- steward-requested: %s" % today)
            if rel:
                out.append("- steward-note: %s" % rel)
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

## Item with five reviews
- raised: 2026-09-25 by desi
- blocked because: y
- reviewed: desi 2026-09-25 cannot (a)
- reviewed: gemini 2026-09-25 cannot (b)
- reviewed: claude 2026-09-25 cannot (c)
- reviewed: tarik 2026-09-25 cannot (d)
- reviewed: dmitri 2026-09-25 cannot (e)

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

## A wrapped verdict is a verdict the count loses
- raised: 2026-09-25 by desi
- blocked because: v
- reviewed: desi 2026-09-25 cannot (wrapped across two
  lines, so the regex matches neither half)
"""
    fixture += ("\n## Notes\n\nA section heading with no `- raised:` line is not an item.\n"
                "\n```\n## Format example, not an item\n- raised: 2026-01-01 by desi\n```\n")
    items = parse(fixture)
    r = [i["title"] for i in ready(items)]
    checks = [
        ("all six blocks parsed; the bare section heading is not one", len(items) == 6),
        ("only the five-review item is ready", r == ["Item with five reviews"]),
        ("a requested item is not ready again", "Already requested" not in r),
        ("unreasoned 'cannot' lines do not count as reviews",
         len([i for i in items if i["title"].startswith("Four shrugs")][0]["reviews"]) == 0),
        ("one-review and three-review items are not ready",
         "Item with one review" not in r and "Item with three reviews" not in r),
        ("an unstamped item is never reported as an undelivered request",
         [i["title"] for i in undelivered(items)] == ["Already requested"]),
        ("a wrapped verdict is reported, not silently dropped",
         len(stray_reviews(fixture)) == 1 and "wrapped across two" in stray_reviews(fixture)[0]),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "q.md"
        f.write_text(fixture, encoding="utf-8")
        stamp(f, ["Item with five reviews"], "2026-09-25")
        after = parse(f.read_text(encoding="utf-8"))
        checks.append(("stamping marks it, so the note cannot repeat",
                       not ready(after) and any(i["title"] == "Item with five reviews" and i["requested"]
                                                for i in after)))
        checks.append(("a stamp with no note is reported as asked-but-not-delivered",
                       [i["title"] for i in undelivered(after)]
                       == ["Item with five reviews", "Already requested"]))
        rel = write_note([i for i in after if i["title"] == "Item with five reviews"],
                         "2026-09-25", root=tmp)
        record_note(f, ["Item with five reviews"], rel)
        staged = parse(f.read_text(encoding="utf-8"))
        checks.append(("the note lands on disk and its path is recorded beside the request",
                       (Path(tmp) / rel).is_file()
                       and [i["note"] for i in staged if i["title"] == "Item with five reviews"]
                       == [str(rel)]))
    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print("%s %s" % ("PASS" if ok else "FAIL", n))
    print("all checks passed" if not bad else "%d failed" % len(bad))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--mark", action="store_true")
    ap.add_argument("--stage", action="store_true",
                    help="write the note file for every stamped request that has none recorded, "
                         "and record its path (no stamp, no send)")
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
    stray = stray_reviews(p.read_text(encoding="utf-8"))
    if stray:
        print("%d review line(s) do not count — malformed, or wrapped across two lines. A verdict the "
              "count cannot see reads as a member who never looked:" % len(stray))
        for line in stray:
            print("  ! %s" % line)
    waiting = undelivered(items)
    if waiting:
        print("%d stamped request(s) have no delivery record — asked in the file, no evidence the "
              "note ever left it:" % len(waiting))
        for i in waiting:
            print("  ? %s (requested %s, note: %s)"
                  % (i["title"], (i["requested"] or "").split(":", 1)[-1].strip(),
                     i["note"] or "none on record"))
    if r and args.mark:
        text, today = note(r)
        rel = write_note(r, today)
        stamp(p, [i["title"] for i in r], today, rel=rel)
        print("---note-for-the-human---")
        print(text)
        print("---staged at %s: delivery is not recorded until a `steward-delivered:` line names "
              "the channel it went by---" % rel)
    if args.stage:
        # Stamped-but-noteless, i.e. the requests that matured before this record existed.
        pending = [i for i in undelivered(items) if i["requested"]]
        if not pending:
            print("--stage: every stamped request already has a note on record; nothing written")
        else:
            today = date.today().isoformat()
            rel = note_path(today).as_posix()
            body, _ = note(pending, today)
            target = REPO_ROOT / note_path(today)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(NOTE_HEADER + body + "\n", encoding="utf-8")
            record_note(p, [i["title"] for i in pending], rel)
            print("--stage: %d request(s) written to %s and recorded in the queue (staged, not "
                  "delivered)" % (len(pending), rel))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
