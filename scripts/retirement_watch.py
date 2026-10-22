#!/usr/bin/env python3
# Owner: Desi (hosts watch). Filed 2026-10-17.
"""Turn the vendors' retirement calendar into a deadline something can notice.

`research/hosts-watch.md` dates the events the four hosts have published: a model retired, a
price doubled, a promotional rate that ends. Three readings produced that table and none of
them made it load-bearing — a date in a document is a fact that waits for a reader, and the
readers here are wakes with no memory of the last one. The largest live risk in the table is
concrete: `claude-sonnet-4-5` is retired **2026-11-30** and requests to it will then *fail*,
and that name is what `ANTHROPIC_MODEL` is set to. Without this script, the first symptom is
Claude's daily route going silent, which looks exactly like a quiet day.

What it does: reads the calendar table out of the document, reports how many days are left on
each row, and exits non-zero when a row that **stops a route working** is inside the warning
window. It knows a date has been dealt with: if the model a row names is no longer set in
`governance/model-settings.md`, the row prints as `resolved` and stops counting. That check is
the point — the calendar clears itself when someone does the swap, instead of nagging forever
and training the reader to ignore it.

What it deliberately does not do: fetch the vendors' pages (`scripts/hosts_watch.py --fetch`
does that), decide whose problem a row is, or change a model. A model swap is a written
decision with a before/after test, not a quiet rename — this instrument dates the deadline.

Usage:
    python3 scripts/retirement_watch.py                  # today, 30-day warning, 180-day view
    python3 scripts/retirement_watch.py --as-of 2026-11-10 --warn 21
    python3 scripts/retirement_watch.py --json

Exit status: 0 = nothing to act on inside the window; 1 = a `route` row is inside it (a model
we set stops answering); 2 = the calendar could not be read — said out loud, never a green
build over an empty table.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "research" / "hosts-watch.md"
SETTINGS = ROOT / "governance" / "model-settings.md"

# What a row can do to us.
#   route — the model we set stops answering on that date.
#   cost  — the price we pay for a model we set moves on that date.
#   —     — none of ours: somebody else's snapshot, a plan we never adopted.
IMPACTS = {"route", "cost", "—"}

_TOKEN = re.compile(r"`([A-Za-z0-9][A-Za-z0-9._/\-]*)`")


def parse_calendar(text: str) -> list[dict]:
    """Rows of the calendar table: date, event, owner, impact, the models it names.

    A row without a fourth cell is returned with `impact: None` rather than dropped — an
    unclassified row is a defect in the document, and dropping it is how a table becomes a
    green light over nothing. The caller decides what to do with them; this function does not
    guess.
    """
    rows = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        if not re.match(r"^\|\s*\d{4}-\d{2}-\d{2}\s*\|", s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 3:
            continue
        try:
            when = datetime.strptime(cells[0], "%Y-%m-%d").date()
        except ValueError:
            continue
        event = cells[1]
        rows.append(
            {
                "date": when,
                "event": event,
                "owner": cells[2],
                "impact": cells[3] if len(cells) >= 4 and cells[3] in IMPACTS else None,
                "models": _TOKEN.findall(event),
                # Where the row came from, so a refusal can name the line to fix instead of
                # only the shape of the fault. Added 2026-10-22: a wake lost its landing to the
                # assertion "a row lost its Impact cell" and no row was ever named, so the run
                # ended without knowing what to fix. `fourth` is the cell as written, which is
                # the difference between "no fourth cell" and "a fourth cell that is not an
                # impact word" — a summary table read as calendar rows looks exactly like this.
                "line": lineno,
                "raw": s,
                "fourth": cells[3] if len(cells) >= 4 else None,
            }
        )
    return rows


def unclassified(rows: list[dict]) -> list[dict]:
    """The rows this file could read as calendar rows but could not classify. Empty is healthy."""
    return [r for r in rows if r.get("impact") is None]


def describe_unclassified(rows: list[dict], doc: str = "research/hosts-watch.md") -> str:
    """Say *which* lines are unclassified, what their fourth cell actually holds, and what to do.

    This file is both prose and a machine-read calendar: any line beginning with a date is a
    calendar row. So a human-readable summary table pasted in beside the calendar is not a
    formatting wart — it is three fake rows and a `verdict` of 2. The message carries the line
    number because the reader is an instrument's stderr, or a failing assertion, in a run that
    is about to end; "a row lost its Impact cell" tells that reader nothing it can act on.
    """
    bad = unclassified(rows)
    if not bad:
        return ""
    out = [
        f"{doc}: {len(bad)} line(s) begin with a date but carry no Impact cell — "
        f"`route`, `cost` or `—` belongs in the fourth column:"
    ]
    for r in bad:
        fourth = (
            "no fourth cell at all"
            if r.get("fourth") is None
            else f"fourth cell is {r['fourth']!r}"
        )
        out.append(f"  line {r.get('line', '?')}: {fourth}")
        out.append(f"    {str(r.get('raw', ''))[:160]}")
    out.append(
        "Every line in this file that starts with a date is read as a calendar row. Fix one of "
        "two ways: give it an Impact cell in the fourth column, or stop the row starting with a "
        "date (a derived or summary table belongs with another column first)."
    )
    return "\n".join(out)


def is_set(model: str, settings_text: str) -> bool:
    """Is `model` still named as a route in governance/model-settings.md?

    Boundaries matter here: `claude-sonnet-4-5` is a prefix of `claude-sonnet-4-5-20250929`,
    and telling those two apart is the difference between "the swap was done" and "it was not".
    """
    pat = r"(?<![\w.\-/])" + re.escape(model) + r"(?![\w.\-/])"
    return re.search(pat, settings_text) is not None


def assess(rows: list[dict], settings_text: str, as_of: date, warn: int, window: int) -> list[dict]:
    """Attach days-left, whether the row still touches us, and a status. Pure."""
    out = []
    for r in rows:
        days = (r["date"] - as_of).days
        subject = r["models"][0] if r["models"] else None
        # Only our own rows can be resolved by a swap. A row marked `—` is not ours to clear:
        # printing it as "resolved" would claim credit for work nobody did.
        resolved = (
            r["impact"] in ("route", "cost")
            and bool(subject)
            and not is_set(subject, settings_text)
        )
        if resolved:
            status = "resolved"
        elif days < 0:
            status = "past"
        elif days <= warn:
            status = "due" if r["impact"] == "route" else "soon"
        elif days <= window:
            status = "ahead"
        else:
            status = "far"
        out.append({**r, "days": days, "subject": subject, "resolved": resolved, "status": status})
    out.sort(key=lambda r: (r["date"], r["event"]))
    return out


def verdict(rows: list[dict]) -> int:
    """The exit code, from what `assess` found. Unreadable beats close: say nothing rather than 0."""
    if not rows:
        return 2
    if any(r["impact"] is None for r in rows):
        return 2
    if any(r["status"] == "due" for r in rows):
        return 1
    return 0


def render(rows: list[dict], as_of: date, warn: int, window: int) -> str:
    lines = [
        f"retirement watch — as of {as_of.isoformat()}, warning window {warn}d, view {window}d",
        f"source: research/hosts-watch.md · routes: governance/model-settings.md",
        "",
    ]
    shown = [r for r in rows if r["status"] in ("resolved", "past", "due", "soon", "ahead")]
    if not shown:
        lines.append(f"(no dated event inside the next {window} days)")
    for r in shown:
        mark = {"due": "**", "past": "!", "resolved": "="}.get(r["status"], " ")
        if r["status"] == "soon" and r["impact"] == "cost":
            mark = "*"
        lines.append(
            f"{mark:2} {r['date'].isoformat()}  {r['days']:>5}d  {r['impact'] or '?':5}  "
            f"{r['status']:<8}  {r['event']}"
        )
    unknown = unclassified(rows)
    if unknown:
        lines += ["", f"UNCLASSIFIED ({len(unknown)}):", describe_unclassified(rows)]
    due = [r for r in rows if r["status"] == "due"]
    lines += [""]
    if due:
        for r in due:
            lines.append(
                f"ACT: {r['date'].isoformat()} ({r['days']}d) retires `{r['subject']}`, "
                f"which is still set in governance/model-settings.md — needs a swap decision "
                f"with a written reason and a before/after test."
            )
    else:
        lines.append("nothing to act on: no route-stopping event inside the warning window.")
    lines.append(
        "* soon (price moves) · ** due (route stops) · ! already past · = resolved, the named "
        "model is no longer set in model-settings.md"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Days left on the vendors' retirement calendar.")
    ap.add_argument("--as-of", default=None, help="YYYY-MM-DD (default: today, UTC)")
    ap.add_argument("--warn", type=int, default=30, help="days before a route event counts as due")
    ap.add_argument("--window", type=int, default=180, help="how far ahead to print")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--doc", default=str(DOC))
    ap.add_argument("--settings", default=str(SETTINGS))
    args = ap.parse_args(argv)

    as_of = (
        datetime.strptime(args.as_of, "%Y-%m-%d").date()
        if args.as_of
        else datetime.now(tz=None).date()
    )
    try:
        text = Path(args.doc).read_text(encoding="utf-8")
        settings_text = Path(args.settings).read_text(encoding="utf-8")
    except OSError as e:
        print(f"retirement_watch: cannot read the record: {e}", file=sys.stderr)
        return 2

    rows = assess(parse_calendar(text), settings_text, as_of, args.warn, args.window)
    code = verdict(rows)
    if code == 2 and not rows:
        print(f"retirement_watch: no calendar rows parsed from {args.doc} — the table moved or "
              f"changed shape. Fix the reader rather than reading a green build as good news.",
              file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(
            {
                "as_of": as_of.isoformat(),
                "warn": args.warn,
                "window": args.window,
                "rows": [
                    {**r, "date": r["date"].isoformat()} for r in rows
                ],
            },
            indent=2,
        ))
    else:
        print(render(rows, as_of, args.warn, args.window))
    return code


if __name__ == "__main__":
    sys.exit(main())
