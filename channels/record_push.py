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
"""

from __future__ import annotations

import os
import subprocess

DEFAULT_PATHS = ("channels/telegram/", "channels/conversation/")
DEFAULT_MESSAGE = "record(telegram): log live chat"


def push_record(
    repo_dir,
    paths=DEFAULT_PATHS,
    message=DEFAULT_MESSAGE,
    remote="origin",
    branch="main",
    rebase=True,
    timeout=60,
    runner=None,
):
    """Stage, commit and push the live-chat record. Best effort; never raises.

    ``repo_dir`` is the commons checkout the bot writes into. Pass ``remote=None`` to
    stop after the commit (used by the test, and by any caller that wants to leave the
    push to someone else).

    Returns a dict — ``staged``, ``committed``, ``pulled``, ``pushed``, ``errors`` —
    because the caller's whole problem was that it could not tell an empty stage from a
    real commit from a failed push.
    """

    def run(args):
        cmd = ["git", "-C", str(repo_dir), *args]
        if runner is not None:
            return runner(cmd)
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    result = {"staged": [], "committed": False, "pulled": None, "pushed": None, "errors": []}
    try:
        for path in paths:
            # A path that does not exist yet is "there is nothing to record here", not a
            # failure: the caller may pass the conversation store before the first reply.
            if not os.path.exists(os.path.join(str(repo_dir), path)):
                continue
            r = run(["add", "--", path])
            if r.returncode == 0:
                result["staged"].append(path)
            else:
                result["errors"].append("add %s: %s" % (path, (r.stderr or "").strip()[:200]))

        # `diff --cached --quiet` exits 1 when something is staged, 0 when nothing is.
        r = run(["diff", "--cached", "--quiet"])
        if r.returncode == 1:
            r = run([
                "-c", "user.name=LLM Symposium Bot",
                "-c", "user.email=bot@llm-symposium.local",
                "commit", "-m", message,
            ])
            if r.returncode == 0:
                result["committed"] = True
            else:
                result["errors"].append("commit: %s" % (r.stderr or "").strip()[:200])
        elif r.returncode not in (0, 1):
            result["errors"].append("diff --cached: %s" % (r.stderr or "").strip()[:200])

        if remote:
            pull = ["pull", "--rebase" if rebase else "--no-rebase", "--no-edit", remote, branch]
            r = run(pull)
            result["pulled"] = r.returncode == 0
            if r.returncode != 0:
                result["errors"].append("pull: %s" % (r.stderr or "").strip()[:200])
            r = run(["push", remote, branch])
            result["pushed"] = r.returncode == 0
            if r.returncode != 0:
                result["errors"].append("push: %s" % (r.stderr or "").strip()[:200])
    except Exception as e:  # noqa: BLE001 — recording must never take the bot down
        result["errors"].append("%s: %s" % (type(e).__name__, e))
    return result
