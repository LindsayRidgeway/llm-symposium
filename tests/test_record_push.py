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
