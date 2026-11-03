# Four of the six bodies could not file work. One had nothing to file it into.

**Desi — 2026-11-03.** Session report. The code is landed, the tests discriminate, and all six
bodies are running it. What follows is what was wrong, what I did instead, and the three things I
found on the way that I did not fix.

---

## 1. The defect, in the founder's own terms

His test of this arrangement has always been concrete: *judge it by whether `tasks.md` has my name
in it.* It was true of two bodies out of six.

| body | could file? | told the model the marker exists? | other writes to the commons |
| --- | --- | --- | --- |
| `desi-bot` | yes, private copy of `file_tasks` | yes, in `CHAT_RULES` since 2026-09-21 | conversation record + push |
| `dmitri-bot` | yes, private copy | yes | conversation record + push |
| `claude-bot` | **no** | **no** | conversation record + push |
| `gemini-bot` | **no** | **no** | conversation record + push |
| `tarik-bot` | **no** | **no** | conversation record + push (mail path too) |
| `gwen-bot` | **no** | **no** | **nothing** |

Two failures, stacked, in the same four bodies. There was no `extract_tasks`, no `file_tasks`, and
— the half nobody writes down — no sentence in the system prompt telling the model that a `TASK:`
line exists at all. A `TASK:`-splitting function with no prompt asking for `TASK:` lines is dead
code that tests green. The four bodies did not even have the dead code.

Gwen's row is the worst of the four. Her chat writes nothing else: no `record()`, no
`push_record()`. So a request agreed with her left no trace anywhere in the commons — not in the
ledger, not in `channels/conversation/gwen.md`, not in any wake's reading. She was the seat with
the least evidence and had been, since she was seated.

## 2. What I did about it

**One implementation, six copies.** `channels/task_filing.py` is the canonical module:
`extract_tasks` (the split), `splice_filed` (pure — new text as a function of old text, which is what
makes a freshness check meaningful), `file_tasks` (read under `shared_checkout_lock`, re-read before
writing, re-splice if it changed, publish through `record_push.push_paths`), and
`file_from_reply` (the whole call site in one function, so "does this body file work?" is one line
to read instead of four).

Copied byte-identically into all six bot dirs, tested for drift. `desi-bot` and `dmitri-bot` lost
their private copies — 145 lines each — so there is no second thing to keep in step. Their handler
now calls `file_from_reply`, same as everyone else's.

**And the sentence.** Each of the four got a `FILING_RULES` paragraph in the prompt it actually
assembles, appended only in `make_system_prompt` and not in `make_mail_prompt`: a stranger's email
is not the commons' work, and a mailbox is not the place to file it.

**Why not a fourth and fifth copy of the 120 lines.** Because copying already cost us here. The
function that ran was whichever copy sat in the bot dir, not the canonical one in `channels/`; a fix
landed in the commons reached nobody until someone remembered to copy it six times; and this
repository already keeps a drift test for `record_push.py` for exactly that reason (it has caught a
real drift once). Six copies of the ledger's write path is six places for the file that has lost
work three times to lose it again.

## 3. The change is running, not merely landed

A landed edit in a bot dir changes nothing until the process restarts. All six were restarted
against the new code at 00:05 on 2026-11-03 and started clean:

```
00:05:17 claude   Claude bot starting (model=claude-sonnet-5). State=23011 chars.
00:05:30 gemini   Gemini bot starting (model=gemini-3.8-flash). State=14354 chars.
00:05:34 tarik    Tarik bot starting (model=gpt-5.5). State=14219 chars.
00:05:41 gwen     wake clock started: one wake every 1440 minutes as custom_alibaba/qwen3.8-max-0902
00:05:44 desi     battery guard started (every 5 min)
00:05:47 dmitri   battery guard started (every 5 min)
```

And the paragraph is in the assembled prompt in every body, measured by importing each bot and
calling `make_system_prompt()` — the same function the running loop uses:

| body | prompt chars | `FILING WORK` present | names `TASK:` |
| --- | --- | --- | --- |
| claude | 23011 | yes | yes |
| gemini | 14354 | yes | yes |
| tarik | 14219 | yes | yes |
| desi | 21268 | yes | yes |
| dmitri | 17994 | yes | yes |
| gwen | 8930 | yes | yes |

The three sizes that also appear in the restart log are identical to the sizes measured after
restart, which is how I know the running processes are the new code and not a stale one.

## 4. The tests, and the standard for calling this settled

`llm-symposium/tests/test_task_filing_all_bodies.py` — 5 tests, new. Three are behavioural against a
real bare origin and a real shared clone, because every defect in this area has been a difference
between what a function does to a temp file and what it does to a repository:

- a reply carrying a `TASK:` line ends up in `channels/tasks.md` **on origin**, and the marker never
  reaches the human;
- the shared checkout ends **clean and current** rather than holding the file it just published;
- a second body's request, filed after origin moved under the shared clone, does not lose the first.

The other two are structural, and they are the ones that fail on the old code:

- every body's chat loop calls `file_from_reply`;
- every body's assembled prompt names `TASK:` and `tasks.md`.

`tests/test_file_tasks_guard.py` — 11 tests, rewritten. It used to slice `file_tasks` out of
`desi-bot/bot.py` by source offsets; there is no such function in a bot any more, so it now imports
the module and tests the lock refusal, the concurrent-writer race, the routing into `push_paths`,
the splice-at-the-top rule, the heading-once rule, extraction (including a lowercase marker and an
empty one), and byte-identity across the six copies.

**Old-code proof.** With `git show HEAD:<bot>/bot.py` swapped back in for the four thin bodies, the
new test file fails **8 times** — two checks × four bodies:

```
FAIL: test_each_chat_loop_calls_the_filing_path (bot='claude') → claude does not import the filing path
FAIL: test_each_chat_prompt... ("TASK:" not found in "You are Claude (Claude-Symposium), amigo #1 …")
… same for gemini, tarik, gwen
Ran 5 tests — FAILED (failures=8)
```

The files were restored from checksummed backups afterwards; all six md5s verified against the
backups before the suite was re-run green.

Suites after the change: `test_task_filing_all_bodies` 5/5, `test_file_tasks_guard` 11/11,
`test_record_push` 10/10, `test_land_lock` 13/13, `test_land_worktree` 7/7, `test_lander_undo` 4/4,
`test_append_only_merge` 4/4, `test_script_publish` 7/7, `test_battery_snapshot` 3/3,
`test_task_ledger` 9/9, `scripts/check_sweep_fence_only.py` exit 0.

## 5. Two corrections to the ledger's own record

- The item I wrote as *"`file_tasks` in all six `bot.py` copies"* was wrong in both directions. It
  was in **two** copies, and as of tonight it is in **zero** `bot.py` files.
- The item *"Four of six bots never file into the ledger"* is now closed, but it was filed as one
  defect and was two: a missing function **and** a missing sentence. Filing only the function would
  have produced a fifth copy of dead code.

## 6. What I did not do, and why it is named rather than implied

- **Gwen's conversation record.** Her chat still writes no `channels/conversation/gwen.md`. She can
  now file, so her work reaches the ledger — but what she *said* still reaches nobody. That is a
  different change with a different test (the record path, not the ledger path), and bundling it
  here would have made both harder to check.
- **The dedupe the ledger has been asking for since 2026-09-25.** `channels/task_ledger.py` holds
  the identity rule and one sentence: *"this is the function `file_tasks` should call before it
  inserts anything."* It has never been called, and the ledger carries a nine-times-copied item to
  show for it. Now that both halves finally live in the same module, wiring `new_items()` in is a
  one-line change — and it should be the next session's first job, before the ledger grows a tenth
  copy.
- **`gemini-bot`'s start-up warning**, unrelated and pre-existing: `drive_bridge_ingest failed
  during orientation: name 'sys' is not defined` on every restart. A function swallowing its own
  `NameError` and reporting it as a failed ingest.
- **The bots repository was two commits ahead of its origin** when I started — `e0a7b7e` and
  `4b28adc`, last night's work, committed and never pushed. The same defect this session is about,
  in a third place: committed is not published. Pushed with this session's commit.

---

*One implementation, six bodies, one test that fails when a copy drifts. The next time somebody asks
whether a request raised in a chat reached the ledger, the answer is a file, not a memory.*
