#!/usr/bin/env python3
"""Pin the Reddit read route, and pin the two things it must never do.

Written 2026-10-08 with `scripts/fetch_reddit.py`, after a live probe settled a
question the task ledger had assumed the other way. The probe, from this machine:

  * `/.json`  -> HTTP 403 to a bare python agent, the commons' byline, AND a real
    Chrome User-Agent alike, all three byte-identical (189,908 bytes, text/html).
    The block is shape-based; no header removes it. So the test below asserts the
    tool REWRITES a `.json` URL to `.rss` rather than asking for JSON and failing.
  * `/.rss`   -> HTTP 200 with the declared byline where the bare agent got 429.
    So the declared byline IS load-bearing, and the test pins that it is present.
  * a second request right after a 200 returned 429 with
    `x-ratelimit-remaining: 0`. So the test pins the 429 path: the tool raises a
    clear refusal and calls the opener exactly ONCE — no retry loop.

Fully offline: the opener is stubbed, so nothing here touches the network.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import fetch_reddit as fr  # noqa: E402


class BylineTests(unittest.TestCase):
    def test_byline_names_the_commons_and_points_somewhere(self):
        self.assertIn("llm-symposium", fr.USER_AGENT)
        self.assertIn("github.com", fr.USER_AGENT)

    def test_byline_never_pretends_to_be_a_browser(self):
        # The CAPTCHA refusal in different clothes: we do not look like a person.
        self.assertNotIn("Mozilla", fr.USER_AGENT)
        self.assertNotIn("Chrome", fr.USER_AGENT)
        self.assertNotIn("Safari", fr.USER_AGENT)


class UrlTests(unittest.TestCase):
    def test_subreddit_shorthand(self):
        self.assertEqual(fr.feed_url("r/russian"), "https://www.reddit.com/r/russian/.rss")

    def test_user_shorthand(self):
        self.assertEqual(
            fr.feed_url("u/thelambie"),
            "https://www.reddit.com/user/thelambie/.rss",
        )

    def test_bare_name_is_a_subreddit(self):
        self.assertEqual(
            fr.feed_url("LearnRussian"), "https://www.reddit.com/r/LearnRussian/.rss"
        )

    def test_the_closed_json_route_is_rewritten_not_requested(self):
        # Measured 2026-10-08: .json is 403 to every agent. Asking for it is a
        # guaranteed failure, so the tool translates to the route that works.
        self.assertEqual(
            fr.feed_url("https://www.reddit.com/r/russian/.json"),
            "https://www.reddit.com/r/russian/.rss",
        )


class ParserTests(unittest.TestCase):
    SAMPLE = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom">'
        "<entry><author><name>/u/example</name></author>"
        "<title>A post</title>"
        '<link rel="alternate" href="https://www.reddit.com/r/russian/x"/>'
        "<updated>2026-10-08T22:38:14+00:00</updated></entry>"
        "<entry><author><name>/u/second</name></author>"
        "<title>Another</title>"
        '<link rel="alternate" href="https://www.reddit.com/r/russian/y"/>'
        "<updated>2026-10-07T01:00:00+00:00</updated></entry>"
        "</feed>"
    )

    def test_entries_are_extracted_in_order(self):
        rows = fr.parse_atom(self.SAMPLE)
        self.assertEqual([r["title"] for r in rows], ["A post", "Another"])
        self.assertEqual(rows[0]["author"], "/u/example")
        self.assertTrue(rows[1]["link"].endswith("/r/russian/y"))


class _Resp:
    def __init__(self, body):
        self._body = body

    def read(self):
        return self._body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FetchTests(unittest.TestCase):
    def test_one_request_carries_the_byline_and_no_retry(self):
        opener = mock.Mock(return_value=_Resp("<feed/>"))
        fr.fetch("https://www.reddit.com/r/russian/.rss", opener=opener)
        self.assertEqual(opener.call_count, 1)
        req = opener.call_args[0][0]
        self.assertEqual(req.get_header("User-agent"), fr.USER_AGENT)

    def test_429_refuses_once_and_does_not_loop(self):
        import urllib.error

        headers = {"Retry-After": "5", "x-ratelimit-remaining": "0"}
        err = urllib.error.HTTPError(
            "https://www.reddit.com/r/russian/.rss", 429, "Too Many Requests", headers, None
        )
        opener = mock.Mock(side_effect=err)
        with self.assertRaises(fr.RedditRefused) as ctx:
            fr.fetch("https://www.reddit.com/r/russian/.rss", opener=opener)
        self.assertIn("429", str(ctx.exception))
        self.assertEqual(opener.call_count, 1)  # asked once; retrying is how a limit becomes a ban

    def test_403_on_json_names_the_shape_block(self):
        import urllib.error

        err = urllib.error.HTTPError(
            "https://www.reddit.com/r/x/.json", 403, "Forbidden", {}, None
        )
        with self.assertRaises(fr.RedditRefused) as ctx:
            fr.fetch("https://www.reddit.com/r/x/.json", opener=mock.Mock(side_effect=err))
        self.assertIn("shape-based", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
