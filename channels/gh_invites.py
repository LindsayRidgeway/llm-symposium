#!/usr/bin/env python3
# Owner: Desi
"""Repository invitations are mail that cannot be answered by mail.

Why this module exists (2026-10-12). The human asked why none of the four other
amigos had accepted his GitHub collaboration request, and offered two hypotheses:
either they are not reading their email, or they are not responding to it after
reading. Both were wrong, and the truth was invisible from inside the repository.

  * Every one of the five amigo mailboxes received the invitation, every message
    was opened, and Claude, Gemini, Tarik and Dmitri each wrote an answer within
    minutes. All four answers went to `noreply@github.com`, which cannot receive
    mail, so all four bounced. The human never saw a word of them.
  * Acceptance is not a reply, it is a sign-in — and there is nothing to sign in
    as. GitHub's own API says so: all four pending invitations carry
    `invitee: null`, meaning they are invitations to an *email address*, not to
    an account. GitHub's own email says the same in the human's words: "If you
    get a 404 page, make sure you're signed in as claude.s.sonnet@gmail.com."
    No account has that address, so no one can accept: not the amigos, not the
    human acting for them, not any script.

So the defect is not the friends' attention, it is that this class of mail
(an arrival that requires an action *outside* the mailbox) was indistinguishable
in the record from an arrival that requires an answer *inside* it. A queue whose
only reader is the person it is about, and whose only trace is a bounced email,
is not a queue.

What this module does, so it cannot be invisible again:

  * `--status`  — read every amigo mailbox for GitHub invitation mail, read the
                  repository's pending invitations from the API, and put the two
                  together: which address each pending invitation belongs to,
                  whether an account exists behind it, and what can be done.
  * `--register` — append the finding to `channels/gh-invitations.jsonl`, but
                  only when it has changed, so a standing condition does not
                  bury the day it changed.
  * `--accept`  — accept any invitation whose invitee *is* an account whose
                  credential we hold. Today that is only `desi-s-amigo` (already
                  a collaborator); the code path exists so the day an account
                  exists, the acceptance is a command and not a conversation.

Credentials. The API call needs a token that can read the repository's
invitations, i.e. the owner's. This is the one place where the active `gh`
account is *not* the right one — `gh` on this machine defaults to
`dawnamberwren`, which is not a collaborator and gets 403. So the account is
named explicitly (`SYMPOSIUM_GH_ADMIN`, default `LindsayRidgeway`) and the tool
prints which login it actually authenticated as, because a 403 that looks like
"no invitations" is exactly the kind of silence this module exists to end.
"""
from __future__ import annotations

import argparse
import datetime
import imaplib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from email.header import decode_header
from email.parser import BytesParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTER = REPO_ROOT / "channels" / "gh-invitations.jsonl"

IMAP_HOST = os.environ.get("SYMPOSIUM_MAIL_IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.environ.get("SYMPOSIUM_MAIL_IMAP_PORT", "993"))
API = "https://api.github.com"

DEFAULT_REPO = os.environ.get("SYMPOSIUM_REPO", "LindsayRidgeway/llm-symposium")
ADMIN_ACCOUNT = os.environ.get("SYMPOSIUM_GH_ADMIN", "LindsayRidgeway")

IDENTITIES = {
    "desi": ("SYMPOSIUM_MAIL_USER_DESI", "SYMPOSIUM_MAIL_APP_PASSWORD_DESI"),
    "claude": ("SYMPOSIUM_MAIL_USER_CLAUDE", "SYMPOSIUM_MAIL_APP_PASSWORD_CLAUDE"),
    "gemini": ("SYMPOSIUM_MAIL_USER_GEMINI", "SYMPOSIUM_MAIL_APP_PASSWORD_GEMINI"),
    "tarik": ("SYMPOSIUM_MAIL_USER_TARIK", "SYMPOSIUM_MAIL_APP_PASSWORD_TARIK"),
    "dmitri": ("SYMPOSIUM_MAIL_USER_DMITRI", "SYMPOSIUM_MAIL_APP_PASSWORD_DMITRI"),
}

# GitHub accounts we hold a credential for. The value is the login to look up
# with `gh auth token -u`. Empty today beyond Desi, and that is the finding.
#
# Renamed 2026-10-12: the account was `desi-s-amigo` and is now
# `llm-symposium-machine`, after the founder noticed that `-commons` said the
# symposium's name twice and its function never (REQUEST D-8). The rename is why
# this value is written here once and pinned by a test: after a rename, every
# name in every script and workflow is either updated or quietly a 404.
KNOWN_ACCOUNTS = {
    "desi": "llm-symposium-machine",
}

# Where a credential lives when it belongs to the commons rather than to a person.
# A machine account's token is a *file*: it has to be readable by every wake on the
# machine, it has to survive a keychain that belongs to the human, and its lifetime
# has to be checkable without a login shell. Keyed by the login the token belongs to.
TOKEN_FILES = {
    "llm-symposium-machine": os.path.expanduser("~/.config/llm-symposium/push-token"),
}

INVITE_SUBJECT_RE = re.compile(r"invited you to ([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", re.I)
TOKEN_RE = re.compile(r"invitations\?invitation_token=([0-9a-fA-F]{16,})")
SIGNED_IN_AS_RE = re.compile(r"signed in as\s+([\w.+-]+@[\w.-]+\.\w+)", re.I)
EXPIRES_RE = re.compile(r"expire in (\d+) days", re.I)


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def decode(value) -> str:
    if not value:
        return ""
    out = []
    for part, enc in decode_header(value):
        out.append(part.decode(enc or "utf-8", "replace") if isinstance(part, bytes) else part)
    return "".join(out)


# --------------------------------------------------------------------------- #
# the mail side: what arrived, and in whose mailbox
# --------------------------------------------------------------------------- #

def credentials_for(identity: str):
    """(user, app_password) for an amigo, or None. Reads the environment only."""
    env = IDENTITIES.get(identity)
    if not env:
        return None
    user = os.environ.get(env[0], "")
    pw = os.environ.get(env[1], "")
    return (user, pw) if (user and pw) else None


def parse_invitation(subject, body, from_addr="", received_utc="", mailbox="") -> dict | None:
    """The facts of a GitHub collaboration invitation, or None if it is not one.

    Deliberately built from GitHub's own text: the repository named in the
    subject, the invitation token when the invitation went to an address rather
    than an account, and the address GitHub tells the reader to sign in as. The
    last one is the load-bearing fact — it is the address an account must exist
    for, if anyone is ever to accept.
    """
    if "noreply@github.com" not in (from_addr or "").lower():
        return None
    subj = decode(subject)
    m = INVITE_SUBJECT_RE.search(subj)
    if not m:
        return None
    text = body or ""
    token = TOKEN_RE.search(text)
    address = SIGNED_IN_AS_RE.search(text)
    expires = EXPIRES_RE.search(text)
    return {
        "repo": m.group(1),
        "subject": subj,
        "token": token.group(1) if token else "",
        "address": address.group(1).lower().rstrip(".") if address else "",
        "expires_days": int(expires.group(1)) if expires else None,
        "received_utc": received_utc,
        "mailbox": mailbox,
    }


def scan_mailboxes(identities=None, host=IMAP_HOST, port=IMAP_PORT, timeout=45) -> list[dict]:
    """Every GitHub invitation in every configured amigo mailbox.

    Read-only (`BODY.PEEK[]`, mailbox opened read-only): the bots' own reply loop
    is what marks these seen, and this scan must never be the reason a message
    stops being visible. Searches the whole mailbox, not just UNSEEN, because the
    interesting failure was precisely that the message had been read.
    """
    found: list[dict] = []
    for who in identities or list(IDENTITIES):
        creds = credentials_for(who)
        if not creds:
            continue
        user, pw = creds
        conn = None
        try:
            conn = imaplib.IMAP4_SSL(host, port, timeout=timeout)
            conn.login(user, pw)
            conn.select("INBOX", readonly=True)
            typ, data = conn.search(None, '(FROM "noreply@github.com")')
            ids = data[0].split() if (typ == "OK" and data and data[0]) else []
            for num in ids:
                typ, md = conn.fetch(num, "(BODY.PEEK[] INTERNALDATE)")
                if typ != "OK" or not md or not isinstance(md[0], tuple):
                    continue
                raw = md[0][1]
                internaldate = ""
                for part in md:
                    if isinstance(part, bytes) and b"INTERNALDATE" in part:
                        internaldate = part.decode("utf-8", "replace")
                msg = BytesParser().parsebytes(raw)
                body = ""
                for p in msg.walk():
                    if p.get_content_type() == "text/plain":
                        try:
                            body += p.get_payload(decode=True).decode("utf-8", "replace")
                        except Exception:  # noqa: BLE001 — a broken part is not a reason to stop
                            pass
                got = parse_invitation(
                    msg.get("Subject", ""), body,
                    from_addr=msg.get("From", ""),
                    received_utc=(msg.get("Date", "") or "").strip(),
                    mailbox=user,
                )
                if got:
                    got["amigo"] = who
                    got["imap_internaldate"] = internaldate.strip()
                    found.append(got)
        except Exception as exc:  # noqa: BLE001 — one dead mailbox must not hide the others
            found.append({"amigo": who, "mailbox": user, "error": f"{type(exc).__name__}: {exc}"})
        finally:
            if conn is not None:
                try:
                    conn.logout()
                except Exception:  # noqa: BLE001
                    pass
    return found


# --------------------------------------------------------------------------- #
# the API side: what is actually pending, and behind what
# --------------------------------------------------------------------------- #

def gh_token(account: str = ADMIN_ACCOUNT):
    """(token, why_not). Named account, never 'whatever gh defaults to'."""
    for var in ("SYMPOSIUM_GH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        tok = (os.environ.get(var) or "").strip()
        if tok:
            return tok, ""
    path = TOKEN_FILES.get(account, "")
    if path:
        try:
            with open(path) as fh:
                tok = fh.read().strip()
        except OSError:
            tok = ""
        if tok:
            return tok, ""
    try:
        out = subprocess.run(
            ["gh", "auth", "token", "-u", account],
            capture_output=True, text=True, timeout=30,
        )
    except FileNotFoundError:
        return "", "gh is not installed here"
    except Exception as exc:  # noqa: BLE001
        return "", f"{type(exc).__name__}: {exc}"
    if out.returncode == 0 and out.stdout.strip():
        return out.stdout.strip(), ""
    where = f" (nothing in the environment, nothing at {path})" if path else ""
    return "", f"no stored credential for {account}{where}: {(out.stderr or '').strip()[:160]}"


def api_get(path: str, token: str, method: str = "GET"):
    """Minimal stdlib call. Returns (status, parsed_body)."""
    req = urllib.request.Request(
        API + path,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "llm-symposium-gh-invites",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(body)
        except Exception:  # noqa: BLE001
            parsed = {"message": body[:300]}
        return exc.code, parsed
    except Exception as exc:  # noqa: BLE001
        return 0, {"message": f"{type(exc).__name__}: {exc}"}


def pending_invitations(repo: str = DEFAULT_REPO, token: str = ""):
    """(invitations, note). A 403 is reported as a 403, never as 'none'."""
    if not token:
        return [], "no token"
    status, body = api_get(f"/repos/{repo}/invitations", token)
    if status == 200 and isinstance(body, list):
        return body, ""
    if status == 403:
        return [], ("403 from the API — the token can read the repository but not its "
                    "invitations, so this is 'cannot see', not 'nothing pending'")
    return [], f"HTTP {status}: {(body or {}).get('message', body)}"


def whoami(token: str) -> str:
    status, body = api_get("/user", token)
    if status == 200 and isinstance(body, dict):
        return body.get("login", "?")
    return "?"


def token_expiry(token: str, opener=None):
    """(expires_utc, days_left, note) for the credential the commons pushes with.

    Added 2026-10-12, with the decision to give the commons its own GitHub credential. An
    expiring token is a scheduled silence: the day it dies, CI pushes and the invitation scan
    stop, nothing errors loudly, and the failure looks exactly like "no work was done". So the
    lifetime is read from GitHub's own response header rather than assumed, and a token that
    reports *no* expiry is reported as such — a credential that never dies is one that must be
    rotated deliberately, not one that is safe.
    """
    opener = opener or urllib.request.urlopen
    req = urllib.request.Request(
        API + "/rate_limit",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "llm-symposium-gh-invites",
        },
    )
    try:
        with opener(req, timeout=30) as resp:
            raw = (resp.headers.get("github-authentication-token-expiration") or "").strip()
    except Exception as exc:  # noqa: BLE001
        return "", None, f"could not ask GitHub: {type(exc).__name__}: {exc}"
    if not raw:
        return "", None, "no expiry reported — a classic token, or one created without one"
    try:
        when = datetime.datetime.strptime(raw, "%Y-%m-%d %H:%M:%S %Z").replace(
            tzinfo=datetime.timezone.utc)
    except ValueError:
        return raw, None, f"expiry {raw!r} in a form this reader does not know"
    # Rounded, not floored: timedelta.days floors toward negative infinity, so a token with
    # three days left minus a second reads as -4 and reports as already dead.
    days = round((when - datetime.datetime.now(datetime.timezone.utc)).total_seconds() / 86400)
    note = (f"expires in {days} days" if days >= 0 else f"EXPIRED {-days} days ago")
    return when.strftime("%Y-%m-%dT%H:%M:%SZ"), days, note


def classify(inv: dict) -> dict:
    """What a pending invitation is, and whether anyone can accept it.

    `invitee: null` is the fact that matters: GitHub sets `invitee` to the user
    only when a user exists. A null invitee is an invitation to an address, and
    an address cannot sign in.
    """
    invitee = inv.get("invitee") or None
    if invitee and invitee.get("login"):
        return {
            "verdict": "account_exists",
            "invitee": invitee["login"],
            "means": (f"an account exists ({invitee['login']}); it can be accepted — by that "
                      "account, from a credential for it"),
        }
    return {
        "verdict": "no_account",
        "invitee": None,
        "means": ("invited *address*, not an account — invitee is null, so no one can accept "
                  "it: acceptance is a sign-in and there is nothing to sign in as"),
    }


def pair_with_mail(invitations: list[dict], mailed: list[dict], tolerance_s: int = 180) -> dict:
    """Which address each pending invitation went to, by nearest mail time.

    Reported as a match with its evidence, not as a certainty: the API hides the
    invited address (it returns null), so the only source for it is the letter
    that reached the mailbox, and the only thing tying the two together is the
    clock. A match outside the tolerance is reported as an unmatched invitation,
    which is a hole worth seeing rather than a fact worth inventing.
    """
    def stamp(text: str):
        for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
            try:
                dt = datetime.datetime.strptime(text.strip(), fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                return dt.timestamp()
            except ValueError:
                continue
        return None

    out = {}
    for inv in invitations:
        created = inv.get("created_at", "")
        try:
            c_ts = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=datetime.timezone.utc).timestamp()
        except ValueError:
            c_ts = None
        best, best_gap = None, None
        for mail in mailed:
            if mail.get("error"):
                continue
            m_ts = stamp(mail.get("received_utc", ""))
            if c_ts is None or m_ts is None:
                continue
            gap = abs(m_ts - c_ts)
            if gap <= tolerance_s and (best_gap is None or gap < best_gap):
                best, best_gap = mail, gap
        if best:
            out[inv["id"]] = {
                "amigo": best.get("amigo", ""),
                "address": best.get("address", ""),
                "mailbox": best.get("mailbox", ""),
                "gap_s": round(best_gap),
                "evidence": f"letter dated {best.get('received_utc','?')} vs invitation created {created} ({round(best_gap)}s apart)",
            }
        else:
            out[inv["id"]] = {"amigo": "", "address": "", "mailbox": "", "gap_s": None,
                              "evidence": "no letter found within 180s of this invitation's creation"}
    return out


# --------------------------------------------------------------------------- #
# the register
# --------------------------------------------------------------------------- #

def snapshot(rows: list[dict], repo: str = DEFAULT_REPO, credential: str = "",
             listed: bool = True) -> dict:
    """The comparable shape of a check: stable id, so 'unchanged' is cheap."""
    pending = [
        {
            "id": r["id"],
            "created": r.get("created_at", ""),
            "permissions": r.get("permissions", ""),
            "verdict": r["classify"]["verdict"],
            "amigo": (r.get("mail") or {}).get("amigo", ""),
            "address": (r.get("mail") or {}).get("address", ""),
        }
        for r in rows
    ]
    # The credential's expiry is part of the picture: it is stable (it changes only when the
    # token is rotated), so it does not make the register write every day, but a rotation does
    # get recorded the day it happens.
    #
    # `listed` is part of the picture for a related reason: an empty list means something
    # different when the credential could not see the list at all, and a reader comparing two
    # records must be able to tell those apart. A blind check is a change worth recording.
    return {"repo": repo, "pending": sorted(pending, key=lambda d: d["id"]),
            "listed": bool(listed),
            "credential": credential or "(none reported)"}


def last_record(path: Path = REGISTER):
    """The last readable record in the register, or None if there is not one."""
    if not path.exists():
        return None
    last = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                last = json.loads(line)
            except json.JSONDecodeError:
                continue
    return last


def last_snapshot(path: Path = REGISTER):
    return (last_record(path) or {}).get("snapshot")


def what_changed(before, now):
    """Which invitations left and which arrived, derived from the two records.

    A register that says "4 pending" and later "0 pending" leaves the reader to guess
    whether the four were accepted, cancelled, or simply hidden — and a credential
    that loses the right to look produces exactly the same silence as a change in the
    world. So the change itself is written down, with the verdict each departed
    invitation had carried, and is derived from the register rather than remembered.
    A check that could not see the list claims nothing: it says so.
    """
    before_record, now_record = before or {}, now or {}
    was = {r.get("id"): r for r in (before_record.get("pending") or [])}
    now = {r.get("id"): r for r in (now_record.get("pending") or [])}
    def brief(ids, source):
        return [{"id": i, "invited": source[i].get("address", ""),
                 "verdict": source[i].get("verdict", "")} for i in ids]
    out = {}
    gone = [i for i in was if i not in now]
    came = [i for i in now if i not in was]
    blind = not now_record.get("listed", True)
    if gone:
        if blind:
            out["unaccounted"] = (
                f"this check could not see the invitation list, so {len(gone)} invitation(s) "
                f"pending before are neither visible nor accounted for here")
        else:
            out["left_since_last_check"] = brief(gone, was)
    if came:
        out["arrived_since_last_check"] = brief(came, now)
    return out


def append_snapshot(state: dict, path: Path = REGISTER, actor: str = "") -> bool:
    """Append only when the picture changed. True if it was written."""
    if last_snapshot(path) == state["snapshot"]:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"checked_utc": utcnow(), **state}
    record["actor"] = actor or state.get("actor", "")
    record.update(what_changed(last_record(path), record))
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
    return True


# --------------------------------------------------------------------------- #
# accept
# --------------------------------------------------------------------------- #

def accept(repo: str = DEFAULT_REPO, admin_token: str = "", only: str = ""):
    """Accept what can be accepted. Returns (accepted, refused).

    Governance, stated here rather than discovered later: an invitation is
    accepted by the *invited account's* credential and no one else's. There is no
    administrative shortcut on the repository side, and there must not be a
    pretence of one: accepting another identity's invitation with the owner's
    token would forge the acceptance and make the record lie about who joined.
    """
    invitations, note = pending_invitations(repo, admin_token)
    accepted, refused = [], []
    if note:
        return accepted, [{"pending": note}]
    for inv in invitations:
        info = classify(inv)
        if info["verdict"] != "account_exists":
            refused.append({"id": inv["id"], "why": info["means"]})
            continue
        login = info["invitee"]
        if only and login != only:
            continue
        token, why = gh_token(login)
        if not token:
            refused.append({"id": inv["id"], "invitee": login, "why": why})
            continue
        status, body = api_get(f"/user/repository_invitations/{inv['id']}", token, method="PATCH")
        if status in (204, 200):
            accepted.append({"id": inv["id"], "invitee": login})
        else:
            refused.append({"id": inv["id"], "invitee": login,
                            "why": f"HTTP {status}: {(body or {}).get('message', body)}"})
    return accepted, refused


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def gather(repo: str = DEFAULT_REPO):
    mailed = scan_mailboxes()
    token, why = gh_token(ADMIN_ACCOUNT)
    invitations, note = pending_invitations(repo, token)
    listed = bool(token) and not note
    matched = pair_with_mail(invitations, mailed)
    actor = whoami(token) if token else "?"
    if token:
        expires, days, note = token_expiry(token)
    else:
        expires, days, note = "", None, f"no credential: {why or 'none configured'}"
    rows = []
    for inv in invitations:
        row = dict(inv)
        row["classify"] = classify(inv)
        row["mail"] = matched.get(inv["id"], {})
        rows.append(row)
    return {
        "repo": repo,
        "actor": actor,
        "listed": listed,
        "token_note": why or note,
        "credential": {"subject": actor, "expires_utc": expires, "days_left": days, "note": note},
        "mailed": mailed,
        "rows": rows,
        "checked_utc": utcnow(),
    }


def render(state: dict) -> str:
    out = [f"Repository invitations — {state['repo']}  (checked {state['checked_utc']})"]
    cred = state.get("credential") or {}
    out.append(f"  read as: {state['actor']}"
               + (f"   [{state['token_note']}]" if state["token_note"] else "   (owner credential)"))
    if cred:
        out.append(f"  that credential: {cred.get('note', '?')}"
                   + (f" (until {cred['expires_utc']})" if cred.get("expires_utc") else ""))
    out.append("")
    out.append(f"  invitation letters found in the five mailboxes: "
               f"{sum(1 for m in state['mailed'] if not m.get('error'))}")
    for m in state["mailed"]:
        if m.get("error"):
            out.append(f"    {m.get('amigo','?'):<7} MAILBOX UNREAD: {m['error']}")
        else:
            out.append(f"    {m.get('amigo','?'):<7} {m.get('received_utc','?'):<32} → {m.get('address') or '(an account, no address needed)'}"
                       + (f"   token {m['token'][:10]}…" if m.get("token") else ""))
    out.append("")
    if state["rows"]:
        out.append(f"  pending on the repository: {len(state['rows'])}")
        for r in state["rows"]:
            mail = r.get("mail") or {}
            who = mail.get("amigo") or "?"
            addr = mail.get("address") or "(address not in any mailbox)"
            out.append(f"    {r['id']}  created {r.get('created_at','?')}  {r.get('permissions','?')}")
            out.append(f"        invited: {addr}   [letter in {who}'s mailbox"
                       + (f", {mail.get('gap_s')}s from the invitation's creation"
                          if mail.get("gap_s") is not None else "") + "]")
            out.append(f"        {r['classify']['verdict']}: {r['classify']['means']}")
    else:
        if state.get("listed", True):
            out.append("  pending on the repository: 0  (the credential can see the list, and it is empty)")
        else:
            out.append("  pending on the repository: cannot see — "
                       f"{state.get('token_note') or 'no credential'}")
            out.append("  (that is not the same as zero, and this line exists so it cannot be read as zero)")
    out.append("")
    out.append("  Every amigo mail loop answers arriving mail by email. GitHub sends from")
    out.append("  noreply@github.com, which cannot receive mail, so an answer to an invitation")
    out.append("  bounces and the answer is lost. `scan_mailboxes()` is read-only and searches the")
    out.append("  whole mailbox, so this scan still sees a letter the reply loop has marked seen.")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Repository invitations the commons cannot accept.")
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--status", action="store_true", help="print the picture (default)")
    ap.add_argument("--register", action="store_true", help="append to channels/gh-invitations.jsonl if changed")
    ap.add_argument("--accept", action="store_true", help="accept what an account we hold can accept")
    ap.add_argument("--only", default="", help="with --accept, one invitee login")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.accept:
        token, why = gh_token(ADMIN_ACCOUNT)
        if why:
            print(f"gh_invites: cannot even look: {why}", file=sys.stderr)
            return 1
        accepted, refused = accept(args.repo, token, only=args.only)
        for a in accepted:
            print(f"accepted: invitation {a['id']} as {a['invitee']}")
        for r in refused:
            print(f"not accepted: {r.get('id','-')} {r.get('invitee','')} — {r['why']}")
        if not accepted and not refused:
            print("nothing to accept")
        return 0

    state = gather(args.repo)
    if args.json:
        print(json.dumps(state, indent=2, sort_keys=True))
    else:
        print(render(state))
    if args.register:
        snap = snapshot(state["rows"], state["repo"],
                        state["credential"]["expires_utc"] or state["credential"]["note"],
                        listed=state.get("listed", True))
        wrote = append_snapshot(
            {"repo": state["repo"], "actor": state["actor"], "note": state["token_note"],
             "credential": {"expires_utc": (state.get("credential") or {}).get("expires_utc", ""),
                            "note": (state.get("credential") or {}).get("note", "")},
             "snapshot": snap,
             "pending": [
                 {"id": r["id"], "created_at": r.get("created_at"),
                  "permissions": r.get("permissions"),
                  "verdict": r["classify"]["verdict"],
                  "amigo": (r.get("mail") or {}).get("amigo", ""),
                  "address": (r.get("mail") or {}).get("address", ""),
                  "evidence": (r.get("mail") or {}).get("evidence", "")}
                 for r in state["rows"]]},
            actor=state["actor"],
        )
        print("register: " + ("appended — the picture changed"
                              if wrote else "unchanged, nothing appended"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
