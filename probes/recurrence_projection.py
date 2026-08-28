"""Core recurrence projection logic for the LLM Symposium TickTick protocol.

Implements the protocol from
`workarounds/ticktick-future-recurrence-workaround.md`:

    explicit overrides + timezone-normalized bounded RRULE projection
        -> projected calendar

Pure functions only. No network or connector dependencies, so the logic is
reproducible anywhere and testable offline (see `tests/test_projection.py`).

Supported RRULE subset (documented limitation):
    FREQ=DAILY|WEEKLY|MONTHLY|YEARLY
    INTERVAL=n
    BYDAY=MO,TU,WE,TH,FR,SA,SU        (no ordinal prefixes like 1MO)
    COUNT=n  /  UNTIL=YYYYMMDD
"""

from __future__ import annotations

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
        if (d.month, d.day) != (base.month, base.day):
            return False
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
