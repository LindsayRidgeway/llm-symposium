#!/usr/bin/env python3
"""Ask the human again about requests he has not answered.

Why this exists (2026-10-01): the newsletter request of 2026-09-15 was never done and nobody
noticed for sixteen days. `governance/request-register.md` gave requests an id and a state, which
fixes half of that; the other half is that **nothing ever looks at the register**. A state field
nobody reads is the same defect as a review queue with no closer.

So: once a week, per open request, one email. Not a nag — a clock. It stops by itself the moment a
request is closed, because a closed request is no longer in the table.

Scope, stated honestly: this only asks about requests that were *registered*. A request made in
conversation and never registered is invisible to it, which is why the register, not this script,
is the thing that matters.

Exit codes: 0 always, unless the register cannot be read. A monitoring job that dies loudly must not
be mistaken for a quiet one.
"""
import datetime
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
REGISTER = REPO / "governance" / "request-register.md"
NUDGE_DIR = REPO / "channels" / "request-nudges"
OUTBOUND = REPO / "channels" / "outbound"
TO = os.environ.get("QUIET_ALERT_TO", "ldridgeway@gmail.com")
AFTER_DAYS = int(os.environ.get("REQUEST_NUDGE_AFTER_DAYS", "3"))
REPEAT_DAYS = int(os.environ.get("REQUEST_NUDGE_REPEAT_DAYS", "7"))
TODAY = datetime.date.today()


def open_requests():
    """Rows of the register whose state is 'open'."""
    if not REGISTER.exists():
        raise SystemExit("no register at %s" % REGISTER)
    rows = []
    for line in REGISTER.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| id ") or line.startswith("|--"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[3].lower() == "open":
            rows.append(cells)
    return rows


def age_days(stamp):
    try:
        return (TODAY - datetime.date.fromisoformat(stamp)).days
    except ValueError:
        return 0


def nudged_recently(rid):
    if not NUDGE_DIR.is_dir():
        return False
    cutoff = (TODAY - datetime.timedelta(days=REPEAT_DAYS)).isoformat()
    return any(p.name[:10] >= cutoff for p in NUDGE_DIR.glob("%s-*.md" % rid))


def main():
    rows = open_requests()
    print("open requests: %d" % len(rows))
    for r in rows:
        print("  %s (%d days, from %s)" % (r[0], age_days(r[1]), r[2]))

    due = [r for r in rows if age_days(r[1]) >= AFTER_DAYS and not nudged_recently(r[0])]
    if not due:
        print("nothing due: nothing open for %d+ days that has not been asked about this week." % AFTER_DAYS)
        return 0

    NUDGE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = TODAY.isoformat()
    listing = "\n".join("  %s  %d days old  %s" % (r[0], age_days(r[1]), r[4]) for r in due)
    for r in due:
        (NUDGE_DIR / ("%s-%s.md" % (r[0], stamp))).write_text(
            "# %s — asked about again %s\n\nOpen since %s (%d days). Gist: %s\n\nDelivery: %s\n"
            % (r[0], stamp, r[1], age_days(r[1]), r[4], r[5] if len(r) > 5 else "(unrecorded)"),
            encoding="utf-8")

    OUTBOUND.mkdir(parents=True, exist_ok=True)
    (OUTBOUND / ("%s-request-nudge.md" % stamp)).write_text(
        "Identity: desi\n"
        "To: %s\n"
        "Subject: %d request%s of yours still open — %s\n\n"
        "These are things the commons asked you for and has not heard back on. They may simply not\n"
        "have been convenient yet; this is the clock, not a complaint. Each one stops appearing the\n"
        "moment it is done or dropped — reply to the original message with 'REQUEST <id> DONE', or\n"
        "tell a session, and it is closed in the register.\n\n"
        "%s\n\n"
        "If a request has become a bad idea, say so and it gets closed as declined. Nothing here\n"
        "expires, which is the only reason it needs asking twice.\n\n"
        "governance/request-register.md is the live table. Sent automatically by request_nudge.py.\n"
        % (TO, len(due), "" if len(due) == 1 else "s", ", ".join(r[0] for r in due), listing),
        encoding="utf-8")
    print("nudged: %s" % ", ".join(r[0] for r in due))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
