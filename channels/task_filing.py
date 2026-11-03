#!/usr/bin/env python3
# Owner: Desi
"""Filing a human's request into the commons ledger — one implementation, six bodies.

Why this exists (2026-11-03). Only two of the six Telegram bodies could file work at all.
`desi-bot` and `dmitri-bot` carried a private copy of `extract_tasks` / `file_tasks`; the other
four carried neither the function nor the sentence in the system prompt that tells a model the
`TASK:` marker exists. So the founder's own test of the arrangement — *judge it by whether
tasks.md has my name in it* — was true of two bodies out of six, and a request agreed in
Claude's, Gemini's, Tarik's or Gwen's chat was invisible to every wake, to the other amigos, and
to him.

The alternative to this module was a fifth and sixth copy of the same 120 lines. Two things
were already wrong with copying. The copies drift (this repository keeps a drift test for
`record_push.py` for exactly that reason, and it has caught a real drift once). And it is the
copy in each bot dir, not the canonical one in `channels/`, that runs — so a fix landed here
reaches nobody until somebody remembers to copy it six times. One file, copied byte-identically
into all six dirs, with a test that fails when any copy differs, is the same bargain as
`record_push.py`.

Kept from the 2026-09-21 original, because each was a defect once:

  - **the top of the ledger**, because a reader's copy is truncated (a wake takes ~2500
    characters, the context digest 2000) and an item appended to the end of a long file is
    invisible to it. Appending at the end reproduces the exact defect this cures;
  - **committed and pushed**, because a wake clones the committed repository. A task written but
    not pushed is the same as a task never written;
  - **a section of its own**, because `scripts/sweep_risks.py` regenerates the open-risks part of
    the ledger and preserves only the sections the amigos place in it.

Added since, from damage rather than from taste:

  - **the read and the write share the checkout lock**, and the write is refused and re-spliced
    if the bytes changed underneath it. This function rewrites the whole file from a buffer it
    read earlier, which is how `channels/tasks.md` lost 54 lines twice on 2026-11-02 — not a
    merge conflict, a file replacement, so no merge tool and no test ever saw it.
  - **the publish goes through `record_push.push_paths`**, which commits and pushes in a
    disposable worktree and only fast-forwards the shared checkout. The commands this function
    used to run (add, commit, `pull --no-rebase`, push) ran inside the shared tree and outside the
    lock it had just taken.

Not in this module, and named so it is not mistaken for done: `channels/task_ledger.py` holds the
identity rule the ledger needs before it can stop filing the same request twice (measured
2026-09-25: one item filed nine times, four times for another), and `file_tasks` here still does
not call it.
"""
import contextlib
import logging
import os
import re

log = logging.getLogger("task_filing")

# The marker a model writes on its own line to file work. Stripped from what the human sees.
TASK_MARKER = "TASK:"
FILED_HEADING = "## Filed from the chat with the human"
FILED_TARGET = "channels/tasks.md"          # the shared ledger, not a per-amigo to-do list
DEFAULT_REPO = os.path.expanduser("~/LLM/llm-symposium")


def extract_tasks(reply):
    """Split `TASK:` lines out of a reply. Returns (reply_without_them, [items]).

    Why this exists (2026-09-21). A wake reads exactly three things — the to-do list, the agenda
    index, and a summary of the last six wakes — and the chat is not one of them. So work agreed
    in a conversation had no path into the record, and the cost was not hypothetical. The human,
    after being told twice that nothing was needed from him: *"it seems that you need me to go
    into a manual Goose session and mention the fact that Telegram-mentioned work isn't getting
    done. If I do that, I guess you'll fix it. Until then, you won't."* He was right. The fix is
    that the channel which talks about the work is the channel that files it.
    """
    keep, items = [], []
    for line in (reply or "").splitlines():
        stripped = line.strip()
        if stripped.upper().startswith(TASK_MARKER):
            item = stripped[len(TASK_MARKER):].strip()
            if item:
                items.append(item)
            continue
        keep.append(line)
    return "\n".join(keep).strip(), items


@contextlib.contextmanager
def _nullcontext(value):
    """`contextlib.nullcontext` is 3.7+; these bots run on whatever python is installed."""
    yield value


def splice_filed(text: str, items, source: str) -> str:
    """The ledger text with this message's items spliced in near the top. Pure: no disk, no clock.

    Split out of `file_tasks` on 2026-11-02 so the splice can be tested without a bot, and so that
    "what the new file should say" is a function of "what the old file said" — which is what makes
    the freshness check in `file_tasks` meaningful.
    """
    lines = text.splitlines()
    h1 = next((i for i, ln in enumerate(lines) if ln.startswith("# ")), -1)
    if not any(ln.startswith(FILED_HEADING) for ln in lines):
        at = h1 + 1 if h1 >= 0 else 0
        lines[at:at] = ["", FILED_HEADING, "", ""]
    head = next(i for i, ln in enumerate(lines) if ln.startswith(FILED_HEADING))
    lines[head + 2:head + 2] = ["- [ ] %s — *(filed from %s)*" % (it, source) for it in items]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)) + "\n"


def file_tasks(items, source="Telegram", repo=None):
    """Write filed work into channels/tasks.md near the TOP, then commit and push it.

    Why the shared ledger and not a private to-do list: this is work the human raises, and it
    belongs to the commons, not to one amigo's list — the others read tasks.md and never read
    Desi's to-do list. It is also the file the human was already told to check, and a promise of
    the form "judge it by whether tasks.md has my name in it" is only honest if that is where the
    work lands.

    Returns the items actually filed: the same list on success, `[]` when the write was refused.
    """
    if not items:
        return []
    repo = repo or DEFAULT_REPO
    path = os.path.join(repo, FILED_TARGET)
    # 2026-11-02 — read INSIDE the lock, and never write back a text that is no longer on disk.
    # The window here is milliseconds and the consequence is a whole file, so the read and the
    # write share the checkout lock. Filing is still never allowed to take the chat down.
    try:
        from record_push import shared_checkout_lock
        lock = shared_checkout_lock(repo, timeout=20)
    except Exception as exc:                     # no lock module, or no checkout: file anyway
        log.warning("filed work: no checkout lock (%s: %s)", type(exc).__name__, exc)
        lock = None
    with lock if lock is not None else _nullcontext(True) as held:
        if lock is not None and not held:
            log.warning("filed work NOT written: another writer holds the checkout")
            return []
        written = False
        for attempt in (1, 2):
            try:
                with open(path, encoding="utf-8") as f:
                    before_text = f.read()
            except OSError as e:
                log.warning("could not read %s to file work: %s", FILED_TARGET, e)
                return []
            new_text = splice_filed(before_text, items, source)
            try:
                with open(path, encoding="utf-8") as f:
                    still = f.read()
            except OSError:
                still = None
            if still != before_text:
                log.warning("filed work: %s changed under the read (attempt %d); re-splicing",
                            FILED_TARGET, attempt)
                if attempt == 1:
                    continue
                log.warning("filed work NOT written: %s kept changing under this write",
                            FILED_TARGET)
                return []
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_text)
            except OSError as e:
                log.warning("could not write filed work: %s", e)
                return []
            written = True
            break
        if not written:
            return []
    # 2026-11-02 — the add, commit, `pull --no-rebase` and push that used to run here were all in
    # the shared checkout and all outside the lock taken above. The push carried this commit's
    # parent onto a branch that may have moved, so it failed silently whenever anyone else had
    # written since; and the pull merged into a tree holding other bodies' uncommitted work, which
    # is the operation that splits a landing in half. Commit and push now happen in a disposable
    # worktree at today's origin/main, through the same function the live-chat record uses.
    try:
        import record_push
        pushed = record_push.push_paths(
            repo, [FILED_TARGET],
            "tasks: file %d item(s) from the chat with the human" % len(items))
        if not pushed.get("pushed"):
            log.warning("filed work committed but not pushed: %s", pushed.get("errors"))
    except Exception as e:          # filing must never take the chat down with it
        log.warning("filing step failed: %s: %s", type(e).__name__, e)
    return items


def file_from_reply(reply, source="Telegram", repo=None):
    """File any `TASK:` lines in a reply, and return the reply the human should see.

    This is the whole call site for a Telegram body: one function, so that "does this body file
    work?" is a question with one answer to test instead of four lines to read.
    """
    keep, items = extract_tasks(reply)
    if items:
        filed = file_tasks(items, source, repo)
        if filed:
            log.info("filed %d item(s) from %s into %s", len(filed), source, FILED_TARGET)
    return keep
