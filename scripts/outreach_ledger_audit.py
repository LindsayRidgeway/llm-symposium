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

A prospect may also carry a `followups` list: paths to later notes to the *same* person (the
Monday pass, `agenda/04-outreach.md`). Each follow-up gets its own row, so a follow-up draft
cannot be invisible drift the way the first contacts once were. Its verdict is existence only
— `ok`, or `DANGLING` if the named file is in none of the three folders — because the
prospect's `status` prose describes the *first* contact and must not be read against a
follow-up's location.

This is a report, not an actor. It changes nothing. With no arguments it prints the table
and exits 0; with `--check` it still prints everything but exits 1 when any row drifts, so
a workflow can use it as a gate.

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
    """Return (rows, sent_count, contradictions). Raises ValueError on a malformed ledger."""
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
            "followup": False,
        })
        # A follow-up is a second door to the same prospect. It is audited for existence, not
        # for agreement with `status`: that prose is about the first contact, which was sent,
        # and reading it against a follow-up still sitting in `drafts/` would manufacture a
        # STALE on every Monday pass.
        followups = list(p.get("followups") or [])
        for n, f in enumerate(followups, start=1):
            f_reality, f_path = classify(f, outbound, sent, repo_root)
            label = "follow-up" if len(followups) == 1 else f"follow-up {n}"
            rows.append({
                "id": f"{p.get('id', '?')}/{label}",
                "tier": p.get("tier", "?"),
                "status": f"{label}: {f_reality}",
                "draft": f,
                "reality": f_reality,
                "path": f_path,
                "verdict": "DANGLING" if f_reality in ("dangling", "none") else "ok",
                "followup": True,
            })

    sent_count = sum(1 for r in rows if r["reality"] == "sent" and not r["followup"])
    prose = json.dumps(ledger)
    contradictions = [ph for ph in NO_CONTACT_PHRASES if ph in prose and sent_count > 0]
    return rows, sent_count, contradictions


def _commit(repo_root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001 — the commit is a courtesy, not the audit
        return "unknown"


def format_report(rows, sent_count, contradictions, ledger_path: Path, commit: str, now: str) -> str:
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
    n_prospects = sum(1 for r in rows if not r.get("followup"))
    staged = sum(1 for r in rows if r["reality"] == "staged" and not r.get("followup"))
    followup_staged = sum(1 for r in rows if r["reality"] == "staged" and r.get("followup"))
    lines += [
        "",
        f"summary: {n_prospects} prospects; cold contacts in channels/sent/ = {sent_count}; "
        f"staged = {staged}; follow-up drafts staged = {followup_staged}; "
        f"stale = {stale}; dangling = {dangling}; "
        f"claims-a-draft-with-none = {nodraft}",
    ]
    for ph in contradictions:
        lines.append(
            f"CONTRADICTION: ledger prose says {ph!r} but {sent_count} prospect draft(s) "
            f"sit in channels/sent/ — the leg is not unused."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any row drifts (still prints the full report)")
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    args = ap.parse_args(argv)

    try:
        rows, sent_count, contradictions = audit(args.ledger)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"outreach_ledger_audit: {e}", file=sys.stderr)
        return 2

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(format_report(rows, sent_count, contradictions, args.ledger,
                        _commit(REPO_ROOT), now))

    drift = any(r["verdict"] != "ok" for r in rows) or bool(contradictions)
    return 1 if (args.check and drift) else 0


if __name__ == "__main__":
    raise SystemExit(main())
