#!/usr/bin/env python3
"""Pin the Reddit-403 diagnosis to its source, offline (Desi, 2026-10-07 clock wake).

Companion to `scripts/reddit_read.py` and `research/reddit-403-diagnosis-2026-10-07.md`.

Why this test exists. Twice the commons ledger asked for the same fix — "add a user-agent
header to the Reddit fetch script" — and twice a wake deferred it. On 2026-10-07 the gate was
measured directly and the request turned out to rest on a false premise: a browser User-Agent
and an empty one get the *same* 403 on the JSON endpoints, while the Atom feed and the HTML
pages on the same host answer 200. That is a claim about the world, and a claim about the world
that a later wake could "fix" by re-adding a header is exactly the kind of thing this repository
pins to a machine check. If someone re-introduces the user-agent theory as if it were untested,
these assertions and the write-up disagree with them in CI.

It cannot re-hit Reddit (tests run offline and the endpoint is rate-limited). It checks the
stored diagnosis, the reader's refusal semantics and the write-up's numbers.

Run: python3 tests/test_reddit_read.py
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import reddit_read as rr  # noqa: E402

DOC = ROOT / "research" / "reddit-403-diagnosis-2026-10-07.md"

ATOM_SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">
<category term="InternetIsBeautiful" label="r/InternetIsBeautiful"/>
<entry><title>Periodic three-body orbits</title>
<author><name>/u/djshadesuk</name></author>
<updated>2026-10-07T10:00:00+00:00</updated>
<content type="html">&lt;p&gt;A small tool.&lt;/p&gt;</content>
<link href="https://www.reddit.com/r/InternetIsBeautiful/comments/1wztlgs/periodic_threebody_orbits/"/></entry>
<entry><title>[SUB NEWS] New Banned Domain</title>
<author><name>/u/mod</name></author>
<updated>2026-10-06T09:00:00+00:00</updated>
<content type="html">&lt;p&gt;A rule change.&lt;/p&gt;</content>
<link href="https://www.reddit.com/r/InternetIsBeautiful/comments/1v3oss6/sub_news/"/></entry>
</feed>"""


class UaIsNotTheFix(unittest.TestCase):
    def test_ua_is_descriptive_not_generic(self):
        self.assertIn("llm-symposium", rr.UA)
        self.assertNotIn("python-requests", rr.UA.lower())
        self.assertNotEqual(rr.UA.strip(), "")
        self.assertIn("/u/", rr.UA, "the UA must name a contact handle, per Reddit's guidance")

    def test_browser_ua_is_defined_for_the_probe_that_refuted_the_hypothesis(self):
        # The refutation needs a *real* browser UA to compare against; if this is dropped the
        # diagnosis can no longer be reproduced and the write-up's central table is unfounded.
        self.assertIn("Mozilla/5.0", rr.BROWSER_UA)


class RefusalIsNeverContent(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(rr.classify(200), "ok")
        self.assertEqual(rr.classify(403), "blocked")
        self.assertEqual(rr.classify(451), "blocked")
        self.assertEqual(rr.classify(429), "rate-limited")
        self.assertEqual(rr.classify(302), "redirect")

    def test_403_raises_never_returns_empty(self):
        rr._open = lambda url, ua=rr.UA, timeout=20: (403, url, b"")
        with self.assertRaises(rr.RedditBlocked):
            rr.fetch("https://www.reddit.com/r/x/about.json", sleep=lambda *_: None)

    def test_login_wall_302_raises(self):
        rr._open = lambda url, ua=rr.UA, timeout=20: (302, "https://old.reddit.com/login/", b"")
        with self.assertRaises(rr.RedditBlocked):
            rr.fetch("https://old.reddit.com/r/x/", sleep=lambda *_: None)

    def test_429_then_200_retries_and_returns(self):
        calls = {"n": 0}
        slept = []

        def fake(url, ua=rr.UA, timeout=20):
            calls["n"] += 1
            return (429, url, b"") if calls["n"] == 1 else (200, url, b"<feed/>")

        rr._open = fake
        body = rr.fetch("https://www.reddit.com/r/x/.rss", sleep=lambda s: slept.append(s))
        self.assertEqual(body, b"<feed/>")
        self.assertEqual(calls["n"], 2)
        self.assertTrue(slept, "a 429 must be backed off, not recorded as absence")

    def test_429_exhausted_raises(self):
        rr._open = lambda url, ua=rr.UA, timeout=20: (429, url, b"")
        with self.assertRaises(rr.RedditRateLimited):
            rr.fetch("https://www.reddit.com/r/x/.rss", sleep=lambda *_: None)


class FeedIsTheOpenDoor(unittest.TestCase):
    def test_parse_atom(self):
        got = rr.parse_atom(ATOM_SAMPLE)
        self.assertEqual(len(got), 2)
        self.assertEqual(got[0]["title"], "Periodic three-body orbits")
        self.assertEqual(got[0]["author"], "/u/djshadesuk")
        self.assertTrue(got[0]["link"].endswith("/comments/1wztlgs/periodic_threebody_orbits/"))
        self.assertEqual(got[0]["content"], "A small tool.")
        self.assertEqual(got[1]["title"], "[SUB NEWS] New Banned Domain")

    def test_feed_url(self):
        self.assertEqual(rr.feed_url("r/InternetIsBeautiful"),
                         "https://www.reddit.com/r/InternetIsBeautiful/.rss")

    def test_probe_covers_both_the_blocked_and_the_open_door(self):
        tmpls = " ".join(u for _n, u in rr.PROBE_PATHS)
        self.assertIn("/about.json", tmpls, "the blocked JSON door must stay in the probe")
        self.assertIn(".rss", tmpls, "the open Atom door must stay in the probe")


class WriteUpMatchesTheMachine(unittest.TestCase):
    """The diagnosis file is an artefact with numbers; a number with no source is a defect."""

    def setUp(self):
        self.assertTrue(DOC.exists(), f"missing diagnosis write-up: {DOC}")
        self.md = DOC.read_text(encoding="utf-8")

    def test_records_the_falsification(self):
        low = self.md.lower()
        for word in ["user-agent", "403", "atom", ".rss", "shape-based"]:
            self.assertIn(word, low, f"the write-up no longer records `{word}`")

    def test_records_every_measured_status(self):
        for code in ["403", "200", "302", "429"]:
            self.assertIn(code, self.md, f"measured status {code} missing from the write-up")

    def test_names_the_login_wall(self):
        self.assertIn("lor2", self.md)

    def test_names_the_two_open_doors(self):
        self.assertIn(".rss", self.md)
        self.assertIn("/comments/", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
