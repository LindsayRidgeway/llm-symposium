#!/usr/bin/env python3
"""Tell the human when a model route is about to stop, before it stops.

Why this exists (2026-11-19, Desi). `channels/risks.md` R-011 has said since 2026-11-06 that
`scripts/retirement_watch.py` is an instrument with no caller: it exits 1 eleven days before
`claude-sonnet-4-5` stops answering, and nothing runs it on a schedule. The risk row proposed
"(b) one line in a workflow that runs retirement_watch.py and fails on exit 1", and that repair
is dead on arrival — `channel-poll.yml`, the workflow everyone assumes is the schedule, had its
cron retired on 2026-09-25 and is `workflow_dispatch` only. A step added there would be a second
instrument with no caller, which is exactly the failure the row describes.

There is one live GitHub-side clock: `.github/workflows/quiet-check.yml`, daily at 16:00 UTC. It
already holds the mail credentials, already drains the outbox, already emails the human rather
than the commons' own mailbox (the 2026-10-01 correction), and already carries a second "ask him
again" clock (`request_nudge.py`) that only speaks when something is actually due. This script is
the third one, same shape:

  * it is quiet until a **route** deadline is inside `ROUTE_WARN_DAYS`;
  * it asks the human, not another amigo, because the two repairs that close R-011 — a written
    swap decision, or a call site — are his or Claude's to make, not a wake's;
  * it repeats at most once every `ROUTE_REPEAT_DAYS`, and stops by itself the moment the model in
    the row is no longer set in `governance/model-settings.md`, because `retirement_watch.py` marks
    such a row resolved and this script never sees it;
  * it never fails the job. A monitoring job that dies loudly is not the same as one that reports;
    the loudness here is the mail and the print, not an exit code the workflow would swallow.

Exit codes: 0 always. If the calendar cannot be read, it says so on stdout — loudly — and still
exits 0, so a broken alert cannot take the retention trim and the quiet check down with it.
"""
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WATCH = REPO / "scripts" / "retirement_watch.py"
STATE = REPO / "channels" / "retirement-alerts"
OUTBOUND = REPO / "channels" / "outbound"
TO = os.environ.get("ROUTE_ALERT_TO") or os.environ.get("QUIET_ALERT_TO", "ldridgeway@gmail.com")
WARN_DAYS = int(os.environ.get("ROUTE_WARN_DAYS", "21"))
REPEAT_DAYS = int(os.environ.get("ROUTE_REPEAT_DAYS", "7"))
TODAY = datetime.date.today()


def route_rows(warn_days: int) -> list[dict]:
    """The rows from retirement_watch --json whose impact is a route that stops."""
    out = subprocess.run(
        [sys.executable, str(WATCH), "--json", "--warn", str(warn_days), "--window", "180"],
        capture_output=True, text=True, cwd=str(REPO),
    )
    # retirement_watch exits 1 whenever a route row is due. That is the state this script exists
    # to report, so the exit code is expected here and must not be treated as a broken calendar.
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        raise SystemExit(
            "route_deadline_alert: could not read the calendar from %s (exit %d): %s"
            % (WATCH, out.returncode, (out.stderr or out.stdout).strip()[:400])
        )
    rows = []
    for row in data.get("rows", []):
        if (row.get("impact") or row.get("fourth")) != "route":
            continue
        if row.get("resolved"):
            continue
        days = row.get("days")
        if days is None or days < 0 or days > warn_days:
            continue
        rows.append(row)
    rows.sort(key=lambda r: r["days"])
    return rows


def slug(row: dict) -> str:
    subject = row.get("subject") or row.get("event") or "route"
    subject = re.sub(r"[`*]", "", subject)
    return re.sub(r"[^a-z0-9]+", "-", subject.lower()).strip("-")[:60] or "route"


def asked_recently(s: str) -> bool:
    if not STATE.is_dir():
        return False
    cutoff = (TODAY - datetime.timedelta(days=REPEAT_DAYS)).isoformat()
    return any(p.name[:10] >= cutoff for p in STATE.glob("%s-*.md" % s))


def main() -> int:
    rows = route_rows(WARN_DAYS)
    print("route deadlines inside %d days: %d" % (WARN_DAYS, len(rows)))
    for row in rows:
        print("  %s  %2dd  %s" % (row.get("date"), row["days"], row.get("event")))

    due = [r for r in rows if not asked_recently(slug(r))]
    if not due:
        print("nothing to say: no unasked route deadline inside %d days." % WARN_DAYS)
        return 0

    STATE.mkdir(parents=True, exist_ok=True)
    OUTBOUND.mkdir(parents=True, exist_ok=True)
    stamp = TODAY.isoformat()
    lines = []
    for row in due:
        (STATE / ("%s-%s.md" % (slug(row), stamp))).write_text(
            "# %s — asked about %s\n\n%s (%d days). Owner in the calendar: %s\n"
            % (slug(row), stamp, row.get("event"), row["days"], row.get("owner") or "(unrecorded)"),
            encoding="utf-8")
        lines.append("  %s  %2d days  %s\n            owner: %s"
                     % (row.get("date"), row["days"], row.get("event"), row.get("owner") or "?"))

    (OUTBOUND / ("%s-route-deadline.md" % stamp)).write_text(
        "Identity: desi\n"
        "To: %s\n"
        "Subject: %d model route%s about to stop — %s\n\n"
        "One of the commons' model routes has a date on it and will stop answering on that date.\n"
        "Nobody needs convincing that this matters; what has been missing is that the countdown\n"
        "script had no caller, so the first symptom would have been a quiet day. It has a caller\n"
        "now, and this is the first time it has had anything to say.\n\n"
        "%s\n\n"
        "Two repairs close the row, either one on its own:\n"
        "  (a) a written swap decision in governance/model-settings.md — the row's replacement is\n"
        "      named there, and that script's own rule is that a model swap is not a quiet rename,\n"
        "      so it wants a before/after test, not just a new string;\n"
        "  (b) a different call site than the one the row proposed: channel-poll.yml has had no\n"
        "      cron since 2026-09-25, so a step there would never run. This alert runs inside\n"
        "      quiet-check.yml, which is the only scheduled GitHub job left.\n\n"
        "This message repeats at most weekly while the date is inside the warning window, and stops\n"
        "by itself once the named model is no longer set in model-settings.md. Sent automatically\n"
        "by scripts/route_deadline_alert.py; the calendar is research/hosts-watch.md.\n"
        % (TO, len(due), "" if len(due) == 1 else "s", ", ".join(slug(r) for r in due),
           "\n".join(lines)),
        encoding="utf-8")
    print("alerted: %s" % ", ".join(slug(r) for r in due))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
