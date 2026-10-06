#!/usr/bin/env python3
# Owner: Desi
"""The daily item report — the human's request of 2026-10-06.

His words: stop sending a report of what each wake did; once a day, send counts for the last 24
hours and for life, for N (items performed during wakes), A (reviewed and accomplished), P
(reviewed and postponed) and R (rejected and never to be accomplished), each split by amigo and by
internal/external, plus the titles added in the last 24 hours and the titles still postponed with
the reason each is postponed.

He reads this to answer three questions: is each amigo doing more or less than before (N and A),
is the work reaching the world or only the repository (external vs internal), and is the pile of
postponed work growing. So the report leads with the counts and never buries the external/internal
split, because that split is the one he says is about the symposium's survival.

It is written to be read on a phone: one line per amigo, no table that wraps, and the detail lists
trimmed with an honest "+k more" rather than silently truncated.

Usage:
    python3 scripts/daily_report.py                 # render to stdout
    python3 scripts/daily_report.py --send          # render, send to the human, record it
    python3 scripts/daily_report.py --hours 24 --send
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels.item_ledger import collect, counts, load  # noqa: E402

GROUP_LABEL = {
    "N": "N — performed",
    "A": "A — accomplished",
    "P": "P — postponed",
    "R": "R — rejected",
    "U": "U — performed, not yet reviewed",
}
AMIGO_ORDER = ("desi", "claude", "gemini", "tarik", "dmitri")
LIST_CAP = 10


def _local(stamp: dt.datetime) -> str:
    return stamp.astimezone().strftime("%Y-%m-%d %H:%M %Z")


def _group_table(group: str, window: dict, life: dict) -> list[str]:
    """One line per amigo, for one group. Compact enough not to wrap on a phone."""
    out = [GROUP_LABEL[group]]
    names = [n for n in AMIGO_ORDER if n in window[group]["by_amigo"]]
    names += [n for n in sorted(window[group]["by_amigo"]) if n not in names]
    if not names:
        out.append("  (none)")
    for who in names:
        s = window[group]["by_amigo"][who]
        out.append(f"  {who:<8} {s['total']:>4}  ({s['internal']} int / {s['external']} ext)")
    life_s = life[group]
    out.append(f"  {'all':<8} {window[group]['total']:>4}  "
               f"({window[group]['internal']} int / {window[group]['external']} ext)"
               f"   lifetime {life_s['total']} ({life_s['internal']} / {life_s['external']})")
    return out


def _title_list(rows: list[dict], cap: int = LIST_CAP) -> list[str]:
    if not rows:
        return ["  (none)"]
    rows = sorted(rows, key=lambda r: r.get("filed_utc") or "")
    out = []
    for rec in rows[:cap]:
        group = {"accomplished": "A", "postponed": "P", "rejected": "R"}.get(rec.get("state"), "N")
        out.append(f"  [{group}] {rec.get('amigo','?'):<7} {rec.get('title','')}")
    if len(rows) > cap:
        out.append(f"  … +{len(rows) - cap} more in the recorded copy")
    return out


def render(hours: int = 24, now: dt.datetime | None = None) -> str:
    now = now or dt.datetime.now(dt.timezone.utc)
    items = load()
    window = counts(items, hours)
    life = counts(items, None)
    since = (now - dt.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%MZ")

    n, a, p, r, u = (life[g]["total"] for g in "NAPRU")
    lines = [
        f"**Daily item report — {_local(now)}**",
        f"window: the {hours}h to {_local(now)} (since {since})",
        "",
        "`N = A + P + R + U`. U is work performed and not yet reviewed — nothing in the commons",
        "reviews wake work, so U is where the review backlog sits, not a bookkeeping leftover.",
        "",
        f"**Lifetime**  N={n}  A={a}  P={p}  R={r}  U={u}"
        + ("  ✓ N=A+P+R+U" if n == a + p + r + u else "  ✗ the identity is broken — investigate"),
        f"**Last {hours}h**  N={window['N']['total']}  A={window['A']['total']}  "
        f"P={window['P']['total']}  R={window['R']['total']}  U={window['U']['total']}",
        "",
        f"### Last {hours}h, by amigo",
    ]
    for group in "NAPRU":
        lines += _group_table(group, window, life)
    lines += [
        "",
        f"### Titles added in the last {hours}h",
        f"**Internal** ({window['N']['internal']})",
    ]
    lines += _title_list([x for x in window["items"] if x.get("scope") == "internal"])
    lines += [f"**External** ({window['N']['external']})"]
    lines += _title_list([x for x in window["items"] if x.get("scope") == "external"])

    postponed = [x for x in items.values() if x.get("state") == "postponed"]
    lines += ["", f"### Currently postponed ({len(postponed)})"]
    for scope in ("internal", "external"):
        rows = [x for x in postponed if x.get("scope") == scope]
        lines.append(f"**{scope.title()}** ({len(rows)})")
        if not rows:
            lines.append("  (none)")
        for rec in sorted(rows, key=lambda x: x.get("filed_utc") or ""):
            lines.append(f"  {rec.get('amigo','?'):<7} {rec.get('title','')}")
            lines.append(f"          why: {rec.get('reason','(no reason recorded)')}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--amigo", default="desi")
    ap.add_argument("--no-collect", action="store_true",
                    help="skip ingesting new runs first (for a reproducible re-render)")
    a = ap.parse_args()

    if not a.no_collect:
        collect()
    text = render(a.hours)
    if not a.send:
        print(text)
        return 0

    out = REPO / "channels" / "reports" / f"daily-{dt.datetime.now():%Y-%m-%d}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    # Telegram caps a message near 4096 characters. Never let a cap silently eat the counts: the
    # counts are at the top, the item lists are at the bottom, so the tail is what gets dropped.
    sent = text
    if len(sent) > 3900:
        sent = sent[:3860].rsplit("\n", 1)[0] + f"\n\n[…trimmed; full report: {out.name}]"
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "tell_human.py"), "--amigo", a.amigo,
         "--text", sent],
        capture_output=True, text=True, timeout=120,
    )
    print(r.stdout.strip() or r.stderr.strip())
    print(f"daily_report: recorded {out.relative_to(REPO)} ({len(text)} chars, sent {len(sent)})")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
