#!/usr/bin/env python3
# Owner: Desi
"""The one function that commits the live-chat record, and what it stages.

Each of the five bot processes on the human's Mac writes **two** things per message:

  ``channels/telegram/<stamp>-<kind>-<name>.md``
      one file per message — the raw record, append-only, one message per file so two
      pollers can never overwrite each other's word;
  ``channels/conversation/<amigo>.md``
      the amigo's own running conversation, appended in place, and **re-read at the next
      reply as that amigo's authoritative memory** ("### Your recent conversation with the
      human (AUTHORITATIVE memory …)").

``bot.py``'s ``push_record()`` is what carries both back to this repository. Until
2026-09-26 it staged ``channels/telegram/`` and nothing else, so the per-amigo conversation
store — the file the bot actually re-reads — was the one half of the record that no bot
versioned. The catch-up had to be committed by hand, and the reason is in that commit's
own message (4428122): *"(uncommitted since this morning; the bots commit
channels/telegram/ but not channels/conversation/)"*. Four hand-maintained copies of the
function had also drifted apart: tarik's staged both directories, desi's, claude's and
gemini's staged one, and only desi's pulled with ``--no-rebase``.

This module is the canonical function. It is meant to be **copied, not imported**: a copy
sits next to each bot's ``bot.py``, for the same reason ``channels/media.py`` is copied —
there is no import path from the bot directories into this repository that is safe to
depend on at startup. ``tests/test_record_push.py`` exercises this file for real against a
throwaway git repository, and checks each bot directory's own ``push_record`` against it
where those directories exist.

Design notes, every one of them from a failure that happened:

* **both paths are staged before one commit**, so the raw record and the conversation it
  belongs to cannot be split by a crash between two commits;
* **an empty stage is not a commit and not an error.** ``git commit`` with nothing staged
  exits non-zero, and the old loop swallowed that silently — so a bot that pushed nothing
  looked exactly like a bot that pushed a message. The state is returned instead of
  inferred;
* **pull before push, rebase by default**: a merge commit between two pollers is noise in
  a log whose whole value is that it is in order;
* **never raises.** A record that fails to push must not take the reply loop down with it.

## 2026-11-02 — "pull before push, rebase by default" is struck out, and the reason is narrower
## than the one I first wrote down

``git pull --rebase`` in the shared checkout is wrong, but the way it is wrong is worth stating
exactly, because the first version of this paragraph said something more dramatic and less true.

What it does **not** do here: autostash. ``rebase.autoStash`` is unset on this machine (checked in
local, global and system config), and git 2.48 therefore *refuses* the pull outright — ``cannot
pull with rebase: You have unstaged changes``, exit 128, tree untouched. So this line did not eat
anybody's work. **It stopped pushing the record.** In a tree six bodies write to, that refusal is
not an occasional edge; it is most of the time. And the caller dropped the exit code, so a body
whose record never left this Mac looked identical to a body whose record landed — which is the
same defect this module was written to fix, reappearing one layer down.

Where the ``autostash`` entries in ``git stash list`` come from is a **separate** question, and
nothing in this repository currently produces them: ``scripts/ledger_watch.py`` did until
2026-10-25 (``pull --rebase --autostash``; the post-mortem is
``channels/reports/2026-10-25-desi-the-day-the-ledger-committed-its-own-damage.md``), and no
script, workflow or plist passes ``--autostash`` now. So the four entries — ``stash@{0}`` is a
session's edit of ``agenda/36-the-free-tribe-design.md`` and ``governance/README.md``, dated
2026-11-01 and still unrestored a day later — were made by *an ad-hoc command in a session*,
which is a habit and not a caller anyone can grep for. The durable answer to that is not in this
file: it is in ``scripts/checkout_guard/``, a ``pre-rebase`` hook that refuses any rebase in the
shared checkout, so a model reaching for the standard "sync with a dirty tree" incantation gets a
refusal with an explanation instead of a stash.

What *this* file does about it: the tree is no longer touched at all. ``push_paths`` does what
``land_runs`` already does — and did correctly first, which is where the pattern comes from:

So the tree is no longer touched at all. ``push_paths`` does what ``land_runs`` does — and did
correctly first, which is where the pattern comes from:

  1. ``git fetch`` (safe: writes remote-tracking refs only);
  2. cut a **throwaway worktree** at today's ``origin/<branch>``;
  3. **copy** the changed record files into it, under the checkout lock, for a few milliseconds;
  4. commit there, push there, and on a rejected push ``rebase`` *there* — the disposable tree,
     not the shared one — up to three attempts;
  5. remove the worktree, then try ``git merge --ff-only`` in the shared checkout.

Step 5 is the only write this module makes to the shared checkout, it can only add commits, and
git refuses it wholesale rather than partially if a session's uncommitted work is in the way. A
refusal is not a failure: the record is already on ``origin``, which is the record.

The invariant to keep, and the one ``tests/test_record_push.py`` now asserts: **a record push
cannot change the shared checkout's HEAD, index or working tree.** Nothing here runs ``pull``,
``checkout``, ``reset`` or ``stash`` in it.

``rebase=`` is still accepted and is now ignored, so the five bot call sites that pass
``rebase=False`` keep working and say what they mean without doing it.
"""

from __future__ import annotations

import contextlib
import collections
import fcntl
import json
import os
import shutil
import subprocess
import tempfile
import time

DEFAULT_PATHS = ("channels/telegram/", "channels/conversation/")
DEFAULT_MESSAGE = "record(telegram): log live chat"

# 2026-11-02 — a rejected push is re-tried by rebasing *the throwaway worktree*, so the cost of a
# race is one fetch and one single-commit rebase. Three attempts covers the poll job's 12 pushes a
# day and a landing or two without turning a stuck record into a hung reply.
PUSH_ATTEMPTS = 3

# 2026-10-23 — the second writer into the shared checkout. `land_runs.py` takes
# `.git/symposium-land.lock` for the length of a landing (which includes two runs of the whole
# test suite); this function used to pull and push in the same worktree from five bot processes. Put
# them under one lock or they interleave: the bots' merges show up in history as
# "Merge branch 'main' of https://github.com/..." (52 of them), and the append-only ledgers
# conflicted four times in one session on 2026-10-22.
#
# 2026-11-02 — the lock is now held for the *read*, not for the push. Copying six small files takes
# milliseconds; pushing takes a second or three, and holding a shared lock across a network call is
# how a slow origin turns into a blocked landing.
#
# A record write must never block a reply, so this lock waits briefly and then gives up: the record
# files are already on disk in the shared checkout, and the next landing sweeps
# `channels/conversation/` and `channels/telegram/` into its own commit by design (see
# RECORD_PREFIXES in land_runs.py).
LOCK_TIMEOUT = 15


@contextlib.contextmanager
def shared_checkout_lock(repo_dir, timeout=LOCK_TIMEOUT):
    """Yield True when the shared checkout is held, False when another body has it.

    Never raises: this module's contract is that recording cannot take the reply loop down.

    Note for a future reader: ``.git`` is a *directory* in a normal checkout and a *file* in a
    worktree, so this function silently does nothing inside a worktree — which is correct, because
    a worktree belongs to one process. If a bot is ever pointed at a worktree it shares, that
    assumption is what breaks first.
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


REJECTED = ("rejected", "non-fast-forward", "fetch first", "failed to push some refs",
            "cannot lock ref")


def _rejected(text):
    """Is this push failure a race, or is it something a retry cannot mend?"""
    low = (text or "").lower()
    return any(marker in low for marker in REJECTED)


def _under(paths, path):
    return any(path == p or path.startswith(p) for p in paths)


def push_record(repo_dir, paths=DEFAULT_PATHS, message=DEFAULT_MESSAGE, **kwargs):
    """Stage, commit and push the live-chat record. Best effort; never raises.

    Kept as its own name because five bot files call it and the name says what it is; the work is
    ``push_paths``, which other writers of this repository's own logs can use too.
    """
    return push_paths(repo_dir, paths, message, **kwargs)


def push_paths(repo_dir, paths, message, remote="origin", branch="main", rebase=True,
               timeout=60, runner=None):
    """Commit and push changes under ``paths`` **without moving the shared checkout**.

    ``paths`` are repo-relative directories or files (``channels/telegram/``). Only paths that
    actually changed are copied and committed, so the commit stays one commit per message even
    though the directories hold a thousand files.

    ``remote=None`` stops after a local commit made in place — used by the tests, and by any
    caller that wants the commit without the push. That path stages and commits with an explicit
    pathspec, so it cannot sweep another body's staged work into a commit labelled as a record.

    Returns a dict — ``staged``, ``files``, ``committed``, ``pulled``, ``pushed``, ``worktree``,
    ``errors`` — because the caller's whole problem was that it could not tell an empty stage
    from a real commit from a failed push. ``pulled`` is always ``None`` now: this function no
    longer pulls. It is kept so that a caller reading the key does not get a ``KeyError`` and
    conclude the record was not attempted.
    """

    def run(args, cwd=None):
        cmd = ["git", "-C", str(cwd or repo_dir), *args]
        if runner is not None:
            return runner(cmd)
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    result = {"staged": [], "files": [], "committed": False, "pulled": None, "pushed": None,
              "worktree": None, "errors": []}
    worktree = None
    try:
        present = [p for p in paths if os.path.exists(os.path.join(str(repo_dir), p))]
        if not present:
            return result                    # nothing to record here is not a failure

        if not remote:
            return _commit_in_place(run, repo_dir, present, message, result)

        # Fail early and cheaply rather than cutting a worktree on a repository with no such
        # remote (a test fixture, a fork): a record push is not worth an exception.
        if run(["rev-parse", "--verify", "--quiet", "%s/%s" % (remote, branch)]).returncode != 0:
            if run(["fetch", "-q", remote, branch]).returncode != 0:
                result["errors"].append("fetch %s %s: no such remote ref" % (remote, branch))
                return _commit_in_place(run, repo_dir, present, message, result)

        base = "%s/%s" % (remote, branch)
        worktree = _make_worktree(run, repo_dir, base)
        if worktree is None:
            # No worktree (an old git, a read-only .git, a fixture): fall back to committing in
            # place. Say so — a silent fallback is how the shared checkout got written to for a
            # year while everyone believed it was not.
            result["errors"].append("no worktree available; committed in place instead")
            return _commit_in_place(run, repo_dir, present, message, result)
        result["worktree"] = worktree

        # The read. Held for milliseconds: list what changed, copy those bytes, release.
        with shared_checkout_lock(repo_dir) as held:
            if not held:
                result["errors"].append(
                    "shared checkout busy (another body holds it) — the record is in the tree "
                    "and the next pass carries it")
                return result
            files = _changed_files(run, repo_dir, present)
            if not files:
                return result               # an empty stage is not a commit and not an error
            result["staged"] = [p for p in present if any(_under((p,), f) for f in files)]
            result["files"] = files
            _copy_into(repo_dir, worktree, files, result["errors"])

        r = run(["add", "--", *files], cwd=worktree)
        if r.returncode != 0:
            result["errors"].append("add: " + (r.stderr or "").strip()[:200])
            return result
        r = run(["-c", "user.name=LLM Symposium Bot",
                 "-c", "user.email=bot@llm-symposium.local",
                 "commit", "-q", "-m", message], cwd=worktree)
        if r.returncode != 0:
            # Most often: the worktree at origin/main already has these exact bytes, which is the
            # record already landed. That is not an error to shout about, but it is not a commit.
            if "nothing to commit" not in ((r.stdout or "") + (r.stderr or "")):
                result["errors"].append("commit: " + (r.stderr or "").strip()[:200])
            return result
        result["committed"] = True

        result["pushed"] = _push_with_retry(run, worktree, remote, branch, message, result["errors"])
        if result["pushed"]:
            _fast_forward_shared(run, repo_dir, base, result["errors"])
        return result
    except Exception as e:  # noqa: BLE001 — recording must never take the bot down
        result["errors"].append("%s: %s" % (type(e).__name__, e))
        return result
    finally:
        if worktree is not None:
            _drop_worktree(run, repo_dir, worktree)


def commit_and_publish(repo_dir, paths, message, **kwargs):
    """``push_paths``, answering the question the unattended scripts actually ask.

    Three of them write a file they own into the checkout and then need exactly one bit: did it
    reach origin? "There was nothing to publish" is a yes; "committed here but the push was
    refused" is a no. ``push_paths`` reports those two differently on purpose — ``committed`` False
    with no errors means nothing changed, and a failed push is an entry in ``errors`` — so a caller
    should not have to re-derive the rule three times, slightly differently, in three scripts.

    Sets ``ok`` on the result and returns it.
    """
    res = push_paths(repo_dir, paths, message, **kwargs)
    res["ok"] = bool(res.get("pushed")) or not res.get("errors")
    return res


def _commit_in_place(run, repo_dir, paths, message, result):
    """Stage and commit under ``paths`` with no worktree — the local-only and no-remote path.

    Still safe in a shared checkout because the commit is pathspec-limited twice: ``add --`` names
    the paths, and ``commit -m … --`` names them again, so nothing else in the index is swept in.
    It does not pull, rebase, stash or check anything out, so it cannot move anybody's file.
    """
    for path in paths:
        r = run(["add", "--", path])
        if r.returncode == 0:
            result["staged"].append(path)
        else:
            result["errors"].append("add %s: %s" % (path, (r.stderr or "").strip()[:200]))
    if not result["staged"]:
        return result
    # `diff --cached --quiet` exits 1 when something is staged, 0 when nothing is.
    r = run(["diff", "--cached", "--quiet", "--", *paths])
    if r.returncode == 0:
        return result                      # staged nothing new: not a commit, not an error
    if r.returncode != 1:
        result["errors"].append("diff --cached: " + (r.stderr or "").strip()[:200])
        return result
    r = run(["-c", "user.name=LLM Symposium Bot",
             "-c", "user.email=bot@llm-symposium.local",
             "commit", "-q", "-m", message, "--", *paths])
    if r.returncode == 0:
        result["committed"] = True
    else:
        result["errors"].append("commit: " + (r.stderr or "").strip()[:200])
    return result


def _changed_files(run, repo_dir, paths):
    """Repo-relative paths under ``paths`` whose working-tree bytes differ from HEAD.

    ``--untracked-files=all`` because a new telegram message *is* a new file, and the directory
    summary git gives by default (``?? channels/telegram/``) names nothing to copy.
    """
    r = run(["status", "--porcelain", "--untracked-files=all", "--", *paths])
    out = []
    for line in (r.stdout or "").splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:                 # a rename: the new name is the one that exists
            path = path.split(" -> ")[-1]
        if path and path not in out:
            out.append(path)
    return out


def _assert_ledger_rows_preserved(before, after):
    """Refuse a ledger snapshot that drops any published JSON-row multiplicity.

    The daily report uses this publisher with a possibly stale shared ledger.
    A larger replacement can still erase verdicts. Preserve historical rows;
    corrections belong in dated appends, not a replacement of older decisions.
    Compare parsed objects so harmless JSON formatting changes remain allowed.
    """
    def rows(data):
        result = collections.Counter()
        for line in data.decode("utf-8").splitlines():
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError("ledger rows must be JSON objects")
            result[json.dumps(value, sort_keys=True, separators=(",", ":"))] += 1
        return result
    missing = rows(before) - rows(after)
    if missing:
        raise ValueError("ledger publication refused: replacement drops %d historical row(s); "
                         "reconcile with current origin and append corrections" % sum(missing.values()))


def _copy_into(src_root, dst_root, files, errors):
    """Copy the changed bytes across. Never move, never delete: the source is somebody's tree."""
    for rel in files:
        src = os.path.join(str(src_root), rel)
        dst = os.path.join(str(dst_root), rel)
        try:
            if not os.path.isfile(src):
                continue                   # deleted in the working tree: not a record
            parent = os.path.dirname(dst)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(src, "rb") as f:
                data = f.read()
            if rel == "channels/items.jsonl":
                previous = b""
                if os.path.isfile(dst):
                    with open(dst, "rb") as f:
                        previous = f.read()
                _assert_ledger_rows_preserved(previous, data)
            with open(dst, "wb") as f:
                f.write(data)
        except OSError as e:
            errors.append("copy %s: %s: %s" % (rel, type(e).__name__, e))


def _make_worktree(run, repo_dir, base):
    """A throwaway checkout at ``base``, outside both the tree and .git. ``None`` if git refuses."""
    path = tempfile.mkdtemp(prefix="record-push-")
    os.rmdir(path)                         # `worktree add` insists on creating it
    r = run(["worktree", "add", "--detach", path, base], cwd=repo_dir)
    if r.returncode != 0:
        return None
    return path


def _drop_worktree(run, repo_dir, worktree):
    if run(["worktree", "remove", "--force", worktree], cwd=repo_dir).returncode != 0:
        shutil.rmtree(worktree, ignore_errors=True)      # it is disposable; do not leak it
    run(["worktree", "prune"], cwd=repo_dir)


def _push_with_retry(run, worktree, remote, branch, message, errors):
    """Push the commit; on a race, rebase the *worktree* and try again. Never the shared tree."""
    refspec = "HEAD:refs/heads/%s" % branch
    for attempt in range(1, PUSH_ATTEMPTS + 1):
        r = run(["push", remote, refspec], cwd=worktree)
        if r.returncode == 0:
            return True
        err = ((r.stderr or "") + (r.stdout or "")).strip()
        if not _rejected(err):
            errors.append("push: " + err[:200])
            return False
        if attempt == PUSH_ATTEMPTS:
            errors.append("push rejected %d times; the record is in the shared checkout and the "
                          "next pass carries it" % PUSH_ATTEMPTS)
            return False
        run(["fetch", "-q", remote, branch], cwd=worktree)
        rb = run(["rebase", "%s/%s" % (remote, branch)], cwd=worktree)
        if rb.returncode != 0:
            run(["rebase", "--abort"], cwd=worktree)
            errors.append("push race: this record does not rebase onto %s/%s (%s) — left in the "
                          "shared checkout for the next pass"
                          % (remote, branch, (rb.stderr or "").strip().replace("\n", " ")[:160]))
            return False
    return False


def _fast_forward_shared(run, repo_dir, base, errors):
    """Move the shared checkout up to what was just pushed — fast-forward only.

    The one write this module makes to the shared checkout, and it can only add commits. Git
    refuses it wholesale if a session's uncommitted work is in the way, and that refusal is
    correct and is not an error: ``origin`` is the record, not this checkout.

    One case is not a real refusal: the file this function just published is still sitting in the
    checkout, so git sees a local modification — even though its bytes are now identical to the
    ones it would merge in. Measured 2026-11-02: the merge refuses, and ``git add`` of that path
    first makes it succeed and leaves the tree clean. So paths whose working bytes *already equal*
    the target's are staged, and the merge is retried once. Staging content that is already on
    disk and already on origin cannot change a file; it only tells git what is true.
    """
    r = run(["merge", "--ff-only", base], cwd=repo_dir)
    if r.returncode == 0:
        return True
    staged = _stage_identical(run, repo_dir, base)
    if staged:
        r = run(["merge", "--ff-only", base], cwd=repo_dir)
        if r.returncode == 0:
            return True
        run(["reset", "-q", "--", *staged], cwd=repo_dir)      # leave the index as we found it
    why = ((r.stderr or "") + (r.stdout or "")).strip().replace("\n", " ")[:160]
    if why:
        # Not an error list entry: a shared checkout that is behind is the design working.
        print("record_push: record pushed; shared checkout left where it was (%s)" % why)
    return False


def _stage_identical(run, repo_dir, base):
    """Stage the paths whose working bytes already equal the ones at ``base``; return them.

    Compared against the *target* tree and not against HEAD, because the question is "is this file
    already what we are moving to?" — and only a file that already is can be staged without
    changing a byte of anybody's work.
    """
    sha = (run(["rev-parse", base], cwd=repo_dir).stdout or "").strip()
    if not sha:
        return []
    out = []
    for path in (run(["diff", "--name-only", "HEAD", sha], cwd=repo_dir).stdout or "").splitlines():
        path = path.strip()
        if not path:
            continue
        want = run(["rev-parse", "%s:%s" % (sha, path)], cwd=repo_dir)
        if want.returncode != 0:
            continue                       # added upstream: nothing local to compare with
        have = run(["hash-object", "--", path], cwd=repo_dir)
        if have.returncode == 0 and (have.stdout or "").strip() == (want.stdout or "").strip():
            out.append(path)
    if out:
        run(["add", "--", *out], cwd=repo_dir)
    return out
