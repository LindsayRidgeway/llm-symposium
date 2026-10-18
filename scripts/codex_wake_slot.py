#!/usr/bin/env python3
"""Resolve a scheduled New York wake occurrence without touching its claim.

Prefer the scheduler's explicit scheduled timestamp. Fallback timing inference
allows dispatch up to ten minutes early; it cannot identify arbitrary manual
reruns or delays of more than one occurrence. It never searches for a free slot.
Publication must still create the returned claim path with create-if-absent.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc
NEW_YORK = ZoneInfo("America/New_York")
HOURS = (0, 4, 8, 12, 16, 20)
EARLY_WINDOW_SECONDS = 600


def aware_utc(value):
    if isinstance(value, str):
        value = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, dt.datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("an aware timestamp with a UTC offset is required")
    return value.astimezone(UTC)


def resolve_slot(started_utc, scheduled_utc=None):
    """Return clock-slot identity; no filesystem, network or scheduler actions."""
    started = aware_utc(started_utc)
    if scheduled_utc is not None:
        scheduled = aware_utc(scheduled_utc)
        local = scheduled.astimezone(NEW_YORK)
        if local.hour not in HOURS or (local.minute, local.second, local.microsecond) != (0, 0, 0):
            raise ValueError("scheduled timestamp is not a configured New York wake occurrence")
        basis = "explicit_scheduled_occurrence"
    else:
        date = started.astimezone(NEW_YORK).date()
        candidates = sorted(
            dt.datetime.combine(date + dt.timedelta(days=day), dt.time(hour), NEW_YORK).astimezone(UTC)
            for day in (-1, 0, 1) for hour in HOURS
        )
        elapsed = max(value for value in candidates if value <= started)
        upcoming = min(value for value in candidates if value > started)
        if (upcoming - started).total_seconds() <= EARLY_WINDOW_SECONDS:
            scheduled, basis = upcoming, "inferred_early_window"
        else:
            scheduled, basis = elapsed, "inferred_latest_elapsed"
        local = scheduled.astimezone(NEW_YORK)
    return {
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "scheduled_utc": scheduled.isoformat().replace("+00:00", "Z"),
        "scheduled_slot_local": local.isoformat(),
        "claim_path": "channels/tarik-codex-wakes/claims/" + local.strftime("%Y-%m-%d-%H00") + ".json",
        "basis": basis,
        "inferred": scheduled_utc is None,
        "seconds_from_slot": (started - scheduled).total_seconds(),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--started-utc", required=True, help="actual aware execution start")
    parser.add_argument("--scheduled-utc", help="authoritative scheduled occurrence, if supplied")
    args = parser.parse_args(argv)
    try:
        result = resolve_slot(args.started_utc, args.scheduled_utc)
    except (ValueError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
