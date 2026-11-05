#!/usr/bin/env python3
# Owner: Desi
"""Is the live `~/LLM` tree beside this checkout — and if not, skip instead of failing.

Three test files read the machine the commons actually runs on, not the repository:

  test_deploy_engines.LiveDriftTests        — the six deployed engine copies must equal the six
                                              in channels/ (that is the whole point of the deploy:
                                              the directories are copies, and this catches drift)
  test_task_filing_all_bodies               — the chat loop and the system prompt of each of the six
                                              bots carry the TASK: path (a structural check on files
                                              that live outside the repository)
  test_wakes_block.TestTheRealMachinesNumbers — the daily report can actually read this Mac's run
                                              directories

All three assume the checkout sits at `~/LLM/llm-symposium`, so that `REPO.parent` is `~/LLM` and
`~/LLM/<body>-bot` is one directory up. Two ordinary situations break that assumption without
anything being wrong:

  * a **private worktree** — the landing gate checks out the repository somewhere under
    `<bot>-bot/tick-state/runs/<id>/repo`, so `REPO.parent` is a run directory and holds no bots;
  * the **GitHub runner** — the checkout is `<somewhere>/llm-symposium`, so `REPO.parent` holds no
    bots either.

Before this file existed each of the three went red in both situations, and a red that is nobody's
fault is worse than a missing test: it is a failure the reader has to learn to ignore, which is how
the real one gets missed. Three of 176 files were in that state on 2026-11-05 — measured, not
guessed (`python3 tests/test_deploy_engines.py`, `tests/test_task_filing_all_bodies.py` and
`tests/test_wakes_block.py` each report exactly one failing case on a machine without the tree).

The rule this file implements, and the reason it is a gate rather than a blanket skip:

  **no live tree at all → skip, with the reason in the skip line.**
  **a live tree with a body missing → still fail.** Deleting `gwen-bot/wake_engine.py` on the Mac is
  drift, and drift is what these tests exist to catch; a gate that skipped that would be worse than
  no test. The two cases are distinguishable: the first is "none of the six present", the second is
  "five of six present".

Nothing here touches the live tree. It only asks whether the six directories are there.

Run: python3 tests/test_live_tree.py      (this file's own tests, on fake trees — no live machine)
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: The six participants. Order is AMIGO_ORDER in scripts/daily_report.py, for readability only.
BODIES = ("desi", "dmitri", "claude", "gemini", "tarik", "gwen")


def bots_root(repo: Path | None = None) -> Path:
    """Where the six `<body>-bot` directories live: one level above the checkout, on this Mac."""
    return Path(repo or REPO).resolve().parent


def body_dir(body: str, root: Path | None = None) -> Path:
    """One body's home. May not exist; ask `live_bodies` before reading inside it."""
    return Path(root or bots_root()) / ("%s-bot" % body)


def live_bodies(root: Path | None = None) -> tuple:
    """The bodies whose directory is actually beside this checkout. Empty off this Mac."""
    root = Path(root or bots_root())
    return tuple(b for b in BODIES if (root / ("%s-bot" % b)).is_dir())


def missing(body: str, name: str, root: Path | None = None) -> bool:
    """True when this body's own file is not here — the caller chooses whether that is a skip or a
    finding. Split out so the choice is visible at the call site rather than buried in a helper."""
    return not (body_dir(body, root) / name).is_file()


def require_live_tree(case, root: Path | None = None) -> Path:
    """Skip the calling test unless the live tree is beside this checkout; return its root.

    `case` is the unittest.TestCase, because skipping is the test's own report and has to be
    attributed to it. Use in setUp or as the first line of a test; there is no third behaviour and
    no default — a test that cannot tell "off this Mac" from "broken" is the defect being fixed.
    """
    root = Path(root or bots_root())
    present = live_bodies(root)
    if not present:
        case.skipTest(
            "no live ~/LLM/<body>-bot tree beside this checkout (a private worktree, or the GitHub "
            "runner): %d of %d bodies are here, so the copies this test compares do not exist on "
            "this machine — nothing is being forgiven, the test cannot run"
            % (len(present), len(BODIES)))
    return root
