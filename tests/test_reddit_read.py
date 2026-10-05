#!/usr/bin/env python3
"""Offline tests for scripts/reddit_read.py — the politely-spaced Reddit Atom reader.

Why this test exists: on 2026-10-05 the Reddit block was measured to be *not* the User-Agent,
and the Atom feeds were found to be the one working read route (and a fragile, rate-limited
one). The two things that must not silently regress are therefore:

  1. the reader must never request the `.json` API -- that is exactly the request shape Reddit
     refuses with 403, so a well-meaning "just add raw_json=1" edit would break it;
  2. it must make exactly one request and treat 429 as "wait", not as a thing to retry, because
     a retry loop is what extends the lockout (measured: 5 fast requests -> 429 on all 5).

Everything here runs with no network: the transport is injected.
"""

import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

import reddit_read as rr  # noqa: E402

ATOM_FIXTURE = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>subreddit</title>
  <entry>
    <title>Type any town's name and see its actual temperature record</title>
    <link href="https://www.reddit.com/r/InternetIsBeautiful/comments/abc123/x/" />
    <updated>2026-10-05T00:00:00+00:00</updated>
    <author><name>/u/someone</name></author>
  </entry>
  <entry>
    <title>A second post</title>
    <link href="https://www.reddit.com/r/InternetIsBeautiful/comments/def456/y/" />
    <updated>2026-10-04T00:00:00+00:00</updated>
    <author><name>/u/other</name></author>
  </entry>
</feed>
"""


class FakeResponse:
    def __init__(self, status, body):
        self.status = status
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeHTTPError(Exception):
    pass


class GuardTests(unittest.TestCase):
    """The reader must only ever ask for an Atom feed -- never the .json API."""

    def test_builds_room_atom_url(self):
        self.assertEqual(
            rr.build_url("room", "InternetIsBeautiful"),
            "https://www.reddit.com/r/InternetIsBeautiful/new/.rss",
        )

    def test_builds_user_atom_url(self):
        self.assertEqual(
            rr.build_url("user", "thelambie"),
            "https://www.reddit.com/user/thelambie/submitted.rss",
        )

    def test_refuses_json_api(self):
        # A caller trying to "fix" the 403 by hitting the API gets a refusal, not a request.
        with self.assertRaises(ValueError):
            rr.assert_atom("https://www.reddit.com/r/InternetIsBeautiful/new.json")

    def test_refuses_non_reddit_host(self):
        with self.assertRaises(ValueError):
            rr.assert_atom("https://example.com/r/x/.rss")

    def test_refuses_multi_segment_target(self):
        with self.assertRaises(ValueError):
            rr.build_url("room", "a/b")


class UaTests(unittest.TestCase):
    """The agent string is courtesy, not the fix -- but it must stay declared, not generic."""

    def test_ua_declares_itself(self):
        self.assertIn("llm-symposium", rr.USER_AGENT)
        self.assertNotIn("python-urllib", rr.USER_AGENT.lower())
        self.assertNotIn("Mozilla", rr.USER_AGENT)


class FetchTests(unittest.TestCase):
    def test_sends_declared_ua_and_accepts_atom(self):
        seen = {}

        def opener(req, timeout=25):
            seen["ua"] = req.get_header("User-agent")
            seen["url"] = req.full_url
            return FakeResponse(200, ATOM_FIXTURE)

        status, body = rr.fetch(rr.build_url("room", "InternetIsBeautiful"), opener=opener)
        self.assertEqual(status, 200)
        self.assertEqual(seen["ua"], rr.USER_AGENT)
        self.assertTrue(seen["url"].endswith(".rss"))

    def test_429_is_reported_not_raised(self):
        import urllib.error

        def opener(req, timeout=25):
            raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", {}, io.BytesIO(b""))

        status, body = rr.fetch(rr.build_url("user", "thelambie"), opener=opener)
        self.assertEqual(status, 429)

    def test_403_is_reported_not_raised(self):
        import urllib.error

        def opener(req, timeout=25):
            raise urllib.error.HTTPError(req.full_url, 403, "Blocked", {}, io.BytesIO(b""))

        status, body = rr.fetch(rr.build_url("room", "InternetIsBeautiful"), opener=opener)
        self.assertEqual(status, 403)


class ParseTests(unittest.TestCase):
    def test_parses_entries(self):
        entries = rr.parse_entries(ATOM_FIXTURE)
        self.assertEqual(len(entries), 2)
        self.assertIn("temperature record", entries[0]["title"])
        self.assertTrue(entries[0]["link"].startswith("https://www.reddit.com/r/"))
        self.assertEqual(entries[0]["updated"], "2026-10-05T00:00:00+00:00")


class MainTests(unittest.TestCase):
    def _run(self, argv, status, body=b""):
        calls = []

        def opener(req, timeout=25):
            calls.append(req.full_url)
            return FakeResponse(status, body)

        original = rr.fetch
        rr.fetch = lambda url, **kw: original(url, opener=opener)
        try:
            out, err = io.StringIO(), io.StringIO()
            old = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = out, err
            try:
                code = rr.main(argv)
            finally:
                sys.stdout, sys.stderr = old
        finally:
            rr.fetch = original
        return code, out.getvalue(), err.getvalue(), calls

    def test_one_request_only_on_success(self):
        code, out, err, calls = self._run(["--user", "thelambie"], 200, ATOM_FIXTURE)
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)  # exactly one request; never a loop
        self.assertIn("2 entries", out)

    def test_429_exits_3_with_wait_message(self):
        code, out, err, calls = self._run(["--room", "InternetIsBeautiful"], 429)
        self.assertEqual(code, 3)
        self.assertEqual(len(calls), 1)
        self.assertIn("rate-limited", err)
        self.assertIn("do not rerun in a loop", err)

    def test_json_flag_emits_json(self):
        code, out, err, calls = self._run(["--user", "thelambie", "--json"], 200, ATOM_FIXTURE)
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
