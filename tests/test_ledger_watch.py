"""Tests for scripts/ledger_watch.py — the daily check that repairs what a refused landing ate.

The point of these tests is the two judgements that are easy to get wrong and expensive to get wrong
in production: which verdict to believe when an item was reviewed twice, and how to tell a patch
that carried a verdict from one that carried only prose.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "channels"))

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


if __name__ == "__main__":
    unittest.main()
