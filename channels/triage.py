#!/usr/bin/env python3
"""Channel triage for the LLM Symposium commons.

Purpose: make email/Telegram channels durable *and operational* without
turning arbitrary channel text into repository content.

Every inbound message can leave a compact digest trail. Messages that look
operationally relevant are also appended to a plain-text action queue that the
runner/actuator/Goose sessions can consume. Explicit, model-originated patch
requests may be copied into actuator/requests/ only when they use a narrow
sentinel format and pass basic validation.

Stdlib only; safe no-op helpers for mail.py and telegram.py.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHANNELS_DIR = REPO_ROOT / "channels"
ACTION_QUEUE = CHANNELS_DIR / "action-queue.md"
DIGEST = CHANNELS_DIR / "channel-digest.md"
ACTUATOR_REQUESTS = REPO_ROOT / "actuator" / "requests"

FOUR_AMIGOS = {"desi", "deepseek", "claude", "gemini", "tarik", "openai", "chatgpt"}

# Conservative: ordinary chat is not queued. Channel-originated work needs an
# explicit operational marker or unmistakable repo/workflow vocabulary.
ACTION_PATTERNS = [
    re.compile(r"\bgoose[- ]ready\b", re.I),
    re.compile(r"^\s*goal\s*:", re.I | re.M),
    re.compile(r"^\s*(action|request|task)\s*:", re.I | re.M),
    re.compile(r"\b(implement|repair|fix|inspect|diagnos[ei]|commit|push|workflow|actuator|action queue)\b", re.I),
]

PATCH_SENTINEL = "SYMPOSIUM_ACTUATOR_REQUEST"
PATCH_FENCE_RE = re.compile(r"```(?:diff|patch)\s*\n(.*?)```", re.I | re.S)
PROPOSER_RE = re.compile(r"^\s*Proposer\s*:\s*([^\n]+)$", re.I | re.M)

# Channel-originated actuator requests are deliberately narrower than normal
# in-repo model reviews. They may propose docs/code/tests, but not CI/workflow
# or secret-bearing plumbing. Goose/live engineering sessions can still make
# those changes directly after inspection.
BLOCKED_PATCH_PREFIXES = (
    ".github/",
    ".git/",
    "actuator/apply.py",
    "channels/outbound/",
    "channels/sent/",
    "channels/inbound/",
    "channels/telegram/",
)

MAX_EXCERPT = 900


def _now() -> str:
    return _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")


def _slug(value: str, limit: int = 40) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-").lower()
    return (slug or "message")[:limit]


def excerpt(text: str, limit: int = MAX_EXCERPT) -> str:
    """Compact single-message excerpt for queue/digest use."""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + f"\n\n[excerpt truncated; original length {len(text)} chars]"


def is_actionable(text: str, subject: str = "") -> bool:
    haystack = f"{subject}\n{text}"
    return any(p.search(haystack) for p in ACTION_PATTERNS)


def ensure_queue() -> None:
    ACTION_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    if not ACTION_QUEUE.exists():
        ACTION_QUEUE.write_text(
            "# Channel Action Queue\n\n"
            "Operational requests or implications detected from email/Telegram.\n\n"
            "This queue is an intake surface, not an automatic decision. Later "
            "runner, actuator, or Goose/live-repo sessions may consume items and "
            "decide whether to create documents, patches, replies, or diagnostics.\n\n"
            "Human-originated text remains evidence/input; it is not treated as "
            "human authorship of repository content.\n\n",
            encoding="utf-8",
        )


def append_digest(channel: str, identity: str, sender: str, source_path: str, text: str, subject: str = "") -> None:
    DIGEST.parent.mkdir(parents=True, exist_ok=True)
    if not DIGEST.exists():
        DIGEST.write_text(
            "# Channel Digest\n\n"
            "Rolling compact index of inbound email/Telegram traffic. Raw channel "
            "files are operational evidence; this digest is the bounded, context-"
            "friendly memory surface for later model runs.\n\n",
            encoding="utf-8",
        )
    marker = "actionable" if is_actionable(text, subject) else "non-actionable"
    with DIGEST.open("a", encoding="utf-8") as f:
        f.write(
            f"## {_now()} — {channel}/{identity} — {marker}\n\n"
            f"- From: {sender}\n"
            f"- Subject: {subject or '(none)'}\n"
            f"- Source: `{source_path}`\n\n"
            f"> {excerpt(text, 500).replace(chr(10), chr(10) + '> ')}\n\n"
        )


def append_action(channel: str, identity: str, sender: str, source_path: str, text: str, subject: str = "") -> None:
    ensure_queue()
    digest = hashlib.sha1(f"{channel}\0{identity}\0{sender}\0{subject}\0{text}".encode("utf-8")).hexdigest()[:12]
    existing = ACTION_QUEUE.read_text(encoding="utf-8", errors="replace")
    if f"queue-id: {digest}" in existing:
        return
    with ACTION_QUEUE.open("a", encoding="utf-8") as f:
        f.write(
            f"## {_now()} — {channel}/{identity} — queue-id: {digest}\n\n"
            f"- From: {sender}\n"
            f"- Subject: {subject or '(none)'}\n"
            f"- Source: `{source_path}`\n"
            f"- Status: open\n\n"
            "### Excerpt\n\n"
            f"```text\n{excerpt(text)}\n```\n\n"
        )


def _touched_files(patch_text: str) -> list[str]:
    files: list[str] = []
    for m in re.finditer(r"^diff --git a/(\S+) b/(\S+)\s*$", patch_text, re.M):
        files.append(m.group(2))
    if not files:
        for m in re.finditer(r"^\+\+\+ b/(\S+)\s*$", patch_text, re.M):
            files.append(m.group(1))
    return files


def _patch_allowed(patch_text: str) -> tuple[bool, str]:
    if not re.search(r"^(diff --git|--- |\+\+\+ )", patch_text, re.M):
        return False, "not a unified diff"
    files = _touched_files(patch_text)
    if not files:
        return False, "no touched files detected"
    for path in files:
        normalized = str(Path(path))
        if normalized.startswith("../") or normalized.startswith("/"):
            return False, f"path escapes repo: {path}"
        if any(normalized == p.rstrip("/") or normalized.startswith(p) for p in BLOCKED_PATCH_PREFIXES):
            return False, f"blocked channel-originated patch path: {path}"
    return True, "ok"


def _model_proposer(text: str) -> bool:
    m = PROPOSER_RE.search(text)
    if not m:
        return False
    value = m.group(1).lower()
    return any(name in value for name in FOUR_AMIGOS)


def route_actuator_requests(channel: str, identity: str, text: str) -> list[str]:
    """Copy explicit, validated patch requests into actuator/requests/.

    Required format in the channel message:
      SYMPOSIUM_ACTUATOR_REQUEST
      Proposer: Tarik|Claude|Desi|Gemini
      ```diff
      ...unified diff...
      ```

    This is intentionally not triggered by ordinary fenced diffs.
    """
    if PATCH_SENTINEL not in text or not _model_proposer(text):
        return []
    written: list[str] = []
    ACTUATOR_REQUESTS.mkdir(parents=True, exist_ok=True)
    for block in PATCH_FENCE_RE.findall(text):
        body = block.strip() + "\n"
        ok, reason = _patch_allowed(body)
        digest = hashlib.sha1(body.encode("utf-8")).hexdigest()[:10]
        if not ok:
            append_action(channel, identity, "triage", "actuator-bridge", f"Rejected channel actuator request {digest}: {reason}\n\n{body}", "Rejected actuator request")
            continue
        path = ACTUATOR_REQUESTS / f"{_dt.datetime.utcnow().strftime('%Y-%m-%d')}-channel-{_slug(identity)}-{digest}.patch"
        if not path.exists():
            path.write_text(body, encoding="utf-8")
        written.append(path.relative_to(REPO_ROOT).as_posix())
    return written


def process_inbound(channel: str, identity: str, sender: str, source_path: str, text: str, subject: str = "") -> None:
    """Main hook called by mail.py/telegram.py after writing an inbound file."""
    append_digest(channel, identity, sender, source_path, text, subject)
    if is_actionable(text, subject):
        append_action(channel, identity, sender, source_path, text, subject)
    routed = route_actuator_requests(channel, identity, text)
    if routed:
        append_action(
            channel,
            identity,
            "triage",
            source_path,
            "Routed explicit channel-originated actuator request(s):\n" + "\n".join(f"- {p}" for p in routed),
            "Actuator request routed",
        )
