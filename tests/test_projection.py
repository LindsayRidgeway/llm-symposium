#!/usr/bin/env python3
"""Offline tests for the recurrence projection protocol (Gap D).

Run with:  python3 tests/test_projection.py
Exit code 0 = pass. No third-party dependencies.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "probes"))

from recurrence_projection import (  # noqa: E402
    UnsupportedRRULEError,
    RecurringTask,
    expand_rrule,
    parse_date,
    parse_date_tz,
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

print("parse_date: offset-aware ISO parsing (workaround protocol)")
check("naive date unchanged",
      parse_date("2026-08-25") == parse_date("2026-08-25"))
check("compact date unchanged",
      parse_date("20260825") == parse_date("2026-08-25"))
check("naive datetime unchanged",
      parse_date("2026-08-25T12:00:00") == parse_date("2026-08-25"))
check("negative offset crosses date boundary (23:00-08:00 -> next day UTC)",
      parse_date("2026-08-25T23:00:00-08:00") == parse_date("2026-08-26"),
      f"got {parse_date('2026-08-25T23:00:00-08:00')}")
check("positive offset stays same date (23:00+08:00 -> 15:00 UTC)",
      parse_date("2026-08-25T23:00:00+08:00") == parse_date("2026-08-25"),
      f"got {parse_date('2026-08-25T23:00:00+08:00')}")

print("expand_rrule: unsupported-key rejection is enforced in code (workaround protocol)")
UNSUPPORTED_RULES = [
    "FREQ=YEARLY;BYMONTHDAY=29",     # BYMONTHDAY outside the leap-day rule
    "FREQ=MONTHLY;BYMONTHDAY=15",    # BYMONTHDAY on a non-leap-day rule
    "FREQ=YEARLY;BYSETPOS=1",        # BYSETPOS
    "FREQ=WEEKLY;BYYEARDAY=100",     # BYYYEARDAY
    "FREQ=MONTHLY;BYWEEKNO=3",       # BYWEEKNO
    "FREQ=WEEKLY;BYDAY=1MO",         # ordinal prefix
    "FREQ=WEEKLY;BYDAY=-1SU",        # negative ordinal prefix
    "FREQ=WEEKLY;BYDAY=TU,1WE",      # ordinal inside a multi-value BYDAY
    "FREQ=DAILY;INTERVAL=x",         # malformed value
    "FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29;BYMONTH=3",  # conflicting months
]
for bad_rule in UNSUPPORTED_RULES:
    try:
        expand_rrule(bad_rule, parse_date("2026-01-01"), horizon_days=30)
        check(f"rejected: {bad_rule}", False, "no exception raised")
    except UnsupportedRRULEError:
        check(f"rejected: {bad_rule}", True)

print("expand_rrule: leap-day anniversary rule (BYMONTH=2;BYMONTHDAY=29)")
dates, truncated = expand_rrule(
    "FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29", parse_date("2024-02-29"), horizon_days=1600)
check("leap years only — Feb 29 never invented",
      dates == [parse_date("2024-02-29"), parse_date("2028-02-29")], f"got {dates}")
check("not truncated", truncated is False)

print("project_task: leap-day gap flagged, no invented occurrence")
task_leap = RecurringTask(
    id="leap", title="Leap-day anniversary",
    rrule="FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29",
    explicit=[{"date": "2024-02-29", "status": "completed"}],
)
cal_leap, _ = project_task(task_leap, horizon_days=1600)
leap_projected = [e["date"] for e in cal_leap if e["source"] == "projected"]
check("2028-02-29 projected; 2025/2026/2027 never invented",
      leap_projected == ["2028-02-29"], f"got {leap_projected}")
leap_notes = [e for e in cal_leap if e["source"] == "note"]
check("non-leap-year gap flagged to the user",
      any("2025" in n["status"] and "2027" in n["status"] for n in leap_notes),
      f"got {leap_notes}")

print("parse_date_tz: DST transitions (Sunday boundaries, spring + fall)")
check("spring-forward Sunday 2026-03-08 is a Sunday", parse_date("2026-03-08").weekday() == 6)
check("spring-forward 02:30 is nonexistent -> shifted forward, same date",
      parse_date_tz("2026-03-08T02:30:00", "America/New_York") == parse_date("2026-03-08"),
      f"got {parse_date_tz('2026-03-08T02:30:00', 'America/New_York')}")
check("no ±1 day shift the day before spring-forward",
      parse_date_tz("2026-03-07T23:30:00", "America/New_York") == parse_date("2026-03-07"),
      f"got {parse_date_tz('2026-03-07T23:30:00', 'America/New_York')}")
check("fall-back Sunday 2026-11-01 is a Sunday", parse_date("2026-11-01").weekday() == 6)
check("fall-back ambiguous 01:30 -> deterministic first occurrence, same date",
      parse_date_tz("2026-11-01T01:30:00", "America/New_York") == parse_date("2026-11-01"),
      f"got {parse_date_tz('2026-11-01T01:30:00', 'America/New_York')}")
check("explicit offsets preserved on fall-back day (-04:00 and -05:00 both -> 11-01)",
      parse_date_tz("2026-11-01T01:30:00-04:00", "America/New_York") == parse_date("2026-11-01")
      and parse_date_tz("2026-11-01T01:30:00-05:00", "America/New_York") == parse_date("2026-11-01"))
check("parse_date_tz UTC agrees with parse_date (offset preserved)",
      parse_date_tz("2026-08-25T23:00:00-08:00", "UTC") == parse_date("2026-08-26"))
check("parse_date_tz UTC default on naive input",
      parse_date_tz("2026-08-25T12:00:00") == parse_date("2026-08-25"))

print("expand_rrule/project_task: N=50 truncation cap (Gap A label)")
dates50, trunc50 = expand_rrule("FREQ=DAILY", parse_date("2026-01-01"), horizon_days=90, limit=50)
check("exactly 50 in-window instances", len(dates50) == 50, f"got {len(dates50)}")
check("truncated flag set before window end", trunc50 is True)
cal50, trunc50t = project_task(
    RecurringTask(id="daily50", title="daily", rrule="FREQ=DAILY",
                  explicit=[{"date": "2026-01-01", "status": "open"}]),
    horizon_days=90, limit=50)
trunc_notes = [e for e in cal50 if e["source"] == "note"]
check("downstream calendar labeled [Truncated at 50]",
      any("[Truncated at 50]" in n["status"] for n in trunc_notes), f"got {trunc_notes}")
check("truncated result not presented as complete", trunc50t is True)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("ALL TESTS PASSED")
