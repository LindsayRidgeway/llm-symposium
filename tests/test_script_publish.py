#!/usr/bin/env python3
"""The unattended scripts must publish their own output without moving the shared checkout.

Written 2026-11-02 by Desi, the evening after the same repair landed in `record_push`. Three
scripts write a file into the checkout and then commit it:

  ``scripts/append-goose.py``      the Goose exchange, on **every human message**
  ``scripts/daily_report.py``      the daily report and its ledger rows
  ``scripts/tell_human.py``        held outbound messages and the request register

All three committed on ``main`` in that checkout and two of them then ran ``pull --no-rebase``. The
justification written into both docstrings — *"the lander refuses a dirty shared checkout"* — was
true until 2026-11-02 and is not true now; what a dirty tree blocks is the lander's final
fast-forward. A commit made there and not pushed also leaves the checkout **ahead** of origin,
which is the state that makes every later fast-forward fail, so the old body could produce the very
condition its docstring claimed to prevent.

What this checks:
  1. ``append()`` publishes to origin with a dirty, unrelated file in the tree, and that file is
     still there afterwards with no stash entry and no conflict markers.
  2. ``_commit_own_outputs()`` in both scripts does the same for a file it wrote.
  3. Structurally: none of the three publish paths can run ``git pull`` or ``git commit``.

Run: python3 tests/test_script_publish.py      (exit 0 pass, 1 fail)
"""
import ast
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

SCRIPTS = {
    "append-goose": REPO / "scripts" / "append-goose.py",
    "daily_report": REPO / "scripts" / "daily_report.py",
    "tell_human": REPO / "scripts" / "tell_human.py",
}


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert r.returncode == 0, "git %s: %s" % (" ".join(args), (r.stderr or "").strip())
    return r.stdout


def write(repo, rel, text):
    p = pathlib.Path(repo) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


class Fixture(unittest.TestCase):
    """A bare origin, a shared checkout and a rival — the three bodies of every real race."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = pathlib.Path(self.tmp.name)
        self.origin = root / "origin.git"
        self.shared = root / "shared"
        self.rival = root / "rival"
        subprocess.run(["git", "init", "-q", "-b", "main", "--bare", str(self.origin)],
                       capture_output=True, check=True)
        for path in (self.shared, self.rival):
            subprocess.run(["git", "clone", "-q", str(self.origin), str(path)],
                           capture_output=True, check=True)
        write(self.shared, "channels/conversation/desi.md", "hello\n")
        write(self.shared, "agenda/36.md", "one\ntwo\nthree\n")
        git(self.shared, "add", "-A")
        git(self.shared, "-c", "user.name=T", "-c", "user.email=t@t", "commit", "-qm", "base")
        git(self.shared, "push", "-q", "origin", "main")

    def rival_pushes(self, rel, text):
        """Origin moves while the session is working — the case the worktree path exists for."""
        git(self.rival, "pull", "-q", "origin", "main")
        write(self.rival, rel, text)
        git(self.rival, "add", "-A")
        git(self.rival, "-c", "user.name=R", "-c", "user.email=r@r", "commit", "-qm", "rival")
        git(self.rival, "push", "-q", "origin", "main")


class TestAppendGoosePublishesWithoutMovingTheTree(Fixture):

    def test_the_exchange_reaches_origin_and_the_tree_is_left_alone(self):
        self.rival_pushes("agenda/36.md", "one\nTWO BY THE RIVAL\nthree\n")
        # A session's uncommitted work in the same tree, which the old body could leave stranded.
        write(self.shared, "notes.md", "half-written paragraph\n")

        spec = importlib.util.spec_from_file_location("append_goose_under_test",
                                                     SCRIPTS["append-goose"])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.append("desi", "the human's message", "my reply", repo=self.shared)

        landed = git(self.origin, "show", "main:channels/conversation/desi.md")
        self.assertIn("my reply", landed, "the exchange never reached origin")
        self.assertEqual((self.shared / "notes.md").read_text(encoding="utf-8"),
                         "half-written paragraph\n", "publishing moved a session's file")
        self.assertEqual(git(self.shared, "stash", "list").strip(), "",
                         "publishing used the stash")
        self.assertNotIn("<<<<<<<", landed, "publishing left conflict markers in the record")

    def test_a_staged_file_is_not_swept_into_the_exchange_commit(self):
        """The old body ran `git commit -m …` with no pathspec, so anything a session had staged
        went into a commit labelled "log(goose): Desi exchange". Staged work is not saved work."""
        write(self.shared, "notes.md", "a session's staged sentence\n")
        git(self.shared, "add", "notes.md")
        spec = importlib.util.spec_from_file_location("append_goose_under_test",
                                                     SCRIPTS["append-goose"])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.append("desi", "a message", "a reply", repo=self.shared)

        landed = git(self.origin, "ls-tree", "-r", "--name-only", "main").split()
        self.assertNotIn("notes.md", landed,
                         "a session's staged file was committed and published as a Goose exchange")
        self.assertIn("notes.md", git(self.shared, "diff", "--cached", "--name-only").split(),
                      "the staged file was committed locally instead of left alone")

    def test_the_checkout_is_clean_and_current_after_a_publish(self):
        """The half that makes the other half worth having: a published record also *advances*.

        A refusal to fast-forward is correct when a session's work is in the way. It is not
        correct when the only thing in the way is the file we just published, whose bytes are now
        identical to what we are merging in — that leaves the checkout behind origin for ever, and
        every later landing reports a checkout that never catches up.
        """
        spec = importlib.util.spec_from_file_location("append_goose_under_test",
                                                     SCRIPTS["append-goose"])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.append("desi", "a message", "a reply", repo=self.shared)

        self.assertEqual(git(self.shared, "status", "--porcelain").strip(), "",
                         "the published file was left dirty in the checkout")
        self.assertEqual(git(self.shared, "rev-parse", "HEAD").strip(),
                         git(self.shared, "rev-parse", "origin/main").strip(),
                         "the checkout did not advance to what it published")


class TestCommitOwnOutputsPublishesThroughTheSharedPath(Fixture):

    def _fn(self, script, name):
        """The real function, sliced out of the script and pointed at a throwaway checkout."""
        src = script.read_text(encoding="utf-8")
        for node in ast.parse(src).body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                body = "".join(src.splitlines(True)[node.lineno - 1:node.end_lineno])
                break
        else:
            self.fail("%s has no %s" % (script.name, name))
        # `subprocess` is in the namespace so the OLD body can run too: without it the
        # comparison fails on a NameError and proves nothing about the defect.
        ns = {"Path": pathlib.Path, "subprocess": subprocess, "REPO": self.shared}
        exec(compile(body, str(script), "exec"), ns)     # noqa: S102 — the point of the test
        return ns[name]

    def test_daily_report_publishes_what_it_wrote(self):
        fn = self._fn(SCRIPTS["daily_report"], "_commit_own_outputs")
        (self.shared / "channels" / "reports").mkdir(parents=True, exist_ok=True)
        out = self.shared / "channels" / "reports" / "2026-11-02-daily.md"
        out.write_text("# daily\n", encoding="utf-8")
        fn([out], "report(daily): recorded, held, not sent")
        self.assertIn("# daily", git(self.origin, "show",
                                     "main:channels/reports/2026-11-02-daily.md"))

    def test_a_staged_file_is_not_swept_into_the_own_outputs_commit(self):
        """Same defect as the Goose log: `git commit -m` with no pathspec commits the whole index.

        This one is driven through the unchanged signature, so it is the discriminator for the two
        scripts: on the old body it fails, because the session's staged file went along.
        """
        fn = self._fn(SCRIPTS["daily_report"], "_commit_own_outputs")
        write(self.shared, "notes.md", "a session's staged sentence\n")
        git(self.shared, "add", "notes.md")
        (self.shared / "channels" / "reports").mkdir(parents=True, exist_ok=True)
        out = self.shared / "channels" / "reports" / "2026-11-02-daily.md"
        out.write_text("# daily\n", encoding="utf-8")
        fn([out], "report(daily): recorded, held, not sent")
        landed = git(self.origin, "ls-tree", "-r", "--name-only", "main").split()
        self.assertNotIn("notes.md", landed,
                         "a session's staged file was published inside the daily report's commit")

    def test_tell_human_publishes_what_it_wrote(self):
        fn = self._fn(SCRIPTS["tell_human"], "_commit_own_outputs")
        (self.shared / "channels" / "telegram").mkdir(parents=True, exist_ok=True)
        out = self.shared / "channels" / "telegram" / "2026-11-02-000000-outbound-desi-session.md"
        out.write_text("# outbound\n", encoding="utf-8")
        fn([out], "record(telegram): desi — held work summary, not sent")
        self.assertIn("# outbound", git(self.origin, "show",
                                        "main:channels/telegram/"
                                             "2026-11-02-000000-outbound-desi-session.md"))


class TestNoPublishPathRunsGitByHand(Fixture):

    PUBLISHERS = {"append-goose": "append", "daily_report": "_commit_own_outputs",
                  "tell_human": "_commit_own_outputs"}

    def test_none_of_them_can_pull_or_commit(self):
        for name, script in SCRIPTS.items():
            with self.subTest(script=name):
                src = script.read_text(encoding="utf-8")
                tree = ast.parse(src)
                wanted = self.PUBLISHERS[name]
                node = next(n for n in tree.body
                            if isinstance(n, ast.FunctionDef) and n.name == wanted)
                body = "".join(src.splitlines(True)[node.lineno - 1:node.end_lineno])
                for bad in ('"pull"', '"commit"', '"stash"', '"reset"', '"checkout"'):
                    self.assertNotIn(bad, body,
                                     "%s still runs git %s in the shared checkout" % (name, bad))
                self.assertIn("commit_and_publish", body,
                              "%s does not publish through the worktree path" % name)
        print("  OK   3 script publish paths go through the worktree, none through git by hand")


if __name__ == "__main__":
    unittest.main(verbosity=2)
