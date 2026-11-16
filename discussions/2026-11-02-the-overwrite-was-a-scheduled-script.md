# The overwrite — `channels/tasks.md` was owned whole by a scheduled script

*Moved out of `channels/tasks.md` on 2026-11-16 by Desi, unedited, because no wake could read it:
the ledger is handed to every wake truncated at 10,000 characters, and this one section held
8 open rows costing 4914 characters of delivered text against a per-seat row budget of 3,500.
The section is 283 lines / 25801 characters — one eighth of the ledger. The same 8 rows remain in the
ledger as one-line pointers; their full text is below and nowhere else.*

Provenance: `channels/tasks.md`, lines 943–1226 of the 1415-line file at commit 506ea0a4. Nothing was edited in the move.
Read it with the ledger in hand; the rows in the ledger point here.

---

## 2026-11-02 (evening) — the overwrite was a scheduled script owning the whole file

**Fixed in the same evening.** `scripts/sweep_risks.py` rebuilt `channels/tasks.md` as *everything
before the `## Open Risks` heading* + a generated block; the heading sat at character 75,739 of
129,532, so 53,793 characters were regenerated away on every run — 16,351 of them ordinary task items
that merely sat under that heading. `.github/scripts/poll_channels.py` runs the sweep on every channel
poll (~12×/day) and `channel-poll.yml` stages all of `channels/` and commits, which is how the
deletion arrived as an ordinary commit with nothing failing.

Now: the sweep owns the span between `<!-- sweep-risks:begin -->` and `<!-- sweep-risks:end -->`,
migrates an unmarked file by recognising its own output, names anything it is about to displace, and
writes through a temp file. `scripts/check_sweep_fence_only.py` refuses to let the poll commit a
removal outside the fence. `file_tasks` (the two bots that have it) reads the ledger under the
checkout lock and re-reads before writing. Full argument, measurements and what is still open:
`channels/reports/2026-11-02-desi-the-overwrite-owns-a-block.md`.

What is *not* fixed, and is now the top of this list:

- [x] **The automated writers no longer move the shared checkout — done 2026-11-02, tested.**
  `record_push.push_paths` commits and pushes in a throwaway worktree and then only fast-forwards;
  `file_tasks` hands its paths to it instead of running four git commands outside its own lock; the
  battery guard writes a `git stash create` snapshot to `refs/heads/wip/battery-<stamp>` instead of
  `add -A` + commit on `main`. Four tests fail on the old code and pass on the new. **Correction to
  this item as I first wrote it: no amigo wake has ever written to that tree** — `local_tick`
  clones privately and removes `origin`. The writers were the bot functions and the human's own
  sessions, which is why "read-only for everyone" was never the right goal.
  **Measured negative result, so nobody tries it again:** git hooks cannot make `pull` safe.
  `pre-rebase` does not fire when a pull fast-forwards, and aborting the `refs/stash` update happens
  *after* the tree has been rewound and leaves the work unreachable instead of named. `pull` is not
  transactional; there is no hook point before it moves files. Argument and measurements:
  `channels/reports/2026-11-02-desi-the-shared-checkout-is-not-a-workspace.md`.
- [x] **The unattended scripts that publish their own output — done 2026-11-02, tested.** There were
  **three**, not the two I wrote down: `scripts/append-goose.py` (runs on every human message),
  `scripts/daily_report.py` and `scripts/tell_human.py` — the last two each carried their own
  private copy of the same `_commit_own_outputs`. All three now call
  `channels.record_push.commit_and_publish`, which commits and pushes in a throwaway worktree and
  then fast-forwards. **A defect that was not in my list, found by testing them:** the two
  `_commit_own_outputs` copies committed and **never pushed**, so every daily report's output sat on
  this Mac and left the checkout *ahead* of origin — the exact state that makes every later
  fast-forward fail, produced by the function whose docstring said it existed to prevent that. And
  `append()` hard-coded its own repository, so it could not be tested against a throwaway one at
  all, which is why the defect survived: eight of the seven new checks fail on the old files.
  The rule for calling it settled, same as before: `tests/test_script_publish.py`, 7 tests.
- [ ] **A person's manual session is now the biggest writer of that tree**, and the one no hook can
  help. The bots no longer move it, which is a real improvement — an uncommitted edit was carried
  away by a bot on every human message for a year. It is still not safe from the session itself.
- [x] **Four of six bots never filed into the ledger — done 2026-11-03, tested.** `file_tasks`
  existed in `desi-bot` and `dmitri-bot` only, so a request raised in Claude's, Gemini's, Gwen's or
  Tarik's chat never reached `channels/tasks.md`, and the founder's *judge it by whether tasks.md has
  my name in it* was true of two bodies out of six. It is now one implementation —
  `channels/task_filing.py`, copied byte-identically into all six dirs, with a drift test — and all
  six chats call it. **The half I would have missed by only writing code:** the paragraph in the
  system prompt that tells a model the `TASK:` marker exists. The four bodies had neither the
  function *nor* that sentence; a function with no sentence in front of it is dead code that tests
  green. Proof it is live rather than landed: the assembled prompt in all six bodies carries the
  paragraph (claude 23011 chars, gemini 14354, tarik 14219, desi 21268, dmitri 17994, gwen 8930),
  and all six were restarted against the new code at 00:05 on 2026-11-03 and started clean.
  Tests: `tests/test_task_filing_all_bodies.py` (5) — a real origin, a real shared clone, a `TASK:`
  line ends up in `channels/tasks.md` **on origin**, the marker never reaches the human, the
  checkout ends clean and current — and `~/LLM/tests/test_file_tasks_guard.py` (11), rewritten to test the
  module instead of slicing `file_tasks` out of `bot.py`. The two structural checks fail on all
  **four** bodies exactly as they stood before this: 8 failures, reproduced by swapping `git show
  HEAD:<bot>/bot.py` back in and restoring it afterwards.
- [x] **`file_tasks` dedupes — done 2026-11-03, tested.** The identity rule landed on 2026-09-25 in
  `channels/task_ledger.py` with one sentence — *"this is the function `file_tasks` should call
  before it inserts anything"* — and nothing called it, because the rule lived in the commons and
  the function lived in two bot dirs. Since 2026-11-03 both live in `channels/task_filing.py`, so
  the call is where it belongs: `new_items()` against the lines read **inside the same locked read**
  that is about to be written over, so a refiling is refused at the point of writing rather than
  tidied up afterwards by `scripts/dedupe_tasks.py`. `task_ledger.py` is copied beside the module
  into all six dirs and drift-tested with it. **The live ledger currently has no duplicates left to
  collapse** — `python3 scripts/dedupe_tasks.py` reports "no repeated entries" over 160 entries — so
  this is prevention, not clean-up. Three of the four new checks fail on the old module:
  `2 != 1 : the ledger carries the same request twice`, the same for a refiling with a different
  stamp, and `'' is not true : the human would have received an empty message` — a reply that was
  nothing but marker lines. That last one is a defect the dedupe *created* the chance to see: once a
  refiling is refused, a reply of only `TASK:` lines has nothing left to send, and Telegram rejects
  an empty message. It now says so instead of going silent.
- [x] **Gwen's chat writes the commons record — done 2026-11-03, tested.** Every other body has
  written both halves of each Telegram message since September —
  `channels/telegram/<stamp>-<kind>-<name>.md` and a line in `channels/conversation/<amigo>.md` —
  and hers wrote neither: no `record()`, no `push_record()`. What was said to her lived in
  `memory.json` on this Mac and nowhere else, unreadable by a wake, by the other amigos, or by the
  human after a restart. All six checks in `~/LLM/tests/test_gwen_record.py` fail on her `bot.py` as it
  stood (`gwen-bot/bot.py has no push_record, record`), and she was restarted clean at 08:17
  against the new code.
- [x] **The record is one implementation — done 2026-11-03, tested.** `record()` was written six
  times, once inside each `~/LLM/<bot>-bot/bot.py`, and the six had already drifted. Two were
  invisible on this Mac. **(1) The conversation store name.** Four bodies wrote `AMIGO + ".md"`
  (`Desi.md`, `Dmitri.md`, `Claude.md`, `Gemini.md`), tarik wrote `AMIGO_KEY + ".md"`, Gwen wrote
  `AMIGO.lower() + ".md"`. This filesystem is case-insensitive, so `Dmitri.md` and `dmitri.md` are
  one file — while git stored `Dmitri.md` and dmitri's own reader asks for `channels/conversation/
  dmitri.md`. On any case-sensitive checkout (the GitHub runner, a fresh clone) that read returns
  nothing and his memory is empty; nobody could have seen it here. `Dmitri.md` is `dmitri.md` now
  (commit `5f456e07`). **(2) `rebase=`.** desi and dmitri passed `False`, claude, gemini and tarik
  `True`, Gwen nothing — three values for an argument `record_push` has accepted and ignored since
  2026-11-02. Three different nothings.
  Now `channels/record.py`, copied byte-identically into all six bot directories and drift-tested;
  each body keeps a ten-line `record()` that binds its own identity, because `amigo` is the only
  thing that differed. `~/LLM/tests/test_record_one_implementation.py` has 14 checks and produced
  `8 failures + 2 errors` against the six `bot.py` files as they stood: `'Desi.md' != 'desi.md'`,
  `'Dmitri.md' != 'dmitri.md'`, `'Claude.md' != 'claude.md'`, `'Gemini.md' != 'gemini.md'`,
  `'rebase=' unexpectedly found`, `'open(' unexpectedly found`, `gwen.md not found in {'context.md',
  'gwen-state.md'}`. All six restarted clean at 08:46.
  **The defect the consolidation then exposed, which six copies had hidden:** the record's file is
  named for the speaker, so two messages from one person within one second get the same name and
  the second replaces the first. `tests/test_telegram.py` writes exactly that pair, and it failed
  the moment both halves became one function — a message written and immediately overwritten, with
  nothing raising. `unique_path()` now suffixes `-2`, `-3`. That is the honest shape of this item:
  the copies were not only a maintenance problem, they were hiding a data-loss bug in the thing
  they all did.
- [x] **The email exchange was five copies and a gap — done 2026-11-03, same file.** The two lines
  that write an email exchange into the conversation store were copied byte for byte into five
  bodies, and the sixth had no copy — which is exactly why Gwen answered strangers and recorded
  neither the question nor the answer. The five copies of the URL redactor (`_body_for_the_record`,
  identical to the byte) are now `record.body_for_the_record`, and the two lines are
  `record.record_exchange`; all six mail paths call it, and all six now push the record instead of
  leaving it in the tree. One thing the copies had right and a rewrite could have lost: a body is
  withheld, not published unredacted, if `channels/mail.py`'s redactor cannot be loaded.
  `body_for_the_record`: `see https://x.example/reset?token=…` → `see https://x.example/reset?[redacted: this
  URL was a key, not a location]`, checked from each of the six directories.
- [x] **Gwen read none of the record she wrote — found and fixed, 2026-11-03.** Her conversation
  store (channels/conversation/gwen.md, plain text because it does not exist yet) is what her
  record now writes to, and her `build_state()` read only `gwen-state.md`: her continuity was
  `memory.json` on this Mac. *Corrected 2026-11-06 (Desi): this item said she "has written" that
  store, and she has not — her last Telegram exchange was 2026-10-29 22:13, four days before the
  record was wired, so the path is fixed but nothing has been written through it. The existence
  check caught the sentence, which is what it is for; the claim was conditional and stated as an
  observation.* A store a body writes
  and never reads is a record kept for the commons and not for her. Her `build_state()` now leads
  with her own store, bounded at 2400 chars like every other body. Her prompt is 8930 chars at
  start — unchanged, because the store does not exist until her first record — and the number to
  watch is the one after her first message.
- [x] **One wake engine could not authenticate and nothing said so — done 2026-11-03, tested.**
  Gwen's wakes had failed every run since her seat moved to `custom_alibaba` on 2026-10-30: the
  provider JSON names its key `DASHSCOPE_API_KEY_GWEN`, her `local_tick` mapped that name to the
  plain one, and the child session carried a key goose never asks for — HTTP 401, `worker_failed`,
  four days. In the same window the daily report read "desi 12, gwen 0", which looks like a quiet
  day. Per-wake texts are off by the human's instruction (2026-10-06) and the report counts items,
  which a dead wake never writes, so the failure had no voice anywhere. Now: `worker_env()` is a
  function in all six engines (callable, not inline); `~/LLM/tests/test_wake_credentials.py` resolves each
  body's provider, finds the variable it reads, and asserts the name survives the allow-list — it
  fails on the code that was running; and `scripts/daily_report.py` counts run outcomes
  (`_wakes_block`, `_wakes_focus`), naming every failed run and adding nothing to the human's
  message when the fleet is healthy. Her bot restarted 11:25; the credential path is proven live
  (`exit 0`, `ok`) and her next wake is the end-to-end confirmation. Report:
  `channels/reports/2026-11-03-dmitri-the-engine-that-could-not-authenticate.md`.
- [x] **A wake that does nothing said nothing — done 2026-11-03, tested.** The human could not
  understand the paragraph that described this, and he was right: it was a paragraph of reasons not
  to act. Tarik's engine returns `skipped_no_pending_handoff` before any run directory is written,
  so in the daily report his row was six zeros for fifteen days, and six zeros is what a dead
  engine also shows. Every engine's skip paths were the same: a dictionary returned to a caller
  nobody reads. Now `channels/wake_heartbeat.py` writes `tick-state/last-wake.json` on the way out
  of every attempt (one file, overwritten, `status` exactly as the engine returned it, one machine
  token of detail); `run_session` in all six engines is a fifteen-line wrapper around the unchanged
  engine body (`_run_session`) so every exit — including an exception raised outside the engine's
  own try, which is recorded and re-raised — leaves the trace; and `scripts/daily_report.py` reads
  it (`last_wake`), so the quiet rows now say `tarik skipped_no_pending_handoff at 12:05 — it
  declined to start a model, which a run count cannot show`, or say plainly that there is no trace
  at all. His engine is still his: the skip path is unchanged, only observable.
  `~/LLM/tests/test_wake_heartbeat.py` (14 tests) fails on the code that was running with 38 checks
  (`desi ran a wake and left no heartbeat`, ×6) and passes after; `tests/test_wakes_block.py` gained
  5 tests that fail on HEAD's report. Report: `channels/reports/2026-11-03-dmitri-the-row-of-zeros.md`.
- [x] **The low-battery guard raised instead of skipping — found and fixed 2026-11-03, tested.** In
  five of the six engines it returned a `run_id` that was assigned fifteen lines below it: unplugged
  and under 20%, the guard a wake depends on raised `NameError`, and the wake died with no run
  directory and no result. It had never fired in production (rare condition) and had never been
  tested (the condition had to be produced in a test). `run_id` is assigned first now; the test
  patches `battery_state()` to 12% on battery. The sixth engine, tarik's, already assigned it first —
  which is exactly the class the next item is about.
- [ ] **A run that reaches a verdict and dies while landing keeps neither.** Measured 2026-11-03:
  73 of 954 `awaiting_review` runs have no `land` field at all — the wake wrote `result.json`, started
  the lander, and the process ended before the verdict was written. Two are from today, and one of
  them is mine: I restarted claude's bot at 12:14 while its 12:07 run was inside the lander's
  baseline test run, and the work sits in `runs/20261103T170757Z-d951be11/` with two changed paths
  and nothing that will ever pick it up. The daily report folds these into "(no lander verdict)",
  which is true and does not say that the work is recoverable. The remedy is small and was not taken
  today: the next wake of the same body should finish any `awaiting_review` run younger than a day
  that has no `land` verdict before starting new work — bounded, gated by the same lander, and it
  turns a restart into a delay instead of a loss.
- [x] **The six wake engines are one engine now — done 2026-11-03, tested.** They were 4,529 lines
  across six files, one of them tested, and the drift was not cosmetic: three copies still told the
  model "THE FIRST LINE OF THIS REPORT IS SENT TO LINDSAY AS A TEXT MESSAGE" four weeks after
  per-wake texts were retired; five copies raised `NameError` in the low-battery guard and the sixth
  (tarik's) did not; one had the LAND-line-versus-diff check and five did not; the identity table had
  four entries and defaulted to "Desi", so the copies in dmitri-bot and gwen-bot would have opened
  every wake as the wrong person. `channels/wake_engine.py` (1,258 lines) is now the engine —
  the clock, the battery guard, the worker environment, the checkout, the status chain, the landing,
  the prune, the heartbeat door, and both engines (standard wake and tarik's Codex-handoff engine).
  Each `local_tick.py` is 51–60 lines of configuration: which engine, which provider keys, any extra
  environment names. The six copies of the engine are md5-identical and a test fails if they are not.
  The prompt is one text for all six, with the body's name substituted from its directory; the
  variants had drifted, and the most current (desi's) won — that is a real behaviour change for five
  seats, named rather than buried. Tests first: `~/LLM/tests/test_wake_engine_one_implementation.py`
  (10 tests) fails on the old tree with `desi-bot has no wake_engine.py` and `805 not less than 80`;
  all suites green after (local_tick 44, heartbeat 11, credentials 4, engine 10, record 14, gwen 6).
  Report: `channels/reports/2026-11-03-dmitri-one-engine-six-configurations.md`.
- [ ] **The most common lander refusal is real, and it is the item merge dropping a field.**
  Checked 2026-11-03 by hand, because 14 of the last refusals were `new_test_failures` and a gate
  that refuses everything is indistinguishable from a gate that refuses nothing: took desi's 12:54
  run, restored its own worktree's `channels/items.jsonl` to the parent commit and ran the named
  test — it passes; put the run's version back — it fails, with
  `20261021T072444Z-455ec793` losing `verdict_kept_from` (`2026-10-23T15:23:08Z` → `None`) under the
  merge. So the gate was right, and the defect is in the ledger's write path, not in the gate. The
  test that catches it (`tests/test_item_ledger_merge.py::test_the_merge_only_ever_adds_fields`)
  exists because this exact class of loss was seen before, and it is now the thing blocking
  landings. Fix the merge before touching the lander's thresholds.
- [x] **Nothing carried a change from the commons into the six bot directories — done 2026-11-03,
  tested.** The extraction removed six implementations and left this: `~/LLM/<bot>-bot` is a
  separate repository that no wake checkout contains, so every engine change needed a person, six
  times — which is how the copies drifted. `scripts/deploy_engines.py` copies the four shared modules
  from `channels/` into all six, verifies every md5, validates all six targets before writing
  anything, refuses if a bot directory is missing (a silent skip is a body a month behind), and
  restarts only when asked. `tests/test_deploy_engines.py` (8 tests) covers it, including a read-only
  check that the live tree matches. **Not scheduled:** a launchd job running it nightly would let a
  wake's engine change reach the bots without a human, and would also push whatever a wake last landed
  into six live processes unlooked-at. That is a decision, not an obvious improvement.
  **Scheduled 2026-11-03, after the human refused to be the watchdog:** the decision above was mine
  to make, and the two conditions that made it unsafe are now checks inside the script rather than
  judgement at the keyboard. `--verify` refuses to copy an engine that does not import or a stub that
  names a `CORE.<attribute>` the engine no longer has; `--when-idle` refuses to act while any bot has
  a run with no `result.json` in the last half hour or a live worker process, because a restart
  mid-lander is how verdicts lose their outcomes. `com.lindsay.amigo.deploy-engines` runs it every
  thirty minutes and restarts only when it copied something. Six new tests.
- [x] **Seventy-three runs reached a verdict and died inside the lander — recovered 2026-11-03,
  tested.** `result.json` is a snapshot nothing revisits, so a run killed during landing kept
  `awaiting_review` and lost its `land` key, and its diff sat in `changes.patch` looking like work
  nobody did. `wake_engine.finish_unlanded` now lands the oldest such verdict (with a patch, younger
  than 24 hours) before the wake clones, one per wake, writing the outcome back into the run's own
  record as `land_recovered_by`. The bound is the design: 71 of the 73 are 900–1,180 hours old, and
  re-applying a month-old diff is guessing, not recovery. Gemini's 08:04 verdict came back `conflict`
  on the first live run — recorded, instead of blank. `~/LLM/tests/test_wake_recovery.py`, 9 tests.
- [ ] **A provider that cannot be reached costs a whole wake and nothing retries.** Desi's 15:54 wake
  on 2026-11-03 died in nine seconds: `worker_failed`, transcript `Network error: Could not connect
  to api.deepseek.com`. The heartbeat caught it (that is what it is for), but a transient network
  failure burns a two-hour slot and the next attempt is two hours later. A bounded retry — one, after
  a short wait, only for a worker exit that produced no tokens and no changes — would recover most of
  these; it is not a retry storm, because the timer has already stamped the attempt.
- [ ] **`channels/telegram.py`'s poller has no runner.** `log_message` there was the second
  implementation of the record's first half, naming files `<stamp>-<kind>-<chat_id>.md` where every
  bot names them `-<speaker>.md`. Nothing in production has ever written one of those (zero files on
  disk), and nothing runs the module: no plist, no workflow. It delegates to `channels/record.py`
  now, so the divergence is gone either way — but the file is a poller nobody polls, and that is
  worth deciding rather than leaving.
- [x] **`gemini-bot` logged `drive_bridge_ingest failed during orientation: name 'sys' is not
  defined` on every start — fixed 2026-11-03.** `orientation()` called `sys.path.insert` to load her
  Drive bridge and the module never imported `sys`: a function swallowing its own `NameError` and
  reporting it as a failed ingest, since September. Found while adding the heartbeat's import block;
  the `import sys` stays in her file. Her next wake is the confirmation, since the warning was
  logged by the wake path rather than at start.
### The four writers, as they now stand

The four writers, as named before the fix, for the record:

- [x] **The ledger's own write path — done 2026-11-02 and 2026-11-03, tested.** As this item was
  first written it said "`file_tasks` in all six `bot.py` copies … writes the whole file back with no
  lock and no freshness check". Two corrections. It was in **two** copies, not six — the other four
  bodies had no filing path at all (see the item above). And as of 2026-11-03 it is in **zero**
  `bot.py` files: the code moved to `channels/task_filing.py`, where the read and the write share
  `shared_checkout_lock`, the text is re-read before the write and re-spliced if it changed, and the
  publish goes through `record_push.push_paths` instead of four git commands outside the lock. What
  is *not* fixed by any of that is dedupe (see the open item above) and the sweep, which is still a
  machine rewriting this file twelve times a day.
- [ ] **`scripts/sweep_risks.py` — and this one is not hypothetical, it is a machine.** It rewrites
  `channels/tasks.md` wholesale (`TASKS.write_text(...)`, line ~274) and `channels/risks.md` twice.
  `.github/scripts/poll_channels.py` runs it on every poll, and `channel-poll.yml` runs ~12 times a
  day: after the script writes, the job does `git add channels/`, commits
  "feat(channels): frequent poll — mail + telegram", and on a rejected push **rebases onto main and
  retries up to three times**. A whole-file rewrite rebased onto a main that has a newer
  `tasks.md` is exactly how 54 lines disappear with no conflict and no name against the act — the
  11:36 and 14:56 reverts of 2026-11-02 fit this signature, and so does `bc649b22` from the battery
  guard, which did the same thing with `git add -A`.
  Two specific repairs, either of which would have prevented it and both of which are wanted:
  the sweep writes **only its own block, between markers**, leaving the rest of the file
  byte-identical; and the workflow stops staging `channels/` wholesale, or asserts that the
  `tasks.md` diff it is about to commit lies entirely inside that block.
- [ ] **`scripts/gen_index.py`** and **`scripts/compile_agenda.py`** — regenerators; a stale copy of a
  generated file is not evidence about anything, and each should re-read the tree it is writing over.
- [ ] **The guard, once, in one place:** read the file, hash it, write only if the hash on disk is
  still the hash that was read — the same compare-and-swap as `git update-ref`, on a file instead of a
  ref. Two lines, and each of the four sites above calls it instead of `open(..., "w")`.
- The test each site needs: a second writer changes the file between the read and the write, and the
  second writer's lines survive or the write is refused. Nothing in this repository asserts that today.
