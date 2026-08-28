"""Core recurrence projection logic for the LLM Symposium TickTick protocol.

Implements the protocol from
`workarounds/ticktick-future-recurrence-workaround.md`:

    explicit overrides + timezone-normalized bounded RRULE projection
        -> projected calendar

Pure functions only. No network or connector dependencies, so the logic is
reproducible anywhere and testable offline (see `tests/test_projection.py`).

Supported RRULE subset (documented limitation, *enforced* by
`validate_rrule` — any rule outside the subset raises
`UnsupportedRRULEError`):
    FREQ=DAILY|WEEKLY|MONTHLY|YEARLY
    INTERVAL=n
    BYDAY=MO,TU,WE,TH,FR,SA,SU        (no ordinal prefixes like 1MO)
    COUNT=n  /  UNTIL=YYYYMMDD

Single documented exception — the leap-day anniversary rule:
    FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29
    Feb 29 occurrences exist only in leap years; the engine never invents
    one in a non-leap year. Non-leap-year gaps are flagged to the user by
    `project_task` (a note entry), never fabricated.

DST-aware parsing: `parse_date_tz(value, target_tz)` normalizes both
explicit-offset and naive datetimes into a target zone without ±1 day
shifts across the spring-forward / fall-back Sunday boundaries
(workaround protocol edge-case coverage).
"""

from __future__ import annotations

from calendar import isleap
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Gap A: canonical, single-source protocol constants.
# These are the values every implementation should use; the workaround
# document references this module as the authoritative location.
# ---------------------------------------------------------------------------
DEFAULT_HORIZON_DAYS = 90          # was "90 days" (Gemini) vs "1 year" (Claude)
MAX_PROJECTED_INSTANCES = 50       # hard cap per task, per query

WEEKDAYS = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
VALID_FREQS = ("DAILY", "WEEKLY", "MONTHLY", "YEARLY")

# Keys the engine understands. Anything else is rejected, not silently ignored
# (workaround protocol: unsupported-key handling must be explicit and enforced
# in code — at minimum BYMONTHDAY, BYSETPOS, BYWEEKNO, BYYYEARDAY, and
# multi-value BYDAY with ordinal prefixes).
SUPPORTED_RRULE_KEYS = frozenset({"FREQ", "INTERVAL", "BYDAY", "COUNT", "UNTIL"})

# The one BYMONTH/BYMONTHDAY combination the engine supports: the leap-day
# anniversary rule (FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29). Every other use of
# these keys is rejected.
LEAP_DAY_EXCEPTION_KEYS = frozenset({"BYMONTH", "BYMONTHDAY"})


class UnsupportedRRULEError(ValueError):
    """Raised when an RRULE uses keys or values outside the supported subset.

    This is the enforced half of the "supported RRULE subset (documented
    limitation)": the subset is not just prose — rules outside it fail loudly
    instead of being partially or wrongly expanded.
    """


def _is_leap_day_rule(spec: Dict[str, str]) -> bool:
    """True for the documented leap-day exception: FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29."""
    if spec.get("FREQ") != "YEARLY":
        return False
    if "BYMONTH" not in spec or "BYMONTHDAY" not in spec:
        return False
    try:
        return int(spec["BYMONTH"]) == 2 and int(spec["BYMONTHDAY"]) == 29
    except ValueError:
        return False


def is_leap_day_rule(spec: Dict[str, str]) -> bool:
    """Public predicate for the leap-day exception (see `_is_leap_day_rule`)."""
    return _is_leap_day_rule(spec)


def validate_rrule(spec: Dict[str, str]) -> None:
    """Reject rules outside the supported subset. Raises `UnsupportedRRULEError`.

    Enforced in `expand_rrule`; exported so callers can validate up front and
    so the tests can pin the behavior (workaround protocol: unsupported-key
    handling must be explicit and enforced in code).
    """
    unknown = set(spec) - SUPPORTED_RRULE_KEYS - LEAP_DAY_EXCEPTION_KEYS
    if unknown:
        raise UnsupportedRRULEError(
            f"unsupported RRULE keys: {sorted(unknown)} (supported: "
            f"{sorted(SUPPORTED_RRULE_KEYS)}; exception: the leap-day rule)")

    if "BYMONTH" in spec or "BYMONTHDAY" in spec:
        if not _is_leap_day_rule(spec):
            raise UnsupportedRRULEError(
                "BYMONTH/BYMONTHDAY are supported only for the leap-day "
                "anniversary rule FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29")

    # BYDAY ordinal prefixes (1MO, -1SU, 2TU) are not in the subset.
    for b in spec.get("BYDAY", "").split(","):
        b = b.strip()
        if b and (b[0].isdigit() or b[0] in "+-"):
            raise UnsupportedRRULEError(
                f"ordinal BYDAY {b!r} is not supported (no ordinal prefixes)")

    # Numeric values must be sane integers (fail loudly, not with a confusing
    # ValueError from deep in the expansion loop).
    for key in ("INTERVAL", "COUNT", "BYMONTH", "BYMONTHDAY"):
        if key in spec:
            for part in spec[key].split(","):
                if not part.strip().isdigit():
                    raise UnsupportedRRULEError(f"{key}={spec[key]!r}: expected integer values")

    freq = spec.get("FREQ", "DAILY")
    if freq not in VALID_FREQS:
        raise UnsupportedRRULEError(f"FREQ={freq!r} not in {VALID_FREQS}")


def leap_day_skipped_years(
    spec: Dict[str, str], dtstart: date, horizon_days: int
) -> List[int]:
    """Non-leap years in the window where the Feb 29 anniversary does not exist.

    Leap-day rule only; returns [] for any other rule. These are the years the
    protocol says to skip rather than invent — surfaced to the user by
    `project_task` as a note ("flag the gap, never fabricate").
    """
    if not _is_leap_day_rule(spec):
        return []
    end = dtstart + timedelta(days=horizon_days)
    step = max(int(spec.get("INTERVAL", "1") or 1), 1)
    return [y for y in range(dtstart.year, end.year + 1, step) if not isleap(y)]


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_date(value: str) -> date:
    """Parse 'YYYY-MM-DD', 'YYYYMMDD', or an ISO datetime string into a date.

    Offset-aware per the workaround protocol: an ISO datetime carrying an
    explicit offset is converted to UTC before the date is extracted, so a
    boundary case like 2026-08-25T23:00:00-08:00 yields 2026-08-26, not
    2026-08-25. The offset is never truncated.
    """
    s = value.strip()
    if "T" in s:  # ISO datetime with time (and possibly an offset) — convert.
        try:
            dt = datetime.fromisoformat(s)
        except ValueError:
            dt = None
        if dt is not None:
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc)
            return dt.date()
    s = s[:10]
    if len(s) == 8 and s.isdigit():
        return datetime.strptime(s, "%Y%m%d").date()
    return datetime.strptime(s, "%Y-%m-%d").date()


def _get_tz(name: str):
    """Return a tzinfo for `name`. UTC aliases need no tzdata; anything else
    comes from the IANA database (`zoneinfo`). Fails loudly for unknown zones."""
    if name.strip().upper() in ("UTC", "GMT", "Z", "ETC/UTC"):
        return timezone.utc
    from zoneinfo import ZoneInfo
    return ZoneInfo(name)


def parse_date_tz(value: str, target_tz: str = "UTC") -> date:
    """Parse an ISO datetime and return the calendar date in `target_tz`.

    DST-aware per the workaround protocol (edge-case coverage):
    - an explicit offset is preserved and converted to the target zone — the
      offset is never truncated (e.g. `2026-08-25T23:00:00-08:00` is not read
      as a bare date);
    - a naive local wall time is localized to the target zone; on the
      spring-forward Sunday a nonexistent wall time (e.g. 02:30 America/New_York
      2026-03-08) is shifted forward to the first valid instant (03:30 EDT),
      and on the fall-back Sunday an ambiguous wall time (e.g. 01:30 on
      2026-11-01) resolves deterministically to the first occurrence (fold=0).
    In both cases the returned calendar date does not shift by ±1 day as a
    result of the transition itself.
    """
    s = value.strip()
    if "T" in s:
        try:
            dt = datetime.fromisoformat(s)
        except ValueError:
            dt = None
        if dt is not None:
            tz = _get_tz(target_tz)
            if dt.tzinfo is not None:
                return dt.astimezone(tz).date()
            # Naive wall time: localize in the target zone (fold=0), then
            # round-trip through UTC to detect a spring-forward gap: a
            # nonexistent wall time comes back with a different wall clock.
            dt = dt.replace(tzinfo=tz, fold=0)
            back = dt.astimezone(timezone.utc).astimezone(tz)
            if (back.date(), back.time()) != (dt.date(), dt.time()):
                dt = back  # shift forward to the first valid instant; same date
            return dt.date()
    s = s[:10]
    if len(s) == 8 and s.isdigit():
        return datetime.strptime(s, "%Y%m%d").date()
    return datetime.strptime(s, "%Y-%m-%d").date()


def parse_rrule(rrule_str: str) -> Dict[str, str]:
    """Parse an RRULE string into a dict of uppercase keys -> raw values."""
    spec: Dict[str, str] = {}
    for chunk in rrule_str.split(";"):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            continue
        k, v = chunk.split("=", 1)
        spec[k.upper()] = v.strip()
    return spec


def _matches(d: date, spec: Dict[str, str], base: date) -> bool:
    """Return True if date `d` matches the rule anchored at `base`."""
    freq = spec.get("FREQ", "DAILY")
    interval = int(spec.get("INTERVAL", "1") or 1)
    byday = [b for b in spec.get("BYDAY", "").split(",") if b]
    # Month/day-of-month filters — reachable only for the validated leap-day
    # exception (validate_rrule rejects BYMONTH/BYMONTHDAY everywhere else).
    # Applied generally for robustness.
    by_month = [int(m) for m in spec.get("BYMONTH", "").split(",") if m.strip()]
    by_monthday = [int(md) for md in spec.get("BYMONTHDAY", "").split(",") if md.strip()]

    if by_month and d.month not in by_month:
        return False
    if by_monthday and d.day not in by_monthday:
        return False

    if freq == "DAILY":
        if (d - base).days % interval != 0:
            return False
    elif freq == "WEEKLY":
        if (d - base).days % (7 * interval) != 0:
            return False
    elif freq == "MONTHLY":
        months = (d.year - base.year) * 12 + (d.month - base.month)
        if months % interval != 0:
            return False
        # No end-of-month rollover support (documented limitation).
        if d.day != base.day:
            return False
    elif freq == "YEARLY":
        years = d.year - base.year
        if years % interval != 0:
            return False
        if not (by_month or by_monthday):
            # Default: the rule is the anniversary of `base`'s date.
            if (d.month, d.day) != (base.month, base.day):
                return False
        # Else (leap-day exception): the explicit BYMONTH/BYMONTHDAY clauses
        # govern the date; `base` only anchors the INTERVAL phase. A date like
        # Feb 29 simply does not exist in non-leap years, so nothing is
        # invented — the anniversary is skipped by construction.
    else:
        raise ValueError(f"Unsupported FREQ: {freq!r}")

    if byday:
        allowed = {WEEKDAYS[b] for b in byday}
        if d.weekday() not in allowed:
            return False
    return True


def expand_rrule(
    rrule_str: str,
    dtstart: date,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    limit: int = MAX_PROJECTED_INSTANCES,
) -> Tuple[List[date], bool]:
    """Expand the rule from `dtstart` across the horizon.

    Returns (occurrences, truncated) where truncated is True if the hard cap
    was hit before the end of the window (Gap A: caller must label results
    `[Truncated at N]`).
    """
    spec = parse_rrule(rrule_str)
    validate_rrule(spec)
    end = dtstart + timedelta(days=horizon_days)
    if "UNTIL" in spec:
        end = min(end, parse_date(spec["UNTIL"]))
    count = int(spec["COUNT"]) if "COUNT" in spec else None

    out: List[date] = []
    d = dtstart
    while d <= end and len(out) < limit and (count is None or len(out) < count):
        if _matches(d, spec, dtstart):
            out.append(d)
        d += timedelta(days=1)

    truncated = bool(out) and len(out) >= limit and d <= end
    return out, truncated


# ---------------------------------------------------------------------------
# Projection (the protocol itself)
# ---------------------------------------------------------------------------

@dataclass
class RecurringTask:
    id: str
    title: str
    rrule: Optional[str]
    explicit: List[Dict[str, str]] = field(default_factory=list)
    # explicit entries: {"date": "YYYY-MM-DD", "status": "open"|"completed"|"cancelled"}


def project_task(
    task: RecurringTask,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    limit: int = MAX_PROJECTED_INSTANCES,
) -> Tuple[List[Dict[str, str]], bool]:
    """Apply the protocol to one task.

    Returns (calendar, truncated). Each calendar entry:
        {"date": "YYYY-MM-DD", "source": "explicit"|"projected", "status": ...}
    Explicit instances are authoritative overrides (masking): a projected
    occurrence is suppressed when an explicit instance exists for that date,
    and cancelled explicit entries surface as cancellations rather than being
    replaced by the projection.
    """
    calendar: List[Dict[str, str]] = []
    explicit_map: Dict[date, str] = {}
    for e in task.explicit:
        d = parse_date(e["date"])
        explicit_map[d] = e.get("status", "open")
        # Explicit instances are authoritative, including cancellations:
        # a cancelled occurrence surfaces as cancelled and is never replaced
        # by a projected one.
        calendar.append({"date": d.isoformat(), "source": "explicit", "status": explicit_map[d]})

    truncated = False
    if task.rrule:
        spec = parse_rrule(task.rrule)
        if not explicit_map:
            # No anchor: we cannot expand safely. Gap B: report rather than invent.
            calendar.append({
                "date": "?",
                "source": "note",
                "status": "no explicit anchor; RRULE not expanded (never invent occurrences)",
            })
        else:
            anchor = min(explicit_map)
            projected, truncated = expand_rrule(task.rrule, anchor, horizon_days, limit)
            for d in projected:
                if d in explicit_map:
                    continue  # explicit wins (masking)
                calendar.append({"date": d.isoformat(), "source": "projected", "status": "open"})
            # Leap-day exception: the Feb 29 anniversary does not exist in
            # non-leap years. Never invent an occurrence — flag the gap.
            if is_leap_day_rule(spec):
                skipped = leap_day_skipped_years(spec, anchor, horizon_days)
                if skipped:
                    calendar.append({
                        "date": "?",
                        "source": "note",
                        "status": (
                            "leap-day anniversary (Feb 29) does not exist in non-leap years; "
                            f"occurrences skipped: {', '.join(str(y) for y in skipped)}"
                        ),
                    })
    if truncated:
        # Gap A: the hard cap was hit before the end of the window — the
        # calendar is NOT complete and must be labeled as such downstream.
        calendar.append({
            "date": "?",
            "source": "note",
            "status": f"[Truncated at {limit}] — projection hit the hard cap before the end of "
                      "the window; calendar is NOT complete",
        })

    calendar.sort(key=lambda r: r["date"])
    return calendar, truncated


# ---------------------------------------------------------------------------
# Gap B: truncation probe (positive probe for a silent, under-returning connector)
# ---------------------------------------------------------------------------

def probe_overlap(
    returned_a: List[str],
    returned_b: List[str],
    overlap_start: date,
    overlap_end: date,
) -> Dict:
    """Compare two windows' returned instances over their shared date range.

    If the connector returns the same instances regardless of window, the
    overlap should agree exactly. Divergence is evidence of truncation —
    the positive probe the freshness check needs (Gap B).
    """
    a = {parse_date(x) for x in returned_a}
    b = {parse_date(x) for x in returned_b}
    in_overlap = lambda s: {d for d in s if overlap_start <= d <= overlap_end}
    oa, ob = in_overlap(a), in_overlap(b)
    return {
        "in_b_not_a": sorted(d.isoformat() for d in ob - oa),
        "in_a_not_b": sorted(d.isoformat() for d in oa - ob),
        "divergent": bool(oa ^ ob),
    }


def projected_but_not_returned(
    calendar: List[Dict[str, str]],
    returned_per_window: List[Tuple[date, date, List[str]]],
) -> List[str]:
    """Projected dates that fall inside a probe window's range but were not
    returned by the connector for that window -> truncation evidence."""
    returned = {parse_date(x) for _, _, r in returned_per_window for x in r}
    missing: List[str] = []
    for entry in calendar:
        if entry["source"] != "projected" or entry["date"] == "?":
            continue
        d = parse_date(entry["date"])
        for ws, we, _ in returned_per_window:
            if ws <= d <= we and d not in returned:
                missing.append(d.isoformat())
                break
    return missing
