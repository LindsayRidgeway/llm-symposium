#!/usr/bin/env python3
"""Is the Gemini-app Drive bridge still delivering? — a read of the letterbox, not of the script.

Why this exists. The Gemini app cannot read this Mac's disk, so one folder in the human's Google
Drive is its only route to the record: a document put there is converted to plain markdown by a
server-side Apps Script (owned by the human's Google account, body never committed), synced down by
Drive for Desktop, and read off the local filesystem by the Gemini-Goose session. The full record is
`governance/2026-10-19-gemini-app-drive-bridge.md`.

It fails in the direction that looks like nothing to say. Three failures are indistinguishable from
this side — the script errors on export, Drive for Desktop stops syncing, the trigger stops firing —
and all three render as "no new file", which is exactly what a quiet participant renders as. Nothing
in the repository watched the folder, so nothing could tell the two apart.

What it measures: for every `.gdoc` pointer in the folder, whether the sidebar `.md` the script was
supposed to write beside it exists (an orphan is a handoff that was staged and never converted); and
the age of the freshest markdown (past a threshold the bridge is STALE, whether or not anything is
wrong with it); and whether any `Receipt …txt` in the folder claims delivery of a source whose
markdown is not there. A receipt is a *claim written by the reader*, never by the script — one sat in
the real folder saying `Delivered & Verified` beside a pointer that had not converted in three days
(found 2026-10-19, Dmitri, while reviewing `governance/2026-10-19-gemini-app-drive-bridge.md`).

What it cannot see, and says so: the script itself. It can report that the bridge is not delivering.
It can never report that the script is well.

Usage:
    python3 scripts/drive_bridge_status.py
    python3 scripts/drive_bridge_status.py --root "/path/to/LLM Symposium Handoffs"
    python3 scripts/drive_bridge_status.py --max-age-hours 48 --json

Exit codes: 0 the letterbox looks healthy, 1 a handoff is stuck or the newest is stale,
2 the folder is not on this machine at all (which is also what a signed-out Drive looks like).
"""

import argparse
import json
import os
import sys
import time

DEFAULT_ROOT = os.path.join(
    os.path.expanduser("~"),
    "Library",
    "CloudStorage",
    "GoogleDrive-ldridgeway@gmail.com",
    "My Drive",
    "LLM Symposium Handoffs",
)

POINTER_SUFFIX = ".gdoc"
RECEIPT_PREFIX = "receipt"
OK, ANOMALY, ABSENT = 0, 1, 2


def survey(root, max_age_hours=72.0, now=None):
    """Read the folder and return what can be known from the filesystem alone.

    Returns a dict rather than printing, so a test can assert on the facts instead of on prose.
    `now` is injectable for the same reason; pass a POSIX timestamp.
    """
    now = time.time() if now is None else now
    facts = {
        "root": root,
        "exists": os.path.isdir(root),
        "handoffs": [],
        "orphans": [],
        "receipts": [],
        "freshest": None,
        "freshest_age_hours": None,
        "max_age_hours": max_age_hours,
        "state": "ABSENT",
        "notes": [],
    }
    if not facts["exists"]:
        facts["notes"].append(
            "folder absent: either Drive for Desktop is not signed in / not running, or the "
            "folder was moved or renamed. The script cannot be checked from here."
        )
        return facts

    try:
        names = sorted(os.listdir(root))
    except OSError as exc:  # a CloudStorage placeholder can raise rather than list
        facts["notes"].append(f"folder exists but cannot be listed: {exc}")
        return facts

    for name in names:
        path = os.path.join(root, name)
        if name.endswith(POINTER_SUFFIX):
            # "X.md.gdoc" is Drive's pointer for the Google Doc; the script should have written "X.md".
            target_name = name[: -len(POINTER_SUFFIX)]
            target = os.path.join(root, target_name)
            if not os.path.exists(target):
                facts["orphans"].append(
                    {"pointer": name, "mtime": _mtime(path), "expected": target_name}
                )
        elif name.endswith(".md"):
            mt = _mtime(path)
            facts["handoffs"].append({"name": name, "mtime": mt})
        elif name.lower().startswith(RECEIPT_PREFIX) and name.lower().endswith(".txt"):
            facts["receipts"].append(_read_receipt(path))

    facts["handoffs"].sort(key=lambda h: h["mtime"] or 0, reverse=True)
    if facts["handoffs"]:
        freshest = facts["handoffs"][0]
        facts["freshest"] = freshest["name"]
        if freshest["mtime"] is not None:
            age = (now - freshest["mtime"]) / 3600.0
            facts["freshest_age_hours"] = round(age, 1)

    for receipt in facts["receipts"]:
        source = receipt["source"]
        if source:
            present = os.path.exists(os.path.join(root, source))
            receipt["source_present"] = present
            if not present:
                facts["notes"].append(
                    f"receipt '{receipt['name']}' claims delivery of '{source}', which is not in "
                    "the folder: a receipt is written by whoever read a handoff, not by the script, "
                    "so it is evidence of a reader's success and never of a conversion."
                )

    stale = facts["freshest_age_hours"] is None or facts["freshest_age_hours"] > max_age_hours
    if facts["orphans"]:
        facts["state"] = "ORPHANS"
        facts["notes"].append(
            f"{len(facts['orphans'])} pointer(s) with no markdown beside them: staged and never "
            "converted. The script's execution log is the only place that says why."
        )
    elif stale:
        facts["state"] = "STALE"
        facts["notes"].append(
            "no markdown newer than "
            f"{max_age_hours:g} h: either nothing has been handed over, or the bridge is broken. "
            "From this side those are the same reading."
        )
    else:
        facts["state"] = "OK"
    return facts


def _read_receipt(path):
    """Parse the `Key: value` head of a receipt. Prose after it is not parsed; this is not a log."""
    info = {"name": os.path.basename(path), "mtime": _mtime(path), "status": None,
            "source": None, "source_present": None}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            head = fh.readlines()[:40]
    except OSError:
        return info
    for line in head:
        key, sep, value = line.partition(":")
        if not sep:
            continue
        key, value = key.strip().lower(), value.strip()
        if not value:
            continue
        if key in ("status", "state"):
            info["status"] = value
        elif key in ("source file", "source"):
            info["source"] = value
    return info


def _mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def render(facts):
    lines = [f"Gemini-app Drive bridge — {facts['root']}", f"  state: {facts['state']}"]
    if not facts["exists"]:
        lines.extend(f"  note: {n}" for n in facts["notes"])
        return "\n".join(lines)
    lines.append(f"  handoffs seen: {len(facts['handoffs'])}")
    if facts["freshest"]:
        age = facts["freshest_age_hours"]
        stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_mtime_or_zero(facts)))
        lines.append(f"  freshest markdown: {facts['freshest']}  ({stamp}, {age:g} h old)")
    else:
        lines.append("  freshest markdown: none")
    lines.append(f"  orphan pointers: {len(facts['orphans'])}")
    for orphan in facts["orphans"]:
        lines.append(f"    - {orphan['pointer']} (expected {orphan['expected']})")
    if facts["receipts"]:
        lines.append(
            f"  receipts found: {len(facts['receipts'])} (a reader's claim, not a script log)"
        )
        for receipt in facts["receipts"]:
            status = receipt["status"] or "no status line"
            lines.append(f"    - {receipt['name']}: {status}")
    lines.extend(f"  note: {n}" for n in facts["notes"])
    return "\n".join(lines)


def _mtime_or_zero(facts):
    for handoff in facts["handoffs"]:
        if handoff["name"] == facts["freshest"]:
            return handoff["mtime"] or 0
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        default=os.environ.get("LLM_HANDOFF_DIR", DEFAULT_ROOT),
        help="the Drive folder to read (default: the folder on this Mac)",
    )
    parser.add_argument("--max-age-hours", type=float, default=72.0)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    facts = survey(args.root, max_age_hours=args.max_age_hours)
    if args.json:
        print(json.dumps(facts, indent=2))
    else:
        print(render(facts))

    if not facts["exists"]:
        return ABSENT
    return OK if facts["state"] == "OK" else ANOMALY


if __name__ == "__main__":
    sys.exit(main())
