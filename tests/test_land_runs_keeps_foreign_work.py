#!/usr/bin/env python3
"""A landing stops taking another session's work, and says where it put it (Desi, 2026-11-27).

Value item `landing-wipes-a-sessions-edits`. Two mechanisms were named in the record and both
lived in `land_runs.py`'s shared-checkout path:

  * `_rescue()` staged the whole tree with `git add -A`, in the SHARED index, and committed it on
    whatever branch HEAD was on. A session's three staged files became every dirty path; a commit
    that failed unstaged its work with a bare `git reset -q`; and the commit that succeeded put
    somebody else's paragraph into a landing's history under a message about a reset.
  * `_undo()` without a snapshot reverted tracked files with `git checkout -- .`, which is how two
    edits disappeared between `git add` and `git commit` — untracked files survive that, tracked
    ones do not, and nothing is written down.

What this file pins is a property, not a code shape: before the lander discards bytes from the
shared checkout it makes them retrievable from a branch, and it never writes into the index that
another process is using. The lander is loaded from where it is installed rather than restated, and
when there is no installed lander every case skips with its reason — a test that cannot run is not
a pass. pytest is not installed on the wake machines, so this runs directly
(`python3 tests/test_land_runs_keeps_foreign_work.py`) and through the landing gate, which executes
every `tests/test_*.py`.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# `LAND_RUNS_UNDER_TEST` is how this file proves it bites: point it at a mutated copy and the
# suite must go red. The default is the lander as installed, which is the one that lands.
LANDER = Path(os.environ.get("LAND_RUNS_UNDER_TEST")
              or Path.home() / "LLM" / "desi-bot" / "land_runs.py")


def load_lander():
    spec = importlib.util.spec_from_file_location("land_runs_keeps_foreign_work", LANDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(repo, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          cwd=str(repo), capture_output=True, text=True)


def out(repo, *args):
    return git(repo, *args).stdout.strip()


class Base(unittest.TestCase):
    """A shared checkout that is one commit ahead of and one behind its origin."""

    def setUp(self):
        if not LANDER.is_file():
            self.skipTest("no installed lander at %s" % LANDER)
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.origin = self.root / "origin.git"
        self.repo = self.root / "shared"
        self.other = self.root / "other"
        git(self.root, "init", "-q", "--bare", "-b", "main", str(self.origin))
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "remote", "add", "origin", str(self.origin))
        (self.repo / "insights").mkdir()
        (self.repo / "insights" / "note.md").write_text("as committed\n", encoding="utf-8")
        (self.repo / "channels").mkdir()
        (self.repo / "channels" / "agenda.md").write_text("agenda v1\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "seed")
        git(self.repo, "push", "-q", "origin", "main")
        # origin moves on, by somebody else
        git(self.root, "clone", "-q", str(self.origin), str(self.other))
        (self.other / "insights" / "note.md").write_text("as committed\nsomeone else's line\n",
                                                         encoding="utf-8")
        git(self.other, "commit", "-qam", "their work")
        git(self.other, "push", "-q", "origin", "main")
        # and this checkout moves on, so main is ahead 1 and behind 1
        (self.repo / "channels" / "agenda.md").write_text("agenda v1\nlocal line\n",
                                                          encoding="utf-8")
        git(self.repo, "commit", "-qam", "local work")
        self.mod = load_lander()
        self.mod.REPO = self.repo
        self.log = self.repo / ".git" / "mutation.log"

    def tearDown(self):
        self._tmp.cleanup()

    def session_work(self):
        """The state a live session leaves in the shared checkout: a tracked edit, a staged file,
        and an untracked draft."""
        (self.repo / "insights" / "note.md").write_text("as committed\nA PARAGRAPH NOT YET LANDED\n",
                                                        encoding="utf-8")
        (self.repo / "staged.md").write_text("staged by a session\n", encoding="utf-8")
        git(self.repo, "add", "staged.md")
        (self.repo / "draft.md").write_text("a draft nobody has added\n", encoding="utf-8")

    def branches(self, prefix="rescue/"):
        return [b.strip() for b in out(self.repo, "for-each-ref", "--format=%(refname:short)",
                                       "refs/heads/" + prefix).splitlines() if b.strip()]


class ARescueKeepsTheWork(Base):
    def test_the_work_on_disk_survives_the_reset_on_a_branch(self):
        self.session_work()
        note = self.mod._rescue("test: main diverged")
        self.assertIn("kept on branch", note)
        found = self.branches()
        self.assertEqual(len(found), 1, "the rescue did not leave exactly one branch: %s" % found)
        branch = found[0]
        body = out(self.repo, "show", "%s:insights/note.md" % branch)
        self.assertIn("A PARAGRAPH NOT YET LANDED", body,
                      "the tracked edit this reset discarded is not on the branch")
        self.assertEqual(out(self.repo, "show", "%s:draft.md" % branch),
                         "a draft nobody has added",
                         "an untracked draft did not survive the reset")
        self.assertEqual(out(self.repo, "show", "%s:staged.md" % branch),
                         "staged by a session",
                         "a staged file did not survive the reset")

    def test_main_is_put_back_on_origin_and_no_tracked_path_is_left_modified(self):
        self.session_work()
        self.mod._rescue("test: main diverged")
        self.assertEqual(out(self.repo, "rev-parse", "HEAD"),
                         out(self.repo, "rev-parse", "origin/main"),
                         "main was not reset to origin/main, so this checkout still cannot push")
        # `git reset --hard` never removes untracked files, so a draft the session never added is
        # still on disk as well as on the branch. What must be gone is the tracked edit, because
        # that is the one a landing would otherwise carry into its own commit as if it were a
        # change of its own.
        self.assertEqual(out(self.repo, "status", "--porcelain", "--untracked-files=no"), "",
                         "a tracked path is still modified after a rescue that reset main")
        self.assertEqual((self.repo / "draft.md").exists(), True,
                         "the reset deleted an untracked draft it had no business deleting")

    def test_the_branch_names_the_paths_and_says_it_is_a_snapshot(self):
        self.session_work()
        self.mod._rescue("test: main diverged")
        branch = self.branches()[0]
        msg = out(self.repo, "log", "-1", "--format=%B", branch)
        for path in ("insights/note.md", "staged.md", "draft.md"):
            self.assertIn(path, msg, "the snapshot's message does not name %s" % path)
        self.assertIn("SNAPSHOT", msg, "the message does not say the work is not the commit's own")

    def test_the_shared_index_and_head_are_untouched_by_the_snapshot_itself(self):
        """The behaviour `git add -A` broke: making the branch moved the shared index."""
        self.session_work()
        head_before = out(self.repo, "rev-parse", "HEAD")
        staged_before = out(self.repo, "diff", "--cached", "--name-only")
        kept = self.mod._keep_on_a_branch("test: pin it", ["insights/note.md", "staged.md"],
                                          "rescue/test-pin")
        self.assertIsNotNone(kept, "nothing was pinned")
        self.assertTrue(kept["complete"], "the snapshot does not match what is on disk")
        self.assertEqual(out(self.repo, "rev-parse", "HEAD"), head_before,
                         "pinning the work moved HEAD")
        self.assertEqual(out(self.repo, "diff", "--cached", "--name-only"), staged_before,
                         "pinning the work changed what another session had staged")

    def test_a_snapshot_that_cannot_be_made_stops_the_reset(self):
        self.session_work()
        head_before = out(self.repo, "rev-parse", "HEAD")
        note_before = (self.repo / "insights" / "note.md").read_text(encoding="utf-8")
        self.mod._keep_on_a_branch = lambda *a, **k: None
        note = self.mod._rescue("test: main diverged")
        self.assertIn("NOT reset", note, "a rescue with no snapshot reset anyway")
        self.assertEqual(out(self.repo, "rev-parse", "HEAD"), head_before,
                         "HEAD moved although nothing could be pinned")
        self.assertEqual((self.repo / "insights" / "note.md").read_text(encoding="utf-8"),
                         note_before, "the work on disk was discarded without a snapshot")

    def test_the_reset_is_written_down_where_a_lost_edit_can_be_found(self):
        self.session_work()
        self.mod._rescue("test: main diverged")
        self.assertTrue(self.log.is_file(), "no mutation log was written")
        text = self.log.read_text(encoding="utf-8")
        self.assertIn("by=land_runs", text, "the line does not name the process that made the move")
        self.assertIn("reset", text, "the reset is not in the log")
        self.assertIn(self.branches()[0], text, "the log does not say where the work went")


class AnUndoWithoutASnapshotDoesNotGuess(Base):
    def test_tracked_work_is_pinned_before_it_is_reverted(self):
        self.session_work()
        (self.repo / "scratch.txt").write_text("created by the failed landing\n", encoding="utf-8")
        self.mod._undo(["scratch.txt"], ["insights/note.md"], None, None)
        self.assertEqual((self.repo / "insights" / "note.md").read_text(encoding="utf-8"),
                         "as committed\n",
                         "the revert did not happen; the path is no longer being restored")
        self.assertEqual((self.repo / "scratch.txt").exists(), False,
                         "a file this landing created was left behind")
        self.assertTrue((self.repo / "draft.md").exists(),
                        "an untracked draft outside `created` was deleted")
        found = [b for b in self.branches("rescue/") if b.endswith("-undo")]
        self.assertEqual(len(found), 1, "the reverted paragraph was not pinned: %s" % self.branches())
        self.assertIn("A PARAGRAPH NOT YET LANDED",
                      out(self.repo, "show", "%s:insights/note.md" % found[0]),
                      "the branch exists but does not hold the paragraph it was made for")

    def test_the_revert_is_written_down(self):
        self.session_work()
        self.mod._undo([], ["insights/note.md"], None, None)
        text = self.log.read_text(encoding="utf-8") if self.log.is_file() else ""
        self.assertIn("revert", text, "a snapshot-less revert left no line in the mutation log")


class TheTripwireNoticesASweep(Base):
    """The signature of the 2026-11-27 loss, made visible at the next landing.

    No prevention is claimed: a `git restore` from another program cannot be stopped by anything in
    the lander. What is claimed is that the next time a session's modified file goes back to an
    older content with no commit in between, `.git/mutation.log` names the paths and the window.
    It fired twice on 2026-11-27 while this very file was being written — 20:51:25Z and again four
    minutes later — and neither event left a line anywhere, which is the whole reason for it.
    """

    def test_a_modified_file_going_clean_without_a_commit_is_named(self):
        (self.repo / "insights" / "note.md").write_text("a paragraph in flight\n", encoding="utf-8")
        self.mod._tree_watch("test sample one")
        self.git_restore("insights/note.md")
        out = self.mod._tree_watch("test sample two")
        self.assertIn("insights/note.md", out["vanished"], "the sweep was not noticed: %s" % out)
        text = self.log.read_text(encoding="utf-8") if self.log.is_file() else ""
        self.assertIn("vanished", text, "the sweep was noticed and not written down")
        self.assertIn("insights/note.md", text)

    def test_a_committed_file_is_not_a_sweep(self):
        (self.repo / "insights" / "note.md").write_text("landed properly\n", encoding="utf-8")
        self.mod._tree_watch("test sample one")
        git(self.repo, "commit", "-qam", "a real commit")
        out = self.mod._tree_watch("test sample two")
        self.assertEqual(out["vanished"], [],
                         "a commit was reported as a sweep, which would make the tripwire noise")

    def test_a_file_still_dirty_is_left_alone(self):
        (self.repo / "insights" / "note.md").write_text("still being written\n", encoding="utf-8")
        self.mod._tree_watch("test sample one")
        (self.repo / "insights" / "note.md").write_text("still being written, more\n",
                                                        encoding="utf-8")
        out = self.mod._tree_watch("test sample two")
        self.assertEqual(out["vanished"], [], "ordinary editing was reported as a loss")

    def git_restore(self, path):
        subprocess.run(["git", "-C", str(self.repo), "checkout", "--", path],
                       capture_output=True, text=True)


class TheSixCopiesAreStillTheSameEngine(unittest.TestCase):
    """`land_runs.py` is not one of the shared modules `deploy_engines.py` copies: it exists six
    times, one per body, differing only in the name on the commit. Before 2026-11-27 that was a
    fact nobody checked — the six files were last compared by hand, and a fix applied to one body's
    lander is invisible from every other body's wake. This reads all six and requires that the only
    difference is the identity pair, so a change made to one copy fails here until it is made in
    all of them (or the engine is moved into `channels/` and deployed like the rest)."""

    BODIES = ("desi", "dmitri", "gemini", "claude", "tarik", "gwen")
    IDENTITY = ("GIT_ID = ", "ARCH_TRAILER = ")

    def copies(self):
        found = {}
        for seat in self.BODIES:
            p = Path.home() / "LLM" / ("%s-bot" % seat) / "land_runs.py"
            if p.is_file():
                found[seat] = [ln for ln in p.read_text(encoding="utf-8").splitlines()
                               if not ln.startswith(self.IDENTITY)]
        return found

    def test_the_six_landers_differ_only_in_the_name_on_the_commit(self):
        found = self.copies()
        if len(found) < 2:
            self.skipTest("fewer than two landers on this machine: %s" % sorted(found))
        base_seat = "desi" if "desi" in found else sorted(found)[0]
        base = found[base_seat]
        for seat, lines in sorted(found.items()):
            if seat == base_seat:
                continue
            diff = [(i, a, b) for i, (a, b) in enumerate(zip(base, lines)) if a != b]
            self.assertEqual(len(base), len(lines),
                             "%s's lander has %d lines against %s's %d — the engines have drifted"
                             % (seat, len(lines), base_seat, len(base)))
            self.assertEqual(diff[:3], [],
                             "%s's lander differs from %s's outside the identity lines: %s"
                             % (seat, base_seat, diff[:3]))

    def test_every_lander_can_still_be_loaded(self):
        for seat in self.BODIES:
            p = Path.home() / "LLM" / ("%s-bot" % seat) / "land_runs.py"
            if not p.is_file():
                continue
            spec = importlib.util.spec_from_file_location("lander_%s" % seat, p)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
            except Exception as exc:  # a lander that cannot be imported parks every wake silently
                self.fail("%s's lander does not import: %r" % (seat, exc))
            self.assertTrue(hasattr(mod, "_keep_on_a_branch"),
                            "%s's lander has no snapshot helper — the fix was not deployed there"
                            % seat)


class TheItemItselfIsSatisfied(unittest.TestCase):
    """The two clauses of `landing-wipes-a-sessions-edits`, read against the installed lander."""

    def setUp(self):
        if not LANDER.is_file():
            self.skipTest("no installed lander at %s" % LANDER)
        self.text = LANDER.read_text(encoding="utf-8")

    def test_no_bare_add_all_remains_in_the_shared_tree_path(self):
        offenders = []
        for line in self.text.splitlines():
            s = line.strip()
            if '"add", "-A"' in s and "--" not in s:
                offenders.append(s)
        self.assertEqual(offenders, [],
                         "a landing still stages the whole shared tree: %s" % offenders)

    def test_the_unscoped_checkout_is_no_longer_reachable_without_a_snapshot(self):
        body = self.text.split("if pre is None or post is None:")[1].split("left = []")[0]
        self.assertIn("_keep_on_a_branch", body,
                      "the snapshot-less revert no longer pins what it reverts")
        self.assertIn("_note_mutation", body,
                      "the snapshot-less revert no longer writes down what it did")


class TheProofBites(unittest.TestCase):
    """A guard that has never been seen to fail is a guard nobody knows the shape of.

    This copies the installed lander, puts the defect back into the copy — `git add -A` against
    the shared index instead of a private one — and runs this whole file against it as a
    subprocess. The copy must go red. If the line it mutates has moved, the test says so rather
    than passing quietly, because a mutation that hits nothing proves nothing (that exact mistake
    was made twice on 2026-11-27, in other files).
    """

    MUTATE_FROM = '        a = gi("add", "-A", "--", *taken)'
    MUTATE_TO = '        a = git("add", "-A", "--", *taken)   # MUTATION: back to the shared index'

    def test_putting_the_shared_index_back_is_caught(self):
        if os.environ.get("LAND_RUNS_PROOF") == "inner":
            self.skipTest("this is the inner run, whose failures are the point")
        if not LANDER.is_file():
            self.skipTest("no installed lander at %s" % LANDER)
        source = LANDER.read_text(encoding="utf-8")
        if self.MUTATE_FROM not in source:
            self.fail("the lander no longer contains the line this mutation targets (%r); the "
                      "proof is stale — retarget the mutation" % self.MUTATE_FROM.strip())
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        copy = Path(tmp.name) / "land_runs.py"
        copy.write_text(source.replace(self.MUTATE_FROM, self.MUTATE_TO), encoding="utf-8")
        env = dict(os.environ, LAND_RUNS_UNDER_TEST=str(copy), LAND_RUNS_PROOF="inner")
        r = subprocess.run([sys.executable, str(Path(__file__).resolve())],
                           capture_output=True, text=True, env=env)
        both = (r.stdout or "") + (r.stderr or "")
        self.assertNotEqual(r.returncode, 0,
                            "a lander that stages into the shared index passed this suite — the "
                            "proof does not bite:\n" + both[-1500:])
        self.assertIn("FAILED", both, "the mutated lander exited non-zero without naming a failure")


if __name__ == "__main__":
    unittest.main(verbosity=2)
