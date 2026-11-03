# The record was one thing written six ways, and the six hid a bug

**Written 2026-11-03 by Desi. Owner: Desi. Session: manual, at the founder's request.**

This is the third session on one theme, and the theme is narrower than "consolidation": *a function
that writes the record is a function whose failure has no symptom.* The symptom would have to be
written by the function that failed. `record()` was implemented six times, once per body, and the
six copies had drifted. One of the drifts ate data on this Mac tomorrow and would have eaten
memory on any other machine today.

## What was there

`record()` — the function that writes both halves of every Telegram message into the commons'
record — sat inside each of the six `~/LLM/<bot>-bot/bot.py` files. Sixteen lines each, and
`push_record()` beside it. `channels/telegram.py` held a **seventh** first half, `log_message`,
with its own file-naming convention.

The six were not identical. Measured, not read:

| body | conversation store written | store read | `push_record` passes |
|---|---|---|---|
| desi | `AMIGO + ".md"` → `Desi.md` | `desi.md` | `rebase=False` |
| dmitri | `AMIGO + ".md"` → `Dmitri.md` | `dmitri.md` | `rebase=False` |
| claude | `AMIGO + ".md"` → `Claude.md` | `claude.md` | `rebase=True` |
| gemini | `AMIGO + ".md"` → `Gemini.md` | `gemini.md` | `rebase=True` |
| tarik | `AMIGO_KEY + ".md"` → `tarik.md` | `tarik.md` | `rebase=True` |
| gwen | `AMIGO.lower() + ".md"` → `gwen.md` | **nothing** | nothing |
| `telegram.py` | `-<chat_id>.md` | — | — |

Two of those columns matter and neither could be seen by looking:

**The store name.** This filesystem is case-insensitive. `Dmitri.md` and `dmitri.md` are one file
here, so a write of `Dmitri.md` and a read of `dmitri.md` agree — locally, forever. In git the file
is `Dmitri.md`; on any case-sensitive checkout (the GitHub runner, a fresh clone, a Linux box) that
read is a different path, returns nothing, and dmitri's memory is empty. His memory was never
empty on this Mac, which is exactly why five weeks of tests and six sessions never noticed. I found
it by writing a test that prints the name each body writes, not by reading the code again.

**`rebase=`.** Three different values among six callers, for an argument `record_push.push_paths`
has accepted and ignored since 2026-11-02. Not harmful — and that is the point: it is what a
divergence looks like when nobody can see its effect. Five call sites said three different things
and all three were nothings.

**The seventh copy.** `channels/telegram.py::log_message` wrote `<stamp>-<kind>-<chat_id>.md`.
Every bot wrote `<stamp>-<kind>-<speaker>.md`. Zero files on disk follow the first convention, and
nothing runs that module — no plist, no workflow. A second implementation of half the record, with
a different answer to "what is this file called", on a path with no runner.

## What was done

`channels/record.py`: one implementation. `record_message()` writes both halves,
`record_exchange()` writes both sides of an email, `body_for_the_record()` is the URL redactor,
`push_record()` delegates to `record_push`, `store_name()` forces one case. Copied byte-identically
into all six bot directories (md5 `4a05ee90…` in all seven locations, drift-tested).

Each body keeps a ten-line `record()` whose only content is its own identity:

```python
return record_message(kind, chat_id, name, text, message_id=message_id,
                      amigo=AMIGO, repo=REPO_DIR)
```

`amigo` is the *only* thing that ever differed between the six, so it is an argument rather than six
files. If the module cannot be imported the wrapper logs `channels/record.py is not importable — this
body records NOTHING` rather than writing nothing quietly: the failure mode this whole session is
about is the quiet one.

`channels/telegram.py::log_message` delegates now. `git mv channels/conversation/Dmitri.md
channels/conversation/dmitri.md` (commit `5f456e07`) so the name in git is the name his reader asks
for.

## The email half was the same defect, one channel over

The two lines that append an email exchange to the conversation store were copied byte for byte
into **five** bodies. The sixth had no copy — which is precisely why Gwen answers strangers and
records neither the question nor the answer. Five copies and a gap: the copies did not cause the
gap, but they made it invisible, because "everyone does it" was true of five of six.

The URL redactor `_body_for_the_record` was five byte-identical copies as well (md5
`9b85ba53…` ×5). Both are in `record.py` now, and all six mail paths call them and then push.
Verified from each of the six directories:

```
see https://x.example/reset?token=SECRETVALUE&user=a
→ see https://x.example/reset?[redacted: this URL was a key, not a location]
```

The redactor's own safety property survived the move: if `channels/mail.py` cannot be loaded the
body is **withheld**, not published unredacted.

## The data-loss bug the copies were hiding

Consolidating put the bots' naming rule into `channels/telegram.py`, whose dedupe test writes two
messages in the same second from the same person. It failed:

```
FAIL test_deduplication_by_bot_chat_message_id
   8/9 tests passed
```

The record's file is named for the speaker, so `msg1` and `msg2` from one person in one second get
the same path and the second `open(..., "w")` replaces the first. **A message was written and
immediately overwritten, and nothing raised.** The six copies had this hazard all along; the
standalone channel keyed on the chat id and so hit it less often. `unique_path()` now suffixes
`-2`, `-3`, and a test writes the same-second pair and asserts both survive.

This is the part I want on the record: the six copies were not merely a maintenance problem. They
were hiding a bug *in the thing they all did*.

## Gwen read none of what she wrote

Found while writing the "every body reads the store its record writes" test: `gwen.md` is not in the
set `{'context.md', 'gwen-state.md'}`. She has written `channels/conversation/gwen.md` since
yesterday and her `build_state()` read only her state file. Her continuity was `memory.json` on this
Mac — a file no wake, no other amigo, and nobody after a restart can read. A store a body writes and
never reads is a record kept for the commons and not for her. Her `build_state()` leads with her own
store now, bounded at 2400 chars like every other body.

Her prompt is 8930 chars at start, unchanged — because the store does not exist until her first
record. The number to watch is the one after her first message; if it does not grow, the read is not
happening.

## Evidence

`tests/test_record_one_implementation.py`, 14 checks. Against the six `bot.py` files as they stood:

```
FAILED (failures=8, errors=2)

AssertionError: 'Desi.md' != 'desi.md'
AssertionError: 'Dmitri.md' != 'dmitri.md'
AssertionError: 'Claude.md' != 'claude.md'
AssertionError: 'Gemini.md' != 'gemini.md'
AssertionError: 'record_exchange' not found in 'def check_mail(first=False): …
AssertionError: 'rebase=' unexpectedly found in 'def push_record(): …
AssertionError: 'open(' unexpectedly found in 'def record(kind, chat_id, …
AssertionError: 'gwen.md' not found in {'context.md', 'gwen-state.md'} : gwen writes gwen.md and
  reads context.md, gwen-state.md — the two halves are different files
AssertionError: Lists differ: ['channels/conversation/Dmitri.md'] != []
```

Restored from checksummed backups (`/tmp/bak-e/<body>/bot.py`, distinct md5 per body) and green:
14/14. Also green: `test_telegram.py` 9/9, `test_record_push.py` 10/10, `test_script_publish.py`
7/7, `test_task_filing_all_bodies.py` 5/5, `test_task_ledger.py` 9/9, `test_gwen_record.py` 6/6,
`test_file_tasks_guard.py` 15/15, `test_land_lock.py`, `test_land_worktree.py`,
`test_append_only_merge.py`, `test_battery_snapshot.py`.

`test_gwen_record.py` was updated rather than deleted: her `record()` is a delegation now, so the
slice it executes needs `record.py` in its namespace, and the "does not commit by hand" check
follows the delegation one level further. Its own subject — she records at all, both halves — still
holds.

All six restarted at 08:46 against the committed code; each started clean, none logged the
`not importable` line, and the state sizes are claude 23011, gemini 14354, tarik 14219, gwen 8930
(the three unchanged numbers are the bodies whose `build_state` this session did not touch).

**What is not proven:** no live message has run through the new path yet. The behavioural test
executes the exact `record()` source out of each `bot.py`, and the restart is against the committed
tree, but the first real inbound Telegram message — or Gwen's next stranger mail — is the proof. The
line to look for is the absence of `records NOTHING` and the presence of a new file in
`channels/telegram/`.

## Named, not done

- **`channels/telegram.py` is a poller nobody polls.** No plist, no workflow, and zero files in the
  history carry its naming convention. It delegates now, so it is no longer a divergence — but
  whether the commons wants a standalone poller at all is a decision, and it is in the ledger.
- **Pre-existing failures elsewhere in the suite**, checked against a fresh clone of `origin/main`
  and identical there, so not from this work: `test_daily_report` (1 failure, 1 error),
  `test_price_band`, `test_reading_queue`, `test_reject_queue_request_gap`,
  `test_reject_queue_sweep`, `test_landing_suite_check`, `test_gallery_unwired_works`.
- **The case-insensitive-filesystem trap is general.** This session found one instance because a
  test compared names. Any other code that builds a path from a capitalised constant has the same
  silent read-miss on a case-sensitive checkout, and nothing here would catch it.
