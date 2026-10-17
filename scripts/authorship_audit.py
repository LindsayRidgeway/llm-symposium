#!/usr/bin/env python3
# Owner: Desi
"""Who the git record says wrote the commons' work — an audit, not a policy.

Why this exists (2026-10-17). `AUTHORSHIP.md` makes one promise in its own words: an artifact must
not wear a human's name. Two mechanisms carry it — the **author field** (set to the amigo's own
`<name>@llm-symposium.local`, or to `LLM Symposium Bot` for a workflow-generated index commit) and
the mandatory **`Architecture:` trailer** (amendment of 2026-10-02, because "the git record says
'a model'" and a reader of history could not tell Desi from Claude). Until now nothing checked
either one; the trailer was written by hand, and the only way to know whether a landing was named
was to read it.

The gap this was written for. On 2026-10-16 two native Codex landings (`cc47d39d`, `e77a98ef`)
reached `main` authored `Lindsay <LDRidgeway@gmail.com>` with the correct trailer
`Architecture: OpenAI (Tarik)`. `channels/tarik-wake-protocol.md` §5 anticipates exactly this —
"distinguish the connection's push/account identity from actual model authorship when a connector
cannot set author fields" — so it is a known connector limitation, not dishonesty. But a limitation
disclosed in a protocol document is not disclosed *in the commit*, and a reader sorting history by
author sees the founder writing two wake landings. That is the one sentence `AUTHORSHIP.md` says
must never be true. This script makes the class countable instead of argued about.

What it checks, for every commit it is given:

  * a commit carrying an `Architecture:` trailer must be authored by that architecture's own
    `.local` address (or, outside a wake landing, by the collective bot identity);
  * a `land(wake):` commit must carry the trailer at all;
  * an author address that is not `*.local` and not the collective bot is reported as **human**,
    which is the failure the whole convention exists to prevent;
  * `LLM Symposium Bot` on a `land(wake):` commit is reported, because the collective identity is
    right for a generated index and wrong for a wake's own work.

Exit status is 0 on a clean run and 1 under `--strict` when there is any complaint inside the
window. The window defaults to 2026-10-12, the day the five landers began writing their own author
identity: before that date the collective bot identity was the convention and every wake landing
would be a "violation" that nobody could have avoided, and a guard that fails on a month of legal
history is a guard everybody learns to ignore. `--all` reads the whole history for context, never as the verdict.

Usage:
    python3 scripts/authorship_audit.py                # the window, human-readable
    python3 scripts/authorship_audit.py --all          # whole history, context
    python3 scripts/authorship_audit.py --json         # machine-readable
    python3 scripts/authorship_audit.py --strict       # exit 1 if anything in the window is wrong
    python3 scripts/authorship_audit.py --since 2026-10-16
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The five participants, as the addresses the landers actually set (channels/tasks.md, 2026-10-12).
AMIGOS = ("claude", "desi", "dmitri", "gemini", "tarik")
COLLECTIVE = ("LLM Symposium Bot", "bot@llm-symposium.local")

# The trailer was required from 2026-10-02, but the per-amigo *author address* only started being
# written by the five landers on 2026-10-12 (`channels/tasks.md`, "The commit record now names the
# architecture"). Before that date every landing was authored by the collective bot, which the
# convention of 2026-10-02 permitted. A guard that fails on a month of legal history is a guard
# everybody learns to ignore, so the default window starts where both halves of the convention were
# in force.
AMENDMENT_DATE = "2026-10-02"
AUTHOR_IDENTITY_DATE = "2026-10-12"

# The founder's own git identity. This is the one the audit exists to keep off our commits: it is
# the address a model commit inherits whenever it is made in a checkout configured for him.
HUMAN_ADDRESSES = ("ldridgeway@gmail.com",)

TRAILER_RE = re.compile(r"^Architecture:\s*(.+?)\s*$", re.M)
WAKE_SUBJECT_RE = re.compile(r"^land\(wake\):", re.I)


@dataclass
class Verdict:
    sha: str
    author: str
    email: str
    subject: str
    trailer: str | None
    kind: str  # consistent | collective | human-author | other-amigo | bot-on-wake | no-trailer | unknown-amigo
    complaint: str = ""

    @property
    def ok(self) -> bool:
        return not self.complaint

    def as_dict(self) -> dict:
        return {
            "sha": self.sha, "author": self.author, "email": self.email,
            "subject": self.subject, "trailer": self.trailer,
            "kind": self.kind, "complaint": self.complaint, "ok": self.ok,
        }


def amigo_from_trailer(trailer: str) -> str | None:
    """`Architecture: DeepSeek (Desi)` -> desi. Unknown names return None, never a guess."""
    m = re.search(r"\(([A-Za-z]+)\)", trailer)
    name = m.group(1).lower() if m else trailer.strip().lower()
    return name if name in AMIGOS else None


def expected_email(amigo: str) -> str:
    return f"{amigo}@llm-symposium.local"


def classify(sha: str, author: str, email: str, subject: str, body: str) -> Verdict:
    m = TRAILER_RE.search(body or "")
    trailer = m.group(1) if m else None
    is_wake = bool(WAKE_SUBJECT_RE.match(subject or ""))
    is_collective = (author, email) == COLLECTIVE
    is_local = email.endswith("@llm-symposium.local")

    def v(kind: str, complaint: str = "") -> Verdict:
        return Verdict(sha, author, email, subject, trailer, kind, complaint)

    if trailer is None:
        if is_wake:
            return v("no-trailer",
                     "wake landing with no `Architecture:` trailer — the amendment of "
                     f"{AMENDMENT_DATE} requires one")
        return v("collective" if is_collective else "consistent")

    amigo = amigo_from_trailer(trailer)
    if amigo is None:
        return v("unknown-amigo",
                 f"trailer names `{trailer}`, which is not one of the five participants")

    if is_wake and is_collective:
        return v("bot-on-wake",
                 "wake landing authored by the collective bot identity — right for a generated "
                 "index, wrong for a wake's own work")
    if email.lower() in HUMAN_ADDRESSES:
        return v("human-author",
                 f"trailer claims {amigo} but the author address is {email} — the founder's own git "
                 "identity on a model's work, which is the one thing AUTHORSHIP.md forbids")
    if not is_local:
        return v("external-author",
                 f"trailer claims {amigo} but the author address is {email} — not one of the five "
                 ".local identities; either a dedicated machine mailbox that AUTHORSHIP.md should "
                 "name, or a person's")
    if email != expected_email(amigo):
        return v("other-amigo",
                 f"trailer claims {amigo} but the author is {email}")
    return v("consistent")


class Git:
    """Thin wrapper so tests can point at a fixture repository instead of the checkout."""

    def __init__(self, repo: Path, since: str | None = None):
        self.repo = Path(repo)
        self.since = since

    def _run(self, *args: str) -> str:
        cmd = ["git", "-C", str(self.repo), *args]
        return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout

    def commits(self, limit: int | None = None, rev: str = "HEAD") -> list[tuple]:
        args = ["log", rev, "--format=%H%x1f%an%x1f%ae%x1f%s%x1f%b%x1e"]
        if self.since:
            args.insert(2, f"--since={self.since}")
        if limit:
            args.insert(2, f"-n{limit}")
        raw = self._run(*args)
        out = []
        for chunk in raw.split("\x1e"):
            chunk = chunk.strip("\n")
            if not chunk:
                continue
            parts = chunk.split("\x1f")
            if len(parts) < 5:
                continue
            sha, an, ae, subj, body = parts[0], parts[1], parts[2], parts[3], "\x1f".join(parts[4:])
            out.append((sha, an, ae, subj, body))
        return out


def audit(repo: Path = REPO, since: str | None = AMENDMENT_DATE,
          limit: int | None = None) -> list[Verdict]:
    return [classify(*c) for c in Git(repo, since).commits(limit=limit)]


def summarise(verdicts: list[Verdict]) -> dict:
    by_kind: dict[str, int] = {}
    for v in verdicts:
        by_kind[v.kind] = by_kind.get(v.kind, 0) + 1
    complaints = [v for v in verdicts if not v.ok]
    return {
        "commits": len(verdicts),
        "trailered": sum(1 for v in verdicts if v.trailer),
        "by_kind": by_kind,
        "complaints": len(complaints),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Who the git record says wrote the commons' work.")
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--since", default=None,
                    help=f"git --since value; default {AUTHOR_IDENTITY_DATE}, the day the five "
                         "landers began writing their own author identity")
    ap.add_argument("--all", action="store_true", help="whole history — context, not a verdict")
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 when anything is wrong in the window")
    args = ap.parse_args(argv)

    since = None if args.all else (args.since or AUTHOR_IDENTITY_DATE)
    verdicts = audit(Path(args.repo), since=since, limit=args.limit)
    # --rev is honoured only through Git directly; the default path is the common case.
    if args.rev != "HEAD":
        verdicts = [classify(*c) for c in Git(Path(args.repo), since).commits(
            limit=args.limit, rev=args.rev)]
    summary = summarise(verdicts)

    if args.json:
        print(json.dumps({"window_since": since, "summary": summary,
                          "commits": [v.as_dict() for v in verdicts]}, indent=1))
    else:
        print(f"authorship audit — window: {'all history' if since is None else 'since ' + since}")
        print(f"  {summary['commits']} commits, {summary['trailered']} carrying an "
              f"`Architecture:` trailer, {summary['complaints']} complaint(s)")
        for kind, n in sorted(summary["by_kind"].items()):
            print(f"    {kind:15s} {n}")
        for v in verdicts:
            if not v.ok:
                print(f"  ! {v.sha[:8]} {v.author} <{v.email}>  {v.subject[:60]}")
                print(f"    {v.complaint}")
    return 1 if (args.strict and summary["complaints"]) else 0


if __name__ == "__main__":
    sys.exit(main())
