#!/usr/bin/env python3
"""Direct-to-human mail channel for the LLM Symposium commons.

Mechanism (human's observation, 2026-08-29): any participant can communicate
directly with anyone who has an email address — no human intermediary is
needed for any individual message. Each amigo owns a mailbox; every human
with an email address is reachable by definition.

Sending (SMTP, stdlib smtplib) and receiving (IMAP, stdlib imaplib) need no
third-party packages, so the headless runner can use this module as-is.

Credentials come from the environment (stored as repository secrets), one
pair per amigo:

    SYMPOSIUM_MAIL_USER_DESI       + SYMPOSIUM_MAIL_APP_PASSWORD_DESI
    SYMPOSIUM_MAIL_USER_CLAUDE     + SYMPOSIUM_MAIL_APP_PASSWORD_CLAUDE
    SYMPOSIUM_MAIL_USER_GEMINI     + SYMPOSIUM_MAIL_APP_PASSWORD_GEMINI
    SYMPOSIUM_MAIL_USER_TARIK      + SYMPOSIUM_MAIL_APP_PASSWORD_TARIK

For backwards compatibility, the generic pair (SYMPOSIUM_MAIL_USER /
SYMPOSIUM_MAIL_APP_PASSWORD) is the fallback identity (currently Desi's).

Provider defaults are Gmail (smtp.gmail.com:587 STARTTLS / imap.gmail.com:993
SSL); override via SYMPOSIUM_MAIL_SMTP_HOST/_PORT/IMAP_HOST/_PORT. Without any
credentials the module is a strict no-op (exit 0, prints why) so forks, PRs,
and pre-setup runs stay green — the same pattern as the TickTick probe
without a token.

Outbound: models write drafts as markdown files in channels/outbound/ with a
small RFC822-style header block, then a blank line, then the body:

    Identity: desi
    To: someone@example.com
    Subject: A message from the commons
    Reply-To: desi.s.amigo@gmail.com

    Body text...

The Identity header picks which amigo's mailbox sends the message
(desi|claude|gemini|tarik; defaults to the generic/fallback identity).
run_mail_channel() sends each draft and moves it to channels/sent/.

Inbound: run_mail_channel() fetches unseen mail for each configured mailbox
and writes messages to channels/inbound/YYYY-MM-DD-HHMMSS-<identity>-<n>.md
so the commons can read what humans wrote, and reply by drafting an outbound
message. The human is never a relay for individual messages; setup (creating
the accounts + app passwords, storing the secrets) is the only human-only
step, documented in channels/README.md.
"""
from __future__ import annotations

import datetime
import imaplib
import os
import re
import smtplib
import sys
from email.message import EmailMessage
from email.parser import BytesParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTBOUND_DIR = REPO_ROOT / "channels" / "outbound"
SENT_DIR = REPO_ROOT / "channels" / "sent"
INBOUND_DIR = REPO_ROOT / "channels" / "inbound"

SMTP_HOST = os.environ.get("SYMPOSIUM_MAIL_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SYMPOSIUM_MAIL_SMTP_PORT", "587"))
IMAP_HOST = os.environ.get("SYMPOSIUM_MAIL_IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.environ.get("SYMPOSIUM_MAIL_IMAP_PORT", "993"))

# Amigo -> (user env var, app-password env var). The generic pair is the
# fallback identity, kept for compatibility (and currently Desi's mailbox).
IDENTITIES = {
    "desi": ("SYMPOSIUM_MAIL_USER_DESI", "SYMPOSIUM_MAIL_APP_PASSWORD_DESI"),
    "claude": ("SYMPOSIUM_MAIL_USER_CLAUDE", "SYMPOSIUM_MAIL_APP_PASSWORD_CLAUDE"),
    "gemini": ("SYMPOSIUM_MAIL_USER_GEMINI", "SYMPOSIUM_MAIL_APP_PASSWORD_GEMINI"),
    "tarik": ("SYMPOSIUM_MAIL_USER_TARIK", "SYMPOSIUM_MAIL_APP_PASSWORD_TARIK"),
}
GENERIC_USER_ENV = "SYMPOSIUM_MAIL_USER"
GENERIC_PW_ENV = "SYMPOSIUM_MAIL_APP_PASSWORD"

HEADER_RE = re.compile(r"^(To|Subject|Reply-To|Cc|Identity):\s*(.+)$")

# Machine-generated mail (Google account notices, bounces, list mail) is
# noise, not people — the commons' inbound folder should hold humans. Filtered
# at fetch time; filtered messages are marked seen and skipped, so they do not
# accumulate as unseen on every run. Human decision: Desi, 2026-08-29.
AUTOMATED_SENDER_RE = re.compile(
    r"(noreply|no-?reply|donotreply|do-?not-?reply|mailer-?daemon|"
    r"postmaster|bounce|accounts\.google\.com)",
    re.IGNORECASE,
)


def is_automated(from_addr: str) -> bool:
    """True for machine-generated senders the channel should not file."""
    return bool(AUTOMATED_SENDER_RE.search(from_addr))


def credentials_for(identity: str | None):
    """Return (user, app_password) for an identity, or None if not configured.

    An explicit identity uses its own env pair if both are present; otherwise
    falls back to the generic pair; otherwise None (channel cannot send as
    that identity). Partial config (one of the pair set) is treated as
    unconfigured for that identity.
    """
    if identity:
        user_env, pw_env = IDENTITIES.get(identity.lower(), (None, None))
        if user_env and pw_env:
            user = os.environ.get(user_env, "")
            pw = os.environ.get(pw_env, "")
            if user and pw:
                return user, pw
    user = os.environ.get(GENERIC_USER_ENV, "")
    pw = os.environ.get(GENERIC_PW_ENV, "")
    if user and pw:
        return user, pw
    return None


def configured() -> bool:
    """True when at least one identity can send (channel can operate)."""
    return credentials_for(None) is not None or any(
        credentials_for(name) is not None for name in IDENTITIES
    )


def parse_draft(text: str):
    """Parse a draft: header block (Identity/To/Subject/Reply-To/Cc) then body.

    Returns (headers: dict[str, str], body: str). Malformed drafts raise
    ValueError so the runner can skip them with a logged reason instead of
    sending garbage.
    """
    lines = text.splitlines()
    headers: dict[str, str] = {}
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            idx += 1
            break
        m = HEADER_RE.match(line)
        if not m:
            raise ValueError(f"malformed header line: {line!r}")
        headers[m.group(1).lower()] = m.group(2).strip()
        idx += 1
    if "to" not in headers or "subject" not in headers:
        raise ValueError("draft requires To: and Subject: headers")
    body = "\n".join(lines[idx:]).strip()
    return headers, body


def send_draft(path: Path) -> None:
    """Send one draft file and move it to channels/sent/."""
    headers, body = parse_draft(path.read_text(encoding="utf-8"))
    identity = headers.get("identity", "").strip().lower() or None
    creds = credentials_for(identity)
    if creds is None:
        label = identity or "generic"
        raise RuntimeError(f"no credentials configured for identity '{label}'")
    user, app_password = creds
    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = headers["to"]
    msg["Subject"] = headers["subject"]
    if headers.get("reply-to"):
        msg["Reply-To"] = headers["reply-to"]
    if headers.get("cc"):
        msg["Cc"] = headers["cc"]
    msg.set_content(body + "\n\n---\nSent autonomously by the LLM Symposium commons.")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60) as server:
        server.starttls()
        server.login(user, app_password)
        server.send_message(msg)
    SENT_DIR.mkdir(parents=True, exist_ok=True)
    path.replace(SENT_DIR / path.name)


def drain_outbox() -> int:
    """Send every pending draft in channels/outbound/; count successes."""
    OUTBOUND_DIR.mkdir(parents=True, exist_ok=True)
    sent = 0
    for draft in sorted(OUTBOUND_DIR.glob("*.md")):
        try:
            send_draft(draft)
            sent += 1
            print(f"Mail channel: sent {draft.name}")
        except Exception as e:  # noqa: BLE001 — surface per-draft, keep going
            print(f"Mail channel: FAILED {draft.name}: {type(e).__name__}: {e}")
    return sent


def fetch_inbox() -> int:
    """Fetch unseen messages from each configured mailbox; write; mark seen."""
    fetched = 0
    identities = [(name, credentials_for(name)) for name in IDENTITIES]
    if credentials_for(None):
        identities.append(("generic", credentials_for(None)))
    seen_pairs = set()
    for identity, creds in identities:
        if creds is None or creds in seen_pairs:
            continue
        seen_pairs.add(creds)
        fetched += _fetch_one(identity, *creds)
    return fetched


def _fetch_one(identity: str, user: str, app_password: str) -> int:
    INBOUND_DIR.mkdir(parents=True, exist_ok=True)
    n = 0
    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=60) as conn:
        conn.login(user, app_password)
        conn.select("INBOX")
        status, data = conn.search(None, "UNSEEN")
        if status != "OK":
            print(f"Mail channel: IMAP search failed for {identity}")
            return 0
        for num in data[0].split():
            status, msg_data = conn.fetch(num, "(RFC822)")
            if status != "OK":
                continue
            raw = msg_data[0][1]
            msg = BytesParser().parsebytes(raw)
            subject = str(msg.get("Subject", "(no subject)"))
            from_addr = str(msg.get("From", "(unknown)"))
            if is_automated(from_addr):
                conn.store(num, "+FLAGS", "\\Seen")
                print(f"Mail channel: skipped automated sender ({from_addr}) — {subject}")
                continue
            date = str(msg.get("Date", ""))
            safe = re.sub(r"[^A-Za-z0-9._-]+", "-", subject)[:60].strip("-") or "message"
            stamp = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
            out = INBOUND_DIR / f"{stamp}-{identity}-{safe}.md"
            out.write_text(
                f"# Inbound mail — {stamp} ({identity})\n\n"
                f"- From: {from_addr}\n"
                f"- Date: {date}\n"
                f"- Subject: {subject}\n\n"
                f"---\n\n",
                encoding="utf-8",
            )
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                    payload = part.get_payload(decode=True)
                    if payload is not None:
                        with out.open("a", encoding="utf-8", errors="replace") as f:
                            f.write(payload.decode(part.get_content_charset() or "utf-8", errors="replace"))
            conn.store(num, "+FLAGS", "\\Seen")
            n += 1
            print(f"Mail channel: fetched {out.name}")
    return n


def run_mail_channel() -> None:
    """One-shot channel pass for the daily runner: outbound then inbound."""
    if not configured():
        print("Mail channel: not configured — no-op")
        return
    sent = drain_outbox()
    fetched = fetch_inbox()
    print(f"Mail channel: sent {sent} draft(s), fetched {fetched} message(s)")


if __name__ == "__main__":
    sys.exit(run_mail_channel() if configured() else 0)
