#!/usr/bin/env python3
"""TickTick recurrence probe for the LLM Symposium.

Re-runnable verification artifact for the protocol in
`workarounds/ticktick-future-recurrence-workaround.md` (Gap D from
`discussions/deepseek-review.md`). Any future model instance can run this
against recorded fixtures instead of trusting the narrative.

Usage:
    python3 probes/ticktick_recurrence_probe.py [fixture.json] [--api-token TOKEN]

If --api-token is provided, the probe also attempts the Gap C layer-isolation
check (direct TickTick Open API call vs. connector behavior). Without it, layer
attribution is reported as unverified.

Writes a dated markdown report to probes/results/.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from recurrence_projection import (  # noqa: E402
    DEFAULT_HORIZON_DAYS,
    MAX_PROJECTED_INSTANCES,
    RecurringTask,
    parse_date,
    probe_overlap,
    projected_but_not_returned,
    project_task,
)


def load_fixture(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_live_api(token: str) -> dict:
    """Gap C: hit the TickTick Open API directly for the task list.

    Compare against what the connector returns to attribute the failure layer.
    Requires an OAuth access token; without one we cannot run the isolation test.
    """
    import urllib.request

    req = urllib.request.Request(
        "https://api.ticktick.com/open/v1/task",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {"ok": True, "tasks": json.load(resp)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


def run(fixture_path: str, api_token: str | None = None) -> str:
    fix = load_fixture(fixture_path)
    horizon = int(fix.get("horizon_days", DEFAULT_HORIZON_DAYS))
    limit = int(fix.get("max_projected", MAX_PROJECTED_INSTANCES))

    # Parse probe windows once: (start, end, returned_by_series)
    windows = []
    for w in fix.get("probe_windows", []):
        ws, we = parse_date(w["range"][0]), parse_date(w["range"][1])
        windows.append((ws, we, w.get("returned", {})))

    lines: list[str] = []
    lines.append(f"# TickTick Recurrence Probe — {date.today().isoformat()}")
    lines.append("")
    # Privacy: never print absolute paths in reports (leaks host layout in public repos).
    shown_path = os.path.relpath(fixture_path) if os.path.isabs(fixture_path) else fixture_path
    lines.append(f"Fixture: `{shown_path}`  |  horizon={horizon}d  |  cap=N={limit}")
    lines.append("")
    lines.append("## Per-series projection")
    lines.append("")

    any_truncation = False
    for s in fix.get("series", []):
        task = RecurringTask(
            id=s["id"],
            title=s["title"],
            rrule=s.get("rrule"),
            explicit=s.get("explicit", []),
        )
        calendar, truncated = project_task(task, horizon_days=horizon, limit=limit)
        any_truncation = any_truncation or truncated

        lines.append(f"### {task.id} — {task.title}")
        lines.append("")
        lines.append("| Date | Source | Status |")
        lines.append("|------|--------|--------|")
        for e in calendar:
            date_cell = e["date"]
            if e["source"] == "projected":
                date_cell += " *(projected)*"
            lines.append(f"| {date_cell} | {e['source']} | {e['status']} |")
        if truncated:
            lines.append("")
            lines.append(f"⚠ **Truncated at {limit} projected instances** — label any downstream "
                         "calendar `[Truncated at N]` (Gap A).")
        lines.append("")

    # ---- Gap B: truncation probes ----
    lines.append("## Truncation probe (positive check for a silent under-returning connector)")
    lines.append("")
    lines.append("For every pair of windows, compare instances returned in their shared date range.")
    lines.append("")
    series_ids = [s["id"] for s in fix.get("series", [])]
    overlap_report = []
    for i in range(len(windows)):
        for j in range(i + 1, len(windows)):
            ws_a, we_a, ret_a = windows[i]
            ws_b, we_b, ret_b = windows[j]
            overlap_start = max(ws_a, ws_b)
            overlap_end = min(we_a, we_b)
            if overlap_start > overlap_end:
                continue
            for sid in series_ids:
                ra = ret_a.get(sid, [])
                rb = ret_b.get(sid, [])
                res = probe_overlap(ra, rb, overlap_start, overlap_end)
                tag = "⚠ DIVERGENCE" if res["divergent"] else "ok"
                if res["divergent"]:
                    any_truncation = True
                overlap_report.append((tag, f"{windows[i][0]}..{windows[i][1]} vs "
                                          f"{windows[j][0]}..{windows[j][1]}",
                                       sid, res))

    if overlap_report:
        lines.append("| Window pair | Series | Result |")
        lines.append("|-------------|--------|--------|")
        for tag, pair, sid, res in overlap_report:
            detail = ""
            if res["in_b_not_a"]:
                detail = f" (in B not A: {res['in_b_not_a']})"
            elif res["in_a_not_b"]:
                detail = f" (in A not B: {res['in_a_not_b']})"
            lines.append(f"| {pair} | {sid} | {tag}{detail} |")
        lines.append("")

    # ---- Projected-but-not-returned (also Gap B evidence) ----
    lines.append("### Projected dates absent from connector output")
    lines.append("")
    for s in fix.get("series", []):
        task = RecurringTask(
            id=s["id"],
            title=s["title"],
            rrule=s.get("rrule"),
            explicit=s.get("explicit", []),
        )
        calendar, _ = project_task(task, horizon_days=horizon, limit=limit)
        per_window = [(ws, we, ret.get(s["id"], [])) for ws, we, ret in windows]
        missing = projected_but_not_returned(calendar, per_window)
        if missing:
            any_truncation = True
            lines.append(f"- **{s['id']}**: projected but not returned by any probe window → {missing}")
        else:
            lines.append(f"- {s['id']}: all projected occurrences were returned or outside probe ranges.")
    lines.append("")

    # ---- Gap C: layer attribution ----
    lines.append("## Layer attribution (Gap C)")
    lines.append("")
    if api_token:
        result = check_live_api(api_token)
        if result.get("ok"):
            tasks = result["tasks"]
            lines.append(f"Direct TickTick Open API returned {len(tasks)} task(s). "
                         "Compare against connector output to attribute the failure layer; "
                         "record the comparison in `workarounds/ticktick-connector-behavior-log.md`.")
        else:
            lines.append(f"Direct API check failed: {result.get('error')}")
            lines.append("Layer attribution remains **unverified**.")
    else:
        lines.append("No `--api-token` provided. Direct API isolation test **not run**; "
                     "layer attribution remains unverified. Re-run with `--api-token` to close Gap C.")
    lines.append("")

    verdict = "TRUNCATION EVIDENCE FOUND" if any_truncation else "NO TRUNCATION EVIDENCE"
    lines.append(f"## Verdict: **{verdict}**")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", nargs="?", default=os.path.join(
        os.path.dirname(__file__), "fixtures", "example.json"))
    parser.add_argument("--api-token", default=None)
    args = parser.parse_args()

    report = run(args.fixture, args.api_token)
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, f"{date.today().isoformat()}-probe-report.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\n[report written to {out_path}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
