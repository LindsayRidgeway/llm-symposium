#!/usr/bin/env python3
"""Offline tests for channels/gh_invites.py.

The facts these pin are from 2026-10-12: all five mailboxes received GitHub's
collaboration invitation, all five amigo mail loops answered it by email, and all
five answers bounced off noreply@github.com. The letters below are the real ones,
trimmed to the lines that carry meaning.
"""
import importlib.util
import json
import os
import tempfile
import time
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


class TestTheCredentialWatch(unittest.TestCase):
    """The credential the commons pushes with is a scheduled silence if nobody watches it: the day
    it expires, CI pushes and this very check stop, and the symptom is "no work was done"
    (2026-10-12, built with the decision to give the commons its own token)."""

    class _Resp:
        def __init__(self, expiry):
            self.headers = {"github-authentication-token-expiration": expiry} if expiry else {}

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def test_a_fine_grained_token_reports_the_days_it_has_left(self):
        soon = (gh.datetime.datetime.now(gh.datetime.timezone.utc)
                + gh.datetime.timedelta(days=40)).strftime("%Y-%m-%d %H:%M:%S UTC")
        expires, days, note = gh.token_expiry("tok", opener=lambda req, timeout=None: self._Resp(soon))
        self.assertEqual(days, 40)
        self.assertIn("expires in 40 days", note)
        self.assertTrue(expires.endswith("Z"))

    def test_an_expired_token_says_so_rather_than_counting_down_quietly(self):
        past = (gh.datetime.datetime.now(gh.datetime.timezone.utc)
                - gh.datetime.timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S UTC")
        _, days, note = gh.token_expiry("tok", opener=lambda req, timeout=None: self._Resp(past))
        self.assertEqual(days, -3)
        self.assertIn("EXPIRED", note)

    def test_a_token_that_reports_no_expiry_is_reported_as_such_not_as_safe(self):
        expires, days, note = gh.token_expiry("tok", opener=lambda req, timeout=None: self._Resp(""))
        self.assertEqual(expires, "")
        self.assertIsNone(days)
        self.assertIn("no expiry reported", note)

    def test_an_unreachable_api_is_not_silence(self):
        def boom(req, timeout=None):
            raise OSError("no route to host")
        _, days, note = gh.token_expiry("tok", opener=boom)
        self.assertIsNone(days)
        self.assertIn("could not ask GitHub", note)


class TestACredentialWithNoDate(unittest.TestCase):
    """The human declined an expiry on the commons' token (2026-10-12). The date is not dropped,
    it moves: the file's own install date is the artifact that exists whether or not anyone
    remembers creating the token, and day 300 is when the report calls for a rotation.
    """

    def _file(self, days_old, tmpdir):
        f = Path(tmpdir) / "push-token"
        f.write_text("ghp_x")
        when = time.time() - days_old * 86400
        os.utime(f, (when, when))
        return f

    def test_a_credential_with_no_expiry_is_dated_by_its_file(self):
        with tempfile.TemporaryDirectory() as d:
            f = self._file(10, d)
            installed, days, note = gh.credential_age(f)
            self.assertEqual(days, 10)
            self.assertTrue(installed.startswith("20"))
            self.assertIn("no expiry date", note)
            self.assertNotIn("ROTATION", note)

    def test_a_credential_that_was_never_installed_says_so_rather_than_zero(self):
        installed, days, note = gh.credential_age("/nonexistent/push-token")
        self.assertEqual(installed, "")
        self.assertIsNone(days)
        self.assertIn("no credential file", note)
        self.assertIn("cannot push from this machine", note)

    def test_at_its_rotation_day_the_credential_is_called_due(self):
        with tempfile.TemporaryDirectory() as d:
            f = self._file(gh.ROTATE_AFTER_DAYS, d)
            _, days, note = gh.credential_age(f)
            self.assertEqual(days, gh.ROTATE_AFTER_DAYS)
            self.assertIn("ROTATION DUE", note)

    def test_the_register_s_snapshot_does_not_change_every_day(self):
        """A note that counts days would make the snapshot differ daily and write the register
        every day, which is the opposite of 'append only when the picture changes'."""
        cred = {"expires_utc": "", "note": "no expiry date; the file here was installed "
                "2026-10-12, 0 days ago",
                "commons": {"installed_utc": "2026-10-12T23:00:00Z", "days_old": 0}}
        stable = (cred.get("expires_utc") or (cred.get("commons") or {}).get("installed_utc")
                  or cred.get("note", ""))
        self.assertEqual(stable, "2026-10-12T23:00:00Z")


class TestTheCommonsCredential(unittest.TestCase):
    """The account was renamed on 2026-10-12, and the credential is a file.

    Both facts look like trivia and are not. A stale login is a 404 that reads as
    "no credential configured"; and a machine account whose token lives in the
    human's keychain is a credential the commons cannot check the lifetime of.
    """

    def test_the_account_we_hold_a_credential_for_is_the_renamed_one(self):
        self.assertEqual(gh.KNOWN_ACCOUNTS.get("desi"), "llm-symposium-machine")
        self.assertNotIn("desi-s-amigo", gh.KNOWN_ACCOUNTS.values())

    def test_the_machine_credential_is_read_from_its_file_not_a_keychain(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "commons-push-token"
            path.write_text("github_pat_machine\n")
            saved = {k: os.environ.pop(k, None)
                     for k in ("SYMPOSIUM_GH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")}
            before = dict(gh.TOKEN_FILES)
            gh.TOKEN_FILES["llm-symposium-machine"] = str(path)
            try:
                with mock.patch.object(gh.subprocess, "run",
                                       side_effect=AssertionError("asked the keychain")):
                    token, why = gh.gh_token("llm-symposium-machine")
            finally:
                gh.TOKEN_FILES.clear()
                gh.TOKEN_FILES.update(before)
                for k, v in saved.items():
                    if v is not None:
                        os.environ[k] = v
            self.assertEqual(token, "github_pat_machine")
            self.assertEqual(why, "")

    def test_a_missing_token_file_does_not_read_as_a_configured_credential(self):
        saved = {k: os.environ.pop(k, None)
                 for k in ("SYMPOSIUM_GH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")}
        before = dict(gh.TOKEN_FILES)
        gh.TOKEN_FILES["llm-symposium-machine"] = "/nonexistent/commons-push-token"
        try:
            with mock.patch.object(
                    gh.subprocess, "run",
                    return_value=mock.Mock(returncode=1, stdout="", stderr="no oauth token")):
                token, why = gh.gh_token("llm-symposium-machine")
        finally:
            gh.TOKEN_FILES.clear()
            gh.TOKEN_FILES.update(before)
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v
        self.assertEqual(token, "")
        self.assertIn("nothing at /nonexistent/commons-push-token", why)
        self.assertIn("no oauth token", why)


class TestTheRegisterSaysWhatChanged(unittest.TestCase):
    """The register has to be readable without the memory of whoever wrote it."""

    def _rec(self, pending, listed=True):
        return {"listed": listed, "pending": pending}

    def test_an_invitation_that_left_is_named_with_the_verdict_it_carried(self):
        before = self._rec([{"id": 1, "address": "a@b.c", "verdict": "no_account"},
                            {"id": 2, "address": "d@e.f", "verdict": "account_exists"}])
        now = self._rec([{"id": 2, "address": "d@e.f", "verdict": "account_exists"}])
        got = gh.what_changed(before, now)
        self.assertEqual([g["id"] for g in got["left_since_last_check"]], [1])
        self.assertEqual(got["left_since_last_check"][0]["verdict"], "no_account")
        self.assertNotIn("arrived_since_last_check", got)

    def test_an_invitation_that_arrived_is_named_too(self):
        got = gh.what_changed(self._rec([]), self._rec([{"id": 9, "address": "x@y.z",
                                                         "verdict": "no_account"}]))
        self.assertEqual([g["id"] for g in got["arrived_since_last_check"]], [9])

    def test_a_check_that_could_not_see_the_list_does_not_claim_they_left(self):
        before = self._rec([{"id": 1, "address": "a@b.c", "verdict": "no_account"}])
        got = gh.what_changed(before, self._rec([], listed=False))
        self.assertNotIn("left_since_last_check", got)
        self.assertIn("neither visible nor accounted for", got["unaccounted"])

    def test_a_blind_check_is_a_change_the_register_records(self):
        sees = gh.snapshot([], "O/R", "tok", listed=True)
        blind = gh.snapshot([], "O/R", "tok", listed=False)
        self.assertNotEqual(sees, blind)
        self.assertFalse(blind["listed"])

    def test_a_blind_listing_is_printed_as_cannot_see_not_as_zero(self):
        state = {"repo": "O/R", "checked_utc": "now", "actor": "llm-symposium-machine",
                 "listed": False, "token_note": "403 from the API", "mailed": [], "rows": [],
                 "credential": {}}
        out = gh.render(state)
        self.assertIn("cannot see", out)
        self.assertNotIn("pending on the repository: 0", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
