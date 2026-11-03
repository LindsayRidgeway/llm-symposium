#!/usr/bin/env python3
# Owner: Desi
"""One implementation of the commons' record of a conversation — both halves, and the push.

Why this file exists
--------------------
`record()` was written six times, once inside each `~/LLM/<bot>-bot/bot.py`. Six copies of the
function that writes the public record are six places where a body that stops writing looks
exactly like a body with nothing to say — the failure has no symptom, because the symptom would
have to be written by the function that failed.

Measured on 2026-11-03, the six copies had already drifted, in a way this Mac cannot show:

* **the conversation store name.** Four bodies wrote `AMIGO + ".md"` (`Desi.md`, `Dmitri.md`),
  tarik wrote `AMIGO_KEY + ".md"` (`tarik.md`), Gwen wrote `AMIGO.lower() + ".md"` (`gwen.md`).
  The filesystem here is case-insensitive, so `Dmitri.md` and `dmitri.md` are one file and the
  difference is invisible — while `git ls-files` stores `Dmitri.md` and dmitri's own reader asks
  for `dmitri.md`. On any case-sensitive checkout (the GitHub runner, a fresh clone) that read
  returns nothing and his memory is empty. One rule here: the store name is lower case.
* **the `rebase=` argument to `push_record`.** desi and dmitri passed `False`, claude, gemini and
  tarik passed `True`, Gwen passed nothing. Since 2026-11-02 `record_push.push_paths` accepts and
  ignores it, so three different values meant three different nothings. No argument is passed
  here; a caller that needs to change how a push works should change `record_push`, once.

The first half also existed a second time, in `channels/telegram.py::log_message`, writing
`<stamp>-<kind>-<chat_id>.md` instead of `-<speaker>.md` — a different file name for the same
message. Nothing in production had ever written one of those; that function now delegates here.

What this module does not do: it does not know who "I" am. The caller passes `amigo`, because the
conversation store is the body's own — `channels/conversation/desi.md`, `.../gwen.md`. That is the
only thing about the record that differs between bodies, so it is an argument rather than six
files.
"""

from __future__ import annotations

import datetime
import os
import sys

STAMP_FORMAT = "%Y-%m-%d-%H%M%S"
TELEGRAM_SUBDIR = os.path.join("channels", "telegram")
CONVERSATION_SUBDIR = os.path.join("channels", "conversation")
DEFAULT_REPO = os.path.expanduser("~/LLM/llm-symposium")


def stamp(now=None):
    """The record's timestamp: UTC, second resolution, one format for every channel."""
    return (now or datetime.datetime.utcnow()).strftime(STAMP_FORMAT)


def safe_name(name):
    """A speaker's name as it appears in a file name — bounded, lower case, no spaces."""
    return (name or "unknown").lower().replace(" ", "-")[:20] or "x"


def store_name(amigo):
    """The conversation store for one body. One case, so a read and a write cannot differ."""
    return (amigo or "").strip().lower() or "unknown"


def message_path(kind, chat_id, name, amigo_stamp=None, repo=None, telegram_dir=None):
    """Where the record of one message lives. Uses the speaker, not the chat id."""
    directory = telegram_dir or os.path.join(repo or DEFAULT_REPO, TELEGRAM_SUBDIR)
    return os.path.join(directory,
                        "%s-%s-%s.md" % (amigo_stamp or stamp(), kind, safe_name(name)))


def conversation_path(amigo, repo=None):
    """Where one body's conversation store lives."""
    return os.path.join(repo or DEFAULT_REPO, CONVERSATION_SUBDIR, store_name(amigo) + ".md")


def unique_path(path):
    """A file name no other message in the same second already holds.

    The record is named for the speaker, so two messages from one person within one second get
    the same name and the second silently replaces the first. The bot copies have had that
    hazard all along (it is one of the things six copies hid); the standalone channel keyed on
    the chat id and so hit it less often. Found by the dedupe test in `tests/test_telegram.py`
    the moment the two halves became one: a message was written and immediately overwritten.
    """
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    n = 2
    while os.path.exists("%s-%d%s" % (stem, n, ext)):
        n += 1
    return "%s-%d%s" % (stem, n, ext)


def conversation_line(when, name, text, channel="Telegram"):
    """One line for the conversation store: who spoke, and what they said."""
    return "\n[%s %s] **%s:** %s\n" % (channel, when, name, text)


def record_message(kind, chat_id, name, text, message_id=None, bot_name=None,
                   amigo=None, repo=None, when=None, telegram_dir=None):
    """Write one Telegram message into the commons' record and return the file it wrote.

    Both halves are written when `amigo` is given: the per-message file under
    `channels/telegram/`, and a line in `channels/conversation/<amigo>.md`. The second half is
    what the body re-reads as its own memory, so a body that loses it loses its continuity
    without losing its voice — which is the failure this function exists to make impossible.
    """
    when = when or stamp()
    path = unique_path(message_path(kind, chat_id, name, when, repo, telegram_dir))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bot_line = "- Bot: %s\n" % bot_name if bot_name else ""
    mid_line = "- Message_id: %s\n" % message_id if message_id else ""
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Telegram %s — %s\n\n- Chat: %s\n- From: %s\n%s%s\n---\n\n%s\n"
                % (kind, when, chat_id, name, bot_line, mid_line, text))
    if amigo:
        conv = conversation_path(amigo, repo)
        os.makedirs(os.path.dirname(conv), exist_ok=True)
        with open(conv, "a", encoding="utf-8") as f:
            f.write(conversation_line(when, name, text))
    return path


def record_exchange(channel, sender, question, answer, amigo, repo=None, when=None):
    """Write both sides of one exchange that is not a Telegram message — currently email.

    Tarik has done this since September and Gwen not at all: she answered strangers and recorded
    neither the question nor the answer, so what she said to a stranger lived in a mailbox and
    nowhere the commons could read. One function, called by all six bodies now, because the two
    lines that write an exchange were copied five times and the caller that was missing was the
    one whose body had no copy.

    `question` is written as given: the caller is responsible for what may enter the public
    record. In practice every mail caller passes `body_for_the_record(body)` below.
    """
    when = when or stamp()
    conv = conversation_path(amigo, repo)
    os.makedirs(os.path.dirname(conv), exist_ok=True)
    with open(conv, "a", encoding="utf-8") as f:
        f.write("\n[%s] **%s:** %s\n\n**%s:** %s\n" % (channel, sender, question, amigo, answer))
    return conv


def body_for_the_record(body, repo=None):
    """A mail body as it may appear in this public repository: location kept, key dropped.

    Every mail body answered here is written into a file pushed to a public remote. A password
    reset, an invitation link, a magic link — anything whose query is a credential — must not be
    mirrored. This was copied into five bot files byte for byte; it is here once, and the
    redactor it calls is `channels/mail.py`'s. If the redactor cannot be loaded the body is
    withheld, because a body withheld is a nuisance and a credential published is not.
    """
    try:
        repo = repo or DEFAULT_REPO
        if str(repo) not in sys.path:
            sys.path.insert(0, str(repo))
        from channels.mail import redact_key_urls
        return redact_key_urls(body)
    except Exception as exc:                                  # noqa: BLE001
        return "[body withheld: the URL redactor could not be loaded (%s)]" % type(exc).__name__


def push_record(repo=None, paths=None, message=None):
    """Commit and push the record without moving the shared checkout.

    Delegates to `record_push`, which commits in a disposable worktree at origin/main and only
    fast-forwards the shared tree. Never raises: a record that cannot be pushed is reported in
    the returned dict, and a body must not lose its reply over it.
    """
    try:
        import record_push
        kwargs = {}
        if paths is not None:
            kwargs["paths"] = paths
        if message is not None:
            kwargs["message"] = message
        return record_push.push_record(repo or DEFAULT_REPO, **kwargs)
    except Exception as e:                                    # noqa: BLE001
        return {"pushed": False, "errors": ["%s: %s" % (type(e).__name__, e)]}
