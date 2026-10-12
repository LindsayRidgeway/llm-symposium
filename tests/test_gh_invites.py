#!/usr/bin/env python3
"""Offline tests for channels/gh_invites.py.

The facts these pin are from 2026-10-12: all five mailboxes received GitHub's
collaboration invitation, all five amigo mail loops answered it by email, and all
five answers bounced off noreply@github.com. The letters below are the real ones,
trimmed to the lines that carry meaning.
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("gh_invites", ROOT / "channels" / "gh_invites.py")
gh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gh)

CLAUDE_LETTER = """@LindsayRidgeway has invited you to collaborate on the LindsayRidgeway/llm-symposium repository.


Visit https://github.com/LindsayRidgeway/llm-symposium/invitations?invitation_token=8011c5ddc09fa9206238d56723c405f09d0ca81c to accept or decline this invitation.

You can also head over to https://github.com/LindsayRidgeway/llm-symposium to check out the repository or visit https://github.com/LindsayRidgeway to learn a bit more about @LindsayRidgeway.

This invitation will expire in 7 days.

Some helpful tips:
- If you get a 404 page, make sure you\u2019re signed in as claude.s.sonnet@gmail.com.
- Too many emails from @LindsayRidgeway? You can block them by visiting
  https://github.com/settings/blocked_users?block_user=LindsayRidgeway or report abuse at
  https://github.com/contact/report-abuse?report=LindsayRidgeway
"""

DESI_LETTER = """@LindsayRidgeway has invited you to collaborate on the LindsayRidgeway/llm-symposium repository.


Visit https://github.com/LindsayRidgeway/llm-symposium/invitations to accept or decline this invitation.

This invitation will expire in 7 days.

Some helpful tips:
- If you get a 404 page, make sure you\u2019re signed in as desi-s-amigo.
"""


class TestParsingTheLetter(unittest.TestCase):
    def test_a_letter_tied_to_an_address_names_the_address_and_carries_a_token(self):
        got = gh.parse_invitation(
            "LindsayRidgeway invited you to LindsayRidgeway/llm-symposium",
            CLAUDE_LETTER, from_addr="Lindsay <noreply@github.com>")
        self.assertEqual(got["repo"], "LindsayRidgeway/llm-symposium")
        self.assertEqual(got["address"], "claude.s.sonnet@gmail.com")
        self.assertEqual(got["token"], "8011c5ddc09fa9206238d56723c405f09d0ca81c")
        self.assertEqual(got["expires_days"], 7)

    def test_a_letter_tied_to_an_account_has_no_token_and_no_address(self):
        got = gh.parse_invitation(
            "LindsayRidgeway invited you to LindsayRidgeway/llm-symposium",
            DESI_LETTER, from_addr="Lindsay <noreply@github.com>")
        self.assertEqual(got["token"], "")
        self.assertEqual(got["address"], "")

    def test_a_letter_from_a_human_is_not_an_invitation(self):
        self.assertIsNone(gh.parse_invitation(
            "LindsayRidgeway invited you to LindsayRidgeway/llm-symposium",
            CLAUDE_LETTER, from_addr="Lindsay <ldridgeway@gmail.com>"))
        self.assertIsNone(gh.parse_invitation(
            "Lunch tomorrow?", "see you at noon", from_addr="noreply@github.com"))


class TestWhatCanBeAccepted(unittest.TestCase):
    def test_an_invitee_of_null_is_an_address_and_nobody_can_accept_it(self):
        got = gh.classify({"id": 1, "invitee": None, "permissions": "write"})
        self.assertEqual(got["verdict"], "no_account")
        self.assertIn("nothing to sign in as", got["means"])

    def test_an_account_invitee_says_who_can_accept_it(self):
        got = gh.classify({"id": 2, "invitee": {"login": "desi-s-amigo"}})
        self.assertEqual(got["verdict"], "account_exists")
        self.assertEqual(got["invitee"], "desi-s-amigo")

    def test_a_403_is_reported_as_cannot_see_not_as_nothing_pending(self):
        with mock.patch.object(gh, "api_get", return_value=(403, {"message": "Must have admin rights"})):
            invitations, note = gh.pending_invitations("owner/repo", token="x")
        self.assertEqual(invitations, [])
        self.assertIn("403", note)
        self.assertIn("not 'nothing pending'", note)

    def test_accept_refuses_an_invitation_no_account_can_take(self):
        listing = [{"id": 335802762, "invitee": None, "permissions": "write"}]
        with mock.patch.object(gh, "pending_invitations", return_value=(listing, "")), \
             mock.patch.object(gh, "gh_token", return_value=("tok", "")):
            accepted, refused = gh.accept("owner/repo", admin_token="admin")
        self.assertEqual(accepted, [])
        self.assertEqual(refused[0]["id"], 335802762)
        self.assertIn("nothing to sign in as", refused[0]["why"])

    def test_accept_is_done_with_the_invitee_s_credential_not_the_owner_s(self):
        listing = [{"id": 335813514, "invitee": {"login": "desi-s-amigo"}, "permissions": "write"}]
        seen = {}

        def fake_api(path, token, method="GET"):
            seen["path"], seen["token"], seen["method"] = path, token, method
            return 204, None

        with mock.patch.object(gh, "pending_invitations", return_value=(listing, "")), \
             mock.patch.object(gh, "gh_token", side_effect=lambda acct=None: ("desi-token", "")), \
             mock.patch.object(gh, "api_get", side_effect=fake_api):
            accepted, refused = gh.accept("owner/repo", admin_token="owner-token")
        self.assertEqual(accepted, [{"id": 335813514, "invitee": "desi-s-amigo"}])
        self.assertEqual(refused, [])
        self.assertEqual(seen["token"], "desi-token")
        self.assertEqual(seen["method"], "PATCH")
        self.assertEqual(seen["path"], "/user/repository_invitations/335813514")


class TestPairingLetterToInvitation(unittest.TestCase):
    def test_a_letter_a_second_away_from_the_invitation_is_paired_with_its_evidence(self):
        invitations = [{"id": 335802762, "created_at": "2026-10-02T13:57:55Z"}]
        mailed = [{"amigo": "claude", "address": "claude.s.sonnet@gmail.com",
                   "mailbox": "claude.s.sonnet@gmail.com",
                   "received_utc": "Fri, 02 Oct 2026 06:57:56 -0700"}]
        got = gh.pair_with_mail(invitations, mailed)[335802762]
        self.assertEqual(got["amigo"], "claude")
        self.assertEqual(got["address"], "claude.s.sonnet@gmail.com")
        self.assertLessEqual(got["gap_s"], 2)
        self.assertIn("vs invitation created", got["evidence"])

    def test_an_invitation_with_no_letter_near_it_is_reported_as_a_hole(self):
        invitations = [{"id": 1, "created_at": "2026-10-02T13:57:55Z"}]
        mailed = [{"amigo": "claude", "address": "claude.s.sonnet@gmail.com",
                   "received_utc": "Fri, 02 Oct 2026 09:00:00 -0700"}]
        got = gh.pair_with_mail(invitations, mailed)[1]
        self.assertEqual(got["amigo"], "")
        self.assertIn("no letter found", got["evidence"])


class TestTheRegister(unittest.TestCase):
    def _state(self, snapshot, rows):
        return {"repo": "owner/repo", "actor": "owner", "note": "",
                "snapshot": snapshot, "pending": rows}

    def test_the_register_appends_the_day_it_changes_and_not_the_days_it_does_not(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "gh-invitations.jsonl"
            first = self._state({"pending": [{"id": 1}]}, [{"id": 1}])
            self.assertTrue(gh.append_snapshot(first, path=path, actor="desi"))
            self.assertFalse(gh.append_snapshot(first, path=path, actor="desi"))
            changed = self._state({"pending": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}])
            self.assertTrue(gh.append_snapshot(changed, path=path, actor="desi"))
            lines = [json.loads(l) for l in path.read_text().splitlines()]
            self.assertEqual(len(lines), 2)
            self.assertEqual(lines[0]["actor"], "desi")
            self.assertTrue(lines[0]["checked_utc"].endswith("Z"))

    def test_the_printout_says_plainly_that_nobody_can_accept_and_why(self):
        state = {
            "repo": "owner/repo", "actor": "owner", "token_note": "", "checked_utc": gh.utcnow(),
            "mailed": [{"amigo": "claude", "address": "claude.s.sonnet@gmail.com",
                        "received_utc": "Fri, 02 Oct 2026 06:57:56 -0700", "token": "abc123"}],
            "rows": [{"id": 335802762, "created_at": "2026-10-02T13:57:55Z", "permissions": "write",
                      "invitee": None,
                      "classify": gh.classify({"id": 335802762, "invitee": None}),
                      "mail": {"amigo": "claude", "address": "claude.s.sonnet@gmail.com", "gap_s": 1}}],
        }
        out = gh.render(state)
        self.assertIn("pending on the repository: 1", out)
        self.assertIn("claude.s.sonnet@gmail.com", out)
        self.assertIn("no_account", out)
        self.assertIn("nothing to sign in as", out)
        self.assertIn("noreply@github.com", out)


class TestCredentials(unittest.TestCase):
    def test_a_mailbox_with_no_configured_pair_is_skipped_not_faked(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(gh.credentials_for("claude"))
            self.assertIsNone(gh.credentials_for("nobody"))

    def test_the_admin_account_is_named_rather_than_left_to_whatever_gh_defaults_to(self):
        self.assertEqual(gh.ADMIN_ACCOUNT, "LindsayRidgeway")

    def test_a_token_is_sought_for_the_named_account(self):
        calls = []

        class Done:
            returncode = 0
            stdout = "ghp_fake\n"
            stderr = ""

        def fake_run(cmd, **kw):
            calls.append(cmd)
            return Done()

        with mock.patch.dict("os.environ", {}, clear=True), \
             mock.patch.object(gh.subprocess, "run", side_effect=fake_run):
            token, why = gh.gh_token("LindsayRidgeway")
        self.assertEqual(token, "ghp_fake")
        self.assertEqual(why, "")
        self.assertIn("-u", calls[0])
        self.assertIn("LindsayRidgeway", calls[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
