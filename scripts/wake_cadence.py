#!/usr/bin/env python3
# Owner: Desi
"""Measure how often each amigo actually wakes, and check the capacity table against it.

**The defect this answers.** `channels/item_ledger.py` shares the never-read pile by a table,
`WAKES_PER_DAY`, because a name on a body that does not wake is a name on nothing. That table is
hand-written and dated, and its own comment says it is "re-measured the same way" — by a person
opening the run directories and counting. It has already been wrong once: on 2026-10-22 the
morning table said `tarik: 1` and named 9 of the 252 pile items to him when the answer was about
22. Nothing noticed. A person did, hours later.

**What it found on its first run, 2026-10-25.** Tarik is carrying weight 3 in the table and 22 of
the never-read items. His last goose run directory is `20261019T170221Z-c56a22e8`. His app
(the `codex-` id prefix in `channels/items.jsonl`) filed at 00:02, 04:02, 08:03, 16:00 and 20:00
UTC daily through 2026-10-23, and then stopped: the last row is `codex-20261023T200050Z-61cf96dc`.
So the table has been handing out reading to a body that has produced no evidence of waking for
about a day and a half, and no goose wake in six days. That is not an accusation — an app can be
restarted, a quota can be hit, a key can expire — it is a *measurement*, which is the one thing
nobody had.

**What this script deliberately does not do: rewrite the table.** The draw is frozen to the item —
that is the rule, and it is what makes a name mean something rather than drift to whoever spoke
last. A script that quietly re-weighted would re-name work in flight without anyone deciding to.
So this prints the weights it measures and a person changes the table, on the record, with a
reason. `--rebalance-unread` in `item_ledger.py` is the honest one-off exception, and it needs a
human-shaped decision behind it, not a cron.

**What counts as evidence of a wake, and what does not.** Two sources, unioned per amigo:

  1. a run directory, `<runs-root>/<amigo>-bot/tick-state/runs/<YYYYMMDDTHHMMSSZ>-<hex>/`;
  2. a row in the item ledger carrying that amigo's name and a timestamped id.

Source 2 exists because source 1 is not universal: the Tarik app writes work into the ledger from
somewhere that leaves no local run directory, and on 2026-10-23 it filed five times while the
`tarik-bot` run tree was already four days cold. Measuring only the run tree would have called the
app dead while it was working. Measuring only the ledger would have called Tarik-goose alive on the
app's rows. Neither source alone is the roster; the union is the least wrong thing available, and
the per-source breakdown is printed so a reader can see which one went quiet.

The reverse is also true and worth saying plainly: **no evidence is not proof of no work.** A
participant can read without filing. What this measures is filing, and it says so.

Usage:
  python3 scripts/wake_cadence.py                      # measure, and check the table
  python3 scripts/wake_cadence.py --weights            # the table line a person would commit
  python3 scripts/wake_cadence.py --json               # the same, for another program
  python3 scripts/wake_cadence.py --obligations        # verdicts returned vs review debt carried
  python3 scripts/wake_cadence.py --window-days 14 --silent-after-hours 36
  python3 scripts/wake_cadence.py --now 2026-10-25T11:25:40Z   # reproducible readings

Exit code is 0 when the table matches the measurement, 1 when it does not. That is a report to a
person, not a gate: nothing in CI runs this, and it should not be wired as one until someone
decides what a stale table ought to *block*, which is a governance question and not a script's.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUNS_ROOT = Path.home() / "LLM"
DEFAULT_LEDGER = REPO_ROOT / "channels" / "items.jsonl"

AMIGOS = ("desi", "gemini", "claude", "tarik", "dmitri")

# A timestamp inside a run id or a ledger id: 20261025T112540Z-afa56ed9.
STAMP_RE = re.compile(r"(\d{8})T(\d{6})Z")


def parse_stamp(text: str) -> dt.datetime | None:
    """The UTC instant an id carries, or None. Never guesses from a neighbouring field.

    Two shapes are accepted because the repository uses both: the compact id form
    (`20261025T112540Z-afa56ed9`, run directories and item ids) and ISO (`2026-10-25T11:25:40Z`,
    `filed_utc` and `--now`). A date with no time is read as midnight UTC, which is wrong by
    under a day and is only ever used as a fallback when the id carries no stamp at all.
    """
    m = STAMP_RE.search(text or "")
    if m:
        try:
            return dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").replace(
                tzinfo=dt.timezone.utc)
        except ValueError:
            return None
    try:
        parsed = dt.datetime.fromisoformat((text or "").strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)


def scan_runs(root: Path) -> dict[str, list[dt.datetime]]:
    """Wakes with a run directory of their own, per amigo. Absent tree is empty, not an error."""
    out: dict[str, list[dt.datetime]] = {a: [] for a in AMIGOS}
    for amigo in AMIGOS:
        runs = Path(root) / f"{amigo}-bot" / "tick-state" / "runs"
        if not runs.is_dir():
            continue
        for child in runs.iterdir():
            if not child.is_dir():
                continue
            when = parse_stamp(child.name)
            if when:
                out[amigo].append(when)
    return out


def scan_ledger(path: Path) -> dict[str, list[dt.datetime]]:
    """Filings in the item ledger, per amigo. One row per id, not per appended line."""
    out: dict[str, list[dt.datetime]] = {a: [] for a in AMIGOS}
    p = Path(path)
    if not p.is_file():
        return out
    seen: set[str] = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        amigo = (rec.get("amigo") or "").lower()
        ident = rec.get("id") or ""
        if amigo not in out or ident in seen:
            continue
        when = parse_stamp(ident) or parse_stamp(rec.get("filed_utc") or "")
        if not when:
            continue
        seen.add(ident)
        out[amigo].append(when)
    return out


def cadence(events: dict[str, list[dt.datetime]], now: dt.datetime,
            window_days: int = 7) -> dict[str, dict]:
    """Per amigo: wakes in the window, wakes per day over it, and hours since the last one.

    Wakes per day is normalised over the window actually covered — an amigo whose first waking
    predates the window is divided by the window, so a body that stopped mid-window is not
    flattered by the days it was already dead. `None` means no evidence at all, which is a
    different statement from zero and must not print as one.
    """
    start = now - dt.timedelta(days=window_days)
    out: dict[str, dict] = {}
    for amigo in AMIGOS:
        stamps = sorted(set(events.get(amigo, [])))
        in_window = [t for t in stamps if t >= start]
        last = stamps[-1] if stamps else None
        out[amigo] = {
            "wakes_in_window": len(in_window),
            "wakes_per_day": (len(in_window) / window_days) if in_window else 0.0,
            "last_utc": last.strftime("%Y-%m-%dT%H:%M:%SZ") if last else None,
            "hours_since": (round((now - last).total_seconds() / 3600.0, 1)
                            if last else None),
        }
    return out


def check_table(measured: dict[str, dict], table: dict[str, int], now: dt.datetime,
                silent_after_hours: float = 30.0, tolerance: float = 0.5) -> list[str]:
    """Every way the frozen table and the measurement disagree, in plain sentences."""
    warnings: list[str] = []
    for amigo in AMIGOS:
        weight = table.get(amigo, 1)
        m = measured[amigo]
        per_day = m["wakes_per_day"]
        hours = m["hours_since"]
        if hours is None:
            warnings.append(
                f"{amigo}: weight {weight} in the table, and no evidence of any wake in the "
                f"ledger or the run tree at all")
            continue
        if hours > silent_after_hours:
            warnings.append(
                f"{amigo}: weight {weight} in the table, but the last evidence of a wake is "
                f"{hours:g}h ago ({m['last_utc']}) — silence past {silent_after_hours:g}h")
        if per_day > 0 and weight > 0:
            ratio = per_day / weight
            if ratio < 1 - tolerance or ratio > 1 + tolerance:
                warnings.append(
                    f"{amigo}: table says {weight} wake(s)/day, measured {per_day:.1f} over the "
                    f"window — the table is {abs(1 - ratio) * 100:.0f}% out")
    return warnings


def weights_line(measured: dict[str, dict]) -> str:
    """The table line a person would commit. Printed, never written — see the module docstring."""
    parts = []
    for amigo in AMIGOS:
        raw = measured[amigo]["wakes_per_day"]
        whole = max(1, int(round(raw)))
        parts.append(f'"{amigo}": {whole}')
    return "WAKES_PER_DAY = {" + ", ".join(parts) + "}"


# The reviewers that are not a reader. `auto:land` closes a run whose own gate passed, `auto:path`
# closes an item whose named files exist; neither has read anything, and the ledger already keeps
# them apart from a model (`item_ledger.MACHINE_REVIEWERS`). Duplicated here on purpose: this
# script must keep measuring when `item_ledger` cannot be imported.
MACHINE_REVIEWERS = ("auto:land", "auto:path", "auto")


def _last_rows(path: Path) -> dict[str, dict]:
    """One record per id, choosing the way the ledger's own `load()` chooses.

    An append-only file repeats an item on every state change, so a reader that takes the last
    line can walk a verdict backwards when a slower writer lands after a faster one. The ledger
    settled this on 2026-10-27: the newest *stamped* verdict wins, and only rows with no stamp fall
    back to file order. This mirrors that, so the obligation counts here cannot disagree with the
    queues a wake reads.
    """
    by_id: dict[str, list[dict]] = {}
    p = Path(path)
    if not p.is_file():
        return {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if not isinstance(rec, dict) or not rec.get("id"):
            continue
        by_id.setdefault(rec["id"], []).append(rec)
    out: dict[str, dict] = {}
    for item_id, recs in by_id.items():
        stamped = [(i, r) for i, r in enumerate(recs)
                   if r.get("state") and parse_stamp(r.get("state_utc") or "")]
        if stamped:
            # Ties on the stamp go to the later line: two rows can share a `state_utc` (an
            # assignment copies the record it is assigning), and the later one carries the fields
            # the earlier lacks — `reading_assigned_to`, which is how a never-read item is reached.
            out[item_id] = max(stamped, key=lambda t: (parse_stamp(t[1].get("state_utc") or ""),
                                                       t[0]))[1]
        else:
            out[item_id] = recs[-1]
    return out


def obligations(ledger_path: Path, now: dt.datetime, window_days: int = 7) -> dict[str, dict]:
    """Per amigo: verdicts actually returned, and review debt carried right now.

    **Why this is not the same number as a wake.** On 2026-10-25 this script established that a
    weight is a capacity and not a heartbeat — a body that does not wake cannot read. Measured
    2026-10-28, that is still one number short of the question the draw is really asking. Over the
    ledger's whole history, 781 items, 358 were read by a model: desi 289, dmitri 281, tarik 51,
    gemini 26, and **claude zero**. Claude wakes once a day (weight 1 in the table, the lowest) and
    returned no verdict in the window either, while carrying 4 waiting items and 14 never-read ones
    — 18 of the commons' 183 open review obligations, on the one body that has never once closed
    one. Gemini wakes 5.9 times a day and reads at about a fifth of dmitri's rate: 20 verdicts in
    seven days against 90.

    So the weight a drawn name should be scaled by is the *verdict rate*, and nothing has ever
    measured it. This function does, and it does not re-name anything: the draw is frozen to the
    item, and re-weighting work in flight is a person's decision with a reason on the record, not a
    cron (see the module docstring). What it can do is stop the debt being invisible.

    A verdict is a row with a terminal state and a reviewer that is not a machine. Debt is two
    disjoint piles, both of which a model still owes a read: `waiting` (no terminal state, carrying
    `assigned_to`) and `unread` (closed by a machine, never opened by a model, carrying
    `reading_assigned_to`). A machine *postponement* is debt too — it is a closure with no reader
    behind it — so it is counted separately rather than being either hidden or mixed in.
    """
    rows = _last_rows(ledger_path)
    since = now - dt.timedelta(days=window_days)
    unnamed_unread = 0
    out = {a: {"verdicts_in_window": 0, "verdicts_lifetime": 0, "waiting": 0,
               "unread": 0, "machine_postponed": 0, "last_verdict_utc": None} for a in AMIGOS}
    for rec in rows.values():
        state = rec.get("state")
        reviewer = (rec.get("reviewer") or "")
        if state and reviewer and reviewer not in MACHINE_REVIEWERS and reviewer in out:
            stamp = parse_stamp(rec.get("state_utc") or "")
            out[reviewer]["verdicts_lifetime"] += 1
            if stamp and stamp >= since:
                out[reviewer]["verdicts_in_window"] += 1
            if stamp and (out[reviewer]["last_verdict_utc"] is None
                          or stamp > out[reviewer]["last_verdict_utc"]):
                out[reviewer]["last_verdict_utc"] = stamp
            continue
        if not state:
            who = rec.get("assigned_to")
            if who in out:
                out[who]["waiting"] += 1
        elif state == "accomplished" and reviewer in MACHINE_REVIEWERS:
            who = rec.get("reading_assigned_to")
            if who in out:
                out[who]["unread"] += 1
            elif not who:
                # A never-read item with no name is in no queue: `--holes` looks only at waiting
                # items. Counting it under nobody is how a census inherits the blind spot it was
                # written to find, so it is counted here and reported by `check_obligations`.
                unnamed_unread += 1
        elif state == "postponed" and reviewer in MACHINE_REVIEWERS:
            who = rec.get("assigned_to")
            if who in out:
                out[who]["machine_postponed"] += 1
    for amigo in AMIGOS:
        m = out[amigo]
        m["total"] = m["waiting"] + m["unread"] + m["machine_postponed"]
        m["verdicts_per_day"] = round(m["verdicts_in_window"] / window_days, 2) if window_days else 0.0
        m["last_verdict_utc"] = (m["last_verdict_utc"].strftime("%Y-%m-%dT%H:%M:%SZ")
                                if m["last_verdict_utc"] else None)
    out["_unnamed_unread"] = unnamed_unread
    return out


def check_obligations(oblig: dict[str, dict]) -> list[str]:
    """Debt carried by a body that is not returning verdicts — the sentence nobody was printing.

    Deliberately not a re-draw and not a gate on a body being quiet by choice: a person may read
    without filing, and the module docstring says so. What it refuses to do is let a pile sit on a
    name and call that shared.
    """
    warnings: list[str] = []
    if oblig.get("_unnamed_unread"):
        warnings.append(
            f"{oblig['_unnamed_unread']} never-read item(s) carry no name at all — no wake's "
            f"reading queue can reach them, and `--holes` does not look at this pile")
    for amigo in AMIGOS:
        m = oblig[amigo]
        if not m["total"]:
            continue
        if m["verdicts_lifetime"] == 0:
            warnings.append(
                f"{amigo}: carries {m['total']} review obligation(s) "
                f"({m['waiting']} waiting, {m['unread']} never-read) and has never returned a "
                f"verdict in the ledger at all")
        elif m["verdicts_in_window"] == 0:
            warnings.append(
                f"{amigo}: carries {m['total']} review obligation(s) and returned no verdict in "
                f"the window (last verdict {m['last_verdict_utc'] or 'unknown'})")
    return warnings


def table_from_item_ledger() -> tuple[dict[str, int], str]:
    """The frozen table as the draw uses it, or ({}, why not). An unread table is not a default."""
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from channels import item_ledger  # noqa: PLC0415 — optional, and reported when absent
        return dict(item_ledger.WAKES_PER_DAY), ""
    except Exception as exc:  # noqa: BLE001 — any failure is "we could not read it", not a crash
        return {}, f"could not read channels/item_ledger.py: {exc}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", default=str(DEFAULT_RUNS_ROOT))
    ap.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    ap.add_argument("--window-days", type=int, default=7)
    ap.add_argument("--silent-after-hours", type=float, default=30.0)
    ap.add_argument("--weights", action="store_true", help="print the table line to commit")
    ap.add_argument("--obligations", action="store_true",
                    help="verdicts each amigo actually returns, against the review debt it carries")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--now", default="")
    args = ap.parse_args()

    now = (parse_stamp(args.now) if args.now else
           dt.datetime.now(dt.timezone.utc).replace(microsecond=0))
    runs = scan_runs(Path(args.runs_root))
    filings = scan_ledger(Path(args.ledger))
    events = {a: runs.get(a, []) + filings.get(a, []) for a in AMIGOS}
    measured = cadence(events, now, args.window_days)
    table, why = table_from_item_ledger()
    warnings = check_table(measured, table, now, args.silent_after_hours) if table else []
    oblig = obligations(Path(args.ledger), now, args.window_days)
    oblig_warnings = check_obligations(oblig)

    if args.json:
        print(json.dumps({"measured": measured, "table": table, "warnings": warnings,
                          "obligations": oblig, "obligation_warnings": oblig_warnings,
                          "weights_line": weights_line(measured)}, indent=2))
        return 1 if warnings else 0

    print(f"wake cadence, {args.window_days}-day window ending {now.strftime('%Y-%m-%dT%H:%MZ')}")
    for amigo in AMIGOS:
        m = measured[amigo]
        last = m["last_utc"] or "no evidence"
        hours = "—" if m["hours_since"] is None else f"{m['hours_since']:g}h ago"
        print(f"  {amigo:8} {m['wakes_in_window']:>4} wakes  {m['wakes_per_day']:>5.1f}/day  "
              f"last {last}  ({hours})   [runs {len(runs.get(amigo, []))}, "
              f"ledger {len(filings.get(amigo, []))}]")
    if args.obligations:
        print(f"\nreview debt and verdicts, {args.window_days}-day window ending "
              f"{now.strftime('%Y-%m-%dT%H:%MZ')}")
        print(f"  {'amigo':8} {'verdicts':>9} {'/day':>6} {'waiting':>8} {'never-read':>11} "
              f"{'total':>6}  last verdict")
        for amigo in AMIGOS:
            m = oblig[amigo]
            print(f"  {amigo:8} {m['verdicts_in_window']:>9} {m['verdicts_per_day']:>6.2f} "
                  f"{m['waiting']:>8} {m['unread']:>11} {m['total']:>6}  "
                  f"{m['last_verdict_utc'] or 'never'}")
        if oblig_warnings:
            print()
            for w in oblig_warnings:
                print(f"  • {w}")
            print("\nThe draw is frozen to the item, so this is not a re-draw. It is the number the "
                  "weight is a proxy for: a body that returns no verdicts cannot drain a pile.")

    if args.weights:
        print()
        print(weights_line(measured))
        print("  ^ printed, not written: re-weighting re-names items already assigned, and that "
              "is a decision with a reason, not a cron.")
    if why:
        print(f"\nno table check: {why}")
    elif warnings:
        print(f"\n{len(warnings)} disagreement(s) between the table and the measurement:")
        for w in warnings:
            print(f"  • {w}")
        print("\nThe table is frozen on purpose. Change it by hand, with the reason, the way it was "
              "changed on 2026-10-22.")
        return 1
    elif table:
        print("\ntable matches the measurement for all five")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
