#!/usr/bin/env python3
"""Offline tests for the Telegram channel (channels/telegram.py).

No network: exercises token resolution, no-op behavior, and the send/poll
helpers against a stubbed HTTP layer.
"""
import os
import sys
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import channels.telegram as tg  # noqa: E402


def _clear():
    return mock.patch.dict(os.environ, {}, clear=True)


def test_configured_false_without_tokens():
    with _clear():
        assert tg.configured() is False


def test_configured_true_with_desi_token():
    with _clear():
        os.environ["TELEGRAM_BOT_TOKEN_DESI"] = "123:abc"
        assert tg.configured() is True


def test_configured_true_with_generic_token():
    with _clear():
        os.environ["TELEGRAM_BOT_TOKEN"] = "123:abc"
        assert tg.configured() is True


def test_run_noop_without_tokens():
    with _clear():
        assert tg.run_telegram_channel() is None  # prints no-op, returns


def test_get_updates_parses_response():
    with _clear():
        os.environ["TELEGRAM_BOT_TOKEN_DESI"] = "123:abc"

        class _Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return b'{"ok":true,"result":[{"update_id":1,"message":{"text":"hi","chat":{"id":42},"from":{"first_name":"Lindsay"}}}]}'

        with mock.patch.object(tg.urllib.request, "urlopen", return_value=_Resp()):
            updates = tg.get_updates("123:abc")
        assert len(updates) == 1
        assert updates[0]["message"]["text"] == "hi"


def test_send_message_posts():
    with _clear():
        class _Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return b'{"ok":true,"result":{"message_id":1}}'

        calls = []
        with mock.patch.object(
            tg.urllib.request, "urlopen", side_effect=lambda *a, **k: calls.append(a) or _Resp()
        ):
            ok = tg.send_message("123:abc", 42, "hello")
        assert ok is True
        assert "sendMessage" in calls[0][0].full_url


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as e:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {e}")
    print(f"\n{6 - failures}/6 tests passed")
    sys.exit(1 if failures else 0)
