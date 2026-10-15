#!/usr/bin/env python3
"""Tests for the unattended sign-in.

What is pinned here is the part that can be pinned without a password: that the tool reads
GitHub's refusal correctly and does not mistake one page for another. The distinction that
matters most is refusal versus progress — D-10 was closed "done" once while the credential
underneath it was broken, and a probe that cannot tell "wrong password" from "carry on"
would repeat that in a machine's voice, faster.

The tool's one safety property is also pinned: it does not store sessions. A flag that
promised to keep one open is refused outright rather than silently ignored.
"""
import pathlib
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.gh_signin import (  # noqa: E402
    describe_rows, load_ledger, main, save_ledger, seconds_until_next_step, session_ids,
    token, verdict, with_retries)

WRONG = '<div class="flash-error">Incorrect username or password.</div>'
TWO_FACTOR_FORM = '<form action="/sessions/two-factor"><input name="app_otp"></form>'
PROFILE = '<meta name="user-login" content="llm-symposium-machine">'


class TestToken(unittest.TestCase):
    def test_both_attribute_orders(self):
        self.assertEqual(token('<input name="authenticity_token" value="abc123">'), "abc123")
        self.assertEqual(token('<input value="abc123" name="authenticity_token">'), "abc123")

    def test_a_page_with_no_token_says_so(self):
        self.assertIsNone(token("<html><body>no form here</body></html>"))

    def test_it_does_not_invent_a_token_from_a_lookalike_field(self):
        self.assertIsNone(token('<input name="authenticity_token_x" value="abc">'))


class TestVerdict(unittest.TestCase):
    def test_a_refusal_is_a_refusal(self):
        self.assertEqual(verdict(WRONG, "https://github.com/session"), "WRONG_PASSWORD")

    def test_a_refusal_wins_over_everything_else(self):
        # A refusal page that also happens to mention two-factor must not read as progress.
        self.assertEqual(verdict(WRONG + TWO_FACTOR_FORM, "https://github.com/sessions/two-factor"),
                         "WRONG_PASSWORD")

    def test_the_two_factor_page_is_recognised_by_its_field_and_by_its_url(self):
        self.assertEqual(verdict(TWO_FACTOR_FORM, "https://github.com/sessions/two-factor"), "NEEDS_2FA")
        self.assertEqual(verdict("<html>enter the code</html>",
                                 "https://github.com/sessions/two-factor/app"), "NEEDS_2FA")

    def test_a_signed_in_page_is_recognised(self):
        self.assertEqual(verdict(PROFILE, "https://github.com/settings/profile"), "SIGNED_IN")
        self.assertEqual(verdict("<html>home</html>", "https://github.com/"), "SIGNED_IN")

    def test_an_unrecognised_page_is_not_called_success(self):
        self.assertEqual(verdict("<html>something new</html>", "https://github.com/oddity"), "UNKNOWN")

    def test_a_throttle_is_named_rather_than_retried(self):
        self.assertEqual(verdict("<h1>Too many attempts</h1>", "https://github.com/session"), "THROTTLED")

    def test_device_verification_is_not_mistaken_for_two_factor(self):
        self.assertEqual(verdict("<h1>Device verification</h1>", "https://github.com/sessions/verify"),
                         "NEEDS_DEVICE_VERIFICATION")


SESSIONS_PAGE = """
<a href="/settings/sessions/2358305052" class="btn btn-sm mt-1" aria-label="View details of
   session from Gaithersburg last accessed October 15, 2026">Details</a>
<a href="/settings/sessions/2358304330" class="btn btn-sm mt-1" aria-label="View details of
   session from Gaithersburg last accessed October 15, 2026">Details</a>
<a href="/settings/sessions/2358305052">Details again</a>
"""


class TestReadingTheSessionList(unittest.TestCase):
    def test_ids_are_found_once_each_in_page_order(self):
        self.assertEqual(session_ids(SESSIONS_PAGE), ["2358305052", "2358304330"])

    def test_ids_come_back_as_text_not_numbers(self):
        # A session id that lost its leading zero would name a different session.
        self.assertEqual(session_ids('<a href="/settings/sessions/0123">x</a>'), ["0123"])

    def test_rows_carry_a_place_and_a_date(self):
        rows = describe_rows(SESSIONS_PAGE)
        self.assertEqual(rows[0]["id"], "2358305052")
        self.assertEqual(rows[1]["place"], "Gaithersburg")
        self.assertEqual(rows[1]["last_accessed"], "October 15, 2026")

    def test_the_newest_is_the_largest_not_the_last_on_the_page(self):
        # Ours is the session the sign-in just made, and ids are issued in order.
        ids = session_ids('<a href="/settings/sessions/9000000009">a</a>'
                          '<a href="/settings/sessions/2358305052">b</a>')
        self.assertEqual(max(ids, key=int), "9000000009")


class TestReplayProtection(unittest.TestCase):
    """GitHub refuses a code it has already accepted. Waiting for the next step is the fix —
    the same seed, the same arithmetic, a code GitHub has never seen."""

    def test_the_wait_lands_in_the_next_step(self):
        for now, expected in ((0.0, 31), (10.0, 21), (29.0, 2), (29.9, 1), (30.0, 31), (600.0, 31)):
            self.assertEqual(seconds_until_next_step(now), expected, msg=f"at {now}")

    def test_the_wait_is_always_positive(self):
        for now in (0.0, 1.0, 15.5, 29.999, 30.0, 59.5):
            self.assertGreater(seconds_until_next_step(now), 0)


class TestTheLedger(unittest.TestCase):
    """The ledger is what stops a session being forgotten. It must survive junk, because the
    failure mode of trusting a bad line is a revoke request for an id that is not ours."""

    def setUp(self):
        self.dir = pathlib.Path(tempfile.mkdtemp())
        self.path = self.dir / "gh-web-sessions"

    def test_a_missing_ledger_is_an_empty_ledger(self):
        self.assertEqual(load_ledger(self.path), [])

    def test_what_is_saved_is_what_is_read(self):
        save_ledger(["2358313800", "2358300759"], self.path)
        self.assertEqual(load_ledger(self.path), ["2358313800", "2358300759"])

    def test_the_ledger_is_not_world_readable(self):
        save_ledger(["2358313800"], self.path)
        self.assertEqual(oct(self.path.stat().st_mode)[-3:], "600")

    def test_junk_lines_are_ignored_not_obeyed(self):
        self.path.write_text("2358313800\n\nnot-an-id\n../../etc/passwd\n2358313800\n")
        self.assertEqual(load_ledger(self.path), ["2358313800"])

    def test_ids_keep_their_digits(self):
        # A session id is a string, not a number: 0123 and 123 are different sessions.
        save_ledger(["0123"], self.path)
        self.assertEqual(load_ledger(self.path), ["0123"])

    def test_an_empty_ledger_writes_no_stray_blank(self):
        save_ledger([], self.path)
        self.assertEqual(self.path.read_text(), "")


class TestRetryingADroppedConnection(unittest.TestCase):
    """A dropped read is not an answer. This machine's network has stranded two of them today."""

    def test_a_transient_failure_is_retried(self):
        calls = []

        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise TimeoutError("read timed out")
            return "answer"

        slept = []
        self.assertEqual(with_retries(flaky, attempts=3, pause=0.01, sleep=slept.append), "answer")
        self.assertEqual(len(calls), 3)
        self.assertEqual(slept, [0.01, 0.01])

    def test_a_real_http_status_is_not_retried(self):
        calls = []

        def refused():
            calls.append(1)
            raise urllib.error.HTTPError("u", 422, "no", {}, None)

        with self.assertRaises(urllib.error.HTTPError):
            with_retries(refused, attempts=3, sleep=lambda _: None)
        self.assertEqual(len(calls), 1)


class TestItRefusesToStoreSessions(unittest.TestCase):
    def test_keep_open_is_refused_loudly(self):
        with self.assertRaises(SystemExit) as caught:
            main(["prove", "--keep-open"])
        self.assertIn("not implemented", str(caught.exception))

    def test_the_tool_signs_out_by_default_without_opening_anything(self):
        # `prove` is the default precisely because it opens no session: the password test
        # must not be the reason the account gains a device it cannot name.
        source = (REPO / "scripts" / "gh_signin.py").read_text()
        self.assertIn('default="prove"', source)
        self.assertIn("save_ledger", source)
        self.assertNotIn("_keep_open_hack", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
