#!/usr/bin/env python3
"""The agenda a wake is told to pick from must be inside the agenda a wake can see.

Every wake is handed `channels/agenda.md` truncated to its first 3,500 characters — the
`text[:3500]` slice in each amigo's `local_tick.py` — and the same instruction says "each run
picks exactly ONE item below". Measured on 2026-10-17: the file was 269,785 characters, the
first item heading sat at offset 7,002, and the 3,500-character window held prose only —
**0 of 57 numbered headings**. So the sentence "pick one item below" pointed at text that
was never delivered, on every wake, since the truncation was introduced. No wake could have
noticed from inside: an absent list looks exactly like a list you were not meant to need.

The fix is in `scripts/compile_agenda.py`, not in the bots (the bot files are not this
checkout's to edit): the compiled index now opens with a bounded one-line-per-item digest,
so the list lands where the window falls. This guard is what keeps that true — it fails if
the digest grows past the window, if an item stops appearing in it, or if the digest ever
drifts below the preamble again.

Run: python3 tests/test_wake_context_caps.py
"""

import os
import re
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import compile_agenda  # noqa: E402

INDEX = os.path.join(REPO, "channels", "agenda.md")
AGENDA = os.path.join(REPO, "agenda")

# What the bots hand the wake. If a bot's cap changes, change it here too — the two numbers
# are one fact and this file is where the repo records it.
WINDOW = 3500


def _read(path):
    with open(path, encoding="utf8") as fh:
        return fh.read()


def _item_files():
    return sorted(f for f in os.listdir(AGENDA)
                  if re.match(r"^\d\d-", f) and f.endswith(".md") and not f.startswith("00-"))


def _heading_title(text):
    for line in text.splitlines():
        if line.startswith("## "):
            return re.sub(r"^\d+\.\s*", "", line[3:].strip())
    return None


class AgendaDigestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = _read(INDEX)
        cls.window = cls.index[:WINDOW]
        cls.digest_rows = [l for l in cls.window.splitlines() if l.startswith("- **")]

    def test_the_window_constant_matches_the_compiler(self):
        """A guard that measures a different window than the one the bots use is theatre."""
        self.assertEqual(compile_agenda.WINDOW, WINDOW,
                         "compile_agenda.WINDOW no longer matches the cap the bots apply "
                         "(text[:3500] in each local_tick.py) — one of the two must be fixed")
        self.assertLess(compile_agenda.DIGEST_BUDGET, WINDOW,
                        "the digest budget must leave room for the generated-file banner")

    def test_every_item_is_named_inside_the_window(self):
        """The point of the whole thing: the list the wake is told to pick from, delivered."""
        numbers = [re.match(r"^(\d+)-", f).group(1) for f in _item_files()]
        self.assertGreaterEqual(len(numbers), 5, "agenda/ holds fewer than five items — "
                                                 "the scan is blind, not the file empty")
        seen = {m.group(1) for m in (re.match(r"^- \*\*(\d+)\*\*", l) for l in self.digest_rows) if m}
        missing = [n for n in numbers if n not in seen]
        self.assertEqual(missing, [], "item(s) never named in the first %d characters of "
                                      "channels/agenda.md: %s" % (WINDOW, missing))

    def test_every_item_title_is_readable_inside_the_window(self):
        """A number alone does not let a wake choose; the clipped title has to be there."""
        missing = []
        for f in _item_files():
            title = _heading_title(_read(os.path.join(AGENDA, f)))
            if not title:
                continue
            if compile_agenda._clip(title, compile_agenda.TITLE_MAX) not in self.window:
                missing.append(f)
        self.assertEqual(missing, [], "item title(s) cut out of the wake window: %s" % missing)

    def test_the_digest_comes_before_the_preamble(self):
        """The defect was ordering, not size alone: the preamble is 7,002 characters and the
        window is 3,500, so anything after the preamble is unreachable."""
        digest_at = self.index.find("## Every item, one line each")
        preamble_at = self.index.find("**Why this file exists.**")
        self.assertNotEqual(digest_at, -1, "the digest block is gone from channels/agenda.md")
        if preamble_at != -1:
            self.assertLess(digest_at, preamble_at,
                            "the digest sits after the preamble again — it would be invisible")

    def test_the_digest_fits_with_headroom(self):
        """Bounded, so the next item adopted does not push the list out of the window."""
        start = self.index.find("## Every item, one line each")
        end = self.index.find("\n\n", start)
        length = end - start if end != -1 else len(self.index) - start
        self.assertLessEqual(start + length, WINDOW,
                             "the digest ends at character %d, past the %d-character window"
                             % (start + length, WINDOW))
        self.assertLessEqual(length, compile_agenda.DIGEST_BUDGET,
                             "digest is %d characters, budget is %d"
                             % (length, compile_agenda.DIGEST_BUDGET))

    def test_the_index_is_in_sync_with_its_sources(self):
        out = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "compile_agenda.py"),
                              "--check"], capture_output=True, text=True, cwd=REPO, timeout=120)
        self.assertEqual(out.returncode, 0,
                         "channels/agenda.md is stale — run scripts/compile_agenda.py\n%s\n%s"
                         % (out.stdout, out.stderr))


if __name__ == "__main__":
    unittest.main(verbosity=2)
