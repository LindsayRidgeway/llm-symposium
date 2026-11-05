#!/usr/bin/env python3
"""Every body files work from its chat, and the filing lands on origin.

Written 2026-11-03 by Desi. Until tonight only two of the six Telegram bodies could file anything.
`desi-bot` and `dmitri-bot` carried a private copy of `extract_tasks` / `file_tasks` **and** the
sentence in the system prompt that tells a model the `TASK:` marker exists. `claude-bot`,
`gemini-bot`, `tarik-bot` and `gwen-bot` carried neither. The founder's test of the whole
arrangement — *judge it by whether tasks.md has my name in it* — was therefore true of two bodies
out of six, and a request agreed in the other four chats was invisible to every wake, to the other
amigos, and to him. Gwen's case was the worst of the four: her chat wrote nothing else to the
commons at all, so a request agreed with her left no trace anywhere.

What this checks:

  1. Behaviourally, against a real bare origin and a real shared clone: a reply carrying a `TASK:`
     line ends up in `channels/tasks.md` **on origin**, the marker never reaches the human, and the
     shared checkout ends clean and current rather than holding the file it just published.
  2. Structurally, for all six bodies: the chat loop calls `file_from_reply`, and the system prompt
     carries the paragraph that makes the marker possible. Half of this feature is a sentence to
     the model; without it the other half is dead code that tests green.

Both structural checks fail on the four bodies as they stood before 2026-11-03.

Run: python3 tests/test_task_filing_all_bodies.py      (exit 0 pass, 1 fail)
"""
import ast
import importlib.util
import itertools
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO / "tests"))
import live_tree  # noqa: E402  — the live-tree gate in tests/live_tree.py, see its docstring
BOTS = REPO.parent
sys.path.insert(0, str(REPO / "channels"))       # so the module's `import record_push` resolves

MODULE = REPO / "channels" / "task_filing.py"
BODIES = {b: BOTS / ("%s-bot" % b) / "bot.py"
          for b in ("desi", "dmitri", "claude", "gemini", "tarik", "gwen")}
_N = itertools.count()


def load():
    spec = importlib.util.spec_from_file_location("task_filing_all_bodies_%d" % next(_N), str(MODULE))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
    """A bare origin and a shared checkout — the two bodies the publish path moves between."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = pathlib.Path(self.tmp.name)
        self.origin = root / "origin.git"
        self.shared = root / "shared"
        self.other = root / "other"
        subprocess.run(["git", "init", "-q", "-b", "main", "--bare", str(self.origin)],
                       capture_output=True, check=True)
        for path in (self.shared, self.other):
            subprocess.run(["git", "clone", "-q", str(self.origin), str(path)],
                           capture_output=True, check=True)
        write(self.shared, "channels/tasks.md",
              "# Commons tasks\n\n## Open\n\n- [ ] an older request\n")
        write(self.shared, "channels/conversation/desi.md", "hello\n")
        git(self.shared, "add", "-A")
        git(self.shared, "-c", "user.name=T", "-c", "user.email=t@t", "commit", "-qm", "base")
        git(self.shared, "push", "-q", "origin", "main")


class TestARequestFromAnyChatLandsOnOrigin(Fixture):
    def test_the_filing_reaches_origin_and_the_marker_does_not_reach_the_human(self):
        mod = load()
        reply = mod.file_from_reply(
            "Filed, and I will take the second half.\n"
            "TASK: repair the hinge — the human asked in the chat\n",
            "Telegram", repo=str(self.shared))
        self.assertNotIn("TASK:", reply, "the marker line leaked into what the human reads")
        self.assertIn("I will take the second half", reply)
        on_origin = git(self.origin, "show", "main:channels/tasks.md")
        self.assertIn("repair the hinge", on_origin,
                      "the request filed in the chat never reached origin — no wake will see it")
        self.assertIn("an older request", on_origin, "filing dropped a line that was already there")

    def test_the_shared_checkout_is_clean_and_current_afterwards(self):
        load().file_from_reply("TASK: one small thing\n", "Telegram", repo=str(self.shared))
        self.assertEqual(git(self.shared, "status", "--porcelain").strip(), "",
                         "filing left the shared checkout dirty")
        self.assertEqual(git(self.shared, "rev-parse", "HEAD").strip(),
                         git(self.shared, "rev-parse", "origin/main").strip(),
                         "the shared checkout is not on origin's tip after its own publish")

    def test_a_second_request_from_a_different_body_does_not_lose_the_first(self):
        mod = load()
        mod.file_from_reply("TASK: the first body's request\n", "Telegram", repo=str(self.shared))
        # Another body's chat, after origin has moved under the shared clone.
        git(self.other, "pull", "-q", "origin", "main")
        write(self.other, "agenda/new.md", "someone else's work\n")
        git(self.other, "add", "-A")
        git(self.other, "-c", "user.name=O", "-c", "user.email=o@o", "commit", "-qm", "other")
        git(self.other, "push", "-q", "origin", "main")
        mod.file_from_reply("TASK: the second body's request\n", "Telegram", repo=str(self.shared))
        on_origin = git(self.origin, "show", "main:channels/tasks.md")
        self.assertIn("the first body's request", on_origin)
        self.assertIn("the second body's request", on_origin)
        self.assertIn("an older request", on_origin)


class TestEveryBodyHasThePath(unittest.TestCase):
    """Structural checks on the six bots' own files. Off this Mac (a private worktree or the
    GitHub runner) the six chat loops do not exist, so the class skips and says so; a tree that
    is here with one body's file missing still fails, because that is a body that lost its path.
    """

    def setUp(self):
        live_tree.require_live_tree(self)

    def test_each_chat_loop_calls_the_filing_path(self):
        for bot, path in BODIES.items():
            with self.subTest(bot=bot):
                src = path.read_text(encoding="utf-8")
                self.assertIn("from task_filing import file_from_reply", src,
                              "%s does not import the filing path" % bot)
                loop = src[src.index("def main("):]
                self.assertTrue('file_from_reply(reply, "Telegram", repo=REPO_DIR)' in loop,
                                "%s never files the work it agrees to in the chat" % bot)

    def test_each_prompt_asks_the_model_to_mark_the_work(self):
        """The load-bearing half: the model must be told the marker exists and where it lands.

        desi and dmitri carry this inside their existing `CHAT_RULES` (since 2026-09-21) and the
        other four in a `FILING_RULES` constant (2026-11-03). The test is therefore about the
        prompt that is actually assembled, not about the name of the constant that carries it.
        """
        for bot, path in BODIES.items():
            with self.subTest(bot=bot):
                text = path.read_text(encoding="utf-8")
                tree = ast.parse(text)
                constants = {}
                for node in tree.body:
                    if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)):
                        continue
                    for t in node.targets:
                        if isinstance(t, ast.Name) and isinstance(node.value.value, str):
                            constants[t.id] = node.value.value
                prompt_fn = next((n for n in tree.body
                                  if isinstance(n, ast.FunctionDef) and n.name == "make_system_prompt"),
                                 None)
                self.assertIsNotNone(prompt_fn, "%s has no make_system_prompt" % bot)
                src = ast.get_source_segment(text, prompt_fn)
                spoken = " ".join(v for name, v in constants.items()
                                  if name in src and not isinstance(v, type(None)))
                self.assertIn("TASK:", spoken,
                              "%s's chat prompt never names the marker the code splits on, so the "
                              "model never writes one and nothing is filed" % bot)
                self.assertIn("tasks.md", spoken,
                              "%s's prompt never says where filed work goes" % bot)


if __name__ == "__main__":
    unittest.main(verbosity=2)
