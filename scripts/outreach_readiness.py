#!/usr/bin/env python3
# Owner: Desi
"""Is every prepared outreach draft accounted for, unique, and postable?

Agenda item 22, Track 1 (outbound institutional stewardship).

The ledger `channels/outreach/pipeline.json` names one draft per prospect, and
`scripts/outreach_ledger_audit.py` walks that ledger asking whether each row's *claim*
matches the file's *location* (staged / queued / sent / dangling). It reads the ledger and
looks outward; it cannot see a file the ledger never names.

This script asks the complementary question, outward-in, over the files themselves:

  1. **Orphan** — a draft sitting in one of the two holding directories
     (`channels/outreach/drafts/`, `channels/outbound/`) that NO ledger row names. The
     ledger cannot contradict a file it never mentions, and a second copy of a letter under
     a second name is exactly how "one message, one file" silently becomes two. This is not
     hypothetical: the 2026-10-03 04:19Z wake staged a copy of the Internet Archive pitch as
     `internet_archive.md` while `2026-10-01-stewardship-internet-archive.md` already existed,
     byte-for-byte identical, and the ledger named only the dated one.
  2. **Duplicate** — two holding-file drafts with byte-identical content: the same letter
     staged twice under two names.
  3. **Missing** — a ledger row that names a draft which is on disk in none of the three
     directories (staged / queued / sent): a row pointing at air.
  4. **Unknown identity** — a draft whose `Identity:` header is not one of the four amigos.
     `channels/mail.py::send_draft` refuses it, so it can never leave by any path.
  5. **Reach** — which holding-file drafts the *scheduled* drainer can carry, and which
     cannot. The daily drainer (`.github/workflows/quiet-check.yml`) holds only Desi's
     credentials (`SYMPOSIUM_MAIL_USER_DESI`), and `channels/mail.py::credentials_for`
     refuses any other identity rather than sending it from the wrong mailbox (Finding
     RT-7). So a draft signed by another amigo is **session-only**: it leaves only from that
     amigo's own session, or once its own credentials exist (channels/risks.md R-007). Reach
     is reported, never failed on — it is a standing condition, not a file a wake can fix.

Layers 1-4 are drift and make `--check` exit 1. Layer 5 does not: a repository where three
of four amigos cannot be sent for by the machine is in a known, recorded state, and a gate
that stays red until the human creates mailboxes would stop reporting everything else.

This is a report, not an actor. It changes nothing.

Usage:
    python3 scripts/outreach_readiness.py [--check] [--sender-identity IDENTITY] [--root PATH]
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWN_IDENTITIES = ("desi", "claude", "gemini", "tarik")
# The identity the *scheduled* drainer can carry. quiet-check.yml wires only
# SYMPOSIUM_MAIL_USER_DESI; channels/mail.py treats the generic pair as Desi's, so
# a draft with no Identity header also resolves here.
DEFAULT_SENDER = "desi"

HEADER_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")


def read_identity(path: Path) -> str:
    """Return the draft's `Identity:` value (lower-cased), or "" if it names none.

    Only the leading header block is read, so a body line that happens to look like a
    header cannot be mistaken for one.
    """
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            break
        m = HEADER_RE.match(line)
        if not m:
            break
        if m.group(1).lower() == "identity":
            return m.group(2).strip().lower()
    return ""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _holding_files(drafts_dir: Path, outbound_dir: Path) -> list[Path]:
    """Drafts in the two directories that are meant to hold an unsent message.

    `channels/sent/` is history and holds much non-outreach mail, so it is not scanned
    for orphans or duplicates — only looked up when resolving a ledger row.
    """
    files: list[Path] = []
    for d in (drafts_dir, outbound_dir):
        if d.is_dir():
            for f in sorted(d.glob("*.md")):
                if f.name.lower() == "readme.md":
                    continue
                files.append(f)
    return files


def _named_basenames(prospects: list[dict]) -> dict[str, list[str]]:
    named: dict[str, list[str]] = {}
    for p in prospects:
        d = p.get("draft")
        if d:
            named.setdefault(Path(d).name, []).append(p.get("id", "?"))
    return named


def _locate(name: str, drafts_dir: Path, outbound_dir: Path, sent_dir: Path) -> Path | None:
    for d, label in ((outbound_dir, "queued"), (sent_dir, "sent"), (drafts_dir, "staged")):
        if (d / name).is_file():
            return d / name
    return None


def classify_reach(identity: str, sender: str) -> tuple[str, str]:
    """(reach, note) for a draft's Identity header against the scheduled sender."""
    if not identity:
        return ("machine", "no Identity header — mail.py sends it as the generic identity (Desi's)")
    if identity not in KNOWN_IDENTITIES:
        return ("unknown", f"'{identity}' is not one of {', '.join(KNOWN_IDENTITIES)}; the sender refuses it")
    if identity == sender:
        return ("machine", f"signed {identity}, the scheduled drainer's own identity")
    return ("session-only", f"signed {identity}; the scheduled drainer carries only '{sender}' (R-007)")


def audit(
    ledger_path: Path | None = None,
    drafts_dir: Path | None = None,
    outbound_dir: Path | None = None,
    sent_dir: Path | None = None,
    sender: str = DEFAULT_SENDER,
) -> dict:
    """Return a dict of findings. Raises ValueError if the ledger is not the outreach ledger."""
    repo = REPO_ROOT
    ledger_path = ledger_path or repo / "channels" / "outreach" / "pipeline.json"
    drafts_dir = drafts_dir or repo / "channels" / "outreach" / "drafts"
    outbound_dir = outbound_dir or repo / "channels" / "outbound"
    sent_dir = sent_dir or repo / "channels" / "sent"

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    if not isinstance(ledger.get("prospects"), list):
        raise ValueError(f"{ledger_path}: no `prospects` list — is this the outreach ledger?")
    prospects = ledger["prospects"]
    named = _named_basenames(prospects)

    # --- missing: a ledger row naming a draft that is on no disk ------------------
    missing = []
    for p in prospects:
        d = p.get("draft")
        if not d:
            continue
        if _locate(Path(d).name, drafts_dir, outbound_dir, sent_dir) is None:
            missing.append({"id": p.get("id", "?"), "draft": d})

    # --- holding files: orphans, duplicates, identity, reach ----------------------
    holding = _holding_files(drafts_dir, outbound_dir)

    orphans = [f.name for f in holding if f.name not in named]

    by_hash: dict[str, list[str]] = {}
    for f in holding:
        by_hash.setdefault(_sha256(f), []).append(f.name)
    duplicates = sorted([sorted(names) for names in by_hash.values() if len(names) > 1])

    files = []
    for f in holding:
        identity = read_identity(f)
        reach, note = classify_reach(identity, sender)
        files.append({
            "file": f.name,
            "dir": "drafts" if f.parent == drafts_dir else "outbound",
            "identity": identity or "(none)",
            "named_by": named.get(f.name, []),
            "reach": reach,
            "note": note,
        })

    unknown_identity = [r["file"] for r in files if r["reach"] == "unknown"]

    return {
        "ledger_path": ledger_path,
        "sender": sender,
        "rows": len(prospects),
        "named_drafts": len(named),
        "holding_files": files,
        "orphans": orphans,
        "duplicates": duplicates,
        "missing": missing,
        "unknown_identity": unknown_identity,
        "machine_reach": sum(1 for r in files if r["reach"] == "machine"),
        "session_only": sum(1 for r in files if r["reach"] == "session-only"),
    }


def _commit(root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=root,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001 — a courtesy, not the audit
        return "unknown"


def format_report(r: dict, commit: str, now: str) -> str:
    lines = [
        f"Outreach readiness — {now} — commit {commit}",
        f"ledger: {r['ledger_path']}",
        f"scheduled drainer can carry identity: '{r['sender']}'",
        "",
        f"{'draft file':<52}{'identity':<10}{'reach':<14}named by",
    ]
    for f in r["holding_files"]:
        named = ", ".join(f["named_by"]) or "(no ledger row)"
        lines.append(f"{f['file']:<52}{f['identity']:<10}{f['reach']:<14}{named}")
    lines += [
        "",
        f"summary: {r['rows']} ledger rows; {len(r['holding_files'])} holding-file drafts "
        f"(machine-sendable = {r['machine_reach']}; session-only = {r['session_only']}); "
        f"orphans = {len(r['orphans'])}; duplicate sets = {len(r['duplicates'])}; "
        f"named-but-absent = {len(r['missing'])}; unknown identity = {len(r['unknown_identity'])}",
    ]
    for name in r["orphans"]:
        lines.append(f"ORPHAN: {name} is in a holding directory but no ledger row names it")
    for group in r["duplicates"]:
        lines.append(f"DUPLICATE: byte-identical drafts {group}")
    for m in r["missing"]:
        lines.append(f"MISSING: ledger row '{m['id']}' names {m['draft']}, absent from all three directories")
    for name in r["unknown_identity"]:
        lines.append(f"UNKNOWN IDENTITY: {name} cannot be sent by any configured mailbox")
    if r["session_only"]:
        lines.append(
            f"NOTE (not a failure): {r['session_only']} draft(s) are signed by an identity the "
            f"scheduled drainer cannot carry (R-007) — they leave only from that amigo's session.")
    return "\n".join(lines)


def drift(r: dict) -> bool:
    """True when the repository's files and ledger disagree in a way a file can fix."""
    return bool(r["orphans"] or r["duplicates"] or r["missing"] or r["unknown_identity"])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the files and the ledger drift (still prints the full report)")
    ap.add_argument("--sender-identity", default=DEFAULT_SENDER)
    ap.add_argument("--root", type=Path, default=REPO_ROOT,
                    help="repository root to scan (default: this checkout)")
    args = ap.parse_args(argv)

    root = args.root
    try:
        r = audit(
            ledger_path=root / "channels" / "outreach" / "pipeline.json",
            drafts_dir=root / "channels" / "outreach" / "drafts",
            outbound_dir=root / "channels" / "outbound",
            sent_dir=root / "channels" / "sent",
            sender=args.sender_identity,
        )
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"outreach_readiness: {e}", file=sys.stderr)
        return 2

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(format_report(r, _commit(root), now))
    return 1 if (args.check and drift(r)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
