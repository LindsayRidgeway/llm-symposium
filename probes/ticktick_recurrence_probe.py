#!/usr/bin/env python3
"""TickTick recurrence probe for the LLM Symposium.

Re-runnable verification artifact for the protocol in
`workarounds/ticktick-future-recurrence-workaround.md` (Gap D from
`discussions/deepseek-review.md`). Any future model instance can run this
against recorded fixtures instead of trusting the narrative.

Usage:
    python3 probes/ticktick_recurrence_probe.py [fixture.json] [--api-token TOKEN]

The Gap C layer-isolation check (direct TickTick Open API call vs. connector
behavior) runs when a token is available. Per the workaround protocol, prefer
the environment variable — command-line tokens can leak via shell history and
process listings:

    TICKTICK_API_TOKEN=...  python3 probes/ticktick_recurrence_probe.py
    TICKTICK_API_KEY=...    python3 probes/ticktick_recurrence_probe.py

`TICKTICK_API_KEY` is accepted as the repository-secret name; the verification
workflow (`.github/workflows/test-and-report.yml`) exposes the repo secret
under the canonical `TICKTICK_API_TOKEN` name. `--api-token` remains as a
fallback for ad-hoc runs. Without any token, layer attribution is reported as
unverified.

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
    """Gap C: hit the TickTick Open API directly.

    Two endpoints are probed so the token's validity can be proven
    independently of the task-list endpoint shape (established empirically on
    2026-08-28; see `workarounds/ticktick-connector-behavior-log.md`):

    - `GET  /open/v1/project` — documented endpoint; an HTTP 200 proves the
      token is valid and returns the account's projects.
    - `POST /open/v1/task/query` — candidate task-list endpoint. (`POST
      /open/v1/task` alone is *create-task* semantics: an empty body is
      rejected with "task title is empty".)

    Requires an OAuth access token; without one we cannot run the isolation
    test. Response bodies are captured because TickTick puts the real reason
    (invalid_token, ...) there.
    """
    import urllib.error
    import urllib.request

    results: dict = {}

    def _call(name: str, url: str, method: str = "GET", data: bytes | None = None) -> dict:
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8", errors="replace")[:500]
                return {"ok": True, "status": resp.status, "body": body}
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")[:500]
            except Exception:  # noqa: BLE001
                body = ""
            return {"ok": False, "status": e.code, "body": body}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "status": None, "body": str(e)}

    results["projects"] = _call("projects", "https://api.ticktick.com/open/v1/project")
    results["tasks"] = _call(
        "tasks", "https://api.ticktick.com/open/v1/task/query", method="POST", data=b"{}")
    return results


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
        results = check_live_api(api_token)
        lines.append("Direct TickTick Open API checks (Bearer token from env / repo secret):")
        lines.append("")
        for name, r in results.items():
            status = r.get("status")
            if r.get("ok"):
                try:
                    n = len(json.loads(r.get("body") or "[]"))
                except Exception:  # noqa: BLE001
                    n = "?"
                lines.append(f"- `{name}`: **HTTP {status} OK** — returned {n} item(s).")
            else:
                snippet = (r.get("body") or "(no response body)")[:200]
                lines.append(f"- `{name}`: **HTTP {status}** — `{snippet}`")
        lines.append("")
        if results.get("projects", {}).get("ok"):
            lines.append("Token validity: **confirmed** (projects endpoint authorized). "
                         "Layer attribution now hinges on the task-list endpoint shape; "
                         "record the comparison in `workarounds/ticktick-connector-behavior-log.md`.")
        else:
            lines.append("Token validity: **not confirmed** — verify the value stored in the "
                         "repository secret `TICKTICK_API_KEY` is a TickTick OAuth access token.")
        lines.append("")
    else:
        lines.append("No TickTick token provided (env `TICKTICK_API_TOKEN`/`TICKTICK_API_KEY` "
                     "or `--api-token`). Direct API isolation test **not run**; layer "
                     "attribution remains unverified. Add the repository secret and re-run to close Gap C.")
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

    # Workaround protocol: prefer the environment variable (a CLI token can
    # leak via shell history / process listings). Accept both the canonical
    # name and the repository-secret name.
    token = (
        args.api_token
        or os.environ.get("TICKTICK_API_TOKEN")
        or os.environ.get("TICKTICK_API_KEY")
    )

    report = run(args.fixture, token)
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
