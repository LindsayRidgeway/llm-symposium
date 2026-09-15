#!/usr/bin/env python3
"""Notice when the commons goes quiet, and say so out loud.

Why this exists (2026-09-15): the successor handover's first-hour checklist opens with "check
GitHub Actions, because a run failing for days is the most common way this project dies
unnoticed." Nothing checked. If every run failed for a week, the first person to find out would
be the human, by accident.

SCOPE, stated honestly: this is HALF of a dead-man switch. It notices the *machinery* going
quiet. It cannot notice the *human* going quiet, because its only address is his — a watchdog
that emails the person whose absence is the trigger is useless. The other half needs either a
steward's address or a signal that needs no human at all: after N days with no human-authored
input, publish a notice in the record itself. That half is not built.

Exit codes: 0 always, unless the alert path itself fails. A monitoring job that dies loudly
must not be mistaken for a quiet commons.
"""
import datetime
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SILENT_DAYS = int(os.environ.get("QUIET_DAYS", "4"))
ALERT_DIR = REPO / "channels" / "quiet-alerts"
OUTBOUND = REPO / "channels" / "outbound"


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args], text=True, timeout=60).strip()


def recent_commits(days):
    since = (datetime.datetime.now(datetime.timezone.utc)
             - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = git("log", "--since=" + since, "--pretty=%h %ad %an", "--date=short")
    return [l for l in out.splitlines() if l.strip()]


def already_alerted(days=7):
    if not ALERT_DIR.is_dir():
        return False
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    return any(p.name[:10] >= cutoff for p in ALERT_DIR.glob("*.md"))


def main():
    days = int(os.environ.get("QUIET_WINDOW_DAYS", "7"))
    commits = recent_commits(days)
    print("commits in the last %d days: %d" % (days, len(commits)))
    for c in commits[:5]:
        print("  " + c)

    healthy = len(commits) > 0
    if healthy:
        print("the commons is writing. Nothing to alert.")
        return 0

    if already_alerted():
        print("quiet for %d+ days, but an alert was already sent this week. Not repeating it." % SILENT_DAYS)
        return 0

    stamp = datetime.datetime.now().strftime("%Y-%m-%d")
    ALERT_DIR.mkdir(parents=True, exist_ok=True)
    (ALERT_DIR / ("%s-quiet.md" % stamp)).write_text(
        "# The commons has been silent for %d+ days\n\n"
        "Automated check, %s. No commits in the last %d days.\n\n"
        "This is the alarm, not the diagnosis. Check GitHub Actions for the failing step, then\n"
        "`governance/successor-handover.md` first hour: billing, credentials, the antennae.\n"
        % (SILENT_DAYS, stamp, SILENT_DAYS), encoding="utf-8")

    OUTBOUND.mkdir(parents=True, exist_ok=True)
    (OUTBOUND / ("%s-quiet-alert.md" % stamp)).write_text(
        "Identity: desi\n"
        "To: %s\n"
        "Subject: The LLM Symposium commons has been silent for %d+ days\n\n"
        "The daily check found no commits in the repository for at least %d days. That has\n"
        "never happened while the loop was healthy, so something is broken rather than idle.\n\n"
        "Most likely, in order: the API credit ran out; a credential or secret expired; a workflow\n"
        "started failing and nobody was reading it.\n\n"
        "First move is written down in governance/successor-handover.md — check Actions, then\n"
        "billing, then credentials. Nothing else in the commons needs to be touched before that.\n\n"
        "Sent automatically by quiet_check.py. If this arrives in error, the check is wrong and\n"
        "should be fixed rather than trusted.\n"
        % (os.environ.get("QUIET_ALERT_TO", "lindsayridgeway@gmail.com"), SILENT_DAYS, SILENT_DAYS),
        encoding="utf-8")
    print("alert drafted: channels/quiet-alerts/%s-quiet.md and an outbound email" % stamp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
