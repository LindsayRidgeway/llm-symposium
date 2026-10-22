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


def verdict(now_m: dict, prev: dict | None, label: str = "yesterday") -> tuple[bool, list[str]]:
    """His rule: the queue must never exceed one day's arrivals. Progress is separate from that."""
    reasons = []
    passes = now_m["queue"] <= max(now_m["arrivals_24h"], 1)
    if passes:
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
    return passes, reasons


def message(m: dict, prev: dict | None, label: str, repairs: dict, passes: bool,
            reasons: list[str], node: str) -> str:
    lines = [f"Review check, {m['at'][:10]} ({node})."]
    lines.append(f"Waiting for review: {m['queue']}" +
                 (f" ({label} {prev['queue']})" if prev else "") +
                 f" · filed in 24h: {m['arrivals_24h']}")
    lines.append(f"Reviews by a model, 24h: {m['model_decisions_24h']}"
                 f" · closed by the landing bot: {m['machine_closures_24h']}")
    lines.append(f"Finished and never read: {m['pile']}"
                 + (f" ({label} {prev['pile']})" if prev else "")
                 + f" · read out of that pile in 24h: {m['pile_read_24h']}")
    lines.append(f"Refused landings, 24h: {m['gate_refusals_24h']}"
                 f" ({m['gate_refusals_carrying_verdicts_24h']} carried a verdict)")
    did = []
    if repairs.get("recovered"):
        did.append(f"recovered {len(repairs['recovered'])} verdict(s) a refused landing had thrown away")
    if repairs.get("collected"):
        did.append(f"filed {repairs['collected']} item(s) no wake had recorded")
    if repairs.get("reconciled") or repairs.get("paths"):
        did.append(f"closed {repairs['reconciled'] + repairs['paths']} landed item(s)")
    lines.append("Repaired: " + ("; ".join(did) if did else "nothing needed repairing"))
    lines.append(("PASS" if passes else "FAIL") + " — " + reasons[0] +
                 ("" if passes else ". The mechanism still needs changing, not the instruction."))
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

    # 1. bring the checkout up to date; a failure here is reported, not fatal
    sync_note = ""
    if not args.dry_run:
        pull = git("pull", "--rebase", "--autostash", "--quiet")
        if pull.returncode != 0:
            sync_note = "checkout could not be synced (conflict); measured what is here"

    # 2. repair
    recovered: list[str] = []
    counts = {"collected": 0, "reconciled": 0, "paths": 0}
    if not args.dry_run:
        recovered = recover_verdicts(now - dt.timedelta(days=args.days), apply=True)
        counts = filed_and_reconciled(apply=True)
    else:
        recovered = [r + " [would recover]" for r in
                     recover_verdicts(now - dt.timedelta(days=args.days), apply=False)]
    repairs = {**counts, "recovered": recovered}

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
        commit_and_push(m)

    return 0 if passes else 1


def commit_and_push(m: dict) -> None:
    status = git("status", "--porcelain").stdout.strip()
    if not status:
        return
    git("add", "channels/items.jsonl", "channels/watch")
    ident = ["-c", "user.name=desi", "-c", "user.email=desi@llm-symposium.local"]
    commit = subprocess.run(["git", "-C", str(REPO), *ident, "commit", "-q", "-m",
                             f"watch: daily ledger check {m['at'][:10]} — "
                             f"queue {m['queue']}, reviews {m['model_decisions_24h']}, "
                             f"pile {m['pile']}"],
                            capture_output=True, text=True, timeout=120)
    if commit.returncode != 0:
        print("ledger_watch: commit failed: " + (commit.stderr or "")[-200:])
        return
    for attempt in range(2):
        push = git("push", "--quiet", "origin", "HEAD:main")
        if push.returncode == 0:
            return
        if attempt == 0:
            git("pull", "--rebase", "--autostash", "--quiet")
    print("ledger_watch: push failed; the repair is committed locally and will go up with the next "
          "wake that pushes")


if __name__ == "__main__":
    sys.exit(main())
