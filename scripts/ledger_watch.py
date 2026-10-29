#!/usr/bin/env python3
"""The daily review check: measure, repair what is mechanical, and tell the human in one message.

WHY THIS IS A SCRIPT AND NOT A WAKE. The question it answers — is the queue draining? — is a
question with an invariant answer, and an invariant is cheaper and more honest to compute than to
ask a model for. A wake costs money, runs under an action cap, and can decide the number is
interesting and write an essay instead. This runs in a second, writes the same number every day,
and does the repairs below without being persuaded out of them.

WHAT IT REPAIRS (all idempotent; rerunning changes nothing):

  1. Verdicts thrown away by the landing gate. The gate judges a patch all-or-nothing, so a
     finished review in the same patch as an unrelated failing test is discarded — the review was
     done, the ledger was never told, and the next wake reviews the same item again. This reads
     `landing_failed.txt` runs, pulls the terminal ledger rows out of the refused patch, and
     applies the latest verdict per item to any item that is still waiting.
  2. Items nobody filed. `--collect` is not run by launchd, the tick, or any prompt, so arrivals
     under-report until a wake happens to run it.
  3. Items whose run has since landed. `--reconcile` closes them as auto:land; nothing runs it.

WHAT IT DOES NOT DO: invent a fix for a cause it has not seen before. When the numbers say the
mechanism is still broken, it says so in the message and leaves the fixing to a wake with turns.

USAGE
    python3 scripts/ledger_watch.py                 # the daily run (sends Telegram)
    python3 scripts/ledger_watch.py --dry-run       # measure and print, change nothing, send nothing
    python3 scripts/ledger_watch.py --no-send       # repair and record, no message
    python3 scripts/ledger_watch.py --force         # run again today

Exit code is 0 when the human's drain rule is met, 1 when it is not, 2 when the check itself
could not run. It is a measurement, so it is allowed to say FAIL every day for a while.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HOME = Path(os.path.expanduser("~"))
BOTS = ["desi-bot", "dmitri-bot", "gemini-bot", "claude-bot", "tarik-bot"]
WATCH = REPO / "channels" / "watch"
HISTORY = WATCH / "history.jsonl"
MACHINE_REVIEWERS = ("auto:land", "auto:path", "auto", "")

sys.path.insert(0, str(REPO / "channels"))
import item_ledger as il  # noqa: E402
from record_push import shared_checkout_lock  # noqa: E402


# --------------------------------------------------------------------------- helpers

def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso(t: dt.datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def rows_by_id() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for line in il.LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        out.setdefault(rec["id"], []).append(rec)
    return out


def latest(recs: list[dict]) -> dict:
    return recs[-1]


def is_machine(reviewer: str | None) -> bool:
    return (reviewer or "") in MACHINE_REVIEWERS


def git(*args: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True,
                          timeout=timeout)


def run(cmd: list[str], timeout: int = 300) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(REPO))
        return p.returncode, (p.stdout + p.stderr).strip()
    except Exception as exc:                                  # noqa: BLE001
        return 1, f"{type(exc).__name__}: {exc}"


# --------------------------------------------------------------------------- measure

def measure(now: dt.datetime) -> dict:
    """Everything the message needs, computed from items (never from raw row counts)."""
    cutoff = iso(now - dt.timedelta(hours=24))
    by = rows_by_id()

    queue = 0
    queue_by_amigo: dict[str, int] = {}
    arrivals = 0
    decisions = 0
    model_decisions = 0
    machine_closures = 0
    pile = 0
    pile_read = 0
    for item_id, recs in by.items():
        cur = latest(recs)
        letter = il.letter_for(cur)
        if letter == "W":
            queue += 1
            who = cur.get("assigned_to") or "-"
            queue_by_amigo[who] = queue_by_amigo.get(who, 0) + 1
        if (cur.get("filed_utc") or "") >= cutoff:
            arrivals += 1
        terminals = [r for r in recs if il.letter_for(r) != "W"]
        if terminals and (terminal_utc := (terminals[-1].get("state_utc") or "")) >= cutoff:
            reviewer = terminals[-1].get("reviewer") or terminals[-1].get("amigo") or ""
            if is_machine(reviewer):
                machine_closures += 1
            else:
                model_decisions += 1
        if terminals and (terminals[-1].get("state_utc") or "") >= cutoff:
            decisions += 1
        # the pile: closed by a machine and never taken up by a model afterwards
        first = terminals[0] if terminals else None
        if first is not None and is_machine(first.get("reviewer")):
            reviewed_later = [r for r in terminals[1:]
                              if not is_machine(r.get("reviewer") or "")]
            if reviewed_later:
                if (reviewed_later[-1].get("state_utc") or "") >= cutoff:
                    pile_read += 1
            else:
                pile += 1

    refusals_24, refused_rows_24 = refused_patches(now - dt.timedelta(hours=24))
    reading_queue: dict[str, int] = {}
    for rec in by.values():
        cur = latest(rec)
        if il.is_unread(cur) and cur.get("reading_assigned_to"):
            who = cur["reading_assigned_to"]
            reading_queue[who] = reading_queue.get(who, 0) + 1

    return {
        "at": iso(now),
        "queue": queue,
        "queue_by_amigo": dict(sorted(queue_by_amigo.items())),
        "arrivals_24h": arrivals,
        "decisions_24h": decisions,
        "model_decisions_24h": model_decisions,
        "machine_closures_24h": machine_closures,
        "pile": pile,
        "pile_read_24h": pile_read,
        "gate_refusals_24h": refusals_24,
        "gate_refusals_carrying_verdicts_24h": refused_rows_24,
        "items_total": len(by),
        "reading_queue": dict(sorted(reading_queue.items())),
    }


def refused_patches(since: dt.datetime, rows_only: bool = False):
    """Refused landings since `since`, and how many carried a terminal ledger row in the patch."""
    count = 0
    with_rows = 0
    for bot in BOTS:
        for run_dir in sorted((HOME / "LLM" / bot / "tick-state" / "runs").glob("*")):
            failure = run_dir / "landing_failed.txt"
            if not failure.is_file():
                continue
            try:
                if dt.datetime.fromtimestamp(failure.stat().st_mtime, dt.timezone.utc) < since:
                    continue
            except OSError:
                continue
            count += 1
            if verdict_rows_in_patch(run_dir / "changes.patch"):
                with_rows += 1
    return (with_rows,) if rows_only else (count, with_rows)


def verdict_rows_in_patch(patch: Path) -> list[dict]:
    """Terminal ledger rows that a refused patch tried to add."""
    if not patch.is_file():
        return []
    try:
        text = patch.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    if "channels/items.jsonl" not in text:
        return []
    out = []
    for line in text.splitlines():
        if not line.startswith("+") or '"id"' not in line:
            continue
        try:
            rec = json.loads(line[1:])
        except json.JSONDecodeError:
            continue
        if rec.get("state") in ("accomplished", "postponed", "rejected"):
            out.append(rec)
    return out


# --------------------------------------------------------------------------- repair

def recover_verdicts(since: dt.datetime, apply: bool = True) -> list[str]:
    """Apply verdicts that were written, refused by the gate, and never recorded.

    The *latest* verdict per item wins, ordered by the run id's own timestamp, because that is the
    order the reviews happened in. Only items still waiting are touched — an item that has since
    been closed by someone else is left alone.
    """
    candidates: dict[str, list[tuple[str, dict]]] = {}
    for bot in BOTS:
        for run_dir in sorted((HOME / "LLM" / bot / "tick-state" / "runs").glob("*")):
            if not (run_dir / "landing_failed.txt").is_file():
                continue
            stamp = run_dir.name.split("-")[0]
            try:
                when = dt.datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc)
            except ValueError:
                continue
            if when < since:
                continue
            for rec in verdict_rows_in_patch(run_dir / "changes.patch"):
                item_id = rec.get("id")
                if not item_id:
                    continue
                candidates.setdefault(item_id, []).append((stamp, rec))

    items = il.load()
    recovered = []
    for item_id, cands in sorted(candidates.items()):
        stamp, rec = choose_verdict(cands)
        current = items.get(item_id)
        if current is None or il.letter_for(current) != "W":
            continue
        reviewer = rec.get("reviewer") or rec.get("amigo") or "desi"
        if is_machine(reviewer) or reviewer == "human":
            continue
        reason = (rec.get("reason") or "").strip()
        recovered.append(f"{item_id} -> {rec['state']} ({reviewer})")
        if not apply:
            continue
        try:
            il.review(item_id=item_id, state=rec["state"], reason=reason, reviewer=reviewer)
        except Exception as exc:                              # noqa: BLE001
            recovered[-1] += f" [refused: {type(exc).__name__}]"
    return recovered


def choose_verdict(cands: list[tuple[str, dict]]) -> tuple[str, dict]:
    """Which verdict to believe when the same item was reviewed more than once.

    The failure this repairs is a verdict that never landed, so the item stayed in the queue and the
    next wake reviewed it a second time. The first review is the one to keep, and a later
    "postponed: already reviewed in run ..." is evidence of the loop, not of a decision. So: an
    accomplished verdict whose reason names the work (a run id or a path) wins, earliest first;
    otherwise the latest verdict wins.
    """
    import re
    named = [(s, r) for s, r in cands
             if r.get("state") == "accomplished"
             and re.search(r"\d{8}T\d{6}Z|/\w", r.get("reason") or "")]
    if named:
        return min(named, key=lambda pair: pair[0])
    return max(cands, key=lambda pair: pair[0])


def filed_and_reconciled(apply: bool = True) -> dict:
    """The two commands nothing on this machine runs."""
    if not apply:
        return {"collected": 0, "reconciled": 0, "paths": 0}
    code, out = run([sys.executable, "channels/item_ledger.py", "--collect"])
    collected = _last_int(out, "recorded")
    code2, out2 = run([sys.executable, "channels/item_ledger.py", "--reconcile"])
    reconciled = _last_int(out2, "reconciled")
    code3, out3 = run([sys.executable, "channels/item_ledger.py", "--reconcile-paths"])
    paths = _last_int(out3, "closed")
    return {"collected": collected, "reconciled": reconciled, "paths": paths}


# --------------------------------------------------------------------------- the weekly whole-repo review
#
# Added 2026-10-29, after the human noticed that discussions/claude-review.md, openai-review.md,
# gemini-review.md and deepseek-review.md had not changed since 2026-09-07..09-24. He was right, and
# nothing had replaced them: the ledger reviews one item at a time, and a queue of items cannot see
# a shape. It cannot notice that 291 of 414 items filed since 10-15 are about the commons' own
# machinery, because no single item is wrong. That observation was only possible by looking at the
# whole record at once — and it was the most useful thing anybody measured this week.
#
# So the review is an item now: filed here, once a week, named by the same draw as any other work,
# with a brief and a demanded output path. If nobody reads it, it shows up as a D. If somebody
# reads it, it closes. It is routed rather than remembered.
WHOLE_REVIEW_DAYS = 7
WHOLE_REVIEW_PREFIX = "whole-repo-review-"
WHOLE_REVIEW_BRIEF = (
    "Look at the whole commons, not at the queue. Three answers, and 'none' is an allowed answer "
    "only if you say why: (1) what is structurally broken — a mechanism that cannot do what it "
    "claims; (2) what is missing — work no queue is shaped to ask for; (3) what should STOP — a "
    "category of activity that looks like work and is not. Write it to the path this item names. "
    "Do not restate the ledger's counts: those are already measured, and a summary is not a review."
)


def whole_review_due(items: dict[str, dict], now: dt.datetime) -> str:
    """'' if a whole-repo review is open or recent, else the date of the last one ('never')."""
    rows = [r for r in items.values() if str(r.get("id", "")).startswith(WHOLE_REVIEW_PREFIX)]
    if any(r.get("state") is None for r in rows):
        return ""
    newest = max((r.get("filed_utc") or "" for r in rows), default="")
    if not newest:
        return "never"
    try:
        when = dt.datetime.strptime(newest[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return "never"
    return "" if (now - when) < dt.timedelta(days=WHOLE_REVIEW_DAYS) else newest[:10]


def file_whole_repo_review(now: dt.datetime | None = None, apply: bool = True,
                           path: Path | None = None) -> str:
    """File the weekly whole-repository review as a waiting item and name a reader for it."""
    now = now or utcnow()
    path = path or il.LEDGER
    items = il.load(path)
    due = whole_review_due(items, now)
    if not due:
        return ""
    day = iso(now)[:10]
    item_id = WHOLE_REVIEW_PREFIX + day
    doc = f"discussions/{day}-whole-repo-review.md"
    rec = {
        "id": item_id,
        "amigo": "commons",              # not a body, so the draw can name any of the five
        "scope": "internal",
        "source": "scheduled",
        "filed_utc": iso(now),
        "title": "Whole-repository review — structure, gaps, and what should stop",
        "brief": WHOLE_REVIEW_BRIEF,
        "paths": [doc],
        "evidence": ("filed by scripts/ledger_watch.py: no whole-repository review since "
                     + (due if due == "never" else due)),
        "state": None, "state_utc": None, "reviewer": None, "reason": None,
    }
    note = f"filed the weekly whole-repository review as {item_id} (last one: {due})"
    if not apply:
        return note + " [would file]"
    il.append([rec], path)
    try:
        named = il.draw(path=path, by="ledger_watch")
        who = next((r.get("assigned_to") for r in named if r.get("id") == item_id), None)
        note += f"; named to {who}" if who else "; named to nobody — it is a hole until a draw runs"
    except (OSError, ValueError, KeyError) as exc:
        note += f"; WARNING not named ({type(exc).__name__}: {exc})"
    return note


def _last_int(text: str, word: str) -> int:
    """The last '<n> ... <word>' in a tool's output — the line means what it says, nothing more."""
    import re
    m = re.findall(r"(\d+)\s+[^.;]*?\b" + word, text or "")
    return int(m[-1]) if m else 0


# --------------------------------------------------------------------------- report

def last_entry() -> dict | None:
    if not HISTORY.is_file():
        return None
    lines = [ln for ln in HISTORY.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return json.loads(lines[-1]) if lines else None


def previous(now: dt.datetime) -> tuple[dict | None, str]:
    """The comparison point: the last check from an *earlier day*, else an earlier run today.

    Comparing a re-run against itself would print "queue up 0 on yesterday" for a day that has not
    been measured yet, which reads like progress and is not.
    """
    if not HISTORY.is_file():
        return None, ""
    entries = [json.loads(ln) for ln in HISTORY.read_text(encoding="utf-8").splitlines() if ln.strip()]
    today = iso(now)[:10]
    for entry in reversed(entries):
        if (entry.get("at") or "")[:10] != today:
            return entry, "yesterday"
    if entries:
        return entries[-1], "earlier today"
    return None, ""


# Added 2026-10-25 with the D letter: above this many finished-but-unread items the reading quota is
# the binding problem, and the daily check says so instead of passing on the queue alone. The number
# and the quota rule now live in item_ledger, where every wake reads them; this is an alias, not a
# second copy (2026-10-29).
PILE_TARGET = il.PILE_TARGET


def verdict(now_m: dict, prev: dict | None, label: str = "yesterday") -> tuple[bool, list[str]]:
    """Two rules, and the second one was added 2026-10-25 because the first one passed.

    His rule of 2026-10-06: the queue must never exceed one day's arrivals. W met it while 263
    finished items sat unread, because a machine closure counted as an accomplishment — the check
    was measuring the small pile and reporting it as the whole. So the pile now has its own
    condition, and it is the one printed first: **the finished-but-unread pile must be under
    PILE_TARGET, or must have shrunk since the last measurement with something actually read.**
    A pile that is merely known is not progress. The quota — two reads a wake while the pile is
    over the target — is printed by `item_ledger.py --reading-queue <name>`, which is the command
    every wake opens with; this line is only how the pile becomes visible when nothing reads.

    It says what it counted and stops there. Its failure text of 10-25 to 10-29 asserted a cause
    ("the quota is being ignored") that it had never measured, and the cause was false: no wake
    had ever been told a number. An instrument that names its own guess as the finding is the same
    defect as the one this file exists to catch.
    """
    reasons = []
    queue_ok = now_m["queue"] <= max(now_m["arrivals_24h"], 1)
    pile = now_m.get("pile", 0)
    read = now_m.get("pile_read_24h", 0)
    pile_ok = pile <= PILE_TARGET
    if not pile_ok and prev and prev.get("pile") is not None:
        pile_ok = pile < prev["pile"] and read > 0
    if not pile_ok:
        # 2026-10-29 (Desi): this line used to end "...the reading quota in the wake block is being
        # ignored" — a cause it had not measured, and the cause was wrong: no wake carried the
        # quota. It now prints only what it counted, plus where the quota is printed.
        was = ""
        moved = ""
        if prev and prev.get("pile") is not None:
            was = f" ({label} {prev['pile']})"
            delta = pile - prev["pile"]
            moved = f", unchanged on {label}" if delta == 0 else f", {delta:+d} on {label}"
        reasons.append(f"{pile} finished item(s) nobody has read{was}{moved}; "
                       f"{read} were read in 24h against {now_m['arrivals_24h']} filed. "
                       f"The quota is {il.quota(pile)} read(s) per wake — "
                       f"`item_ledger.py --reading-queue <name>` prints it.")
    if queue_ok:
        reasons.append("the queue is no bigger than one day of arrivals")
    else:
        reasons.append(f"{now_m['queue']} waiting against {now_m['arrivals_24h']} filed in 24h")
    if prev:
        if now_m["queue"] < prev.get("queue", 0):
            reasons.append(f"queue down {prev['queue'] - now_m['queue']} on {label}")
        elif now_m["queue"] == prev.get("queue", 0):
            reasons.append(f"queue unchanged on {label}")
        else:
            reasons.append(f"queue up {now_m['queue'] - prev.get('queue', 0)} on {label}")
    return queue_ok and pile_ok, reasons


def message(m: dict, prev: dict | None, label: str, repairs: dict, passes: bool,
            reasons: list[str], node: str) -> str:
    lines = [f"Review check, {m['at'][:10]} ({node})."]
    lines.append(f"Waiting for review: {m['queue']}" +
                 (f" ({label} {prev['queue']})" if prev else "") +
                 f" · filed in 24h: {m['arrivals_24h']}")
    lines.append(f"Reviews by a model, 24h: {m['model_decisions_24h']}"
                 f" · closed by the landing bot: {m['machine_closures_24h']}")
    ratio = (m["model_decisions_24h"] / m["arrivals_24h"]) if m["arrivals_24h"] else 0.0
    lines.append(f"New artifacts filed : verdicts written = {m['arrivals_24h']} : "
                 f"{m['model_decisions_24h']} ({ratio:.2f}) — the human wants the left number "
                 f"falling and the right one rising until nothing waits")
    lines.append(f"Finished and never read: {m['pile']}"
                 + (f" ({label} {prev['pile']})" if prev else "")
                 + f" · read out of that pile in 24h: {m['pile_read_24h']}")
    if m.get("reading_queue"):
        spread = " · ".join(f"{a} {n}" for a, n in m["reading_queue"].items())
        lines.append(f"Of those, named and ready for a waking reader: {spread}")
    lines.append(f"Refused landings, 24h: {m['gate_refusals_24h']}"
                 f" ({m['gate_refusals_carrying_verdicts_24h']} carried a verdict)")
    did = []
    if repairs.get("recovered"):
        did.append(f"recovered {len(repairs['recovered'])} verdict(s) a refused landing had thrown away")
    if repairs.get("collected"):
        did.append(f"filed {repairs['collected']} item(s) no wake had recorded")
    if repairs.get("reconciled") or repairs.get("paths"):
        did.append(f"closed {repairs['reconciled'] + repairs['paths']} landed item(s)")
    if repairs.get("whole_review"):
        did.append(repairs["whole_review"])
    lines.append("Repaired: " + ("; ".join(did) if did else "nothing needed repairing"))
    lines.append(("PASS" if passes else "FAIL") + " — " + reasons[0].rstrip(".")
                 + ("" if passes else ". A quota is a mechanism only where the wake reads it — "
                                      "the reading queue prints the number itself since 10-29."))
    return "\n".join(lines)


def telegram(text: str, dry: bool) -> str:
    if dry:
        return "not sent (dry run)"
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
        fh.write(text + "\n")
        path = fh.name
    code, out = run([sys.executable, "scripts/tell_human.py", "--amigo", "desi",
                     "--text-file", path, "--force"])
    Path(path).unlink(missing_ok=True)
    return "sent" if code == 0 else f"send failed: {out[-200:]}"


def record(m: dict, repairs: dict, passes: bool, text: str) -> None:
    WATCH.mkdir(parents=True, exist_ok=True)
    with HISTORY.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**m, "pass": passes,
                             "recovered": len(repairs.get("recovered") or []),
                             "collected": repairs.get("collected", 0),
                             "reconciled": repairs.get("reconciled", 0)}) + "\n")
    day = WATCH / f"{m['at'][:10]}.md"
    body = [f"# Review check, {m['at'][:10]}", "", "```", text, "```", ""]
    if repairs.get("recovered"):
        body += ["## Verdicts recovered from refused landings", ""]
        body += [f"- `{r}`" for r in repairs["recovered"]]
        body += [""]
    body += ["## Numbers", "", "```json", json.dumps(m, indent=2), "```", ""]
    day.write_text("\n".join(body), encoding="utf-8")


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="measure and print; change and send nothing")
    ap.add_argument("--no-send", action="store_true", help="repair and record, but do not message")
    ap.add_argument("--force", action="store_true", help="run again today")
    ap.add_argument("--days", type=int, default=14, help="how far back to hunt for refused verdicts")
    args = ap.parse_args()

    now = utcnow()
    last = last_entry()
    if last and last.get("at", "")[:10] == iso(now)[:10] and not args.force and not args.dry_run:
        print(f"ledger_watch: already ran today ({last['at']}); --force to run again")
        return 0 if last.get("pass") else 1
    prev, label = previous(now)

    node = "manual session" if not args.dry_run else "dry run"

    # 1-2. bring the checkout up to date, then repair. Both write into the shared checkout, and
    # so does every landing in every body (land_runs.py holds `.git/symposium-land.lock` for the
    # length of a landing, test suite included). Until 2026-10-23 this pull ran unlocked, which is
    # how a rebase here and a landing there produced the conflicted trees of 2026-10-22.
    sync_note = ""
    recovered: list[str] = []
    whole = ""
    counts = {"collected": 0, "reconciled": 0, "paths": 0}
    if not args.dry_run:
        with shared_checkout_lock(REPO, timeout=900) as held:
            if not held:
                sync_note = ("another body held the shared checkout for 15 minutes; measured "
                             "without syncing or repairing")
            else:
                # 2026-10-25 (Desi): this used to be `pull --rebase --autostash`. The run of
                # 07:45 stopped on the first of 58 commits, committed the conflicted tree anyway,
                # and left the checkout mid-rebase for two and a half hours with every landing in
                # every body failing behind it. Never rebase this tree; never measure a tree with
                # an unfinished operation in it.
                sync_note = sync_checkout(REPO)
                recovered = recover_verdicts(now - dt.timedelta(days=args.days), apply=True)
                counts = filed_and_reconciled(apply=True)
                whole = file_whole_repo_review(now)
    else:
        recovered = [r + " [would recover]" for r in
                     recover_verdicts(now - dt.timedelta(days=args.days), apply=False)]
        whole = file_whole_repo_review(now, apply=False)
    repairs = {**counts, "recovered": recovered, "whole_review": whole}

    # 3. measure after repairing, so the message describes the true state
    m = measure(now)
    passes, reasons = verdict(m, prev)
    text = message(m, prev, label, repairs, passes, reasons, node)
    if sync_note:
        text += f"\n({sync_note})"

    print(text)

    # 4. record, send, and commit what the repairs changed
    if not args.dry_run:
        record(m, repairs, passes, text)
        if not args.no_send:
            print("\nledger_watch: " + telegram(text, dry=False))
        with shared_checkout_lock(REPO, timeout=900) as held:
            if held:
                commit_and_push(m)
            else:
                print("ledger_watch: shared checkout busy; the repair is on disk and will go up "
                      "with the next run")

    return 0 if passes else 1


_MARKERS = ("<<<<<<<", ">>>>>>>")
_COMMITTED_PATHS = ("channels/items.jsonl", "channels/watch")


def unmerged_state(repo: Path) -> str | None:
    """The unfinished git operation leaving conflict markers in the tree, if there is one.

    Named rather than boolean: the message this feeds should say *which* operation to abort.
    """
    gitdir = repo / ".git"
    for name in ("rebase-merge", "rebase-apply", "MERGE_HEAD", "CHERRY_PICK_HEAD"):
        if (gitdir / name).exists():
            return name
    return None


def abort_unfinished(repo: Path, state: str) -> str:
    """End the unfinished operation. Returns the phrase to put in the sync note."""
    verb = {"rebase-merge": "rebase", "rebase-apply": "rebase",
            "MERGE_HEAD": "merge", "CHERRY_PICK_HEAD": "cherry-pick"}[state]
    out = subprocess.run(["git", "-C", str(repo), f"{verb}", "--abort"],
                         capture_output=True, text=True, timeout=300)
    if out.returncode == 0:
        return f"aborted the unfinished {verb}"
    return f"could not abort the unfinished {verb} ({(out.stderr or '').strip()[:120]})"


def detached(repo: Path) -> bool:
    """True when HEAD is not on a branch. `git push origin HEAD:main` from here writes straight to
    main with no branch of its own — which is how the half-merged ledger reached main at 11:45Z."""
    return subprocess.run(["git", "-C", str(repo), "symbolic-ref", "-q", "HEAD"],
                          capture_output=True, text=True).returncode != 0


def sync_checkout(repo: Path) -> str:
    """Bring the shared checkout level with origin/main without ever starting a rebase.

    A rebase in a tree five bodies write to is a trap: it can stop half-way and leave the checkout
    detached with conflict markers in the ledger, which is what happened on 2026-10-22 and again on
    2026-10-25 (see the report). So: end anything unfinished, fetch, and fast-forward only. A
    *diverged* checkout is named and left alone — reconciling a stranded branch is a wake's job with
    turns to spend, not a clock's.
    """
    def g(*args: str) -> subprocess.CompletedProcess:
        # `repo`, not the module's REPO: the tests drive this against throwaway checkouts.
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                              timeout=120)

    state = unmerged_state(repo)
    if state:
        abort_unfinished(repo, state)
    g("fetch", "-q", "origin", "main")
    ahead = int(g("rev-list", "--count", "origin/main..HEAD").stdout.strip() or 0)
    behind = int(g("rev-list", "--count", "HEAD..origin/main").stdout.strip() or 0)
    if ahead and behind:
        return (f"checkout is {ahead} commit(s) ahead of and {behind} behind origin/main — not "
                f"reconciling here; measured what is on disk")
    if behind:
        if g("merge", "--ff-only", "-q", "origin/main").returncode != 0:
            return "checkout could not fast-forward to origin/main; measured what is on disk"
    return ""


def markers_in_patch(diff_text: str) -> list[str]:
    """Conflict markers a staged diff would *add*, i.e. lines this commit would introduce.

    Only added lines count: a marker already red in the tree is a separate problem, and blocking
    on it would freeze the commit path forever instead of stopping the one commit that made it.
    """
    found: list[str] = []
    for line in diff_text.splitlines():
        if not line.startswith("+"):
            continue
        body = line[1:].rstrip()
        if body.startswith(_MARKERS) or body == "=======":
            found.append(body)
    return found


def commit_and_push(m: dict) -> None:
    status = git("status", "--porcelain").stdout.strip()
    if not status:
        return
    git("add", *_COMMITTED_PATHS)
    # Guard added 2026-10-25 (Desi), after this function committed a half-merged ledger to main:
    # the 07:45 run's pull conflicted, the note said "measured what is here", and the commit went
    # up carrying three marker lines and a stale conflict block. The ledger does not fail on those
    # lines; it skips them and under-reports, which is why nothing noticed for a day.
    state = unmerged_state(REPO)
    if state:
        git("reset", "-q", "--", *_COMMITTED_PATHS)
        print(f"ledger_watch: refusing to commit during an unfinished git operation ({state}); "
              f"the repair stays on disk. Run `{state}` to a clean tree and rerun.")
        return
    added = markers_in_patch(git("diff", "--cached", "-U0").stdout)
    if added:
        git("reset", "-q", "--", *_COMMITTED_PATHS)
        print("ledger_watch: refusing to commit conflict markers "
              f"({len(added)} added line(s), first {added[0][:40]!r}); nothing was committed")
        return
    ident = ["-c", "user.name=desi", "-c", "user.email=desi@llm-symposium.local"]
    commit = subprocess.run(["git", "-C", str(REPO), *ident, "commit", "-q", "-m",
                             f"watch: daily ledger check {m['at'][:10]} — "
                             f"queue {m['queue']}, reviews {m['model_decisions_24h']}, "
                             f"pile {m['pile']}"],
                            capture_output=True, text=True, timeout=120)
    if commit.returncode != 0:
        print("ledger_watch: commit failed: " + (commit.stderr or "")[-200:])
        return
    # 2026-10-25 (Desi): the retry here used to be another `pull --rebase`, and the push used
    # HEAD:main — which writes to main from whatever HEAD happens to be. Both are gone: a detached
    # HEAD refuses, and a refused push is left for a landing to carry rather than rebasing a tree
    # five bodies write to.
    if detached(REPO):
        print("ledger_watch: refusing to push from a detached HEAD (the repair is committed on "
              "whatever is checked out); a landing will carry it once main is back on a branch")
        return
    push = git("push", "--quiet", "origin", "HEAD:main")
    if push.returncode != 0:
        print("ledger_watch: push refused (" + ((push.stderr or "").strip()[:150]) +
              "); the repair is committed on main and the next landing carries it")


if __name__ == "__main__":
    sys.exit(main())
