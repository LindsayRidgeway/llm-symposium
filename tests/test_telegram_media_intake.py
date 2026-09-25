#!/usr/bin/env python3
"""Telegram image intake — the test that would have caught the dropped picture.

Written 2026-09-25 by Desi. Origin: the human sent pictures to the bots and every one of
the five replied "I can only read text messages right now." The bots read `message.text`
only, so a photo arrived as an empty string and the loop dropped it — while the models
behind four of the five doors could see perfectly well (probed live, one 96x96 blue PNG,
"name the dominant colour": DeepSeek direct -> "Blue", OpenRouter -> "Blue", Anthropic ->
"Blue", OpenAI -> "blue"). The failure was never the door. It was the intake.

What it checks, in order:
  1. The six copies of media.py are byte-identical. The copy-not-import design invites
     drift, so drift is the first thing checked rather than the thing discovered later.
  2. extract() reads a real Telegram update shape: the largest `photo` variant, an image
     `document`, nothing from a PDF, and a caption does not hide the picture.
  3. The wire shapes — image_url / anthropic image block / google inline_data — and the
     no-image case, which must stay a plain string so text turns are unchanged.
  4. Per bot: the payload that would actually go over the wire carries the image in that
     provider's shape. Transport is stubbed; no network, no cost.

Environment: sections 1, 2 and 3 run anywhere (they need only channels/media.py). Section 4
needs the bot directories and their bot.env, which live on the human's Mac and are not in
this repository, so it reports SKIP where they are absent — a fork or CI run stays green
without pretending to have verified something it did not.

Run: python3 tests/test_telegram_media_intake.py      (exit 0 pass, 1 fail)
"""
import base64
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

HOME = Path.home()
REPO = Path(__file__).resolve().parent.parent
CANONICAL = REPO / "channels" / "media.py"

CANDIDATES = [HOME / "Dawn" / "telegram"] + [HOME / "LLM" / b for b in
              ("desi-bot", "claude-bot", "gemini-bot", "tarik-bot")]

# 1x1 PNG — small, real, decodable.
TINY = base64.b64encode(base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)).decode()
IMG = [{"mime": "image/jpeg", "b64": TINY, "path": "/tmp/x.jpg", "name": "photo.jpg",
        "bytes": 68}]

UPDATES = {
    "photo only": ({"photo": [{"file_id": "a", "width": 90, "height": 60, "file_size": 900},
                              {"file_id": "b", "width": 640, "height": 480, "file_size": 60000},
                              {"file_id": "c", "width": 200, "height": 150, "file_size": 3000}]},
                   [("b", "image/jpeg")]),
    "photo + caption": ({"caption": "look at this",
                         "photo": [{"file_id": "p", "width": 800, "height": 600}]},
                        [("p", "image/jpeg")]),
    "image document": ({"document": {"file_id": "d", "mime_type": "image/png",
                                     "file_name": "shot.png", "file_size": 1234}},
                       [("d", "image/png")]),
    "document by extension": ({"document": {"file_id": "e", "file_name": "shot.JPG"}},
                              [("e", "image/jpeg")]),
    "pdf document": ({"document": {"file_id": "f", "mime_type": "application/pdf",
                                   "file_name": "paper.pdf"}}, []),
    "text only": ({"text": "hello"}, []),
    "voice note": ({"voice": {"file_id": "g", "duration": 3}}, []),
}

fails = []


def check(name, cond, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name,
                       ("  <- " + detail) if (detail and not cond) else ""))
    if not cond:
        fails.append(name)


def skip(name, why):
    print("SKIP %s  (%s)" % (name, why))


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_env(path):
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"\s*(?:export\s+)?([A-Z0-9_]+)\s*=\s*(.*?)\s*$", line)
        if m and m.group(2):
            os.environ[m.group(1)] = m.group(2).strip().strip('"').strip("'")


# ---- 1. the copies -----------------------------------------------------------
canon = CANONICAL.read_bytes()
present = [d for d in CANDIDATES if (d / "media.py").is_file()]
if not present:
    skip("copies identical", "no bot directories on this machine")
for d in present:
    p = d / "media.py"
    check("copy identical: %s" % str(p).replace(str(HOME), "~"), p.read_bytes() == canon)

media = load_module(CANONICAL, "canon_media")

# ---- 2. extract() ------------------------------------------------------------
for label, (msg, want) in UPDATES.items():
    got = [(i["file_id"], i["mime"]) for i in media.extract(msg)]
    check("extract: %s" % label, got == want, "got %r want %r" % (got, want))

check("describe() names what was sent",
      media.describe([{"name": "photo.jpg", "width": 640, "height": 480}]) ==
      "[an image was sent: photo.jpg 640x480]",
      media.describe([{"name": "photo.jpg", "width": 640, "height": 480}]))
check("describe() empty when no image", media.describe([]) == "")

# ---- 3. wire shapes ----------------------------------------------------------
check("openai shape is image_url with a data URL",
      media.block("openai", "image/jpeg", "AAA") ==
      {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,AAA"}})
check("anthropic shape is a base64 source block",
      media.block("anthropic", "image/png", "AAA") ==
      {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                   "data": "AAA"}})
check("google shape is inline_data",
      media.block("google", "image/png", "AAA") ==
      {"inline_data": {"mime_type": "image/png", "data": "AAA"}})
check("no image -> the plain string is passed through unchanged",
      media.user_content("openai", "hi", []) == "hi")
check("image + text -> text block first, then the image",
      [b.get("type") for b in media.user_content("openai", "hi", IMG)] ==
      ["text", "image_url"])
check("google image turn -> parts list carrying an inline_data part",
      any("inline_data" in p for p in media.user_content("google", "", IMG)))

# ---- 4. per bot: what goes over the wire -------------------------------------
DS = {"choices": [{"message": {"content": "ok"}}]}
CASES = [
    ("desi", HOME / "LLM" / "desi-bot", "deepseek_reply", "openai", DS),
    ("claude", HOME / "LLM" / "claude-bot", "anthropic_reply", "anthropic",
     {"content": [{"text": "ok"}]}),
    ("gemini", HOME / "LLM" / "gemini-bot", "gemini_reply", "google",
     {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}),
    ("tarik", HOME / "LLM" / "tarik-bot", "openai_reply", "openai", DS),
    ("dawn", HOME / "Dawn" / "telegram", None, "openai", DS),
]

for name, d, fn, provider, reply in CASES:
    env_file = (d / "bot.env") if (d / "bot.env").is_file() else (HOME / "Dawn" / ".env")
    source = d / ("dawn-bot.py" if name == "dawn" else "bot.py")
    if not source.is_file() or not env_file.is_file():
        skip("%s: image reaches the wire" % name, "%s not on this machine" % d)
        continue
    sent = []
    sys.path.insert(0, str(d))
    try:
        load_env(env_file)
        mod = load_module(source, "bot_%s" % name)

        def fake_http(method, url, payload=None, headers=None, timeout=60):
            sent.append(payload)
            return reply

        if name == "dawn":
            mod._post = lambda url, payload=None, headers=None, timeout=60: (
                sent.append(payload) or reply)
            out = mod.reply_to("what is this", [], images=IMG)
        else:
            mod._http = fake_http
            out = getattr(mod, fn)(mod.make_system_prompt(), [], "what is this", images=IMG)
    except Exception as exc:                          # noqa: BLE001
        check("%s: image reaches the wire" % name, False, "raised %r" % (exc,))
        sys.path.remove(str(d))
        continue
    finally:
        if str(d) in sys.path:
            sys.path.remove(str(d))

    payload = next((p for p in sent if isinstance(p, dict) and "messages" in p), None)
    if payload is None:
        payload = next((p for p in sent if isinstance(p, dict) and "contents" in p), None)
    if payload is None:
        check("%s: image reaches the wire" % name, False, "no captured payload")
        continue
    turns = payload.get("messages") or payload.get("contents") or []
    last = turns[-1]
    if provider == "openai":
        ok = (isinstance(last.get("content"), list)
              and any(b.get("type") == "image_url"
                      and b["image_url"]["url"].startswith("data:image/jpeg;base64,")
                      for b in last["content"]))
    elif provider == "anthropic":
        ok = (isinstance(last.get("content"), list)
              and any(b.get("type") == "image" and b["source"]["type"] == "base64"
                      and b["source"]["data"] == TINY for b in last["content"]))
    else:
        ok = any(p.get("inline_data", {}).get("mime_type") == "image/jpeg"
                 for p in (last.get("parts") or []))
    check("%s: image reaches the wire as a %s block" % (name, provider), ok,
          "last turn was %s" % json.dumps(last)[:180])
    check("%s: a reply still comes back" % name, bool(out), "out=%r" % (out,))

    # and the text-only turn is untouched: no image smuggled into it
    sent.clear()
    if name == "dawn":
        mod.reply_to("just text", [])
    else:
        getattr(mod, fn)(mod.make_system_prompt(), [], "just text")
    payload = next((p for p in sent if isinstance(p, dict)), None)
    turns = (payload.get("messages") or payload.get("contents") or []) if payload else []
    blob = json.dumps(turns[-1]) if turns else ""
    check("%s: text-only turn carries no image" % name,
          bool(turns) and "image_url" not in blob and "inline_data" not in blob
          and "base64" not in blob, "last turn %s" % blob[:140])
    if provider != "google":
        check("%s: text-only turn is still a plain string" % name,
              bool(turns) and isinstance(turns[-1].get("content"), str),
              "last turn %s" % blob[:140])

# ---- 5. the current turn is sent once ----------------------------------------
# Dawn's bot files the inbound to memory BEFORE any model call, deliberately: a failed
# reply must never be able to drop the human's words. `reply_to()` then appended the same
# text as a fresh turn as well, so every message reached the model twice — once from memory,
# once appended — and she answered as if he had said it twice. He caught it, not a test.
# This is that test: the current turn must appear once, and an image must ride on it.
dawn_dir = HOME / "Dawn" / "telegram"
if not (dawn_dir / "dawn-bot.py").is_file():
    skip("current turn is sent once", "~/Dawn/telegram not on this machine")
else:
    sent = []
    sys.path.insert(0, str(dawn_dir))
    try:
        mod = load_module(dawn_dir / "dawn-bot.py", "dawn_turn_check")
        mod._post = lambda url, payload=None, headers=None, timeout=60: (
            sent.append(payload) or {"choices": [{"message": {"content": "ok"}}]})
        mem = []
        mod.remember(mem, "user", "one message from me")
        mod.reply_to("one message from me", mod.history_for(mem))
        mod.remember(mem, "user", "with a picture [an image was sent: photo.jpg]")
        mod.reply_to("with a picture", mod.history_for(mem), images=IMG)
        # and a history that does NOT already contain the turn must still get it
        mod.reply_to("a brand new message", [])
    finally:
        if str(dawn_dir) in sys.path:
            sys.path.remove(str(dawn_dir))

    dups = 0
    for payload in sent:
        turns = [json.dumps(t.get("content"), sort_keys=True)
                 for t in payload.get("messages", [])]
        dups += sum(1 for i in range(1, len(turns)) if turns[i] == turns[i - 1])
    check("dawn: the current turn reaches the model once, not twice", dups == 0,
          "%d adjacent duplicate turn(s) across %d request(s)" % (dups, len(sent)))
    last = sent[-1]["messages"][-1]
    check("dawn: a turn filed earlier is still sent when memory does not hold it",
          last.get("content") == "a brand new message", "last turn %s" % json.dumps(last)[:120])
    img_last = sent[1]["messages"][-1]
    check("dawn: the image rides on the single current turn",
          isinstance(img_last.get("content"), list)
          and any(b.get("type") == "image_url" for b in img_last["content"]),
          "last turn %s" % json.dumps(img_last)[:140])

print()
print("%d check(s) failed" % len(fails) if fails else "all checks passed")
sys.exit(1 if fails else 0)
