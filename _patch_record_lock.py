#!/usr/bin/env python3
"""One-off: put the shared-checkout lock around push_record's pull+push."""
import pathlib

P = pathlib.Path("/Users/lindsayridgeway/LLM/llm-symposium/channels/record_push.py")
t = P.read_text(encoding="utf-8")

old_imports = """import os
import subprocess
"""
new_imports = """import contextlib
import fcntl
import os
import subprocess
import time
"""
assert t.count(old_imports) == 1
t = t.replace(old_imports, new_imports)

anchor = '''DEFAULT_MESSAGE = "record(telegram): log live chat"
'''
assert t.count(anchor) == 1
t = t.replace(anchor, anchor + '''
# 2026-10-23 — the second writer into the shared checkout. `land_runs.py` takes
# `.git/symposium-land.lock` for the length of a landing (which includes two runs of the whole
# test suite); this function pulls and pushes in the same worktree from five bot processes. Put
# them under one lock or they interleave: the bots' merges show up in history as
# "Merge branch 'main' of https://github.com/..." (52 of them), and the append-only ledgers
# conflicted four times in one session on 2026-10-22.
#
# A record write must never block a reply, so this lock waits briefly and then gives up: the
# commit is already made, and the next landing sweeps `channels/conversation/` and
# `channels/telegram/` into its own commit by design (see RECORD_PREFIXES in land_runs.py).
LOCK_TIMEOUT = 15


@contextlib.contextmanager
def shared_checkout_lock(repo_dir, timeout=LOCK_TIMEOUT):
    """Yield True when the shared checkout is held, False when another body has it.

    Never raises: this module's contract is that recording cannot take the reply loop down.
    """
    lock_path = None
    fh = None
    try:
        git_dir = os.path.join(str(repo_dir), ".git")
        if not os.path.isdir(git_dir):
            yield True                     # not a checkout (a test fixture): nothing to lock
            return
        lock_path = os.path.join(git_dir, "symposium-land.lock")
        fh = open(lock_path, "a+")
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    yield False
                    return
                time.sleep(0.25)
        try:
            yield True
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
    except OSError:
        yield True                        # a lock that cannot be taken must not stop the write
    finally:
        if fh is not None:
            fh.close()
''')

old_remote = """        if remote:
            pull = ["pull", "--rebase" if rebase else "--no-rebase", "--no-edit", remote, branch]
            r = run(pull)
            result["pulled"] = r.returncode == 0
            if r.returncode != 0:
                result["errors"].append("pull: %s" % (r.stderr or "").strip()[:200])
            r = run(["push", remote, branch])
            result["pushed"] = r.returncode == 0
            if r.returncode != 0:
                result["errors"].append("push: %s" % (r.stderr or "").strip()[:200])
"""
new_remote = """        if remote:
            with shared_checkout_lock(repo_dir) as held:
                if not held:
                    result["pushed"] = False
                    result["errors"].append(
                        "push: shared checkout busy (another body is landing) — the record is "
                        "committed and the next landing carries it")
                    return result
                pull = ["pull", "--rebase" if rebase else "--no-rebase", "--no-edit",
                        remote, branch]
                r = run(pull)
                result["pulled"] = r.returncode == 0
                if r.returncode != 0:
                    result["errors"].append("pull: %s" % (r.stderr or "").strip()[:200])
                r = run(["push", remote, branch])
                result["pushed"] = r.returncode == 0
                if r.returncode != 0:
                    result["errors"].append("push: %s" % (r.stderr or "").strip()[:200])
"""
assert t.count(old_remote) == 1
t = t.replace(old_remote, new_remote)

P.write_text(t, encoding="utf-8")
print("patched", P)
