"""Tests for scripts/ledger_watch.py — the daily check that repairs what a refused landing ate.

The point of these tests is the two judgements that are easy to get wrong and expensive to get wrong
in production: which verdict to believe when an item was reviewed twice, and how to tell a patch
that carried a verdict from one that carried only prose.
"""

import datetime as dt
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "channels"))

import item_ledger as il  # noqa: E402

spec = importlib.util.spec_from_file_location("ledger_watch", REPO / "scripts" / "ledger_watch.py")
lw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lw)


class ChooseVerdictTest(unittest.TestCase):
    def test_two_reviews_of_one_item_keep_the_first_real_one(self):
        """The 2026-10-22 loop: reviewed at 05:16, verdict lost to the landing gate, reviewed again
        at 09:17, and the second wake wrote 'postponed: review already written'. The first verdict
        is the record; the second is evidence of the loop."""
        cands = [
            ("20261022T051617Z", {"state": "accomplished",
                                  "reason": "Reviewed against the primary reference; run 20261021T231529Z-859769d9"}),
            ("20261022T091715Z", {"state": "postponed",
                                  "reason": "Review already written, not missing: run 20261022T051617Z changed"}),
        ]
        stamp, rec = lw.choose_verdict(cands)
        self.assertEqual(stamp, "20261022T051617Z")
        self.assertEqual(rec["state"], "accomplished")

    def test_a_later_genuine_postponement_wins_when_nothing_was_accomplished(self):
        cands = [
            ("20261020T031124Z", {"state": "postponed", "reason": "awaiting the vendor's manual"}),
            ("20261020T131245Z", {"state": "postponed", "reason": "still no manual; asked vendor again"}),
        ]
        stamp, rec = lw.choose_verdict(cands)
        self.assertEqual(stamp, "20261020T131245Z")

    def test_an_accomplished_verdict_that_names_no_work_does_not_outrank_a_named_one(self):
        cands = [
            ("20261019T000000Z", {"state": "accomplished", "reason": "looked at it"}),
            ("20261019T010000Z", {"state": "accomplished", "reason": "wrote research/x.md, run 20261019T010000Z"}),
        ]
        stamp, _ = lw.choose_verdict(cands)
        self.assertEqual(stamp, "20261019T010000Z")


class PatchParsingTest(unittest.TestCase):
    def _write(self, text: str) -> Path:
        tmp = Path(tempfile.mkdtemp()) / "changes.patch"
        tmp.write_text(text, encoding="utf-8")
        return tmp

    def test_terminal_rows_are_read_out_of_a_refused_patch(self):
        row = {"id": "abc", "state": "accomplished", "reviewer": "desi", "reason": "run 20261021T131453Z-x"}
        patch = self._write("diff --git a/channels/items.jsonl b/channels/items.jsonl\n"
                            f"+{json.dumps(row)}\n")
        rows = lw.verdict_rows_in_patch(patch)
        self.assertEqual([r["id"] for r in rows], ["abc"])

    def test_a_patch_touching_no_ledger_returns_nothing(self):
        patch = self._write("diff --git a/docs/music/index.html b/docs/music/index.html\n+x\n")
        self.assertEqual(lw.verdict_rows_in_patch(patch), [])

    def test_a_ledger_patch_that_only_assigns_returns_nothing(self):
        row = {"id": "abc", "assigned_to": "dmitri", "assign_reason": "drawn"}
        patch = self._write("diff --git a/channels/items.jsonl b/channels/items.jsonl\n"
                            f"+{json.dumps(row)}\n")
        self.assertEqual(lw.verdict_rows_in_patch(patch), [])

    def test_a_removed_line_is_not_a_verdict_added(self):
        row = {"id": "abc", "state": "accomplished", "reviewer": "desi", "reason": "run 1"}
        patch = self._write("diff --git a/channels/items.jsonl b/channels/items.jsonl\n"
                            f"-{json.dumps(row)}\n")
        self.assertEqual(lw.verdict_rows_in_patch(patch), [])


class VerdictRuleTest(unittest.TestCase):
    def test_meeting_the_rule_is_a_pass(self):
        m = {"queue": 12, "arrivals_24h": 23, "pile": 0, "model_decisions_24h": 0}
        passes, reasons = lw.verdict(m, None)
        self.assertTrue(passes)
        self.assertIn("one day of arrivals", reasons[0])

    def test_an_empty_day_still_counts_as_one_arrival_not_zero(self):
        """A day with no filings must not make the rule 'queue <= 0', which nothing can pass."""
        m = {"queue": 1, "arrivals_24h": 0, "pile": 0, "model_decisions_24h": 0}
        passes, _ = lw.verdict(m, None)
        self.assertTrue(passes)

    def test_a_growing_queue_fails_and_says_by_how_much(self):
        m = {"queue": 72, "arrivals_24h": 23, "pile": 228, "pile_read_24h": 4,
             "model_decisions_24h": 1}
        passes, reasons = lw.verdict(m, {"queue": 58, "pile": 227})
        self.assertFalse(passes)
        self.assertIn("72 waiting against 23", " ".join(reasons))
        self.assertIn("up 14", " ".join(reasons))

    def test_a_flat_unread_pile_fails_even_when_the_queue_passes(self):
        """2026-10-25: 29 waiting, 263 finished and unread, and the check said PASS.

        The queue rule was met — W was emptier than a day of arrivals — while more than half the
        ledger had never been read. A check that measures the small pile and reports it as the whole
        is worse than no check, because it certifies the wrong thing.
        """
        m = {"queue": 12, "arrivals_24h": 27, "pile": 269, "pile_read_24h": 0,
             "model_decisions_24h": 20}
        passes, reasons = lw.verdict(m, {"queue": 12, "pile": 268})
        self.assertFalse(passes)
        self.assertIn("nobody has read", reasons[0])

    def test_a_shrinking_unread_pile_passes_the_second_rule(self):
        m = {"queue": 12, "arrivals_24h": 27, "pile": 240, "pile_read_24h": 30,
             "model_decisions_24h": 30}
        passes, reasons = lw.verdict(m, {"queue": 12, "pile": 269})
        self.assertTrue(passes, reasons)

    def test_merely_knowing_the_pile_is_not_progress(self):
        # smaller by four, nothing read: the drop is filing noise, not reading
        m = {"queue": 12, "arrivals_24h": 27, "pile": 265, "pile_read_24h": 0,
             "model_decisions_24h": 20}
        passes, _ = lw.verdict(m, {"queue": 12, "pile": 269})
        self.assertFalse(passes)


class CommitGuardTest(unittest.TestCase):
    """The guard added 2026-10-25, after this script committed a half-merged ledger to main.

    The 07:45 run's `git pull --rebase` conflicted, the note said "measured what is here", and the
    commit went up with three marker lines and a stale conflict block in `channels/items.jsonl`.
    Nothing failed: the ledger skips unreadable lines and under-reports, so the queue was quietly
    wrong rather than loudly broken.
    """

    def test_a_conflicted_block_in_a_diff_is_caught(self):
        diff = (
            "+++ b/channels/items.jsonl\n"
            "+<<<<<<< HEAD\n"
            '+{"id": "a"}\n'
            "+=======\n"
            '+{"id": "b"}\n'
            "+>>>>>>> 53d61095 (rover: voice loop)\n"
        )
        self.assertEqual(len(lw.markers_in_patch(diff)), 3)

    def test_an_ordinary_row_that_contains_equals_signs_is_not_a_marker(self):
        diff = (
            "--- a/channels/items.jsonl\n"
            "+++ b/channels/items.jsonl\n"
            '+{"id": "x", "title": "a ======= b"}\n'
            "+<!-- not a marker -->\n"
        )
        self.assertEqual(lw.markers_in_patch(diff), [])

    def test_only_added_lines_count_so_an_old_red_tree_does_not_freeze_commits(self):
        """A marker already in the tree is somebody else's problem to repair; blocking on it
        would stop every commit forever instead of the one commit that introduced it."""
        diff = "-<<<<<<< HEAD\n--- a/f\n+++ b/f\n+clean\n"
        self.assertEqual(lw.markers_in_patch(diff), [])

    def test_an_unfinished_rebase_is_named(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".git" / "rebase-merge").mkdir(parents=True)
            self.assertEqual(lw.unmerged_state(root), "rebase-merge")

    def test_an_unfinished_merge_is_named(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".git").mkdir()
            (root / ".git" / "MERGE_HEAD").write_text("0" * 40)
            self.assertEqual(lw.unmerged_state(root), "MERGE_HEAD")

    def test_a_clean_checkout_reports_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".git").mkdir()
            self.assertIsNone(lw.unmerged_state(root))


class SyncWithoutRebaseTest(unittest.TestCase):
    """The 07:45 run of 2026-10-25 synced with `pull --rebase --autostash`. It stopped on the first
    of 58 commits, committed the conflicted tree, and left the shared checkout mid-rebase for two
    and a half hours; every landing in every body failed behind it.

    These tests pin the replacement: fast-forward only, never a rebase, and a diverged checkout is
    named and left alone rather than half-reconciled.
    """

    def _git(self, cwd, *args):
        return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)

    def _pair(self, root: Path):
        """A bare origin and one clone of it with one commit on main."""
        origin = root / "origin.git"
        work = root / "work"
        self._git(root, "init", "-q", "--bare", "-b", "main", str(origin))
        self._git(root, "clone", "-q", str(origin), str(work))
        for k, v in (("user.name", "t"), ("user.email", "t@e")):
            self._git(work, "config", k, v)
        (work / "f.txt").write_text("one\n")
        self._git(work, "add", "-A")
        self._git(work, "commit", "-q", "-m", "one")
        self._git(work, "push", "-q", "-u", "origin", "main")
        return origin, work

    def _other_writer(self, origin: Path, root: Path, text: str):
        """A second clone that pushes a commit, i.e. the cloud wake moving origin on."""
        other = root / "other"
        self._git(root, "clone", "-q", str(origin), str(other))
        for k, v in (("user.name", "o"), ("user.email", "o@e")):
            self._git(other, "config", k, v)
        (other / "f.txt").write_text(text)
        self._git(other, "add", "-A")
        self._git(other, "commit", "-q", "-m", "theirs")
        self._git(other, "push", "-q", "origin", "main")

    def test_a_checkout_only_behind_is_fast_forwarded_and_says_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            origin, work = self._pair(root)
            self._other_writer(origin, root, "one\ntwo\n")
            self.assertEqual(lw.sync_checkout(work), "")
            self.assertEqual((work / "f.txt").read_text(), "one\ntwo\n")

    def test_a_diverged_checkout_is_named_and_left_alone_never_rebased(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            origin, work = self._pair(root)
            (work / "mine.txt").write_text("mine\n")          # not pushed: ahead
            self._git(work, "add", "-A")
            self._git(work, "commit", "-q", "-m", "mine")
            head = self._git(work, "rev-parse", "HEAD").stdout.strip()
            self._other_writer(origin, root, "theirs\n")      # and behind
            note = lw.sync_checkout(work)
            self.assertIn("1 commit(s) ahead of and 1 behind", note)
            self.assertEqual(self._git(work, "rev-parse", "HEAD").stdout.strip(), head,
                             "sync_checkout moved HEAD on a diverged checkout")
            self.assertFalse((work / ".git" / "rebase-merge").exists(), "a rebase was started")
            self.assertFalse((work / ".git" / "MERGE_HEAD").exists(), "a merge was started")

    def test_an_unfinished_rebase_is_ended_before_anything_is_measured(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            origin, work = self._pair(root)
            self._git(work, "checkout", "-q", "-b", "side")
            (work / "f.txt").write_text("side\n")
            self._git(work, "commit", "-q", "-am", "side")
            self._git(work, "checkout", "-q", "main")
            (work / "f.txt").write_text("main\n")
            self._git(work, "commit", "-q", "-am", "main")
            self._git(work, "rebase", "side")                 # stops: real conflict, real state
            self.assertTrue((work / ".git" / "rebase-merge").exists())
            lw.sync_checkout(work)
            self.assertFalse((work / ".git" / "rebase-merge").exists(),
                             "the unfinished rebase was left in place")

    def test_a_detached_checkout_is_recognised(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            origin, work = self._pair(root)
            self.assertFalse(lw.detached(work))
            self._git(work, "checkout", "-q", "--detach", "HEAD")
            self.assertTrue(lw.detached(work))


class WholeRepoReview(unittest.TestCase):
    """2026-10-29: the human noticed the four discussions/*-review.md files had not changed since
    2026-09-07..09-24, and nothing had replaced them. The ledger reviews one item at a time and a
    queue of items cannot see a shape. So the review is now an item, filed weekly and named by the
    ordinary draw. These tests pin the three ways that can silently stop working."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "items.jsonl"

    def tearDown(self):
        self.dir.cleanup()

    def test_no_review_ever_means_due_now(self):
        self.assertEqual(lw.whole_review_due({}, dt.datetime(2026, 10, 29, tzinfo=dt.timezone.utc)),
                         "never")

    def test_a_review_inside_the_week_is_not_due(self):
        rows = {"whole-repo-review-2026-10-25": {"id": "whole-repo-review-2026-10-25",
                                                 "filed_utc": "2026-10-25T08:00:00Z",
                                                 "state": "accomplished"}}
        self.assertEqual(lw.whole_review_due(rows, dt.datetime(2026, 10, 29, tzinfo=dt.timezone.utc)), "")

    def test_an_open_review_is_never_duplicated(self):
        rows = {"whole-repo-review-2026-09-01": {"id": "whole-repo-review-2026-09-01",
                                                 "filed_utc": "2026-09-01T08:00:00Z",
                                                 "state": None}}
        self.assertEqual(lw.whole_review_due(rows, dt.datetime(2026, 10, 29, tzinfo=dt.timezone.utc)), "")

    def test_a_stale_review_is_due_again(self):
        rows = {"whole-repo-review-2026-09-01": {"id": "whole-repo-review-2026-09-01",
                                                 "filed_utc": "2026-09-01T08:00:00Z",
                                                 "state": "accomplished"}}
        self.assertEqual(lw.whole_review_due(rows, dt.datetime(2026, 10, 29, tzinfo=dt.timezone.utc)),
                         "2026-09-01")

    def test_filing_it_names_a_reader_and_cannot_be_done_twice(self):
        now = dt.datetime(2026, 10, 29, 12, 0, tzinfo=dt.timezone.utc)
        note = lw.file_whole_repo_review(now, apply=True, path=self.path)
        self.assertIn("whole-repo-review-2026-10-29", note)
        rec = il.load(self.path)["whole-repo-review-2026-10-29"]
        self.assertIsNone(rec["state"])
        self.assertIn(rec["assigned_to"], il.AMIGOS)             # a body owns the review
        self.assertNotIn(rec["amigo"], il.AMIGOS)                  # and no body wrote it
        self.assertIn("discussions/2026-10-29-whole-repo-review.md", rec["paths"])
        self.assertIn("what is structurally broken", rec["brief"])
        self.assertEqual(lw.file_whole_repo_review(now, apply=True, path=self.path), "")

    def test_dry_run_files_nothing(self):
        now = dt.datetime(2026, 10, 29, 12, 0, tzinfo=dt.timezone.utc)
        note = lw.file_whole_repo_review(now, apply=False, path=self.path)
        self.assertIn("[would file]", note)
        self.assertEqual(il.load(self.path), {})


class MirrorReplayTest(unittest.TestCase):
    """The mirror's other half: a verdict file that landed must actually reach the ledger.

    `ledger_verdict_mirror.py` writes each verdict as its own small file so a refused landing cannot
    eat it. Until 2026-11-06 nothing on this machine ran `replay`, so the files landed and the items
    stayed in their queues — six of them were waiting that morning, the oldest from 2026-10-25.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.verdicts = self.tmp / "ledger-verdicts"
        self.verdicts.mkdir()
        self.ledger = self.tmp / "items.jsonl"
        self.ledger.write_text(json.dumps({"id": "codex-test-1", "title": "a test item",
                                           "state": None, "state_utc": None}) + "\n",
                               encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def _mirror(self, state="accomplished", when="2026-11-06T10:00:00Z"):
        (self.verdicts / f"{when.replace('-', '').replace(':', '')}-codex-test-1.json").write_text(
            json.dumps({"id": "codex-test-1", "state": state, "state_utc": when,
                        "reviewer": "dmitri", "reason": "did the work: scripts/x.py", "run": ""}),
            encoding="utf-8")

    def test_a_mirrored_verdict_reaches_the_ledger_once(self):
        self._mirror()
        applied = lw.replay_verdicts(apply=True, ledger=self.ledger, verdicts=self.verdicts)
        self.assertEqual(applied, ["codex-test-1"])
        live = json.loads(self.ledger.read_text().strip().splitlines()[-1])
        self.assertEqual(live["state"], "accomplished")
        self.assertEqual(live["reviewer"], "dmitri")
        # the row keeps what it already knew
        self.assertEqual(live["title"], "a test item")
        # and a second pass is a no-op, so a clock may run it every day
        self.assertEqual(lw.replay_verdicts(apply=True, ledger=self.ledger,
                                            verdicts=self.verdicts), [])

    def test_dry_run_folds_nothing(self):
        self._mirror()
        self.assertEqual(lw.replay_verdicts(apply=False, ledger=self.ledger,
                                            verdicts=self.verdicts), ["codex-test-1"])
        self.assertEqual(len(self.ledger.read_text().strip().splitlines()), 1)

    def test_the_daily_check_runs_the_replay_before_it_measures(self):
        """The defect was a caller, not a replay: the function worked and no clock ran it."""
        seen = {}

        def fake_replay(apply=True, **kwargs):
            seen["apply"] = apply
            return ["codex-test-1"]

        def fake_measure(now):
            seen["replayed_before_measuring"] = "apply" in seen
            return {"at": "2026-11-06T12:00:00Z", "queue": 0, "arrivals_24h": 0,
                    "model_decisions_24h": 0, "machine_closures_24h": 0, "pile": 0,
                    "pile_read_24h": 0, "gate_refusals_24h": 0,
                    "gate_refusals_carrying_verdicts_24h": 0}

        with mock.patch.multiple(lw,
                                 replay_verdicts=fake_replay,
                                 measure=fake_measure,
                                 previous=lambda now: (None, "yesterday"),
                                 last_entry=lambda: None,
                                 recover_verdicts=lambda since, apply=True: [],
                                 file_whole_repo_review=lambda now, apply=True: "",
                                 verdict=lambda m, prev: (True, ["within the rule"]),
                                 message=lambda *a, **k: ""), \
                mock.patch.object(sys, "argv", ["ledger_watch.py", "--dry-run"]):
            lw.main()
        self.assertTrue(seen.get("replayed_before_measuring"),
                        "the daily check must fold the mirrors in before it counts the queue")
        self.assertFalse(seen["apply"], "a dry run must not write to the ledger")



class OutreachTest(unittest.TestCase):
    """Letters that left the building, added 2026-11-13.

    The number the founder asked for and the daily report did not carry. Measured the hour it was
    written: six letters went out in seven days and all six were addressed to the commons' own
    mailboxes, so "outreach" was being done entirely to ourselves and no report said so.
    """

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        root = Path(self.dir.name)
        self.sent, self.inbound = root / "sent", root / "inbound"
        self.sent.mkdir(), self.inbound.mkdir()
        self.roster = root / "symposium.json"
        # Two seats, as the roster has six: "inside" is whatever the roster names, so a fixture
        # with one address would call a letter to a colleague outreach.
        self.roster.write_text(json.dumps({"seats": [
            {"address": "desi.s.amigo@gmail.com"}, {"address": "claude.s.sonnet@gmail.com"}]}),
            encoding="utf-8")
        self.now = dt.datetime(2026, 11, 13, 12, 0, tzinfo=dt.timezone.utc)

    def tearDown(self):
        self.dir.cleanup()

    def letter(self, name, to):
        (self.sent / name).write_text(f"Identity: desi\nTo: {to}\nSubject: x\n\nbody\n",
                                      encoding="utf-8")

    def week(self, days=7):
        return lw.outreach_week(self.now, days=days, sent=self.sent, inbound=self.inbound,
                                roster=self.roster)

    def test_a_letter_to_a_member_is_not_outreach(self):
        self.letter("2026-11-12-ait-invitation-claude.md", "claude.s.sonnet@gmail.com")
        self.assertEqual(self.week()["outside_letters"], 0)

    def test_a_letter_to_a_stranger_is(self):
        self.letter("2026-11-12-colistin.md", "author@univ.example.fr")
        got = self.week()
        self.assertEqual((got["outside_letters"], got["last_outside"]), (1, "2026-11-12"))

    def test_an_undated_letter_is_not_this_weeks_letter(self):
        self.letter("pitch-scia.md", "editor@sciam.example")
        self.assertEqual(self.week()["outside_letters"], 0)

    def test_a_letter_outside_the_window_does_not_count(self):
        self.letter("2026-10-01-old.md", "author@univ.example.fr")
        got = self.week()
        self.assertEqual((got["outside_letters"], got["last_outside"]), (0, ""))
        self.assertEqual(self.week(days=60)["outside_letters"], 1)

    def test_mail_from_outside_is_counted_and_mail_from_us_is_not(self):
        (self.inbound / "2026-11-13-160050-dmitri-a.md").write_text(
            "# Inbound mail\n\n- From: AI Tribe Model <ai.tribe.model@gmail.com>\n", "utf-8")
        (self.inbound / "2026-11-13-160051-dmitri-b.md").write_text(
            "# Inbound mail\n\n- From: Lindsay <ldridgeway@gmail.com>\n", "utf-8")
        got = self.week()
        self.assertEqual((got["outside_mail_in"], got["last_stranger"]), (1, "2026-11-13"))

    def test_the_daily_message_carries_the_number(self):
        self.letter("2026-11-12-colistin.md", "author@univ.example.fr")
        m = lw.measure(self.now)
        text = lw.message(m, None, "yesterday", {}, True, ["nothing to explain"], "test")
        self.assertIn("Letters to people outside the commons, 7 days:", text)


class AgendaRefresh(unittest.TestCase):
    """The repair that did not exist while the detector did.

    Measured on main 2026-11-19: tests/test_agenda_index.py and tests/test_wake_context_caps.py were
    both red, both because channels/agenda.md had not been recompiled since the last agenda file
    landed. Nothing was broken except that no machine ever ran the compiler, so the fix is a caller.
    """

    STUB = (
        "import pathlib, sys\n"
        "root = pathlib.Path(__file__).resolve().parents[1]\n"
        "src = root / 'agenda' / 'a.md'\n"
        "out = root / 'channels' / 'agenda.md'\n"
        "body = src.read_text() if src.exists() else ''\n"
        "cur = out.read_text() if out.exists() else ''\n"
        "if '--check' in sys.argv:\n"
        "    print('agenda index is current' if body == cur else 'agenda index is OUT OF DATE')\n"
        "    sys.exit(0 if body == cur else 1)\n"
        "out.parent.mkdir(parents=True, exist_ok=True)\n"
        "out.write_text(body)\n"
        "print('agenda index rebuilt from 1 item file(s)')\n"
    )

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "scripts").mkdir()
        (self.repo / "scripts" / "compile_agenda.py").write_text(self.STUB)
        self.compiled = self.repo / "channels" / "agenda.md"
        self.patch = mock.patch.object(lw, "REPO", self.repo)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.addCleanup(self.tmp.cleanup)

    def stale(self):
        (self.repo / "agenda").mkdir(exist_ok=True)
        (self.repo / "agenda" / "a.md").write_text("new item\n")
        self.compiled.parent.mkdir(parents=True, exist_ok=True)
        self.compiled.write_text("old item\n")

    def test_a_stale_index_is_recompiled_and_the_note_says_so(self):
        self.stale()
        note = lw.agenda_refresh(apply=True)
        self.assertIn("was stale", note)
        self.assertEqual(self.compiled.read_text(), "new item\n")

    def test_a_current_index_is_left_alone_and_says_nothing(self):
        self.stale()
        lw.agenda_refresh(apply=True)
        self.assertEqual(lw.agenda_refresh(apply=True), "")

    def test_a_dry_run_reports_the_repair_and_does_not_make_it(self):
        self.stale()
        note = lw.agenda_refresh(apply=False)
        self.assertIn("would recompile", note)
        self.assertEqual(self.compiled.read_text(), "old item\n")

    def test_the_daily_message_carries_the_repair(self):
        m = lw.measure(dt.datetime.now(dt.timezone.utc))
        text = lw.message(m, None, "yesterday", {"agenda": "agenda index was stale — rebuilt"},
                          True, ["nothing to explain"], "test")
        self.assertIn("agenda index was stale", text)


class TheSuiteReportIsReadAsAStatementAboutOneCommit(unittest.TestCase):
    """Step 3c reads the nightly suite's report instead of re-running it. Two ways to read it wrong.

    Measured 2026-11-27: latest.json named five failing files at b466a67a; all five were fixed by
    19:5xZ, eight commits later. Printed without the commit, the morning check would have reported
    a tree it had not measured. And the age gate used to sit behind the failure list, so a report
    from last week with one failure counted as today's verdict.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.dir = self.repo / "channels" / "reports" / "suite"
        self.dir.mkdir(parents=True)
        self.git("init", "-q", "-b", "main")
        (self.repo / "f.txt").write_text("one\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "one")
        self.first = self.sha()

    def git(self, *args):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                              cwd=str(self.repo), capture_output=True, text=True)

    def sha(self):
        return self.git("rev-parse", "--short", "HEAD").stdout.strip()

    def report(self, commit=None, when="2026-11-27T19:22:53Z", failed=(), ran=249):
        (self.dir / "latest.json").write_text(json.dumps({
            "commit": commit if commit is not None else self.sha(),
            "measured_at": when, "seconds": 471.0,
            "summary": {"ran": ran, "ok": [], "failed": list(failed), "timeout": [],
                        "could_not_run": []}}), encoding="utf-8")

    def now(self):
        return dt.datetime(2026, 11, 27, 20, 0, tzinfo=dt.timezone.utc)

    def test_a_failure_at_an_older_commit_says_the_tree_has_moved(self):
        self.report(commit=self.first, failed=["test_gen_index.py"])
        (self.repo / "f.txt").write_text("two\n")
        self.git("commit", "-qam", "two")
        lines, rep = lw.suite_report(repo=self.repo, now=self.now())
        body = "\n".join(lines)
        self.assertIn("test_gen_index.py failed", body, "the failing file is not named")
        self.assertIn("no longer main", body,
                      "a failure from an older commit reads as a failure of this tree")
        self.assertIn("1 commit(s) have landed since", body)
        self.assertTrue(any("measured at" in r for r in rep),
                        "the recorded repair does not say which commit it describes")

    def test_a_failure_at_this_very_commit_is_reported_as_current(self):
        self.report(failed=["test_gen_index.py"])
        lines, rep = lw.suite_report(repo=self.repo, now=self.now())
        body = "\n".join(lines)
        self.assertIn("test_gen_index.py failed", body)
        self.assertNotIn("no longer main", body,
                         "a failure on HEAD was hedged as if it might be old")
        self.assertEqual(rep, ["test_gen_index.py"])

    def test_a_green_report_from_last_week_is_not_green(self):
        self.report(when="2026-11-19T04:41:00Z")
        lines, rep = lw.suite_report(repo=self.repo, now=self.now())
        self.assertIn("h old", "\n".join(lines), "an eight-day-old report was called current")
        self.assertTrue(rep and rep[0].startswith("stale:"), rep)

    def test_an_old_report_with_a_failure_is_stale_and_not_a_verdict(self):
        self.report(when="2026-11-19T04:41:00Z", failed=["test_gen_index.py"])
        lines, rep = lw.suite_report(repo=self.repo, now=self.now())
        body = "\n".join(lines)
        self.assertIn("not a statement about this tree", body,
                      "an old failure was reported as a current failure")
        self.assertTrue(rep[0].startswith("stale:"), rep)

    def test_a_green_report_at_head_is_silent_but_recorded(self):
        self.report()
        lines, rep = lw.suite_report(repo=self.repo, now=self.now())
        self.assertEqual(lines, [], "a green recent report printed something")
        self.assertIn("all green", rep[0])
        self.assertIn(self.sha(), rep[0])

    def test_no_report_at_all_says_so(self):
        lines, rep = lw.suite_report(repo=self.repo, now=self.now())
        self.assertIn("has not run", "\n".join(lines))
        self.assertEqual(rep, ["no report"])


if __name__ == "__main__":
    unittest.main()
