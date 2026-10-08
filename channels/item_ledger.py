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

State, second scheme (the human, 2026-10-07 — this supersedes the four-letter version below it).
He took the two collapsed words apart again, and the split is the whole point:

    N  performed, no review needed      V  performed, needs review
    A  accomplished                      P  postponed **by a decision** (reason on disk)
    W  waiting for review (nobody has looked)          R  rejected

    N + V = A + P + W + R

Two rules make that work **without anyone maintaining a new field** (his constraint: "just the
reporting algorithm to become more sophisticated"):

1. `P` is not the remainder any more. An item counts as P only if the reason for postponing it is
   already written on the item. No reason on disk -> it is `W`, however long it has sat. The old
   four-letter version made P the remainder, which is exactly why P was useless as a number: it
   equalled "everything that is not A or R" and told the human nothing about whether anyone had
   looked. That was his point on 2026-10-08 and he was right.
2. `N` is an exemption, and an exemption must be *claimed in writing* — otherwise it is a
   self-granted pass, which is how N would become the dumping ground P used to be. No stated reason
   to skip review -> the item reads as `V`. The honest failure mode: something unexplained reads as
   waiting, which is what it is. Today that means N=0 — nothing has ever declared itself exempt.

His reading of the two numbers, kept because it is the point of the whole exercise:
`N = P` in the lifetime totals means the criteria are broken — everything looks reviewable so
nothing is ever exempted and nothing is ever settled; `N = P` for one amigo means *that* amigo's
process is worth a look. And the drain is measured as Δ(V−W): how many items left W in the window.
Δ(V−W)=0 while ΔW>0 is a broken process (nothing draining, inflow continuing); both positive is a
capacity problem. Dwell is computed only when V−W>0, which is the one case V=W cannot answer.

A is one letter with two causes, and the report prints both: `by_review` (somebody looked and kept
it) and `by_gate` (the lander's test suite passed, so it reached main — verifiable, but not the same
as reviewed). The earlier version of this ledger set A for lander-passed runs and said so in prose;
splitting it inside the letter is the same disclosure, in the report rather than in a footnote.

The history, kept because the reasoning is not in the git log: the human corrected an earlier
version on 2026-10-06 — it had published a fourth group `U` (performed, not yet reviewed), and he
said U is just a particular case of P. That produced the collapsed four-letter scheme (`N = A + P +
R`, with a decided/undecided split hidden inside P). On 2026-10-07 he un-collapsed it, on his own
reasoning: P and W "were doing opposite work under one word — P is a decision with a reason
attached, W is nobody having looked — and collapsing them hid exactly the thing that tells you which
failure you have." The `U` letter does not come back; the *distinction* does, under the name W.

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


LANDING_STAMP = "land(wake)"


def last_landing(repo: Path = REPO) -> str | None:
    """ISO-8601 UTC timestamp of the newest `land(wake)` commit on main, or None if there is none.

    This is the *delivery* clock, and it is not the same question as `landed_run_ids`. That function
    says which runs reached main; this says whether the landing pipeline is running at all. It has
    to be asked separately because the two failures look identical in the item states: an item that
    was reviewed and put off and an item whose whole wake was refused by land_runs.py are both
    simply "not accomplished". Measured 2026-10-06: the pipeline had been silent for 2.7 days while
    22 items were filed, and the daily report presented that as a review backlog — "nobody has
    looked" — when the true cause was that no work was being landed. One cheap git call.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%cI", "--grep", LANDING_STAMP],
            capture_output=True, text=True, timeout=60, check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    if not out:
        return None
    try:
        when = dt.datetime.fromisoformat(out)
    except ValueError:
        return None
    return when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def landing_gap(items: dict[str, dict], last: str | None) -> int:
    """How many items were filed after the last landing. Non-zero with an old `last` is a stall."""
    if not last:
        return sum(1 for r in items.values() if r.get("filed_utc"))
    return sum(1 for r in items.values() if (r.get("filed_utc") or "") > last)


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


def letter_for(rec: dict) -> str:
    """Which of A/P/W/R an item sits in. W is the remainder, and deliberately so.

    W is the honest place for anything undecided: an item is *waiting for review* unless the
    artifact already carries a decision. `postponed` without a written reason reads as W too —
    a postponement nobody wrote down is not a decision, it is an absence, and the rule from
    2026-10-07 says an unwritten claim does not count.
    """
    state = rec.get("state")
    if state == "accomplished":
        return "A"
    if state == "rejected":
        return "R"
    if state == "postponed" and (rec.get("reason") or "").strip():
        return "P"
    return "W"


def is_exempt(rec: dict) -> bool:
    """True only if the item itself says why it needs no review (so it counts as N, not V).

    The default is V. An exemption nobody wrote down is a self-granted pass, and a self-granted
    pass is how a letter turns into a dumping ground — the exact failure the human diagnosed in P.
    """
    return bool((rec.get("no_review_reason") or "").strip())


def counts(items: dict[str, dict], hours: int | None = None) -> dict:
    """The six groups, split by amigo and by internal/external. `hours=None` is lifetime.

    Returns one blank() per letter plus `items` (the rows in the window) and `decisions` (how many
    items left W in the window — a written decision, whatever letter it landed in). `decisions` is
    what makes Δ(V−W) derivable: each decision takes exactly one item out of waiting, so
    Δ(V−W) = decisions and ΔW = filed − decisions.
    """
    cutoff = None
    if hours:
        cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours))

    def in_window(stamp: str | None) -> bool:
        if cutoff is None:
            return bool(stamp)
        if not stamp:
            return False
        try:
            when = dt.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
        except ValueError:
            return False
        return when >= cutoff

    rows = [rec for rec in items.values() if in_window(rec.get("filed_utc"))]

    def blank() -> dict:
        return {"total": 0, "internal": 0, "external": 0, "by_amigo": {}}

    out = {g: blank() for g in ("N", "V", "A", "P", "W", "R")}
    out["A"]["by_review"] = 0
    out["A"]["by_gate"] = 0
    out["decisions"] = 0
    out["items"] = rows

    def add(letter: str, who: str, scope: str) -> None:
        out[letter]["total"] += 1
        out[letter]["internal" if scope == "internal" else "external"] += 1
        slot = out[letter]["by_amigo"].setdefault(who, {"total": 0, "internal": 0, "external": 0})
        slot["total"] += 1
        slot[scope] += 1

    for rec in rows:
        who = rec.get("amigo", "?")
        scope = rec.get("scope", "internal")
        # Two axes, not one: the review-needed axis (N/V) and the outcome axis (A/P/W/R). Every item
        # is exactly one of each, so N+V = A+P+W+R holds by construction.
        add("N" if is_exempt(rec) else "V", who, scope)
        letter = letter_for(rec)
        add(letter, who, scope)
        if letter == "A":
            out["A"]["by_review" if rec.get("reviewer") not in (None, "auto:land") else "by_gate"] += 1
        if in_window(rec.get("state_utc")):
            out["decisions"] += 1
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
        for label, hours in (("lifetime", None), (f"last {args.hours}h", args.hours)):
            c = counts(items, hours)
            left = c["N"]["total"] + c["V"]["total"]
            right = sum(c[g]["total"] for g in ("A", "P", "W", "R"))
            print(f"{label:10s} "
                  + "  ".join(f"{g}={c[g]['total']}" for g in ("N", "V", "A", "P", "W", "R"))
                  + ("  ✓ N+V=A+P+W+R" if left == right else "  ✗ identity broken")
                  + f"   (A: {c['A']['by_review']} reviewed / {c['A']['by_gate']} gate;"
                    f" decisions this window: {c['decisions']})")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
