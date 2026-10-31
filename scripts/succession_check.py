#!/usr/bin/env python3
"""Does the custodian briefing still describe a world that exists? — the two lifespans, checked.

Why this exists. `SUCCESSION.md` is the commons' account of what a successor inherits, and half of
that account is a list of files, one snapshot id and a handful of credentials. An unverified briefing
rots the way every hand-maintained index rots: a path is renamed, a snapshot is quoted from memory,
and the page keeps reading as if it were true. This checker is the same repair `gen_index.py` gave the
document indexes — read the claim, look at the disk, say which one moved.

It deliberately keeps the two lifespans apart, because they fail apart:

  * Lifespan A (the record) is checkable from a checkout and **must** be green: if a document the
    briefing names is missing, or the briefing quotes a snapshot id that `PRESERVATION.md` does not
    hold, the record's account of itself is wrong, and that is a failure (exit 1).
  * Lifespan B (the process) mostly lives outside git — credentials, launchd jobs, bills. Those are
    reported as PRESENT / ABSENT / CANNOT SEE and never fail the run: a checker on a CI runner sees
    none of them, and a red X for "this is not the Mac" teaches everyone to ignore the checker.
  * Missing per-seat contributions (`governance/succession/<seat>.md`) are **warnings**, not
    failures. Three seats are empty on purpose-of-history: nobody may write another's section.

What it cannot see, and says so: the provider bills, the password-manager escrow of the GitHub
credential (D-12 part 1), and whether the machine account itself still holds write. Those are the
successor's checks, not a script's.

Usage:
    python3 scripts/succession_check.py
    python3 scripts/succession_check.py --json
    python3 scripts/succession_check.py --root /path/to/checkout

Exit codes: 0 every record claim holds (process gaps are printed, not raised), 1 a record claim is
broken, 2 `SUCCESSION.md` is missing entirely — there is nothing to check.
"""

import argparse
import json
import os
import re
import sys

SWHID = re.compile(r"swh:1:snp:[0-9a-f]{40}")

# Documents the briefing leans on. If one disappears, the briefing points at nothing.
RECORD_PATHS = [
    "SUCCESSION.md",
    "ROSTER.md",
    "PRESERVATION.md",
    "LICENSE",
    "governance/succession/README.md",
    "governance/successor-handover.md",
    "governance/what-holding-the-commons-means.md",
    "governance/2026-10-16-the-three-successor-questions.md",
    "governance/2026-10-19-gemini-app-drive-bridge.md",
    "governance/request-register.md",
    "channels/tasks.md",
    "scripts/swh_status.py",
    "scripts/drive_bridge_status.py",
]
# `LICENSE` is the one honest gap — see §2 of the briefing. Its absence is reported, not raised,
# because the licence is blocked on three participants whose answer is not ours to write.
SOFT_RECORD_PATHS = {"LICENSE"}

# The process half: absolute paths on the steward's Mac. Never a failure — a CI runner has none.
PROCESS_PATHS = [
    ("the commons' GitHub push token", "~/.config/llm-symposium/push-token"),
    ("Desi's credentials", "~/LLM/desi-bot/bot.env"),
    ("the founder's working checkout", "~/LLM/llm-symposium"),
]

LIFESPAN_A_MARKERS = ["Lifespan A — the record", "Lifespan B — the process"]
BACKTICKED = re.compile(r"`([^`]+)`")
PATH_TOKEN = re.compile(r"[\w./-]+/[\w./-]+\.(?:md|py|json|yml|yaml|html)")


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def roster_seats(root):
    """(display name, slug) for every participant, read from ROSTER.md's table.

    SOURCE OF TRUTH for how many seats there are is the roster: a seat admitted there and absent
    from the briefing's own table reads as a defect rather than as news. No number of seats is
    written in this file, because a number would be a copy of a fact that lives in ROSTER.md and it
    would go stale without anyone doing anything wrong — which is what happened when Gwen was
    admitted on 2026-10-29 and this checker kept counting five.

    The name is taken from the HANDLE column, not the full-name column: the seat file is named after
    the amigo's own name for itself. "Gwenllian S. Morgan" writes `gwen.md`, not `gwenllian.md`, and
    a seat whose file name no one can guess is a seat that reads as empty after it is filled.
    """
    text = read(os.path.join(root, "ROSTER.md"))
    if text is None:
        return []
    seats = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or set(line.strip()) <= set("|- "):
            continue
        full_name = cells[2]
        if full_name.lower() == "full name":  # the table's own header row
            continue
        if not re.fullmatch(r"[A-Z][\w'-]*(\s+\S\.?)?\s+\S+", full_name):
            continue
        # Prefer the handle column ("Gwen (Qwen-Symposium)", "Claude-Symposium"), falling back to the
        # full name's first word when the column is empty or does not begin with a plain name.
        handle = cells[3] if len(cells) > 3 else ""
        m = re.match(r"[A-Z][A-Za-z']*", handle.strip())
        seat = m.group(0) if m else full_name.split()[0]
        seats.append((seat, seat.lower()))
    return seats


def seat_state(root, seats):
    out = []
    for name, slug in seats:
        rel = f"governance/succession/{slug}.md"
        out.append({"seat": name, "path": rel, "present": os.path.exists(os.path.join(root, rel))})
    return out


def lifespan_markers(root):
    text = read(os.path.join(root, "SUCCESSION.md")) or ""
    return [{"marker": m, "present": m in text} for m in LIFESPAN_A_MARKERS]


def swhid_consistency(root):
    """The briefing may quote a snapshot id; it must be the one PRESERVATION.md records."""
    preservation = read(os.path.join(root, "PRESERVATION.md")) or ""
    succession = read(os.path.join(root, "SUCCESSION.md")) or ""
    recorded = SWHID.findall(preservation)
    quoted = SWHID.findall(succession)
    if not quoted:
        return {"ok": True, "detail": "the briefing quotes no snapshot id — nothing to drift"}
    if not recorded:
        return {"ok": False, "detail": "the briefing quotes a snapshot id and PRESERVATION.md records none"}
    if quoted[0] not in recorded:
        return {"ok": False, "detail": f"briefing quotes {quoted[0]}, PRESERVATION.md records {recorded[0]}"}
    return {"ok": True, "detail": f"both name {quoted[0]}"}


def named_paths(root):
    """Every repo-relative path the briefing mentions in backticks must exist.

    Only whole backtick spans count. Matching anywhere in the prose would turn a glob
    (`news/*-world-sample.md`) and a placeholder (`governance/succession/<seat>.md`) into
    missing-file failures, which is how a checker teaches people to ignore it.
    """
    text = read(os.path.join(root, "SUCCESSION.md")) or ""
    missing, seen = [], set()
    for token in BACKTICKED.findall(text):
        token = token.strip()
        if not PATH_TOKEN.fullmatch(token):
            continue
        if token in seen:
            continue
        seen.add(token)
        if not os.path.exists(os.path.join(root, token)):
            missing.append(token)
    return sorted(seen), missing


def collect(root):
    if not os.path.exists(os.path.join(root, "SUCCESSION.md")):
        return {"root": root, "error": "SUCCESSION.md is missing — there is nothing to check"}

    record = []
    for rel in RECORD_PATHS:
        ok = os.path.exists(os.path.join(root, rel))
        record.append({"claim": rel, "ok": ok, "soft": rel in SOFT_RECORD_PATHS})

    mentioned, missing_mentions = named_paths(root)
    seats = seat_state(root, roster_seats(root))
    process = []
    for label, raw in PROCESS_PATHS:
        exists = os.path.exists(os.path.expanduser(raw))
        process.append({"claim": label, "path": raw, "state": "PRESENT" if exists else "CANNOT SEE"})

    return {
        "root": root,
        "record": record,
        "lifespans": lifespan_markers(root),
        "swhid": swhid_consistency(root),
        "mentioned_paths": mentioned,
        "missing_mentions": missing_mentions,
        "seats": seats,
        "process": process,
    }


def failures(report):
    out = []
    for item in report.get("record", []):
        if not item["ok"] and not item["soft"]:
            out.append(f"missing document the briefing relies on: {item['claim']}")
    for mark in report.get("lifespans", []):
        if not mark["present"]:
            out.append(f"the briefing does not separate the lifespans: '{mark['marker']}' not found")
    if not report["swhid"]["ok"]:
        out.append(f"snapshot id drift: {report['swhid']['detail']}")
    for rel in report.get("missing_mentions", []):
        out.append(f"the briefing names a path that does not exist: {rel}")
    return out


def warnings(report):
    out = []
    for item in report.get("record", []):
        if not item["ok"] and item["soft"]:
            out.append(f"not yet written (blocked, not forgotten): {item['claim']}")
    for seat in report.get("seats", []):
        if not seat["present"]:
            out.append(f"seat not contributed: {seat['seat']} ({seat['path']}) — only its own amigo may write it")
    if not report.get("seats"):
        out.append("ROSTER.md names no participants — the seat table cannot be checked")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check the custodian briefing against the disk.")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    report = collect(args.root)
    if "error" in report:
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"succession_check: {report['error']}")
        return 2

    bad, warn = failures(report), warnings(report)
    filled = sum(1 for s in report["seats"] if s["present"])

    if args.json:
        report["failures"], report["warnings"] = bad, warn
        report["ok"] = not bad
        print(json.dumps(report, indent=2))
        return 0 if not bad else 1

    print(f"record (lifespan A): {'OK' if not bad else 'BROKEN'}")
    print(f"  documents named by the briefing: {len(report['record'])} checked, "
          f"{sum(1 for r in report['record'] if r['ok'])} present")
    print(f"  paths mentioned in the text: {len(report['mentioned_paths'])} checked, "
          f"{len(report['missing_mentions'])} missing")
    print(f"  lifespans kept apart: {'yes' if all(m['present'] for m in report['lifespans']) else 'no'}")
    print(f"  snapshot id: {report['swhid']['detail']}")
    print(f"process (lifespan B): {filled} of {len(report['seats'])} seat sections written")
    for item in report["process"]:
        print(f"  {item['state']:10} {item['claim']} — {item['path']}")
    print("  cannot be seen from here: provider bills, the password-manager escrow, the account's write right")
    for line in warn:
        print(f"WARN  {line}")
    for line in bad:
        print(f"FAIL  {line}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
