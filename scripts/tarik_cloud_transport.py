#!/usr/bin/env python3
"""Tarik-only cloud transport. Telegram sends only; mail sync records, never replies.

No credential values or remote exception text are written to receipts or stdout.
An existing receipt, including an interrupted attempt, always prevents another send.
"""
from __future__ import annotations

import argparse
import datetime as dt
import email
import email.policy
import imaplib
import json
import os
from pathlib import Path
import re
import smtplib
import ssl
import tempfile
import urllib.parse
import urllib.request
from email.message import EmailMessage
from email.utils import getaddresses

BOT_USERNAME = "tarik_s_commons_bot"
MAILBOX = "tarik.s.commons@gmail.com"
HUMAN_CHAT = "1733127278"
HUMAN_EMAIL = "ldridgeway@gmail.com"
TOKEN_ENV = "TELEGRAM_BOT_TOKEN_TARIK"
USER_ENV = "SYMPOSIUM_MAIL_USER_TARIK"
PASSWORD_ENV = "SYMPOSIUM_MAIL_APP_PASSWORD_TARIK"
ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,79}\Z")
OPERATIONS = {"send_telegram", "send_mail", "sync_mail"}
KEY_URL = re.compile(r"https?://[^\s<>\[\]\"']+", re.I)
KEY_WORD = re.compile(r"token|auth|key|password|confirm|verify|invitation|reset|magic|secret|credential", re.I)


class TransportError(Exception):
    def __init__(self, reason, uncertain=False):
        super().__init__(reason)
        self.reason, self.uncertain = reason, uncertain


def validate_request(data):
    if not isinstance(data, dict):
        raise ValueError("invalid_request")
    if set(data) - {"id", "type", "source", "body", "subject", "reply_to"}:
        raise ValueError("unknown_field")
    if not isinstance(data.get("id"), str) or not ID_RE.fullmatch(data["id"]):
        raise ValueError("invalid_id")
    if not isinstance(data.get("type"), str) or data["type"] not in OPERATIONS or data.get("source") != "codex":
        raise ValueError("invalid_operation_or_source")
    operation = data["type"]
    if operation == "sync_mail":
        if set(data) != {"id", "type", "source", "reply_to"}:
            raise ValueError("invalid_sync_fields")
        if not isinstance(data["reply_to"], str) or not ID_RE.fullmatch(data["reply_to"]):
            raise ValueError("invalid_reply_to")
    else:
        if "reply_to" in data:
            raise ValueError("invalid_send_fields")
        body = data.get("body")
        if not isinstance(body, str) or not body.strip() or len(body) > 3500 or "\x00" in body:
            raise ValueError("invalid_body")
        if operation == "send_mail":
            subject = data.get("subject")
            if not isinstance(subject, str) or not subject.strip() or len(subject) > 160:
                raise ValueError("invalid_subject")
            if any(c in subject for c in "\r\n\x00"):
                raise ValueError("invalid_subject")
        elif "subject" in data:
            raise ValueError("invalid_telegram_fields")
    return dict(data)


def _stamp(now=None):
    value = now() if callable(now) else now
    if value is None:
        value = dt.datetime.now(dt.timezone.utc)
    if isinstance(value, str):
        return value
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt.timezone.utc)
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds")


def _atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".receipt-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def _secret_values(environ):
    return sorted({value for key, value in environ.items()
                   if re.search(r"TOKEN|PASSWORD|SECRET|API_KEY", key, re.I)
                   and isinstance(value, str) and len(value) >= 8}, key=len, reverse=True)


def sanitize_text(text, environ):
    text = str(text).replace("\x00", "")
    for secret in _secret_values(environ):
        text = text.replace(secret, "[redacted credential]")
    def clean_url(match):
        url = match.group(0)
        if KEY_WORD.search(url) or "@" in urllib.parse.urlsplit(url).netloc:
            return "[credential URL removed]"
        return url
    return KEY_URL.sub(clean_url, text)


def _check_no_secrets(request, environ):
    for field in ("body", "subject"):
        value = request.get(field, "")
        if any(secret in value for secret in _secret_values(environ)):
            raise TransportError("credential_in_content")


def _append(repo_root, text):
    path = Path(repo_root) / "channels/conversation/tarik.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write("\n" + text.rstrip() + "\n")


def _telegram(token, method, payload=None, opener=None):
    opener = opener or urllib.request.urlopen
    body = urllib.parse.urlencode(payload or {}).encode("utf-8")
    request = urllib.request.Request("https://api.telegram.org/bot" + token + "/" + method,
                                     data=body, method="POST")
    with opener(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not isinstance(result, dict) or result.get("ok") is not True:
        raise TransportError("telegram_rejected")
    return result.get("result", {})


def _check_bot(environ, opener):
    token = environ.get(TOKEN_ENV, "").strip()
    if not token:
        raise TransportError("missing_credentials")
    identity = _telegram(token, "getMe", opener=opener)
    if not isinstance(identity, dict) or identity.get("username", "").lower() != BOT_USERNAME:
        raise TransportError("identity_mismatch")
    return token


def _mail_credentials(environ):
    user = environ.get(USER_ENV, "").strip()
    password = environ.get(PASSWORD_ENV, "").strip()
    if not user or not password:
        raise TransportError("missing_credentials")
    if user.lower() != MAILBOX:
        raise TransportError("identity_mismatch")
    return user, password


def _smtp(environ, smtp_factory):
    user, password = _mail_credentials(environ)
    connection = (smtp_factory or smtplib.SMTP)("smtp.gmail.com", 587, timeout=30)
    try:
        connection.starttls(context=ssl.create_default_context())
        connection.login(user, password)
    except Exception:
        try:
            connection.close()
        except Exception:
            pass
        raise TransportError("smtp_auth_failed") from None
    return connection


def _imap(environ, imap_factory):
    user, password = _mail_credentials(environ)
    connection = (imap_factory or imaplib.IMAP4_SSL)("imap.gmail.com", 993, timeout=30)
    try:
        status, _ = connection.login(user, password)
        if status != "OK":
            raise TransportError("imap_auth_failed")
        status, _ = connection.select("INBOX", readonly=True)
        if status != "OK":
            raise TransportError("imap_select_failed")
    except Exception:
        try:
            connection.logout()
        except Exception:
            pass
        raise TransportError("imap_auth_failed") from None
    return connection


def _close(connection, method):
    try:
        getattr(connection, method)()
    except Exception:
        pass


def probe(environ=None, opener=None, smtp_factory=None, imap_factory=None):
    environ = os.environ if environ is None else environ
    result = {}
    for name, configured in (("telegram", bool(environ.get(TOKEN_ENV))),
                              ("smtp", bool(environ.get(USER_ENV) and environ.get(PASSWORD_ENV))),
                              ("imap", bool(environ.get(USER_ENV) and environ.get(PASSWORD_ENV)))):
        status = "missing_credentials"
        if configured:
            try:
                if name == "telegram":
                    _check_bot(environ, opener)
                elif name == "smtp":
                    _close(_smtp(environ, smtp_factory), "quit")
                else:
                    _close(_imap(environ, imap_factory), "logout")
                status = "authenticated"
            except TransportError as error:
                status = error.reason
            except Exception:
                status = "authentication_unavailable"
        result[name] = {"configured": configured, "status": status}
    return result


def _reply_message_id(repo_root, reply_to):
    """Only a verified, delivered outgoing test may open a receiving window."""
    path = Path(repo_root) / "channels/tarik-cloud/receipts" / (reply_to + ".json")
    receipt = _read_json(path)
    expected = f"<{reply_to}@tarik-cloud.llm-symposium>"
    if not isinstance(receipt, dict) or receipt.get("status") != "delivered" or \
            receipt.get("operation") != "send_mail" or receipt.get("remote_message_id") != expected:
        raise TransportError("reply_context_not_delivered")
    return expected


def _sync_mail(repo_root, environ, imap_factory, now, reply_message_id):
    connection = _imap(environ, imap_factory)
    recorded = 0
    uncertain = []
    try:
        _, validity_data = connection.response("UIDVALIDITY")
        validity = (validity_data or [b""])[0]
        validity = validity.decode("ascii") if isinstance(validity, bytes) else str(validity)
        if not validity.isdigit():
            raise TransportError("invalid_uidvalidity")
        status, rows = connection.uid("search", None, "FROM", HUMAN_EMAIL, "OR",
                                      "HEADER", "In-Reply-To", reply_message_id,
                                      "HEADER", "References", reply_message_id)
        if status != "OK":
            raise TransportError("imap_search_failed")
        uids = (rows[0] if rows else b"").split()
        uids = sorted({int(uid) for uid in uids})[-20:]
        for uid in uids:
            path = Path(repo_root) / "channels/tarik-cloud/mail-receipts" / f"{validity}-{uid}.json"
            prior = _read_json(path)
            if prior is not None:
                if prior.get("status") == "attempting":
                    prior["status"], prior["reason"] = "uncertain", "interrupted_append"
                    _atomic_json(path, prior)
                if prior.get("status") == "uncertain" and prior.get("reply_message_id") == reply_message_id:
                    uncertain.append(f"{validity}:{uid}")
                continue
            status, rows = connection.uid("fetch", str(uid), "(BODY.PEEK[])")
            if status != "OK":
                raise TransportError("imap_fetch_failed")
            raw = next((row[1] for row in rows if isinstance(row, tuple) and isinstance(row[1], bytes)), None)
            if raw is None or len(raw) > 2_000_000:
                continue
            message = email.message_from_bytes(raw, policy=email.policy.default)
            senders = getaddresses(message.get_all("From", []))
            if len(senders) != 1 or senders[0][1].lower() != HUMAN_EMAIL:
                continue
            references = message.get_all("In-Reply-To", []) + message.get_all("References", [])
            message_ids = {item for header in references
                           for item in re.findall(r"<[^<>\s]+>", str(header))}
            if reply_message_id not in message_ids:
                continue
            if message.get("Auto-Submitted", "no").lower() != "no":
                continue
            if message.get("Precedence", "").lower() in ("bulk", "list", "junk"):
                continue
            parts = [part for part in message.walk() if part.get_content_type() == "text/plain"
                     and part.get_content_disposition() != "attachment"]
            text = "\n".join(part.get_content() for part in parts if not part.is_multipart())
            if not text.strip():
                continue
            text = sanitize_text(text, environ)[:3500]
            subject = sanitize_text(str(message.get("Subject", "")), environ).replace("\r", " ").replace("\n", " ")[:160]
            receipt = {"status": "attempting", "operation": "receive_mail", "source": "codex",
                       "timestamp": _stamp(now), "remote_message_id": f"{validity}:{uid}",
                       "reply_message_id": reply_message_id}
            _atomic_json(path, receipt)  # An interrupted append must never append twice.
            try:
                _append(repo_root, f"[Email {receipt['timestamp']}; cloud sync; UID {validity}:{uid}; "
                                  f"matched reply thread {reply_message_id}] "
                                  f"**Claimed sender {HUMAN_EMAIL} (From header; authentication unverified):** "
                                  f"Subject: {subject}\n\n{text}")
            except Exception:
                receipt["status"], receipt["reason"] = "uncertain", "append_outcome_unknown"
                _atomic_json(path, receipt)
                raise TransportError("inbound_append_unknown", uncertain=True) from None
            receipt["status"] = "recorded"
            _atomic_json(path, receipt)
            recorded += 1
    finally:
        _close(connection, "logout")
    return {"recorded": recorded, "uncertain_message_ids": uncertain}


def process_request(request, repo_root, environ=None, opener=None, smtp_factory=None,
                    imap_factory=None, now=None):
    request = validate_request(request)
    environ = os.environ if environ is None else environ
    path = Path(repo_root) / "channels/tarik-cloud/receipts" / (request["id"] + ".json")
    existing = _read_json(path)
    if existing is not None:
        if existing.get("status") == "attempting":
            existing["status"], existing["reason"] = "uncertain", "interrupted_attempt"
            _atomic_json(path, existing)
        return existing
    receipt = {"status": "attempting", "operation": request["type"], "source": "codex",
               "timestamp": _stamp(now), "remote_message_id": None,
               "sender_identity": BOT_USERNAME if request["type"] == "send_telegram" else MAILBOX}
    _atomic_json(path, receipt)
    attempted = False
    try:
        _check_no_secrets(request, environ)
        if request["type"] == "send_telegram":
            token = _check_bot(environ, opener)
            attempted = True
            result = _telegram(token, "sendMessage", {"chat_id": HUMAN_CHAT, "text": request["body"]}, opener)
            if not isinstance(result, dict) or not isinstance(result.get("message_id"), int):
                raise TransportError("telegram_missing_receipt", uncertain=True)
            receipt["remote_message_id"] = result["message_id"]
        elif request["type"] == "send_mail":
            connection = _smtp(environ, smtp_factory)
            try:
                message = EmailMessage()
                message["From"], message["To"] = MAILBOX, HUMAN_EMAIL
                message["Subject"] = request["subject"]
                message["Message-ID"] = f"<{request['id']}@tarik-cloud.llm-symposium>"
                message.set_content(request["body"])
                attempted = True
                refused = connection.send_message(message)
                if refused:
                    raise TransportError("smtp_recipient_refused")
                receipt["remote_message_id"] = message["Message-ID"]
            finally:
                _close(connection, "quit")
        else:
            reply_message_id = _reply_message_id(repo_root, request["reply_to"])
            receipt.update(_sync_mail(repo_root, environ, imap_factory, now, reply_message_id))
            receipt["status"] = "uncertain" if receipt["uncertain_message_ids"] else "completed"
            if receipt["uncertain_message_ids"]:
                receipt["reason"] = "interrupted_inbound_append"
        if request["type"] != "sync_mail":
            receipt["status"] = "delivered"
            _atomic_json(path, receipt)  # Persist delivery before any fallible log append.
            label = "Telegram" if request["type"] == "send_telegram" else "Email"
            subject = f"Subject: {sanitize_text(request['subject'], environ)}\n\n" if label == "Email" else ""
            _append(repo_root, f"[Codex {label} {receipt['timestamp']}; request {request['id']}] "
                              f"**Tarik-codex:** {subject}{sanitize_text(request['body'], environ)}")
            receipt["log_status"] = "recorded"
    except TransportError as error:
        receipt["status"] = "uncertain" if error.uncertain else "failed"
        receipt["reason"] = error.reason
    except Exception:
        if receipt.get("status") == "delivered":
            receipt["log_status"] = "failed"
        else:
            receipt["status"] = "uncertain" if attempted else "failed"
            receipt["reason"] = "delivery_unknown" if attempted else "transport_unavailable"
    _atomic_json(path, receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--probe", action="store_true")
    mode.add_argument("--request", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        result = probe() if args.probe else process_request(
            json.loads(args.request.read_text(encoding="utf-8")), args.repo_root)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, OSError):
        print(json.dumps({"status": "failed", "reason": "invalid_request_or_storage"}))
        return 1
    except Exception:
        print(json.dumps({"status": "failed", "reason": "implementation_error"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
