#!/usr/bin/env python3
"""Liveness check — the failures that are absences, not errors.

Why this exists, and why yesterday's plan for it was wrong:

The human asked on the morning of 2026-09-14 whether it was a concern that the repository had no new
files. It was not, yet — but nothing could tell him so. The lesson is that most of this project's
real failures are not *errors*: they are jobs that silently did not run. GitHub does not emit a
failure event for a scheduled workflow it simply never started, so **failure alerting cannot catch
silence**. What catches silence is a check on liveness: "this job was expected to have run by now,
and it has not."

Measured 2026-09-14: `channel-poll.yml` is configured `*/15` — ninety-six runs a day — and had run
twelve times in the previous twenty-four hours. `symposium.yml` runs about three to four hours after
its cron on every day observed. So "every fifteen minutes" means "every couple of hours, sometimes
six", and any design that assumed the cron is a clock is wrong. Build on that assumption if you like,
but know that it is wrong.

Usage:
    python3 scripts/heartbeat.py                # report; exit 1 if anything is stale
    python3 scripts/heartbeat.py --telegram     # also tell the human, once per newly stale job
    python3 scripts/heartbeat.py --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ALERTS = REPO / "channels" / "alerts.md"
STATE = REPO / "channels" / ".heartbeat-state.json"

# workflow file -> (label, [(hour, minute) UTC crons], tolerance_hours, also_max_gap_hours)
#
# A max-gap check is the wrong shape: a job scheduled twice a day naturally has a 22-hour gap
# overnight, so any window loose enough to avoid nightly false alarms is too loose to notice a
# missed noon run. So the question asked here is the precise one: for the most recent scheduled
# instant, has a run appeared? Tolerance allows for GitHub's known delays.
EXPECTED = {
    "channel-poll.yml":            ("Channel Poll", [], 0, 7),
    "symposium.yml":               ("Daily runner", [(12, 0), (13, 30)], 2.5, 26),
    "actuator.yml":                ("Actuator", [(12, 45)], 2.5, 26),
    "test-and-report.yml":         ("Verification", [(12, 30)], 2.5, 26),
    "autonomous-goose-tarik.yml":  ("Autonomous Goose (Tarik)", [(15, 7)], 2.5, 27),
}


def most_recent_cron(crons, now):
    """The latest scheduled instant at or before now (may be yesterday)."""
    if not crons:
        return None
    for back in range(0, 3):
        day = (now - dt.timedelta(days=back)).replace(hour=0, minute=0, second=0, microsecond=0)
        cands = [day.replace(hour=h, minute=m) for h, m in crons if day.replace(hour=h, minute=m) <= now]
        if cands:
            return max(cands)
    return None


def last_run(workflow: str) -> tuple[str | None, str | None]:
    """(createdAt ISO, conclusion) for the most recent run, or (None, None) if never."""
    try:
        out = subprocess.run(
            ["gh", "run", "list", "--workflow", workflow, "--limit", "1",
             "--json", "createdAt,conclusion"],
            capture_output=True, text=True, timeout=60,
        )
        data = json.loads(out.stdout or "[]")
        if data:
            return data[0].get("createdAt"), data[0].get("conclusion")
    except Exception:
        pass
    return None, None


def check() -> list[dict]:
    now = dt.datetime.now(dt.timezone.utc)
    rows = []
    for wf, (label, crons, tol, max_gap) in EXPECTED.items():
        created, conclusion = last_run(wf)
        when = None
        age = None
        if created:
            when = dt.datetime.fromisoformat(created.replace("Z", "+00:00"))
            age = (now - when).total_seconds() / 3600.0

        due = most_recent_cron(crons, now)
        stale = False
        reason = ""
        if when is None:
            stale, reason = True, "never run"
        elif max_gap and age is not None and age > max_gap:
            stale = True
            reason = f"last run {age:.1f}h ago, beyond a {max_gap}h window"
        elif due is not None:
            late = (now - due).total_seconds() / 3600.0
            if late > tol and when < due - dt.timedelta(minutes=15):
                stale = True
                reason = (f"the {due.strftime('%H:%M')} UTC run has not happened — {late:.1f}h late "
                          f"(tolerance {tol}h)")

        rows.append({"workflow": wf, "label": label,
                     "last": when.isoformat() if when else None,
                     "hours": None if age is None else round(age, 1),
                     "last_conclusion": conclusion,
                     "due_utc": due.strftime("%Y-%m-%d %H:%M") if due else None,
                     "stale": stale, "reason": reason or "inside its window"})
    return rows


def write_alerts(rows: list[dict]) -> None:
    """One deduplicated block in channels/alerts.md, rewritten each run — never appended to."""
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    stale = [r for r in rows if r["stale"]]
    block = [f"<!-- heartbeat:begin -->", f"## Heartbeat — {stamp}", ""]
    if not stale:
        block.append("All expected jobs have run inside their windows.")
    else:
        block.append("**Jobs that have NOT run inside their expected window** — this is silence, not an")
        block.append("error, which is why it needs a liveness check rather than failure alerting:")
        block.append("")
        for r in stale:
            age = "never run" if r["hours"] is None else f"{r['hours']}h ago"
            block.append(f"- **{r['label']}** (`{r['workflow']}`) — last run {age}. {r['reason']}.")
    block.append("<!-- heartbeat:end -->")
    text = ALERTS.read_text(encoding="utf-8") if ALERTS.exists() else "# Alerts\n"
    if "<!-- heartbeat:begin -->" in text:
        head = text.split("<!-- heartbeat:begin -->")[0].rstrip("\n")
        tail = text.split("<!-- heartbeat:end -->")[-1].lstrip("\n") if "<!-- heartbeat:end -->" in text else ""
        text = head + "\n\n" + "\n".join(block) + ("\n\n" + tail if tail.strip() else "\n")
    else:
        text = text.rstrip("\n") + "\n\n" + "\n".join(block) + "\n"
    ALERTS.write_text(text, encoding="utf-8")


def newly_stale(rows: list[dict]) -> list[dict]:
    """Only the ones that were not already stale last time — so the human is told once, not hourly."""
    prev = set()
    if STATE.exists():
        try:
            prev = set(json.loads(STATE.read_text()) or [])
        except Exception:
            prev = set()
    now = sorted(r["workflow"] for r in rows if r["stale"])
    fresh = [r for r in rows if r["stale"] and r["workflow"] not in prev]
    STATE.write_text(json.dumps(now), encoding="utf-8")
    return fresh


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--telegram", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()

    rows = check()
    if not a.no_write:
        write_alerts(rows)
    fresh = newly_stale(rows) if not a.no_write else []

    if a.json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            mark = "STALE " if r["stale"] else "ok    "
            age = "never" if r["hours"] is None else f"{r['hours']}h"
            due = r.get("due_utc") or "—"
            print(f"  {mark} {r['label']:<26} last {age:<8} due {due[-5:]:<6} {r['reason']}")
        print(f"\n  {sum(1 for r in rows if r['stale'])} of {len(rows)} jobs outside their window")

    if a.telegram and fresh:
        names = ", ".join(r["label"] for r in fresh)
        msg = (f"Heartbeat: {names} have not run inside their expected window. "
               f"Details in channels/alerts.md. This is an absence, not an error — nothing failed, "
               f"nothing happened.")
        try:
            subprocess.run([sys.executable, str(REPO / "scripts" / "tell_human.py"),
                            "--amigo", "desi", "--text", msg], check=False, timeout=60)
            print("  told the human on Telegram")
        except Exception as e:
            print(f"  telegram failed: {e}")

    return 1 if any(r["stale"] for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
