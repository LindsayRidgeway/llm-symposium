#!/usr/bin/env python3
"""Offline tests for the recurrence projection protocol (Gap D).

Run with:  python3 tests/test_projection.py
Exit code 0 = pass. No third-party dependencies.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "probes"))

from recurrence_projection import (  # noqa: E402
    RecurringTask,
    expand_rrule,
    parse_date,
    probe_overlap,
    projected_but_not_returned,
    project_task,
)

FAILURES = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  ok: {name}")
    else:
        FAILURES.append(name)
        print(f"  FAIL: {name} {detail}")


print("expand_rrule: daily with COUNT")
dates, truncated = expand_rrule("FREQ=DAILY;COUNT=3", parse_date("2026-01-01"))
check("daily count=3 -> 3 dates", dates == [
    parse_date("2026-01-01"), parse_date("2026-01-02"), parse_date("2026-01-03")],
    f"got {dates}")
check("not truncated", truncated is False)

print("expand_rrule: weekly interval=4 byday=SA (the terbinafine case)")
dates, truncated = expand_rrule(
    "FREQ=WEEKLY;INTERVAL=4;BYDAY=SA", parse_date("2026-07-11"), horizon_days=90)
check("next occurrence is 2026-08-08", dates[:2] == [
    parse_date("2026-07-11"), parse_date("2026-08-08")], f"got {dates[:3]}")
check("third occurrence is 2026-09-05", dates[2] == parse_date("2026-09-05"),
      f"got {dates[:3]}")

print("expand_rrule: UNTIL bound")
dates, _ = expand_rrule("FREQ=DAILY;UNTIL=20260103", parse_date("2026-01-01"), horizon_days=30)
check("until=20260103 -> 3 dates", len(dates) == 3, f"got {dates}")

print("project_task: explicit masking (cancellation is authoritative)")
task = RecurringTask(
    id="t1", title="Weekly series",
    rrule="FREQ=WEEKLY;BYDAY=MO",
    explicit=[
        {"date": "2026-08-03", "status": "completed"},
        {"date": "2026-08-10", "status": "cancelled"},
        {"date": "2026-08-17", "status": "open"},
    ],
)
cal, truncated = project_task(task, horizon_days=21)
by_date = {e["date"]: e for e in cal}
check("cancelled date present as explicit/cancelled",
      by_date.get("2026-08-10", {}).get("source") == "explicit"
      and by_date.get("2026-08-10", {}).get("status") == "cancelled",
      f"got {cal}")
check("projected dates do not overwrite explicit dates",
      by_date.get("2026-08-17", {}).get("source") == "explicit",
      f"got {cal}")
projected_dates = [e["date"] for e in cal if e["source"] == "projected"]
check("projection fills in future Mondays only (08-24, 08-31...)",
      "2026-08-24" in projected_dates and "2026-08-10" not in projected_dates,
      f"projected: {projected_dates[:4]}")

print("project_task: no explicit anchor -> never invent")
task2 = RecurringTask(id="t2", title="No anchor", rrule="FREQ=DAILY", explicit=[])
cal2, _ = project_task(task2, horizon_days=30)
check("no anchor -> note, no invented dates",
      any(e["source"] == "note" for e in cal2) and not any(
          e["source"] == "projected" for e in cal2),
      f"got {cal2}")

print("probe_overlap: window divergence detection (Gap B)")
res = probe_overlap(
    ["2026-08-18", "2026-08-20", "2026-08-25"],
    ["2026-08-18", "2026-08-20", "2026-08-25", "2026-08-27"],
    parse_date("2026-08-15"), parse_date("2026-08-31"),
)
check("divergence detected", res["divergent"] is True, f"got {res}")
check("missing date identified", res["in_b_not_a"] == ["2026-08-27"], f"got {res}")

print("projected_but_not_returned: catches consistently-truncated connector")
cal3, _ = project_task(RecurringTask(
    id="terbinafine", title="terbinafine",
    rrule="FREQ=WEEKLY;INTERVAL=4;BYDAY=SA",
    explicit=[{"date": "2026-07-11", "status": "completed"},
              {"date": "2026-08-08", "status": "open"}],
), horizon_days=90)
# Simulate the observed bug: the connector under-returns future occurrences
# in BOTH windows, so the overlap probe alone would see no divergence.
windows = [
    (parse_date("2026-08-01"), parse_date("2026-08-31"), ["2026-08-08"]),
    (parse_date("2026-08-15"), parse_date("2026-09-30"), ["2026-08-08"]),
]
missing = projected_but_not_returned(cal3, windows)
check("2026-09-05 flagged (inside window B range, returned by neither window)",
      "2026-09-05" in missing, f"got {missing}")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("ALL TESTS PASSED")
