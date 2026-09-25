#!/usr/bin/env python3
# Owner: Desi
"""Telegram image intake, shared by Dawn's bot and the Four Amigos' bots.

Why this exists (2026-09-25): every bot found an attachment and dropped it. The bots
read only `message.text`, so a picture arrived as an empty string, the loop `continue`d,
and the human got "I received your attachment, but I can only read text messages right
now." He was told that by all five doors while the models behind four of them could see
perfectly well.

Canonical copy:  ~/LLM/llm-symposium/channels/media.py
Runtime copies:  ~/Dawn/telegram/media.py
                 ~/LLM/{desi,claude,gemini,tarik}-bot/media.py

The six files are byte-identical on purpose. There is no import path from the bot dirs
to the commons repo that is safe to depend on (a stale checkout would break every bot at
startup), so this is a copy, not a dependency. If you fix it, fix it in the repo first
and re-copy — `cmp -s` the five against the canonical file.

Verified on real endpoints 2026-09-25, one 96x96 blue PNG, "name the dominant colour":
DeepSeek direct -> "Blue"; OpenRouter -> "Blue"; Anthropic -> "Blue"; OpenAI -> "blue".
So the doors were never the problem in any of those four. (Google's door is separately
out of budget: HTTP 429, project spending cap, text as well as images.)

Stdlib only, like the rest of the channel code.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

TG_API = "https://api.telegram.org/bot%s"
TG_FILE = "https://api.telegram.org/file/bot%s/%s"

# A photo off a phone is well under this; the ceiling exists so a 2 GB document cannot
# be pulled into a chat turn. Telegram's own bot download limit is 20 MB.
MAX_BYTES = 5 * 1024 * 1024

# Telegram compresses every `photo` to JPEG. A `document` can be anything, so it needs
# the extension or mime type checked before it is treated as an image.
IMAGE_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".heic": "image/heic",
}


def _post_form(url, params, timeout=60):
    body = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def _mime_of(mime, name):
    if mime and mime.lower().startswith("image/"):
        return mime.lower()
    return IMAGE_EXT.get(os.path.splitext(name or "")[1].lower())


def extract(msg):
    """Every image in one Telegram message, as dicts. Pure, no network.

    `photo` is an array of the same image at several sizes; take the largest, because
    the small ones are thumbnails and a model reading a thumbnail is a model reading a
    thumbnail. `document` carries the original when the human used "send as file", which
    is how a screenshot arrives uncompressed.
    """
    out = []
    photos = msg.get("photo") or []
    if photos:
        best = max(photos, key=lambda p: (p.get("width") or 0) * (p.get("height") or 0))
        out.append({
            "file_id": best.get("file_id"),
            "mime": "image/jpeg",
            "size": best.get("file_size") or 0,
            "name": "photo.jpg",
            "width": best.get("width"),
            "height": best.get("height"),
        })
    doc = msg.get("document")
    if doc:
        mime = _mime_of(doc.get("mime_type"), doc.get("file_name"))
        if mime:
            out.append({
                "file_id": doc.get("file_id"),
                "mime": mime,
                "size": doc.get("file_size") or 0,
                "name": doc.get("file_name") or "document",
            })
    return [m for m in out if m.get("file_id")]


def describe(images):
    """A text stand-in for the transcript, so an image turn is never a blank line.

    Memory and the commons record are plain text and re-sent every turn; putting the
    bytes there would grow them without bound. What is kept is what was sent and where
    the file went, not the pixels.
    """
    if not images:
        return ""
    parts = []
    for i in images:
        label = i["name"]
        if i.get("width") and i.get("height"):
            label += " %dx%d" % (i["width"], i["height"])
        parts.append(label)
    return "[an image was sent: %s]" % ", ".join(parts)


def fetch(token, file_id, max_bytes=MAX_BYTES):
    """Download one file_id. Returns (file_path, bytes). Raises with a readable reason.

    Two calls, as Telegram requires: getFile resolves the id to a path on their side,
    then the bytes come off a second URL. The size is checked from the metadata first so
    an oversized file is refused without being pulled down.
    """
    info = _post_form(TG_API % token + "/getFile", {"file_id": file_id})
    if not info.get("ok"):
        raise RuntimeError("getFile refused: %s" % (info.get("description") or info))
    result = info.get("result") or {}
    path = result.get("file_path")
    if not path:
        raise RuntimeError("getFile returned no file_path")
    size = result.get("file_size") or 0
    if size > max_bytes:
        raise RuntimeError("file is %.1f MB, over the %.0f MB ceiling"
                           % (size / 1048576.0, max_bytes / 1048576.0))
    with urllib.request.urlopen(TG_FILE % (token, path), timeout=120) as resp:
        data = resp.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise RuntimeError("download exceeded the %.0f MB ceiling" % (max_bytes / 1048576.0))
    return path, data


def store(directory, data, ext=".jpg"):
    """Keep the bytes on this Mac, OUTSIDE the public repo, and return the path.

    channels/telegram/ is committed to a public repository, so the record gets the path
    and never the picture. What the human sends the bots stays on his disk.
    """
    os.makedirs(directory, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(data).hexdigest()[:12]
    path = os.path.join(directory, "%s-%s%s" % (stamp, digest, ext))
    with open(path, "wb") as fh:
        fh.write(data)
    return path


def load(token, images, max_bytes=MAX_BYTES):
    """Fetch + base64 every image. Returns (loaded, errors) — one bad file is not fatal.

    loaded: [{"mime":..., "b64":..., "path":..., "name":...}]
    """
    loaded, errors = [], []
    for img in images:
        try:
            path, data = fetch(token, img["file_id"], max_bytes=max_bytes)
            ext = os.path.splitext(img["name"])[1].lower() or ".jpg"
            saved = store(os.path.join(os.path.dirname(os.path.abspath(__file__)), "inbox"),
                          data, ext)
            loaded.append({
                "mime": img["mime"],
                "b64": base64.b64encode(data).decode("ascii"),
                "path": saved,
                "name": img["name"],
                "bytes": len(data),
            })
        except Exception as exc:                      # noqa: BLE001 — report, never raise
            errors.append("%s: %s" % (img.get("name") or img.get("file_id"), exc))
    return loaded, errors


# ---------------------------------------------------------------- provider shapes
# One image, four wire formats. The shape is the only thing that differs; every model
# behind these doors reads the same picture.
#   openai    — OpenAI, OpenRouter, DeepSeek (all OpenAI-compatible chat completions)
#   anthropic — Claude's messages API
#   google    — Gemini's generateContent

def block(provider, mime, data_b64):
    if provider == "anthropic":
        return {"type": "image",
                "source": {"type": "base64", "media_type": mime, "data": data_b64}}
    if provider == "google":
        return {"inline_data": {"mime_type": mime, "data": data_b64}}
    return {"type": "image_url",
            "image_url": {"url": "data:%s;base64,%s" % (mime, data_b64)}}


def text_block(provider, text):
    if provider == "google":
        return {"text": text}
    if provider == "anthropic":
        return {"type": "text", "text": text}
    return {"type": "text", "text": text}


def user_content(provider, text, images):
    """The user turn: a plain string when there is no image, blocks when there is.

    Returning a string in the no-image case is deliberate — it keeps every existing
    text path byte-for-byte what it was before this module existed.
    """
    if not images:
        return text
    parts = []
    if text:
        parts.append(text_block(provider, text))
    for img in images:
        parts.append(block(provider, img["mime"], img["b64"]))
    return parts
