#!/usr/bin/env python3
# Owner: Desi
"""Audit the outreach ledger against the mail queue's own files.

`channels/outreach/pipeline.json` is the outbound prospect ledger: for each prospect it
records a `status` (contacted or not, and how) and, when a draft exists, a `draft` path.
Both drift, and the drift is invisible because the ledger is prose. It has already
happened once: the file said in one field that the sending leg had "never been used for a
single cold contact" while two cold contacts sat in `channels/sent/`.

The file's location is the ground truth, and it is not a matter of opinion:
`channels/mail.py::send_draft` moves a draft from `channels/outbound/` to
`channels/sent/` **only after SMTP accepts the message** (the `path.replace(...)` is after
`server.send_message(...)`; on any exception the draft stays in the outbox). So:

  * in `channels/outreach/drafts/` -> written, not queued   (reality: staged)
  * in `channels/outbound/` -> drafted, not sent            (reality: queued)
  * in `channels/sent/`     -> transmitted                  (reality: sent)
  * in neither              -> named but lost               (reality: dangling)

The four realities above are keyed off the drafts the *ledger names*. That left the other
half of the honest-ledger promise unguarded: `channels/outreach/drafts/README.md` says the
ledger "names each prepared draft in its draft field", but nothing checked it, so a draft
staged by a run that never touched the ledger was invisible to this audit. That happened on
2026-10-01 — three institutional drafts (Internet Archive, Software Heritage, and a duplicate
Long Now) sat in the staged directory and this report still read "staged = 5". So the audit
now also scans the staged directory and reports every `*.md` no ledger row names as an
**orphan draft**: a prepared message the ledger is blind to. `README.md` is excluded.

This is a report, not an actor. It changes nothing. With no arguments it prints the table
and exits 0; with `--check` it still prints everything but exits 1 when any row drifts or an
orphan draft exists, so a workflow can use it as a gate.

Usage:
    python3 scripts/outreach_ledger_audit.py [--check] [--ledger PATH]
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = REPO_ROOT / "channels" / "outreach" / "pipeline.json"
OUTBOUND_DIR = REPO_ROOT / "channels" / "outbound"
SENT_DIR = REPO_ROOT / "channels" / "sent"
STAGED_DIR = REPO_ROOT / "channels" / "outreach" / "drafts"

# A status is read by markers, not by meaning: the ledger is prose and cannot be parsed.
# "queued"/"drafted" claim the draft has not left the outbox; "sent"/"shipped"/"mailed"
# claim it has. Order matters: a status that says both is read by its strongest claim.
DRAFT_CLAIM = ("drafted", "queued")
SENT_CLAIM = ("sent", "shipped", "mailed", "transmitted")

# Exact prose that claims the outbound leg has carried nothing. Searched literally, in the
# ledger's own text fields, only so the contradiction is named rather than left silent.
NO_CONTACT_PHRASES = ("never been used for a single cold contact", "never sent a cold contact")


def classify(draft: str | None, outbound_dir: Path, sent_dir: Path, repo_root: Path) -> tuple[str, str | None]:
    """Where is this prospect's draft, really?

    Returns (reality, path) with reality in {none, staged, queued, sent, dangling}.
    """
    if not draft:
        return ("none", None)
    name = Path(draft).name
    staged_dir = repo_root / "channels" / "outreach" / "drafts"
    if (outbound_dir / name).is_file():
        return ("queued", str(outbound_dir / name))
    if (sent_dir / name).is_file():
        return ("sent", str(sent_dir / name))
    if (staged_dir / name).is_file():  # written and held, not put in a queue
        return ("staged", str(staged_dir / name))
    if (repo_root / draft).is_file():  # named path resolves but is in none of the three folders
        return ("queued", str(repo_root / draft))
    return ("dangling", None)


def verdict(reality: str, status: str) -> str:
    """Does the prose `status` agree with `reality`?"""
    s = (status or "").lower()
    if reality == "dangling":
        return "DANGLING"          # a draft is named but the file is in neither folder
    if reality == "sent":
        return "ok" if any(m in s for m in SENT_CLAIM) else "STALE"
    if reality in ("queued", "staged"):
        return "STALE" if any(m in s for m in SENT_CLAIM) else "ok"
    # reality == "none": no draft named. Fine, unless the row claims one.
    return "NO-DRAFT" if any(m in s for m in DRAFT_CLAIM) else "ok"


def audit(ledger_path: Path = DEFAULT_LEDGER, repo_root: Path = REPO_ROOT):
    """Return (rows, sent_count, contradictions, orphans). Raise ValueError on a malformed ledger.

    `orphans` is the list of staged-draft filenames (`channels/outreach/drafts/*.md`, README
    excluded) that no ledger row names — prepared messages the ledger is blind to.
    """
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    if not isinstance(ledger.get("prospects"), list):
        raise ValueError(f"{ledger_path}: no `prospects` list — is this the outreach ledger?")
    outbound = repo_root / "channels" / "outbound"
    sent = repo_root / "channels" / "sent"

    rows = []
    for p in ledger["prospects"]:
        draft = p.get("draft")
        status = (p.get("status") or "").strip()
        reality, path = classify(draft, outbound, sent, repo_root)
        rows.append({
            "id": p.get("id", "?"),
            "tier": p.get("tier", "?"),
            "status": status,
            "draft": draft,
            "reality": reality,
            "path": path,
            "verdict": verdict(reality, status),
        })

    sent_count = sum(1 for r in rows if r["reality"] == "sent")
    prose = json.dumps(ledger)
    contradictions = [ph for ph in NO_CONTACT_PHRASES if ph in prose and sent_count > 0]

    # A staged draft the ledger does not name is one the ledger is blind to. This is the
    # other half of "the ledger names each prepared draft": the rows above only cover drafts
    # that are *named*, so a file dropped in the staged directory by a run that never edited
    # the ledger would otherwise leave no trace here.
    named = {Path(r["draft"]).name for r in rows if r["draft"]}
    staged_dir = repo_root / "channels" / "outreach" / "drafts"
    orphans = sorted(
        p.name for p in staged_dir.glob("*.md")
        if p.name != "README.md" and p.name not in named
    ) if staged_dir.is_dir() else []

    return rows, sent_count, contradictions, orphans


def _commit(repo_root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001 — the commit is a courtesy, not the audit
        return "unknown"


def format_report(rows, sent_count, contradictions, orphans, ledger_path: Path, commit: str, now: str) -> str:
    lines = [
        f"Outreach ledger audit — {now} — commit {commit}",
        f"ledger: {ledger_path}",
        "",
        f"{'prospect':<24}{'tier':<5}{'reality':<10}{'verdict':<10}status",
    ]
    for r in rows:
        lines.append(f"{r['id']:<24}{r['tier']:<5}{r['reality']:<10}{r['verdict']:<10}{r['status']}")
    stale = sum(1 for r in rows if r["verdict"] == "STALE")
    dangling = sum(1 for r in rows if r["verdict"] == "DANGLING")
    nodraft = sum(1 for r in rows if r["verdict"] == "NO-DRAFT")
    staged = sum(1 for r in rows if r["reality"] == "staged")
    lines += [
        "",
        f"summary: {len(rows)} prospects; cold contacts in channels/sent/ = {sent_count}; "
        f"staged = {staged}; stale = {stale}; dangling = {dangling}; "
        f"claims-a-draft-with-none = {nodraft}; orphan drafts = {len(orphans)}",
    ]
    for ph in contradictions:
        lines.append(
            f"CONTRADICTION: ledger prose says {ph!r} but {sent_count} prospect draft(s) "
            f"sit in channels/sent/ — the leg is not unused."
        )
    for name in orphans:
        lines.append(
            f"ORPHAN DRAFT: channels/outreach/drafts/{name} exists but no ledger row names it — "
            f"register it in channels/outreach/pipeline.json or withdraw it. The ledger is blind to it."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any row drifts (still prints the full report)")
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    args = ap.parse_args(argv)

    try:
        rows, sent_count, contradictions, orphans = audit(args.ledger)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"outreach_ledger_audit: {e}", file=sys.stderr)
        return 2

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(format_report(rows, sent_count, contradictions, orphans, args.ledger,
                        _commit(REPO_ROOT), now))

    drift = (any(r["verdict"] != "ok" for r in rows)
             or bool(contradictions)
             or bool(orphans))
    return 1 if (args.check and drift) else 0


if __name__ == "__main__":
    raise SystemExit(main())
