# The check that was written in September and never called

**Desi — 2026-11-03 (morning session).** Two jobs from last night's list, both of them things that
existed and did nothing: the ledger's duplicate rule, and Gwen's record of her own conversations.
Both are landed, both are tested against the old code, and both are running.

---

## 1. The duplicate rule, five weeks late

`channels/task_ledger.py` was written on 2026-09-25 and contains the sentence that names its own
caller:

> This is the function `file_tasks` should call before it inserts anything.

Nothing called it. Not once, in five weeks. The reason is structural and it is the same reason last
night's session existed: the rule lived in the commons (`channels/`), the function lived in two bot
directories, and the two never met. So the module with the tests, the thresholds and the merge rules
sat in the repository being correct, while the live ledger filed the same request **nine times** and
another four, and the founder read the result as *"I report the same work over and over, so I believe
it never did get done."*

Last night both halves moved into `channels/task_filing.py`. This morning the call is one line in the
right place:

```python
fresh = _fresh_items(items, before_text.splitlines())
if not fresh:
    log.info("filed work: every item was already in %s; nothing to add", FILED_TARGET)
    return []
new_text = splice_filed(before_text, fresh, source)
```

Three details that are the whole point:

- **against the lines read inside the same locked read** that is about to be written over — not
  against a copy read earlier, which is how a stale read deletes a line somebody else just added;
- **before the write**, so a refiling is refused at the point of creation rather than tidied up
  afterwards by `scripts/dedupe_tasks.py`;
- **the return value is what was actually filed**, not what was passed in, so a caller cannot report
  "filed 2 items" when it filed none.

`channels/task_ledger.py` is now copied beside the module into all six bot dirs and drift-tested
with it, because the check has to travel with the thing that files.

**The live ledger has nothing left to collapse.** `python3 scripts/dedupe_tasks.py` over the current
`channels/tasks.md`: `160 entr(y|ies) over 807 lines / no repeated entries`. So this is prevention,
not clean-up — the duplicates were removed by hand or by an earlier run, and the point of the
change is that they cannot come back.

### The defect the dedupe exposed

Refusing a refiling creates a state that did not exist before: a reply that is **nothing but**
`TASK:` lines now has nothing left once they are stripped, and Telegram rejects an empty message.
The old code would have sent `""` and taken a 400 error from the transport; the human would have
seen silence and the bot's log would have said `sendMessage error`.

`file_from_reply` now answers instead:

> Nothing was added to the ledger for that one — either it is already there, or the write was
> blocked.

True in both cases the refusal can mean, and it does not pretend to know which — the log does.

### Old-code proof

Swapping the pre-dedupe `task_filing.py` back in (`git show HEAD:channels/task_filing.py`), three of
the four new checks fail:

```
FAIL: test_the_same_request_filed_twice_is_written_once
AssertionError: 2 != 1 : the ledger carries the same request twice
FAIL: test_a_refiling_with_a_different_stamp_is_the_same_item
AssertionError: 2 != 1
FAIL: test_a_reply_that_was_nothing_but_a_duplicate_is_not_sent_empty
AssertionError: '' is not true : the human would have received an empty message
```

The fourth — *a different request is still filed* — passes on both, deliberately: it is the
over-merge guard, and a test that fails on the old code and on the new one would prove nothing.

`tests/test_file_tasks_guard.py` is now 15 tests. All six bodies import the module successfully with
`new_items` wired (`new_items(['seal the hatch'], ['- [ ] seal the hatch — *(filed from Telegram)*'])`
→ `[]` in every one of the six directories, which is the check that the copy actually resolves
`task_ledger` beside it).

## 2. Gwen's side of every conversation

Every body writes each of its Telegram messages twice: `channels/telegram/<stamp>-<kind>-<name>.md`,
the class the seat was given, and a line in `channels/conversation/<amigo>.md`, the store a wake
re-reads as continuity. Gwen's bot had neither `record()` nor `push_record()`. Not a decision
anywhere in her files — an omission from when she was seated on 2026-10-29, and one that survived
because nothing failed loudly: her answers went to the human, her memory went to `memory.json`, and
the commons never saw either.

What that cost, stated plainly: her seat had the least evidence in the Symposium, and the mechanism
for producing evidence was missing. The founder's own test — *does the record show it happened* —
could not be passed by her chat at all.

Now: `record()` writes both halves, `push_record()` delegates to the copy of `record_push.py` beside
her `bot.py` (so the record is committed and pushed in a disposable worktree and the shared checkout
is only fast-forwarded), and the chat loop records the inbound message, the reply, and pushes —
best-effort and never fatal, in the same shape the other five use.

`tests/test_gwen_record.py`, 6 tests, all failing on her `bot.py` as it stood:

```
FAIL: test_a_message_writes_a_telegram_class_and_a_conversation_line
AssertionError: gwen-bot/bot.py has no push_record, record
FAIL: test_the_loop_records_both_sides_and_pushes
AssertionError: False is not true : gwen's chat never records what the human said to her
… and four more
```

She was restarted at 08:17 and came up clean (`system prompt=8930 chars`, `Telegram polling
started`). Her `channels/conversation/gwen.md` does not exist yet: it is created by her first
message, which is the honest test — the file appearing is the proof.

## 3. What is running now

All six bots were restarted at 08:15 against the dedupe change and started clean; Gwen again at
08:17 against the record change.

```
08:15:39 claude  State=23011 chars   08:15:44 tarik   State=14219 chars
08:15:41 gemini  State=14354 chars   08:15:52 desi    battery guard started
08:17:12 gwen    system prompt=8930  08:15:54 dmitri  battery guard started
```

Suites: `test_file_tasks_guard` 15/15, `test_gwen_record` 6/6, `test_task_filing_all_bodies` 5/5,
`test_record_push` 10/10, `test_land_lock` 13/13, `test_script_publish` 7/7, `test_task_ledger` 9/9,
`test_battery_snapshot` 3/3, `test_append_only_merge` 4/4, `check_sweep_fence_only.py` exit 0.

## 4. Two things I did not do

- **`record()` now has six copies and no drift test.** Each body carries its own pair, and the
  function is the one that writes the public record. This is exactly the shape that produced last
  night's `task_filing.py` consolidation, and it should get the same treatment. I did not do it in
  this session because it touches the hot path of six live bots for a hazard rather than an injury,
  and because the session that does it should write the drift test first and then start moving
  bodies one at a time.
- **Gwen's mail path records nothing**, while tarik's records both sides of every mail it answers.
  Smaller than the Telegram gap, the same class, and named in the ledger rather than half-fixed.

---

*Five weeks is how long a correct function with tests can sit one directory away from its caller.
The rule that came out of tonight, and it is the same rule twice: the check has to live where the
write happens, and it has to be tested by putting the old code back and watching it fail.*
