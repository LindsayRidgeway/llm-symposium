#!/usr/bin/env python3
"""The live-chat record must be committed whole, by the function that says it does.

Written 2026-09-26 by Desi. Origin: ``push_record()`` in the five bot processes staged
``channels/telegram/`` and nothing else, so the per-amigo conversation store — the file
the bot re-reads as its authoritative memory — was the one half of the record that no bot
versioned. It had to be committed by hand (4428122), with the defect written into the
commit message: *"(uncommitted since this morning; the bots commit channels/telegram/ but
not channels/conversation/)"*. Four hand-maintained copies of the function had also
drifted: tarik's staged both directories, desi's, claude's and gemini's staged one.

What it checks, in order:
  1. Both directories are staged and land in ONE commit — not two, so a crash cannot
     split the raw record from the conversation it belongs to.
  2. A second call with nothing new commits nothing. The old loop could not tell these
     apart: ``git commit`` with an empty stage exits non-zero and the exit code was
     dropped on the floor.
  3. A repository with neither directory yet is a no-op, not an error and not a crash.
  4. A change to the conversation store alone is still committed — the exact case that
     went unversioned.
  5. Against the real bot directories (section 6): does each bot's own ``push_record``
     stage both? Where a ``record_push.py`` copy exists, is it byte-identical to the
     canonical one?

Environment: sections 1–4 run anywhere (stdlib git plus this module). Section 5 needs the
bot directories, which live on the human's Mac and are not in this repository, so it
reports SKIP where they are absent. Section 6 is a REPORT and never fails: a test in this
repository must not go red over a file it cannot ship, and the three bot files that still
stage one directory are not this repository's to change — they are named in
to-do-lists/desi.md instead.

Run: python3 tests/test_record_push.py      (exit 0 pass, 1 fail)
"""
import ast
import re
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels.record_push import DEFAULT_PATHS, push_record  # noqa: E402

CANONICAL = REPO / "channels" / "record_push.py"
HOME = Path.home()
BOT_DIRS = {
    "desi": HOME / "LLM" / "desi-bot",
    "claude": HOME / "LLM" / "claude-bot",
    "gemini": HOME / "LLM" / "gemini-bot",
    "tarik": HOME / "LLM" / "tarik-bot",
    "dmitri": HOME / "LLM" / "dmitri-bot",
    "gwen": HOME / "LLM" / "gwen-bot",
}


def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert r.returncode == 0, "git %s failed: %s" % (" ".join(args), r.stderr.strip())
    return r.stdout


def _new_repo():
    tmp = tempfile.TemporaryDirectory()
    repo = Path(tmp.name)
    _git(repo, "init", "-q")
    _git(repo, "-c", "user.name=T", "-c", "user.email=t@t", "commit", "--allow-empty", "-qm", "init")
    return tmp, repo


def _write(repo, rel, text):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return rel


# ---------------------------------------------------------------- 1-4: the function

def test_both_directories_land_in_one_commit():
    tmp, repo = _new_repo()
    with tmp:
        raw = _write(repo, "channels/telegram/2026-09-26-000000-inbound-lindsay.md", "# in\n")
        conv = _write(repo, "channels/conversation/desi.md", "hello\n")
        res = push_record(repo, remote=None)
        assert res["errors"] == [], res["errors"]
        assert set(res["staged"]) == set(DEFAULT_PATHS), res["staged"]
        assert res["committed"] is True
        tracked = _git(repo, "ls-files").split()
        assert raw in tracked, tracked
        assert conv in tracked, tracked
        assert _git(repo, "rev-list", "--count", "HEAD").strip() == "2", "must be one commit, not two"


def test_a_second_call_with_nothing_new_commits_nothing():
    tmp, repo = _new_repo()
    with tmp:
        _write(repo, "channels/telegram/2026-09-26-000000-inbound-lindsay.md", "# in\n")
        _write(repo, "channels/conversation/desi.md", "hello\n")
        first = push_record(repo, remote=None)
        assert first["committed"] is True
        second = push_record(repo, remote=None)
        assert second["committed"] is False, "an empty stage is not a commit"
        assert second["errors"] == [], second["errors"]
        assert _git(repo, "rev-list", "--count", "HEAD").strip() == "2"


def test_missing_directories_are_a_noop_not_an_error():
    tmp, repo = _new_repo()
    with tmp:
        res = push_record(repo, remote=None)
        assert res["staged"] == [], res["staged"]
        assert res["committed"] is False
        assert res["errors"] == [], res["errors"]


def test_conversation_store_alone_is_still_committed():
    """The defect, stated as its own check: only the conversation store changed."""
    tmp, repo = _new_repo()
    with tmp:
        conv = "channels/conversation/desi.md"
        _write(repo, conv, "first\n")
        push_record(repo, remote=None)
        _write(repo, conv, "first\nsecond\n")          # append only; no new telegram file
        res = push_record(repo, remote=None)
        assert res["committed"] is True, "the conversation store must be versioned"
        assert conv in _git(repo, "ls-files").split()
        assert "second" in _git(repo, "show", "HEAD:" + conv)


# ---------------------------------------------------- 5: the real bot directories

_ADD_RE = re.compile(r'"add"\s*,(?P<rest>.*)', re.S)
_QUOTED = re.compile(r'"([^"]+)"')


def _push_record_block(bot_py):
    m = re.search(r"^def push_record\(.*?(?=^def |\Z)", bot_py, re.S | re.M)
    return m.group(0) if m else ""


def _staged_by_bot(bot_py):
    """What the bot's own push_record stages — followed through the delegation.

    2026-09-26: all four bots now call ``record_push.push_record()`` instead of listing the
    paths inline, so a checker that only reads ``git add`` literals reported "read it by hand"
    for every one of them — a check that had gone blind and still said it had looked. A
    delegating bot is reported as staging the canonical module's own default paths, which is
    exactly what it will do at runtime (the test above pins the copy to this file byte for
    byte, so reading the paths from here is reading the bot's).
    """
    block = _push_record_block(bot_py)
    if "record_push" in block:
        return [p for p in DEFAULT_PATHS]
    out = []
    for line in block.splitlines():
        if '"add"' not in line:
            continue
        out.extend(t for t in _QUOTED.findall(line) if t != "add" and "/" in t)
    return out


def test_bot_copies_match_the_canonical_module():
    """Where a record_push.py copy exists next to a bot, it must be this file exactly."""
    checked = 0
    for name, d in sorted(BOT_DIRS.items()):
        copy = d / "record_push.py"
        if not copy.exists():
            print("  SKIP %s-bot: no record_push.py copy (nothing to compare)" % name)
            continue
        checked += 1
        assert copy.read_bytes() == CANONICAL.read_bytes(), \
            "%s-bot/record_push.py has drifted from channels/record_push.py" % name
        print("  OK   %s-bot/record_push.py is byte-identical to the canonical module" % name)
    if checked == 0:
        print("  SKIP no bot directories present (fork or CI) — nothing to compare")


def test_report_which_bots_stage_the_conversation_store():
    """REPORT, never fails: the bot files are not this repository's to change.

    A red test here would block every landing in a repository that cannot fix the cause.
    """
    if not any(d.is_dir() for d in BOT_DIRS.values()):
        print("  SKIP no bot directories present (fork or CI)")
        return
    for name, d in sorted(BOT_DIRS.items()):
        bot_py = d / "bot.py"
        if not bot_py.exists():
            print("  SKIP %s-bot: no bot.py" % name)
            continue
        staged = _staged_by_bot(bot_py.read_text(encoding="utf-8", errors="replace"))
        if not staged:
            print("  ?    %s-bot: no push_record()/git add found — read it by hand" % name)
        elif all(p in staged for p in DEFAULT_PATHS):
            print("  OK   %s-bot stages %s" % (name, ", ".join(staged)))
        else:
            print("  DRIFT %s-bot stages %s — conversation store is NOT versioned by it "
                  "(needs %s; see to-do-lists/desi.md)" % (name, ", ".join(staged), DEFAULT_PATHS[1]))


# -------------------------------- 7-10: the shared checkout is not a workspace

class _Origin:
    """A bare origin, a shared clone and a rival clone — the three bodies of every real race."""


def _origin_fixture():
    f = _Origin()
    f.tmp = tempfile.TemporaryDirectory()
    f.root = Path(f.tmp.name)
    f.origin = f.root / "origin.git"
    f.shared = f.root / "shared"
    f.rival = f.root / "rival"
    subprocess.run(["git", "init", "-q", "-b", "main", "--bare", str(f.origin)],
                   capture_output=True, check=True)
    for path in (f.shared, f.rival):
        subprocess.run(["git", "clone", "-q", str(f.origin), str(path)],
                       capture_output=True, check=True)
    return f


def _seed(f):
    _write(f.shared, "agenda/36.md", "one\ntwo\nthree\n")
    _write(f.shared, "channels/conversation/desi.md", "hello\n")
    _git(f.shared, "add", "-A")
    _git(f.shared, "-c", "user.name=T", "-c", "user.email=t@t", "commit", "-qm", "base")
    _git(f.shared, "push", "-q", "origin", "main")


def _rival_edit(f, rel, text, message="rival"):
    _git(f.rival, "pull", "-q", "origin", "main")
    _write(f.rival, rel, text)
    # `-a` alone misses a new file, and a telegram message *is* a new file.
    _git(f.rival, "add", "-A")
    _git(f.rival, "-c", "user.name=R", "-c", "user.email=r@r", "commit", "-qm", message)
    _git(f.rival, "push", "-q", "origin", "main")


def test_an_uncommitted_edit_survives_a_record_push():
    """The one that matters: a bot recording a message must not take a session's work away.

    The rival edits **the same file the session is editing**, which is the case that made
    `pull --rebase --autostash` leave conflict markers in the tree and the work in an anonymous
    stash entry. Measured on the live checkout on 2026-11-02: four `autostash` entries, the newest
    a session's edit of `agenda/36` one day old and still unrestored.
    """
    f = _origin_fixture()
    with f.tmp:
        _seed(f)
        _rival_edit(f, "agenda/36.md", "one\nTWO BY THE RIVAL\nthree\n")
        _write(f.shared, "agenda/36.md", "one\ntwo\nthree\nMY SESSION EDIT\n")
        _write(f.shared, "channels/telegram/2026-11-02-230000-inbound-human.md", "# human\n")
        head_before = _git(f.shared, "rev-parse", "HEAD").strip()

        res = push_record(f.shared, remote="origin")

        assert res["errors"] == [], res["errors"]
        assert res["pushed"] is True, res
        assert (f.shared / "agenda/36.md").read_text(encoding="utf-8").endswith("MY SESSION EDIT\n"), \
            "a record push took the session's uncommitted line out of the tree"
        assert _git(f.shared, "stash", "list").strip() == "", \
            "a record push put somebody's work in the stash"
        assert _git(f.shared, "rev-parse", "HEAD").strip() == head_before, \
            "a record push moved the shared checkout's HEAD"


def test_the_record_lands_on_origin_although_the_tree_is_not_moved():
    """Refusing to move the tree is not refusing to deliver. Origin is the record."""
    f = _origin_fixture()
    with f.tmp:
        _seed(f)
        _rival_edit(f, "agenda/36.md", "one\nTWO BY THE RIVAL\nthree\n")
        _write(f.shared, "agenda/36.md", "one\ntwo\nthree\nMY SESSION EDIT\n")
        _write(f.shared, "channels/conversation/desi.md", "hello\nmy message\n")
        _write(f.shared, "channels/telegram/2026-11-02-230500-inbound-human.md", "# human\n")

        res = push_record(f.shared, remote="origin")

        assert res["pushed"] is True, res
        names = _git(f.origin, "ls-tree", "-r", "--name-only", "main").split()
        assert "channels/telegram/2026-11-02-230500-inbound-human.md" in names, names
        assert "my message" in _git(f.origin, "show", "main:channels/conversation/desi.md"), \
            "the conversation store, the file a body re-reads as its memory, did not land"


def test_a_rejected_push_is_retried_in_the_worktree_not_the_shared_checkout():
    """Origin moves between our fetch and our push: fetch, rebase, retry — in the throwaway tree."""
    f = _origin_fixture()
    with f.tmp:
        _seed(f)
        _write(f.shared, "channels/telegram/2026-11-02-231000-inbound-human.md", "# mine\n")
        raced = {"done": False}

        def runner(cmd):
            if "push" in cmd and not raced["done"]:
                raced["done"] = True
                _rival_edit(f, "channels/telegram/2026-11-02-231001-inbound-rival.md",
                            "# rival\n", message="rival telegram")
            return subprocess.run(cmd, capture_output=True, text=True)

        res = push_record(f.shared, remote="origin", runner=runner)

        assert raced["done"], "the fixture never produced the race it claims to test"
        assert res["pushed"] is True, res
        names = _git(f.origin, "ls-tree", "-r", "--name-only", "main").split()
        assert "channels/telegram/2026-11-02-231000-inbound-human.md" in names, names
        assert "channels/telegram/2026-11-02-231001-inbound-rival.md" in names, \
            "the record that was already on origin was lost by the retry"
        assert _git(f.shared, "stash", "list").strip() == "", "the retry used the stash"


FORBIDDEN_IN_PUSH = ("pull", "stash", "checkout", "reset", "clean")


def _git_arguments(path):
    """Every non-docstring string literal in the module.

    Deliberately *not* "every argument of a call": the first version of this check did that, and it
    passed on the code it was written to catch, because the old code built the command as
    ``pull = ["pull", "--rebase", …]`` and passed the *variable* to the runner. A check that reads
    the shape of an expression rather than the words in it is a check that goes blind silently.

    Docstrings are excluded by identity, because the module explains at length why `pull`, `stash`,
    `checkout` and `reset` are not there, and a check that reads the explanation as the offence
    gets weakened within a day.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        body = getattr(node, "body", [])
        if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            docstrings.add(id(body[0].value))
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings]


def test_the_push_path_cannot_pull_stash_checkout_or_reset():
    """Structural, over the canonical module and every bot copy that exists."""
    targets = [("canonical", CANONICAL)]
    targets += [("%s-bot" % n, d / "record_push.py") for n, d in sorted(BOT_DIRS.items())
                if (d / "record_push.py").exists()]
    checked = 0
    for name, path in targets:
        checked += 1
        args = _git_arguments(path)
        for bad in FORBIDDEN_IN_PUSH:
            assert bad not in args, \
                "%s issues `git %s` — the shared checkout is not a workspace" % (name, bad)
        if "merge" in args:
            assert "--ff-only" in args, \
                "%s merges in the shared checkout without --ff-only" % name
    assert checked >= 1, "no record_push.py was found to check"
    print("  OK   %d copy/copies cannot pull, stash, check out or reset" % checked)


def _run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            print("PASS %s" % t.__name__)
            passed += 1
        except Exception:
            print("FAIL %s" % t.__name__)
            traceback.print_exc()
    print("\n%d/%d tests passed" % (passed, len(tests)))
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(_run_all())
