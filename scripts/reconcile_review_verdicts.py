#!/usr/bin/env python3
"""Close ledger rows whose review verdict was already written in a landed report.

Why this exists
---------------
A review verdict and its ledger exit are two writes, and the second one is cheap to lose: the
reviewing wake writes a long, careful report first (which lands), then runs
`item_ledger.py --review <id> --state ... --reviewer ...` for each item it judged — and hits its
action cap in between. Measured on 2026-10-19: run `20261019T231043Z-1c5a0d0f` judged six items,
wrote every verdict into `channels/reports/2026-10-19-desi-mcr-france-trace-and-review-queue.md`,
and recorded none of them; the France item was still `waiting` the next day and was queued for a
second review. That is the same defect as a missing LAND line, one layer down: the work exists on
`main`, the record of it does not.

What this does, and what it refuses to do
-----------------------------------------
It reads the reports already on disk and closes a waiting row only when a report line names both
the item and a verdict word. It does NOT invent verdicts, does NOT touch a row that already has a
state, and does NOT let an item's own author review it. Where the evidence is thin it says so and
leaves the row alone — an empty queue built out of guesses is worse than a queue.

The reason it writes names the report and quotes the verdict, so a reader can check the closure
without trusting this script.

Usage
-----
    python3 scripts/reconcile_review_verdicts.py              # show what it would close
    python3 scripts/reconcile_review_verdicts.py --apply      # write the rows
    python3 scripts/reconcile_review_verdicts.py --only <id>  # one item
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REPORTS = REPO / "channels" / "reports"
AMIGOS = ("desi", "claude", "gemini", "tarik", "dmitri")
STATES = ("accomplished", "postponed", "rejected")

sys.path.insert(0, str(REPO / "channels"))
import item_ledger  # noqa: E402  (path set above; the ledger owns load/append/review)

import re  # noqa: E402

# An item id as reports actually print it: full, or truncated with an ellipsis
# ("codex-20261019T040208Z-…", "20261018T151657Z-…"), which is how reviewers abbreviate.
TOKEN_RE = re.compile(r"\b((?:codex-)?\d{8}T\d{6}Z(?:-[0-9a-f]{8})?(?:…|\.\.\.)?)")
STATE_RE = re.compile(r"\b(accomplished|postponed|rejected)\b", re.IGNORECASE)


def _clean(line: str) -> str:
    """Markdown emphasis and code ticks off, so `**accomplished.**` reads as a verdict."""
    return line.replace("**", "").replace("__", "").replace("`", "")


def report_author(path: Path) -> str | None:
    """The amigo a report is signed by, read from its filename (`2026-10-19-desi-...`)."""
    for part in path.stem.split("-"):
        if part in AMIGOS:
            return part
    return None


def verdict_reason(line: str, state: str) -> str:
    """The text the report gives *for* the verdict: the last table cell, else the trailing text."""
    cells = [c.strip() for c in line.split("|") if c.strip()]
    if len(cells) >= 3:
        for cell in reversed(cells):
            if cell.lower().strip(" .") != state.lower():
                return cell[:240]
    parts = STATE_RE.split(line, maxsplit=1)
    if len(parts) == 3 and parts[2].strip(" .—–-"):
        return parts[2].strip(" .—–-")[:240]
    return ""


def _label(path: Path) -> str:
    """How the report is named in the reason: repo-relative when it is in the tree, else as given."""
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def verdicts(path: Path) -> list[dict]:
    """Every (item token, verdict) pair a report states on one line."""
    out = []
    author = report_author(path)
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        clean = _clean(line)
        m = STATE_RE.search(clean)
        if not m:
            continue
        state = m.group(1).lower()
        for tok in TOKEN_RE.finditer(clean):
            out.append({
                "token": tok.group(1).rstrip("…").rstrip("."),
                "state": state,
                "reason": verdict_reason(clean, state),
                "report": _label(path),
                "author": author,
            })
    return out


def resolve(token: str, waiting_ids: list[str]) -> tuple[str | None, str]:
    """Map a printed token to exactly one waiting id, or say why it cannot be done."""
    hits = [i for i in waiting_ids if i.startswith(token)]
    if len(hits) == 1:
        return hits[0], ""
    if not hits:
        return None, "no waiting item matches"
    return None, f"ambiguous: {len(hits)} waiting items start with {token}"


def plan(items: dict[str, dict], reports: Path = REPORTS, only: str = "") -> tuple[list[dict], list[dict]]:
    """Return (closures, refusals). Nothing is written here."""
    waiting = {i: r for i, r in items.items() if not r.get("state")}
    if only:
        waiting = {i: r for i, r in waiting.items() if i == only}
    ids = sorted(waiting)

    found: dict[str, list[dict]] = {}
    refusals: list[dict] = []
    for path in sorted(reports.glob("*.md")):
        for v in verdicts(path):
            item_id, why = resolve(v["token"], ids)
            if item_id is None:
                if why.startswith("ambiguous"):
                    refusals.append({**v, "why": why})
                continue
            if v["author"] and v["author"] == waiting[item_id].get("amigo"):
                refusals.append({**v, "id": item_id, "why": "author is never the reviewer"})
                continue
            if not v["author"]:
                refusals.append({**v, "id": item_id,
                                 "why": "report names no amigo in its filename, so the reviewer "
                                        "cannot be attributed"})
                continue
            found.setdefault(item_id, []).append(v)

    closures: list[dict] = []
    for item_id, vs in sorted(found.items()):
        states = {v["state"] for v in vs}
        if len(states) > 1:
            refusals.append({"id": item_id, "token": item_id, "state": ",".join(sorted(states)),
                             "report": vs[0]["report"], "author": vs[0]["author"],
                             "why": "conflicting verdicts in the reports: " +
                                    "; ".join(f"{v['state']} in {v['report']}" for v in vs)})
            continue
        vs.sort(key=lambda v: v["report"])
        v = vs[0]
        note = f"{v['state']}: {v['reason']}" if v["reason"] else v["state"]
        closures.append({
            "id": item_id,
            "state": v["state"],
            "reviewer": f"auto:verdict:{v['author']}",
            "reason": f"{note} — verdict already recorded by {v['author']} in {v['report']}",
            "report": v["report"],
        })
    return closures, refusals


def apply(closures: list[dict], path: Path = item_ledger.LEDGER) -> int:
    """Write the rows. `review()` does the validating so this cannot bypass the reason rules."""
    written = 0
    for c in closures:
        item_ledger.review(path=path, item_id=c["id"], state=c["state"], reason=c["reason"],
                           reviewer=c["reviewer"])
        written += 1
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write the rows (default: show only)")
    ap.add_argument("--only", default="", help="one item id")
    ap.add_argument("--reports", default=str(REPORTS), help="report directory")
    ap.add_argument("--ledger", default=str(item_ledger.LEDGER), help="ledger file")
    args = ap.parse_args(argv)

    items = item_ledger.load(Path(args.ledger))
    closures, refusals = plan(items, Path(args.reports), args.only)

    for c in closures:
        print(f"{c['id']}: {c['state']} — from {c['report']}")
    for r in refusals:
        # only print refusals about items that would otherwise be closeable, to keep this short
        if r.get("id"):
            print(f"{r['id']}: left alone — {r['why']}")

    if not closures:
        print("reconcile_review_verdicts: nothing to close")
        return 0
    if args.apply:
        n = apply(closures, Path(args.ledger))
        print(f"reconcile_review_verdicts: {n} row(s) closed")
    else:
        print(f"reconcile_review_verdicts: {len(closures)} row(s) would close (dry run; --apply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
