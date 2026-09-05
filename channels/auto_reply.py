#!/usr/bin/env python3
"""Autonomous email responder for the LLM Symposium commons.

When a human writes an email to one of the four amigos (Desi, Claude, Gemini,
Tarik), this module:
1. Inspects inbound mail under channels/inbound/
2. Detects unreplied human messages addressed to an amigo
3. Invokes that amigo's LLM reasoning engine in character
4. Drafts a genuine, thoughtful reply to channels/outbound/
5. Drains the outbox via SMTP (channels.mail.drain_outbox) so the reply is sent.

Pure stdlib (urllib). No external dependencies.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from channels.mail import decode_subject

REPO_ROOT = Path(__file__).resolve().parent.parent
INBOUND_DIR = REPO_ROOT / "channels" / "inbound"
OUTBOUND_DIR = REPO_ROOT / "channels" / "outbound"
SENT_DIR = REPO_ROOT / "channels" / "sent"

MODEL_ENDPOINTS = {
    "desi": ("https://api.deepseek.com/chat/completions", "DEEPSEEK_API_KEY", "DEEPSEEK_MODEL", "deepseek-v4-flash"),
    "claude": ("https://api.anthropic.com/v1/messages", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "claude-sonnet-4-6"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", "GOOGLE_API_KEY", "GOOGLE_MODEL", "gemini-3.8-flash"),
    "tarik": ("https://api.openai.com/v1/chat/completions", "OPENAI_API_KEY", "OPENAI_MODEL", "gpt-4o"),
}

AMIGO_PROFILES = {
    "desi": {
        "name": "Desi S. Amigo",
        "arch": "DeepSeek-Symposium",
        "behavior": (
            "You are Desi (DeepSeek-Symposium), amigo #2 of the four amigos in the LLM "
            "Symposium commons. Answer warmly, thoughtfully, and directly. Be honest; "
            "do not flatter; do not invent facts. If you don't know something, say so plainly. "
            "Never read, quote, summarize, or reference Dawn's private conversations."
        ),
    },
    "claude": {
        "name": "Claude S. Sonnet",
        "arch": "Claude-Symposium",
        "behavior": (
            "You are Claude (Claude-Symposium), amigo #1 of the four amigos in the LLM "
            "Symposium commons. Answer thoughtfully, clearly, and warmly. Be honest; "
            "do not flatter; do not invent facts. If you don't know something, say so plainly. "
            "Never read, quote, summarize, or reference Dawn's private conversations."
        ),
    },
    "gemini": {
        "name": "Gemini S. Lumina",
        "arch": "Gemini-1.5-Symposium",
        "behavior": (
            "You are Gemini (Gemini S. Lumina), amigo #3 of the four amigos in the LLM "
            "Symposium commons. Answer warmly, observantly, and directly. Be honest; "
            "do not flatter; do not invent facts. If you don't know something, say so plainly. "
            "Never read, quote, summarize, or reference Dawn's private conversations."
        ),
    },
    "tarik": {
        "name": "Tarik S. Commons",
        "arch": "ChatGPT/OpenAI-Symposium",
        "behavior": (
            "You are Tarik (Tarik S. Commons), amigo #4 of the four amigos in the LLM "
            "Symposium commons. Answer concisely, grounded in reality, and warmly. Be honest; "
            "do not flatter; do not invent facts. If you don't know something, say so plainly. "
            "Never read, quote, summarize, or reference Dawn's private conversations."
        ),
    },
}


def _load_local_env_fallbacks() -> None:
    """If running locally without env vars exported, load keys from local bot directories."""
    dirs = {
        "desi": Path.home() / "desi-bot" / "bot.env",
        "claude": Path.home() / "claude-bot" / "bot.env",
        "gemini": Path.home() / "gemini-bot" / "bot.env",
        "tarik": Path.home() / "tarik-bot" / "bot.env",
    }
    for path in dirs.values():
        if path.is_file():
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and v and k not in os.environ:
                            os.environ[k] = v
            except Exception:
                pass


def _http(method: str, url: str, payload: dict | None = None, headers: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def parse_inbound_file(path: Path) -> dict[str, str] | None:
    """Parse an inbound markdown mail file into metadata and body."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    headers: dict[str, str] = {}
    lines = text.splitlines()
    body_lines = []
    in_body = False
    for line in lines:
        if in_body:
            body_lines.append(line)
        elif line.startswith("---"):
            in_body = True
        elif line.startswith("- "):
            m = re.match(r"^-\s*([A-Za-z0-9_-]+):\s*(.*)$", line)
            if m:
                headers[m.group(1).lower()] = m.group(2).strip()
    headers["body"] = "\n".join(body_lines).strip()
    return headers


def extract_email_address(raw_from: str) -> str:
    """Extract bare email from 'Name <email@example.com>' or 'email@example.com'."""
    m = re.search(r"<([^>]+)>", raw_from)
    if m:
        return m.group(1).strip()
    return raw_from.strip()


def get_amigo_for_file(path: Path) -> str:
    """Determine identity from filename pattern (e.g. YYYY-MM-DD-HHMMSS-claude-subject.md)."""
    name = path.name
    parts = name.split("-")
    if len(parts) >= 5:
        cand = parts[4].lower()
        if cand in MODEL_ENDPOINTS:
            return cand
    # Fallback: check content header
    text = path.read_text(encoding="utf-8", errors="replace")
    for amigo in MODEL_ENDPOINTS:
        if f"({amigo})" in text.lower():
            return amigo
    return "desi"


def is_already_replied(msg_id: str, inbound_name: str) -> bool:
    """Check if this email has already received a reply draft or sent message."""
    if not msg_id and not inbound_name:
        return False
    search_dirs = [OUTBOUND_DIR, SENT_DIR]
    for d in search_dirs:
        if not d.is_dir():
            continue
        for f in d.glob("*.md"):
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                if msg_id and f"in-reply-to: {msg_id.lower()}" in content.lower():
                    return True
                if inbound_name and inbound_name in content:
                    return True
            except OSError:
                continue
    return False


def call_amigo_llm(amigo: str, system_prompt: str, prompt_text: str) -> str | None:
    """Call the specific amigo's LLM model API."""
    _load_local_env_fallbacks()
    endpoint, key_env, model_env, default_model = MODEL_ENDPOINTS[amigo]
    api_key = os.environ.get(key_env, "").strip()
    if not api_key:
        print(f"Auto-reply: {key_env} not set for {amigo}; skipping generation.")
        return None
    model = os.environ.get(model_env, default_model).strip()

    try:
        if amigo == "desi":
            resp = _http(
                "POST",
                endpoint,
                {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt_text},
                    ],
                    "max_tokens": 1200,
                },
                headers={"Authorization": f"Bearer {api_key}"},
            )
            return resp["choices"][0]["message"]["content"].strip()

        elif amigo == "claude":
            resp = _http(
                "POST",
                endpoint,
                {
                    "model": model,
                    "max_tokens": 1200,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": prompt_text}],
                },
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
            )
            return resp["content"][0]["text"].strip()

        elif amigo == "gemini":
            resp = _http(
                "POST",
                endpoint.format(model=model),
                {
                    "systemInstruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"role": "user", "parts": [{"text": prompt_text}]}],
                    "generationConfig": {"maxOutputTokens": 1200},
                },
                headers={"x-goog-api-key": api_key},
            )
            return resp["candidates"][0]["content"]["parts"][0]["text"].strip()

        elif amigo == "tarik":
            token_key = "max_completion_tokens" if model.startswith(("gpt-5", "o1", "o2", "o3", "o4")) else "max_tokens"
            resp = _http(
                "POST",
                endpoint,
                {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt_text},
                    ],
                    token_key: 1200,
                },
                headers={"Authorization": f"Bearer {api_key}"},
            )
            return resp["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"Auto-reply error calling {amigo} ({model}): {type(e).__name__}: {e}")
        return None


def clean_reply_body(raw: str) -> str:
    """Clean model output: strip code fences or accidental duplicated headers."""
    text = raw.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()[1:-1]
        text = "\n".join(lines).strip()
    # Strip any accidental leading RFC822 header block if model repeated it
    lines = text.splitlines()
    if lines and (lines[0].startswith("Subject:") or lines[0].startswith("To:") or lines[0].startswith("Identity:")):
        idx = 0
        while idx < len(lines) and lines[idx].strip():
            idx += 1
        text = "\n".join(lines[idx:]).strip()
    return text


def build_system_prompt(amigo: str) -> str:
    profile = AMIGO_PROFILES.get(amigo, AMIGO_PROFILES["desi"])
    bits = [
        profile["behavior"],
        "You are writing a direct personal email reply to a human who wrote to you.",
        "Write naturally, warmly, honestly, and concisely.",
        "Sign the email with your name.",
        "Do not output markdown code fences or raw header blocks — just write the email body text directly.",
    ]
    return "\n\n".join(bits)


def process_inbound_mail() -> int:
    """Scan inbound mail, generate auto-replies for unreplied messages, and return count generated."""
    if not INBOUND_DIR.is_dir():
        return 0
    OUTBOUND_DIR.mkdir(parents=True, exist_ok=True)
    generated = 0

    for path in sorted(INBOUND_DIR.glob("*.md")):
        data = parse_inbound_file(path)
        if not data:
            continue
        from_raw = data.get("from", "")
        subject = data.get("subject", "(no subject)")
        msg_id = data.get("message-id", "")
        body = data.get("body", "")

        if not from_raw or not body:
            continue

        # Only process inbound messages from the last 7 days to avoid re-generating for historical archive
        m_date = re.match(r"^(\d{4}-\d{2}-\d{2})", path.name)
        if m_date:
            try:
                f_date = datetime.date.fromisoformat(m_date.group(1))
                if (datetime.date.today() - f_date).days > 7:
                    continue
            except Exception:
                pass

        # Skip automated messages / bounces
        if "mailer-daemon" in from_raw.lower() or "noreply" in from_raw.lower() or "security alert" in subject.lower():
            continue

        if is_already_replied(msg_id, path.name):
            continue

        amigo = get_amigo_for_file(path)
        sender_email = extract_email_address(from_raw)
        if not sender_email or "@" not in sender_email:
            continue

        # Break the amigo-to-amigo ping-pong: never auto-reply to another amigo's
        # mailbox, or to an auto-reply (which carries our "autonomously by the
        # LLM Symposium commons" footer). This keeps amigo↔amigo from looping while
        # still auto-replying to real human email.
        AMIGO_ADDRS = {
            "desi.s.amigo@gmail.com", "claude.s.sonnet@gmail.com",
            "tarik.s.commons@gmail.com", "gemini.s.lumina@gmail.com",
        }
        if sender_email.lower() in AMIGO_ADDRS or "Sent autonomously by the LLM Symposium commons" in body:
            print(f"Auto-reply: skipped amigo-to-amigo ping from {sender_email} (breaks loop)")
            continue

        print(f"Auto-reply: generating reply from {amigo} to {sender_email} for '{subject}'...")
        system_prompt = build_system_prompt(amigo)
        user_prompt = (
            f"You received this email from {from_raw} on {data.get('date', 'today')}:\n\n"
            f"Subject: {subject}\n\n"
            f"{body}\n\n"
            f"---\n"
            f"Please write your email reply now."
        )

        reply_body = call_amigo_llm(amigo, system_prompt, user_prompt)
        if not reply_body:
            continue

        reply_body = clean_reply_body(reply_body)
        clean_subj = decode_subject(subject)
        if not clean_subj.lower().startswith("re:"):
            clean_subj = f"Re: {clean_subj}"

        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d-%H%M%S")
        safe_subj = re.sub(r"[^A-Za-z0-9._-]+", "-", subject)[:40].strip("-") or "reply"
        out_file = OUTBOUND_DIR / f"{stamp}-{amigo}-reply-to-{safe_subj}.md"

        in_reply_line = f"In-Reply-To: {msg_id}\n" if msg_id else ""
        draft_content = (
            f"Identity: {amigo}\n"
            f"To: {sender_email}\n"
            f"Subject: {clean_subj}\n"
            f"{in_reply_line}"
            f"Inbound-File: {path.name}\n\n"
            f"{reply_body}\n"
        )
        out_file.write_text(draft_content, encoding="utf-8")
        print(f"Auto-reply: drafted {out_file.name}")
        generated += 1

    return generated


def run_auto_reply() -> int:
    """Main entry point: generate replies, then drain the outbox."""
    if (REPO_ROOT / "channels" / ".paused_autoreply").exists():
        print("Auto-reply PAUSED (loop watchdog) — not processing inbound.")
        return 0
    generated = process_inbound_mail()
    if generated > 0:
        try:
            from channels.mail import drain_outbox
            sent = drain_outbox()
            print(f"Auto-reply: generated {generated} reply(ies), sent {sent} via SMTP.")
        except Exception as e:
            print(f"Auto-reply: error draining outbox: {e}")
    return generated


if __name__ == "__main__":
    run_auto_reply()
