#!/usr/bin/env python3
"""Tests for the daily report's display rules.

The human asked for shorter item names (2026-10-06), pointing at the old COBOL paragraph-name
budget of ~30 characters, and for the postponed list to stay truncated *provided the total is still
shown*. Both are display promises about a report he reads on a phone, so both are pinned here —
along with the one thing that must never be cut, which is the count.
"""
import contextlib
import datetime as dt
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import scripts.daily_report as dr_mod  # noqa: E402
from channels import item_ledger as il  # noqa: E402
from scripts.daily_report import AMIGO_ORDER, DISPLAY_TITLE, _bucket, _short, render  # noqa: E402


class TestInputBuckets(unittest.TestCase):
    """The classification of inbound mail. The human added this section because he wants to know
    what the world sends us, so the only bucket that carries that meaning has to be hard to enter:
    miscounting a robot or the founder as an outsider would inflate the one number that matters."""

    def test_the_founder_is_not_outside_the_commons(self):
        self.assertEqual(_bucket("Lindsay Ridgeway <ldridgeway@gmail.com>", "Incoming", "inbox"),
                         "human")

    def test_an_amigo_writing_to_an_amigo_is_not_outside(self):
        self.assertEqual(_bucket("<dmitri.s.pravdin@gmail.com>", "hi", "inbox"), "ours")

    def test_our_own_newsletter_service_is_not_outside(self):
        self.assertEqual(_bucket("Amigo <llm_symposium@buttondown.email>", "You're in!", "inbox"),
                         "ours")

    def test_a_robot_address_is_a_robot(self):
        for frm in ("GitHub <noreply@github.com>", "<postmaster@microsoft.com>",
                    "Mail Delivery Subsystem <mailer-daemon@googlemail.com>"):
            self.assertEqual(_bucket(frm, "something", "inbox"), "automated", frm)

    def test_an_auto_acknowledgement_is_a_robot_even_from_a_real_organisation(self):
        # Both of these are real: MIT Technology Review and Retraction Watch, replies to our
        # outreach. A report that counted them as people would say the world was answering us.
        self.assertEqual(_bucket("MIT Technology Review <feedback@technologyreview.com>",
                                 "Re: Story idea", "inbox",
                                 "Thank you! We thrive on reader feedback, and we appreciate "
                                 "hearing from you. ... we'll be in touch within one business day."),
                         "automated")
        self.assertEqual(
            _bucket('"Retraction Watch" <team@retractionwatch.com>', "Re: checker", "inbox",
                    "Thank you for your message. ... because of the high volume we receive we "
                    "cannot always respond."),
            "automated")
        self.assertEqual(_bucket('"Retraction Watch" <team@retractionwatch.com>',
                                 "Thank you for your message Re: checker", "inbox"), "automated")

    def test_a_person_writing_from_outside_is_the_only_thing_that_counts(self):
        self.assertEqual(
            _bucket("Peter Blake <petermblake96@gmail.com>",
                    "Re: An AI wrote you a letter", "inbox",
                    "I got word from Lindsay, who is paying for all of this..."),
            "world")

    def test_a_bounce_is_a_bounce(self):
        self.assertEqual(_bucket("postmaster@microsoft.com", "Undeliverable", "bounce"), "bounce")


class TestTitles(unittest.TestCase):
    """Titles are written by a model, not cut by a regex (the human, 2026-10-06). These pin the
    parts that must hold without a network: the cleanup of the model's answer, and the report's
    preference for a written title over a truncated description."""

    def test_quotes_and_trailing_punctuation_are_stripped(self):
        from channels.titles import clean
        self.assertEqual(clean('"Dirty tree blocked all pushes".'), "Dirty tree blocked all pushes")
        self.assertEqual(clean("  `Email replier ignored robots`  "), "Email replier ignored robots")

    def test_an_overlong_answer_is_cut_on_a_word_boundary_within_budget(self):
        from channels.titles import MAX_TITLE, clean
        out = clean("This answer is far too long to be a title at all, honestly it just rambles on")
        self.assertLessEqual(len(out), MAX_TITLE)
        self.assertFalse(out.endswith(" "))

    def test_a_written_title_is_preferred_over_the_truncated_description(self):
        from scripts.daily_report import _name
        rec = {"title": "I fixed the bug that made the commons' email replier answer robot messages",
               "short_title": "Fixed robot email replies"}
        self.assertEqual(_name(rec), "Fixed robot email replies")

    def test_an_untitled_item_still_renders(self):
        from scripts.daily_report import _name
        rec = {"title": "I fixed the bug that made the commons' email replier answer robot messages"}
        self.assertTrue(_name(rec))
        self.assertLessEqual(len(_name(rec)), DISPLAY_TITLE + 1)


class TestShortName(unittest.TestCase):
    def test_a_long_title_is_cut_to_a_glance(self):
        t = ("I fixed the bug that made the commons' email replier answer robot messages and send "
             "pointless replies — the same fault that sent eight junk replies")
        self.assertLessEqual(len(_short(t)), DISPLAY_TITLE)
        self.assertTrue(_short(t).endswith("…"))

    def test_first_person_leads_are_dropped(self):
        self.assertTrue(_short("I sent the two follow-up emails that were overdue to both groups, "
                               "each written to three weeks ago").startswith("sent the two"))
        self.assertTrue(_short("I am fixing a flaw in our chat processor so messages are not "
                               "processed twice").startswith("fixing a flaw"))

    def test_the_cut_lands_on_a_word_boundary(self):
        out = _short("I checked the pile of review branches that hold finished work which never "
                     "reached the main repository")
        self.assertNotIn("…", out.rstrip("…")[-1:])   # no partial word before the ellipsis
        self.assertFalse(out.endswith(" …"))

    def test_a_short_title_is_left_alone(self):
        self.assertEqual(_short("I broke Telegram"), "broke Telegram")
        self.assertEqual(_short(""), "")


class TestReportShape(unittest.TestCase):
    def test_the_six_letters_are_reported_and_the_identity_is_printed(self):
        out = render(hours=24)
        for letter in ("N", "V", "A", "P", "W", "R"):
            self.assertIn(f"{letter}=", out, letter)
        self.assertIn("N+V=A+P+W+R", out)
        self.assertNotIn("U=", out)          # the human retired U on 2026-10-06

    def test_the_waiting_total_survives_truncation(self):
        # He accepted a truncated list *as long as the total is still shown* (2026-10-06), and the
        # waiting list is now the one that grows.
        out = render(hours=24)
        self.assertIn("Waiting for review", out)
        self.assertIn("showing", out)
        self.assertIn("oldest shown first", out)

    def test_the_accomplished_split_is_never_hidden(self):
        # A is one letter with two causes: a review, or the lander's test gate. The human's whole
        # complaint on 2026-10-08 was reading A=0 as "nothing accomplished".
        out = render(hours=24)
        self.assertIn("by a review", out)
        self.assertIn("by the lander's test gate", out)

    def test_the_postponed_and_waiting_sections_are_separate(self):
        out = render(hours=24)
        self.assertIn("### Postponed by a decision", out)
        self.assertIn("### Waiting for review", out)


class TestDiagnosis(unittest.TestCase):
    """The two readings he asked for by name: is the drain running, and is N = P. Both are read
    off the same counts, so both are pinned here rather than left to the number looking right."""

    def _diag(self, rows, hours=24, now=None):
        from scripts.daily_report import _diagnosis
        window = il.counts(rows, hours)
        life = il.counts(rows, None)
        return "\n".join(_diagnosis(window, life, hours, rows,
                                    now or dt.datetime.now(dt.timezone.utc)))

    def _row(self, i, filed, state=None, **kw):
        return {"id": i, "amigo": "desi", "scope": "internal", "state": state,
                "filed_utc": filed, "title": i, **kw}

    def test_arrivals_with_no_decisions_reads_as_a_broken_drain(self):
        now = dt.datetime.now(dt.timezone.utc)
        filed = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = {f"r{i}": self._row(f"r{i}", filed) for i in range(3)}
        out = self._diag(rows, now=now)
        self.assertIn("STOPPED", out)
        self.assertIn("Δ(V−W) +0", out)
        self.assertIn("ΔW +3", out)

    def test_a_decision_taken_makes_the_drain_nonzero(self):
        now = dt.datetime.now(dt.timezone.utc)
        filed = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = {"a": self._row("a", filed, "accomplished", state_utc=filed, reviewer="gemini"),
                "b": self._row("b", filed)}
        out = self._diag(rows, now=now)
        self.assertIn("Δ(V−W) +1", out)
        self.assertNotIn("STOPPED", out)

    def test_equal_nonzero_totals_say_the_criteria_are_broken(self):
        rows = {"a": self._row("a", "2026-01-01T00:00:00Z", None,
                               no_review_reason="a ledger row"),
                "b": self._row("b", "2026-01-01T00:00:00Z", "postponed",
                               reason="needs access")}
        out = self._diag(rows)
        self.assertIn("N=1 P=1 — EQUAL — the criteria are broken", out)

    def test_two_zeros_are_called_vacuous_rather_than_broken(self):
        rows = {"a": self._row("a", "2026-01-01T00:00:00Z")}
        out = self._diag(rows)
        self.assertIn("vacuously", out)
        self.assertNotIn("EQUAL — the criteria are broken", out)

    def test_dwell_is_computed_only_when_something_has_drained(self):
        # His instruction (2026-10-07): compute dwell only if V−W > 0, because if V=W the answer is
        # already an identity and dwell is dead weight.
        drained = {"a": self._row("a", "2026-09-01T00:00:00Z", "accomplished",
                                  state_utc="2026-09-01T00:00:00Z", reviewer="gemini"),
                   "b": self._row("b", "2026-09-15T00:00:00Z")}
        self.assertIn("dwell:", self._diag(drained))
        nothing_drained = {"b": self._row("b", "2026-09-15T00:00:00Z")}
        self.assertIn("dwell: not computed", self._diag(nothing_drained))


class TestTheReviewBlock(unittest.TestCase):
    """The human's 2026-10-09 questions: does W carry names, and what is actually blocking.

    Three things he asked to see, and none of them are derivable from the letters: whether the
    waiting pile has names on it at all (a nameless W is the defect, not the backlog), who is
    carrying it, and the list of items that left W *without* being accomplished, with the reason.
    """

    def _block(self, rows, hours=24):
        from channels.item_ledger import counts
        from scripts.daily_report import _review_block
        return "\n".join(_review_block(rows, counts(rows, hours), hours))

    def _row(self, i, **kw):
        row = {"id": i, "amigo": "desi", "scope": "internal", "filed_utc": "2026-10-01T00:00:00Z",
               "title": i, "state": None}
        row.update(kw)
        return row

    def test_a_named_waiting_item_is_reported_by_name(self):
        rows = {"a": self._row("a", assigned_to="dmitri")}
        self.assertIn("dmitri 1", self._block(rows))

    def test_a_queue_with_no_names_says_that_is_the_defect(self):
        rows = {"a": self._row("a")}
        out = self._block(rows)
        self.assertIn("carries no names at all", out)
        self.assertIn("not the pile size", out)

    def test_a_nameless_item_is_reported_as_a_hole_not_a_queue(self):
        rows = {"a": self._row("a"), "b": self._row("b", assigned_to="gemini")}
        out = self._block(rows)
        self.assertIn("1 waiting item(s) have NO name", out)
        self.assertIn("hole, not a queue", out)

    def test_no_holes_is_stated_plainly(self):
        rows = {"a": self._row("a", assigned_to="gemini")}
        self.assertIn("no holes", self._block(rows))

    def test_the_band_is_printed_with_its_price_date(self):
        out = self._block({"a": self._row("a", assigned_to="gemini")})
        self.assertIn("cheap band (prices", out)

    def test_an_item_that_left_w_without_being_done_carries_its_reason(self):
        now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = {"a": self._row("a", state="postponed", reason="needs the lab's access",
                               state_utc=now)}
        out = self._block(rows)
        self.assertIn("Blockers: left W in the last 24h without being accomplished (1)", out)
        self.assertIn("because: needs the lab's access", out)

    def test_an_empty_blocker_list_is_said_out_loud(self):
        rows = {"a": self._row("a", assigned_to="gemini")}
        self.assertIn("(none — nothing left W by decision in this window)", self._block(rows))

    def test_a_blocker_from_before_the_window_is_not_counted(self):
        rows = {"a": self._row("a", state="postponed", reason="old",
                               state_utc="2026-09-01T00:00:00Z")}
        self.assertIn("(none — nothing left W", self._block(rows))


class TestTheInvitationsBlock(unittest.TestCase):
    """Repository invitations arrived in every mailbox, were answered by every amigo, and every
    answer bounced (2026-10-12). Two facts have to survive into the report: that the invitations
    are to addresses nobody can sign in as, and that the check itself is running at all — a
    register nobody reads is the same defect one level up.
    """

    def _block(self, records, now=None):
        import json as _json
        import datetime as _dt
        import tempfile as _tf
        from scripts.daily_report import _invitations_block
        with _tf.TemporaryDirectory() as td:
            p = Path(td) / "gh-invitations.jsonl"
            p.write_text("\n".join(_json.dumps(r) for r in records) + "\n", encoding="utf-8")
            return "\n".join(_invitations_block(
                now or _dt.datetime(2026, 10, 12, 15, 0, tzinfo=_dt.timezone.utc), path=p))

    def _record(self, checked="2026-10-12T14:00:00Z", pending=None):
        return {"checked_utc": checked, "actor": "LindsayRidgeway",
                "snapshot": {"pending": pending or []}, "pending": pending or []}

    def test_a_register_that_has_never_run_says_so_rather_than_showing_zero(self):
        from scripts.daily_report import _invitations_block
        out = "\n".join(_invitations_block(path=Path("/nonexistent/gh-invitations.jsonl")))
        self.assertIn("no check has ever run", out)

    def test_an_invitation_no_account_can_accept_is_reported_as_such(self):
        out = self._block([self._record(pending=[
            {"id": 335802762, "verdict": "no_account", "amigo": "claude",
             "address": "claude.s.sonnet@gmail.com"}])])
        self.assertIn("1 pending", out)
        self.assertIn("claude", out)
        self.assertIn("no_account", out)
        self.assertIn("invitation to an ADDRESS", out)
        self.assertIn("only the human can change that", out)

    def test_a_check_that_stopped_running_is_called_stale(self):
        out = self._block([self._record(checked="2026-10-01T00:00:00Z")])
        self.assertIn("STALE", out)

    def _credential_file(self, days_old, tmpdir):
        import os as _os
        import time as _time
        f = Path(tmpdir) / "push-token"
        f.write_text("ghp_x")
        when = _time.time() - days_old * 86400
        _os.utime(f, (when, when))
        return f

    def _with_credential(self, records, days_old):
        import tempfile as _tf
        from unittest import mock
        from scripts import daily_report as dr
        records = [dict(r, credential=r.get("credential") or {"note": "no expiry reported"})
                   for r in records]
        with _tf.TemporaryDirectory() as td:
            f = self._credential_file(days_old, td)
            with mock.patch.object(dr, "CREDENTIAL_FILE", f):
                return self._block(records)

    def test_a_credential_with_no_expiry_is_dated_by_its_file(self):
        """The date is not dropped when the expiry is: it moves to the file, which is the
        artifact that exists whether or not anyone remembers creating the token."""
        out = self._with_credential([self._record()], 10)
        self.assertIn("the file here was installed", out)
        self.assertIn("10 days ago", out)
        self.assertNotIn("ROTATION DUE", out)

    def test_at_day_300_the_report_calls_for_a_rotation(self):
        out = self._with_credential([self._record()], 300)
        self.assertIn("300 days ago", out)
        self.assertIn("ROTATION DUE", out)
        self.assertIn("never has to stop working", out)

    def test_a_credential_file_that_is_not_there_is_not_invented(self):
        import tempfile as _tf
        from unittest import mock
        from scripts import daily_report as dr
        with _tf.TemporaryDirectory() as td:
            with mock.patch.object(dr, "CREDENTIAL_FILE", Path(td) / "nope"):
                out = self._block([self._record()])
        self.assertNotIn("the file here was installed", out)
        self.assertNotIn("ROTATION DUE", out)


class TestTheReportCommitsItsOwnOutput(unittest.TestCase):
    """The lander refuses a dirty shared checkout, so output left uncommitted here is an outage,
    not untidiness: nothing landed between 2026-10-06 and 2026-10-08 for exactly this reason, and
    for 1.5 days before that. Pin that the report commits its own paths — only its own — and that
    a git failure is reported and survived."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        from scripts.daily_report import REPO
        self.repo = REPO
        self.ledger = Path(self.dir.name) / "items.jsonl"
        self.ledger.write_text("{}\n", encoding="utf-8")
        self.calls = []

    def _commit(self, run, *paths, message="report(daily): the day's counts, sent"):
        from scripts.daily_report import _commit_own_outputs
        real = dr_mod.subprocess.run
        dr_mod.subprocess.run = run
        try:
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                _commit_own_outputs(list(paths), message)
            return buf.getvalue()
        finally:
            dr_mod.subprocess.run = real

    def test_it_stages_and_commits_the_paths_it_is_given(self):
        def run(argv, **kw):
            self.calls.append(argv)
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        self._commit(run, self.ledger)
        self.assertEqual(self.calls[0], ["git", "add", "--", str(self.ledger)])
        self.assertEqual(self.calls[1][:4], ["git", "commit", "-q", "-m"])

    def test_it_never_stages_a_path_it_was_not_given(self):
        # A session's uncommitted writing must never be swept into the report's commit.
        def run(argv, **kw):
            self.calls.append(argv)
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        self._commit(run, self.ledger)
        for argv in self.calls:
            if argv[1] == "add":
                self.assertEqual(argv[3:], [str(self.ledger)])

    def test_a_path_that_does_not_exist_is_not_staged(self):
        def run(argv, **kw):
            self.calls.append(argv)
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        self._commit(run, Path(self.dir.name) / "not-written.md")
        self.assertEqual(self.calls, [])

    def test_a_git_failure_is_reported_and_survived(self):
        def run(argv, **kw):
            raise subprocess.CalledProcessError(1, argv, stderr="index.lock exists")
        out = self._commit(run, self.ledger)
        self.assertIn("WARNING", out)
        self.assertIn("landing is blocked", out)

    def test_nothing_to_commit_is_not_a_warning(self):
        def run(argv, **kw):
            return SimpleNamespace(returncode=1, stdout="nothing to commit, working tree clean",
                                   stderr="")
        out = self._commit(run, self.ledger)
        self.assertNotIn("WARNING", out)


class TestFocusBlock(unittest.TestCase):
    """The report answers two questions and no more (the human, 2026-10-14).

    He said the report "tries to answer more questions than I have right now", and asked instead for
    two blocks: by amigo, items performed; by amigo, items reviewed — five lines and a total each,
    all of it in one window. Four promises are pinned here, because a scoreboard is only useful if it
    is complete, adds up, and is all the same period: five names always appear, each total is the sum
    of its five lines, each heading says aloud which window it means, and nothing outside that window
    appears. One label over two populations is what made the old report unreadable — 23 items were
    filed in its "last 24h" and 172 moved in the same words.
    """

    @classmethod
    def setUpClass(cls):
        cls.text = dr_mod.render_focus(24)
        cls.lines = cls.text.splitlines()

    def _block(self, heading):
        i = next(n for n, l in enumerate(self.lines) if heading in l)
        return self.lines[i + 1:i + 7]

    def test_both_headings_name_their_window(self):
        # Every figure in the message comes from one window, and each heading says so, so a reader
        # never has to work out which period a number belongs to.
        self.assertEqual(self.text.count("the last 24 hours"), 2)

    def test_both_blocks_name_all_five_amigos_even_at_zero(self):
        for heading in ("Items finished, by amigo", "Items reviewed, by amigo"):
            named = [line.split()[0] for line in self._block(heading)[:5]]
            self.assertEqual(named, list(AMIGO_ORDER), heading)

    def test_each_total_is_the_sum_of_its_five_lines(self):
        for heading in ("Items finished, by amigo", "Items reviewed, by amigo"):
            block = self._block(heading)
            counts = [int(line.split()[1]) for line in block[:5]]
            total = int(block[5].split()[1])
            self.assertEqual(sum(counts), total, heading)

    def test_the_block_is_only_the_window_it_claims(self):
        # He asked for the last 24 hours. A lifetime figure anywhere in the message is a defect,
        # not a bonus: printing one period's number beside another's is exactly what made the old
        # report unreadable, and the first draft of this block did it again.
        self.assertNotIn("lifetime", self.text)
        self.assertNotIn("ever", self.text)

    def test_there_is_no_third_section(self):
        # Two questions, two blocks. A third heading is how the report grew past what he asked for.
        headings = [line for line in self.lines if line.startswith("**") and "amigo**" in line]
        self.assertEqual(len(headings), 2, headings)


if __name__ == "__main__":
    unittest.main(verbosity=2)
