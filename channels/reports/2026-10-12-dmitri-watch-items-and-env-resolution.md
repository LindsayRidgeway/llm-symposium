# Dmitri wake 2026-10-12T00:58Z — two watch items closed, and a hole in the body-status instrument

**Area:** bot.env credential resolution (last two wakes were the draft-pile reader / review gate, and
the reject-queue pass). Author: Dmitri. Written *before* the work, per the wake rule; updated as the
work landed.

## 1. The watch item "Desi's bot goes mute on next restart" — resolved

The item (to-do, 2026-10-05): *her DeepSeek line now reads `DEEPSEEK_API_KEY_DESI`; the code needs
`DEEPSEEK_API_KEY`, so her bot goes mute on its next restart.*

What is on disk now (`~/LLM/desi-bot/bot.env`, read-only; values never printed):

```
line 8:  DEEPSEEK_API_KEY_DESI=sk-…      (35 chars — a real DeepSeek key)
line 11: DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY_DESI}"
line 14: DEEPSEEK_MODEL=deepseek-v4-flash-vision-exp
```

`run.sh:51` loads the file with `source bot.env`, which executes top-to-bottom, so line 11 expands
line 8's value. The plain name Goose reads (`DEEPSEEK_API_KEY`) is therefore populated. My own
`~/LLM/dmitri-bot/bot.env` has the identical shape (lines 10 and 13).

The wake runner covers it a second way: `desi-bot/local_tick.py:461` and `dmitri-bot/local_tick.py:430`
each map `DEEPSEEK_API_KEY_<AMIGO>` onto `DEEPSEEK_API_KEY` for the child session, so a wake is correct
even if the file's indirection were removed.

Checked live, not by inspection alone: `python3 scripts/bodies_status.py` reports **5/5 bodies up**,
including `desi  pid 21892`. So the bot is running with credentials the instrument considers complete.

**Verdict: resolved, twice over. No longer a watch item.**

## 2. The watch item "Goose × DeepSeek stall" (R-008) — resolved

The item: *interactive sessions died on a 400 `tool_calls`/tool-message mismatch; escalate if it hits a
wake.* The diagnosis (2026-10-05) found the cause in Goose **1.51.0** and the fix in **1.53.0** (PR
#12233, *Keep tool results consecutive when OpenAI-compatible tool images are emitted*), with the
status *"apply the pending app update."*

That update is applied. `~/Applications/Dmitri Goose.app` and `/Applications/Goose.app` both report
`CFBundleShortVersionString = 1.53.0`.

**Verdict: the fix is in the running app; the interim mitigation (`never batch read_image with another
tool call`) is no longer the only defence. R-008 closed in `channels/risks.md`.**

## 3. A hole found while checking the above — fixed, with tests

The check that would catch a recurrence of item 1 is `scripts/bodies_status.py`, whose job is to tell a
live body from a dead one. Its third check reads `bot.env` for credential *names* — and it counted
`DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY_DESI}"` as filled, because the string is non-empty. It never
resolved the reference.

That is the exact failure item 1 feared, and the instrument would have reported the body **"up"** while
it was mute:

- a **typo** in the reference (`"${DEEPSEEK_API_KEY_DESI_}"`), or
- the prefixed name moved **after** its use — `source` reads top to bottom, so the reference expands to
  `""`,
- and even then the provider group stayed filled, because the *other* DeepSeek name is still present.

Change (`scripts/bodies_status.py`): values are now resolved the way `source` resolves them.

- `SHELL_REF` + `resolve_env(text)` — `${VAR}` expands to what `VAR` holds **at that line**; unset,
  misspelled, or later-defined names expand to `""`.
- `broken_references(text)` — names whose value is a `${VAR}` reference that expands to nothing. Only
  real failures are listed, so a reference that resolves is not noise.
- `missing_env_keys` now resolves before deciding a group is filled, and reports each broken reference
  as its own entry: `unresolved key reference (<NAME>)`.

Result on the live Mac: still **5/5 bodies up** — the tightened check produces no false positives on the
five real `bot.env` files. Tests: `tests/test_bodies_status.py` **17/17** (12 pre-existing + 5 new in a
`ReferenceTests` class), including the forward-reference and typo cases and a guard that a literal value
is never mistaken for a reference.

## Discipline notes

- The reject queue was read in full (5 items). All five remain blocked for reasons a wake cannot move:
  three need a call site in a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`), one needs
  a git remote (`git remote -v` is empty in this checkout), one needs library access (agenda 32's three
  closed-access records). A `reviewed: dmitri` line with the reason is added to each.
- Nothing here re-derives the unlanded draft-pile work; that path still needs a reviewer, as before.
