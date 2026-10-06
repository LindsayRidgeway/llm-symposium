#!/usr/bin/env python3
# Owner: Desi
"""The item ledger — one row per item an amigo performed in a wake, and its review outcome.

Why this exists (2026-10-06). The human asked for a daily report of **N** (items performed in
wakes), **A** (reviewed and accomplished), **P** (reviewed and postponed) and **R** (rejected and
never to be accomplished), each split by amigo and by internal/external. The commons had no such
register. It had run records (`<bot>/tick-state/runs/*/`) and five overlapping prose queues
(`channels/tasks.md`, `channels/action-queue.md`, `channels/reject-queue.md`, `channels/agenda.md`,
`to-do-lists/*.md`). "An item, with an originator and a scope" existed nowhere. This is that
register, and it is deliberately one file rather than a sixth queue.

The unit. One item = one unit of work a wake finished. The evidence is the run's own changed paths:
a run that changed nothing performed no item. This is computed from the run record, never from a
model's account of itself, because a wake cut off at its action cap cannot be trusted to finish its
own bookkeeping — and the action-cap cutoff is a known fault, so self-report would undercount
exactly the wakes that did the most. One run that touched several files is one item; a wake that
declares `ITEM:` lines in its report overrides the derivation (see `items_from_report`).

Scope. `external` = the item had a visible effect outside the repository: an email sent
(`channels/sent/`, `channels/outbound/`), a submission to an outside body (`channels/outreach/`),
or a change to the published magazine (`docs/`). Everything else is `internal`. A run that touched
both is one external item — the classification is "did this reach the world", and one yes is enough.

State. An item is filed `performed` and starts **unreviewed**. A review moves it to exactly one of
`accomplished` / `postponed` / `rejected`. Hence, always and by construction:

    N = A + P + R + U          (U = unreviewed)

The human's identity is `N = A + P + R`. It is not yet true, and the reason is not bookkeeping:
**nothing in the commons reviews wake work.** The review pile has no closer (Dmitri's claimed task,
`channels/tasks.md`). So this ledger publishes `U` rather than hiding it inside N, and the day U
reaches zero the human's identity holds exactly. `accomplished` is also set automatically for an
item whose run has a `land(wake): work from run <id>` commit on main — work that is in the
repository and whose tests passed the lander's gate. That is a *verifiable* accomplishment; it is
not the same thing as a *reviewed* one, and the report says which is which.

Ledger format: JSON Lines, append-only, `channels/items.jsonl` — one object per line, later lines
for the same `id` are state changes. Same shape as `channels/usage/ci-usage.jsonl`, for the same
reason: an append-only file cannot be half-written into a plausible lie.

CLI:
    python3 channels/item_ledger.py --collect              # ingest runs from all five bots
    python3 channels/item_ledger.py --backfill             # ingest all history (idempotent)
    python3 channels/item_ledger.py --review <id> --state postponed --reason "why"
    python3 channels/item_ledger.py --summary [--hours 24]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"

# The five bodies. `amigo` is the originator of every item its own wake performed.
HOME = Path(os.path.expanduser("~"))
AMIGOS = ("desi", "claude", "gemini", "tarik", "dmitri")
RUNS_REL = Path("tick-state") / "runs"

# Paths whose change means the item reached the world outside this repository.
EXTERNAL_PREFIXES = (
    "docs/",                    # the published magazine
    "channels/sent/",           # mail this commons sent
    "channels/outbound/",       # ditto, on its way out
    "channels/outreach/",       # submissions/pitches to outside organisations
)

STATES = ("accomplished", "postponed", "rejected")

RUN_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{8}$")
ANY_RUN_ID_RE = re.compile(r"\b(\d{8}T\d{6}Z-[0-9a-f]{8})\b")
ITEM_RE = re.compile(r"^\s*ITEM:\s*\[(?P<scope>internal|external)\]\s*(?P<title>.+?)\s*$", re.I)
TITLE_MAX = 160


def runs_dir(amigo: str) -> Path:
    return HOME / "LLM" / f"{amigo}-bot" / RUNS_REL


def parse_run_time(run_id: str) -> str:
    """`20261006T082758Z-245fa706` -> `2026-10-06T08:27:58Z`."""
    stamp = run_id.split("-", 1)[0]
    d = dt.datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc)
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


# A wake's report opens with whatever it wrote first, and older runners wrote their *intent*
# before doing anything ("Intend to: …"). An intent is not an item; the title must say what the
# wake did or found. Measured on the 2026-09-15/16 runs, which are all intent-first.
_NOT_A_TITLE_RE = re.compile(
    r"^(?:intend(?:ing)?\b|start(?:ing|ed)?\b|i will\b|plan(?:ning)?\b|area this wake\b|"
    r"chose item\b|wake\b\s*[—:-])", re.I)


def best_title(text: str, limit: int = TITLE_MAX) -> str:
    """The report's own one-line summary of the work, not its statement of intent."""
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    for line in lines:
        if _NOT_A_TITLE_RE.match(line):
            continue
        if len(line) >= 25:                      # a title, not a heading fragment
            return line[:limit]
    return (lines[0][:limit] if lines else "(no report)")


def items_from_report(report_text: str) -> list[dict]:
    """Explicit `ITEM: [internal|external] <title>` lines, if the wake declared any.

    A wake that declares its items is believed over the derivation, because it can tell one item
    from three. A wake that declares none falls back to one item for the run.
    """
    out = []
    for line in (report_text or "").splitlines():
        m = ITEM_RE.match(line)
        if m:
            out.append({"scope": m.group("scope").lower(), "title": m.group("title")[:TITLE_MAX]})
    return out


def scope_for_paths(paths: list[str]) -> str:
    for p in paths or []:
        if any(p.startswith(pref) for pref in EXTERNAL_PREFIXES):
            return "external"
    return "internal"


def run_to_items(amigo: str, run_dir: Path) -> list[dict]:
    """The items a single wake performed. Empty when the run changed nothing."""
    result = run_dir / "result.json"
    try:
        data = json.loads(result.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    changed = [p for p in (data.get("changed_paths") or []) if isinstance(p, str)]
    if not changed:
        return []
    report_path = run_dir / "report.txt"
    try:
        report_text = report_path.read_text(encoding="utf-8")
    except OSError:
        report_text = ""
    declared = items_from_report(report_text)
    run_id = data.get("run_id") or run_dir.name
    filed = parse_run_time(run_id) if RUN_ID_RE.match(run_id) else None
    common = {
        "id": run_id,
        "filed_utc": filed,
        "amigo": amigo,
        "evidence": f"{amigo}-bot run {run_id}",
        "paths": changed[:20],
        "source": "declared" if declared else "derived",
    }
    if declared:
        return [dict(common, scope=d["scope"], title=d["title"]) for d in declared]
    return [dict(common, scope=scope_for_paths(changed), title=best_title(report_text))]


def landed_run_ids(repo: Path = REPO) -> set[str]:
    """Run ids named by a `land(wake): work from run <id>` commit — i.e. work that reached main.

    One pass over the log, not one call per run: three hundred and fifty runs would otherwise be
    three hundred and fifty git invocations.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "--pretty=%B"],
            capture_output=True, text=True, timeout=120, check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    return set(ANY_RUN_ID_RE.findall(out))


def load(path: Path = LEDGER) -> dict[str, dict]:
    """Every item, with later lines overriding earlier ones. A corrupt line is skipped loudly."""
    items: dict[str, dict] = {}
    if not path.exists():
        return items
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            items[rec["id"]] = rec
        except (ValueError, KeyError):
            print(f"item_ledger: skipping unreadable line {lineno}", file=sys.stderr)
    return items


def append(records: list[dict], path: Path = LEDGER) -> None:
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")


def collect(path: Path = LEDGER, since: str | None = None, amigo: str | None = None) -> int:
    """Append one `performed` row per new run that changed something. Idempotent by run id."""
    known = load(path)
    landed = landed_run_ids()
    fresh = []
    for who in ([amigo] if amigo else AMIGOS):
        root = runs_dir(who)
        if not root.is_dir():
            continue
        for run_dir in sorted(root.iterdir()):
            if not run_dir.is_dir():
                continue
            if since and run_dir.name < since:
                continue
            for item in run_to_items(who, run_dir):
                if item["id"] in known:
                    continue
                # Verify the accomplishment rather than assert it.
                item["state"] = "accomplished" if item["id"] in landed else None
                item["state_utc"] = item["filed_utc"] if item["state"] else None
                item["reason"] = ("landed on main (lander's test gate passed)"
                                  if item["state"] else None)
                item["reviewer"] = "auto:land" if item["state"] else None
                fresh.append(item)
                known[item["id"]] = item
    append(fresh, path)
    return len(fresh)


def review(path: Path = LEDGER, item_id: str = "", state: str = "", reason: str = "",
           reviewer: str = "human") -> dict:
    """Move one item to a terminal state, with a reason. Postponed/rejected require one."""
    if state not in STATES:
        raise ValueError(f"state must be one of {STATES}, got {state!r}")
    if not reason.strip():
        raise ValueError("a postponed or rejected item needs a reason — that is the whole record")
    rec = load(path).get(item_id)
    if rec is None:
        raise KeyError(f"no such item: {item_id}")
    rec = dict(rec)
    rec.update(state=state, state_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               reason=reason.strip(), reviewer=reviewer)
    append([rec], path)
    return rec


def counts(items: dict[str, dict], hours: int | None = None) -> dict:
    """The four groups, split by amigo and by internal/external. `hours=None` is lifetime."""
    cutoff = None
    if hours:
        cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours))
    rows = []
    for rec in items.values():
        if cutoff is not None:
            filed = rec.get("filed_utc")
            if not filed:
                continue
            when = dt.datetime.strptime(filed, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
            if when < cutoff:
                continue
        rows.append(rec)

    def blank() -> dict:
        return {"total": 0, "internal": 0, "external": 0, "by_amigo": {}}

    out = {"N": blank(), "A": blank(), "P": blank(), "R": blank(), "U": blank(), "items": rows}
    for rec in rows:
        group = {"accomplished": "A", "postponed": "P", "rejected": "R"}.get(rec.get("state"))
        who = rec.get("amigo", "?")
        scope = rec.get("scope", "internal")
        out["N"]["total"] += 1
        out["N"]["internal" if scope == "internal" else "external"] += 1
        slot = out["N"]["by_amigo"].setdefault(who, {"total": 0, "internal": 0, "external": 0})
        slot["total"] += 1
        slot[scope] += 1
        if group is None:
            out["U"]["total"] += 1
            out["U"]["internal" if scope == "internal" else "external"] += 1
            continue
        out[group]["total"] += 1
        out[group]["internal" if scope == "internal" else "external"] += 1
        slot = out[group]["by_amigo"].setdefault(who, {"total": 0, "internal": 0, "external": 0})
        slot["total"] += 1
        slot[scope] += 1
    return out


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--collect", action="store_true", help="ingest new runs from all five bots")
    ap.add_argument("--backfill", action="store_true", help="ingest all history (idempotent)")
    ap.add_argument("--amigo", choices=AMIGOS)
    ap.add_argument("--review", metavar="ID")
    ap.add_argument("--state", choices=STATES)
    ap.add_argument("--reason", default="")
    ap.add_argument("--reviewer", default="human")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.collect or args.backfill:
        n = collect(amigo=args.amigo)
        print(f"item_ledger: {n} new item(s) recorded; ledger now {len(load())}")
        return 0
    if args.review:
        rec = review(item_id=args.review, state=args.state or "", reason=args.reason,
                     reviewer=args.reviewer)
        print(f"item_ledger: {rec['id']} -> {rec['state']}: {rec['reason']}")
        return 0
    items = load()
    if args.list:
        for rec in sorted(items.values(), key=lambda r: r.get("filed_utc") or ""):
            print(f"  {rec.get('filed_utc')}  {rec.get('amigo'):7s} {rec.get('scope'):8s} "
                  f"{rec.get('state') or 'unreviewed':12s} {rec.get('title','')[:70]}")
        print(f"  ({len(items)} item(s))")
        return 0
    if args.summary:
        c = counts(items, args.hours)
        print(f"last {args.hours}h: " + "  ".join(f"{g}={c[g]['total']}" for g in "NAPRU"))
        c = counts(items, None)
        print(f"lifetime:  " + "  ".join(f"{g}={c[g]['total']}" for g in "NAPRU"))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
