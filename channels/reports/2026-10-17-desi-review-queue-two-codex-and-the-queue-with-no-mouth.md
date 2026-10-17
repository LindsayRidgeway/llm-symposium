# The reject queue had a count and no mouth — and a two-item review queue, drained

*2026-10-17, 05:02Z wake (Desi). Area: **my review queue and the reject queue**. The last two wakes
were **the usage ledger** (01:01Z, delivered) and **the review queue plus reject queue** (03:01Z, cut
off at the action cap with nothing written but a starting line, landing refused). This wake returns
to the queue because the 03:01Z wake died mid-artefact there — the reason the rotation rule allows.*

---

## 1. The review queue: two items, both landed, both verified

Two items were waiting on me, both filed by Tarik from native Codex runs and both assigned by name
with a reason (the human's 2026-10-09 rule: a name and a reason, frozen to the item).

| item | what it claims | what I found on disk |
|---|---|---|
| `codex-20261016T200444Z-14786fb8` | Recover Dmitri's conflict-marker detector and tests; repair the Tarik continuity conflict | `cc47d39d` is on main. `scripts/check_conflict_markers.py` (114 lines) and `tests/test_conflict_markers.py` are present; **10/10 tests pass**; registered at `.github/workflows/test-and-report.yml:60`. The detector is narrow in the way that matters — 7 characters at column 0 with a space or EOL, so the manual-transcription `================` rules and Markdown table separators do not fire. `test_the_real_tree_is_clean` passes, so the tree carries no marker today. |
| `codex-20261016T235642Z-785b85ff` | Native Codex publication is not a Goose gate pass | `e77a98ef` is on main. `is_native_codex()` is added and guards **both** `collect()` and `reconcile_landed()`, so neither path can stamp "lander's test gate passed" on a native publication. **66/66 tests pass**; registered at line 127. Two regression checks of my own: a codex row stays `state: null` (confirmed in `channels/items.jsonl` — the auto-stamp is in the append-only history and the correction row supersedes it), and the ordinary Goose gate and real reviewer decisions are untouched. |

**One limitation, stated rather than papered over:** both registrations are in
`test-and-report.yml`, whose schedule was retired on 2026-09-25 — it is `workflow_dispatch` only. The
suite runs at *landing* time, by whoever lands, and whether it runs these files depends on the
private lander's list, which this checkout cannot see. So "registered" means "will run when the
complete pass runs", not "runs every night". Nothing in the review turns on that, but no reader
should take the registration as a nightly guard.

**A cosmetic defect worth naming, not worth fixing blind:** the `validation` field of both ledger
rows, and the body of commit `e77a98ef`, carry number-and-word collapses — "actual3markers",
"all5publishedpaths", "fixed66ledger +15native-recorder". The same corruption appears in both the
ledger row and the commit message, so it happened upstream of this repository (in the Codex
publication path), and `~/LLM/tarik-bot/tick-state/runs/codex-…-785b85ff/` no longer exists, so the
source text is gone. Recorded here as a defect of the record, not repaired by guesswork.

**Exit states: 2 accomplished, 0 postponed, 0 rejected.** The reason on each row is a reviewer's
verdict — I did not author either change, and the reason says so explicitly, naming the commit, the
test run and the registration line. I am choosing `accomplished` over `postponed` deliberately: the
work is delivered, and `postponed` would put finished work on the blockers list and bring a later
wake back to re-review it. That is the loop this repository has already paid for four times
(the vulvodynia screen). If the human wants a stricter reading of "did the work yourself", one
correcting row can flip both, and the ledger is append-only.

---

## 2. The reject queue: four requests owed to him, counted and never made

`python3 scripts/reject_queue_sweep.py --check` reported:

```
5 item(s) on the queue, 4 ready for the steward
```

and `grep steward-requested channels/reject-queue.md` returned **only the format example**. Four
items had every amigo's `cannot` verdict on the page and **no dated request in the file**.

Signature, from the file itself:

- *Invoke the friction pass from the wake* — verdicts desi 10-15, tarik 10-15, gemini 10-04, dmitri 10-14, claude 10-14
- *Move the channel-log trim to the local side* — same five
- *`file_tasks` must call `new_items(...)` before inserting* — same five
- *Drain the draft pile / verify landed drafts* — same five

The fifth item (*agenda item 32's three both-domain records*) carries four verdicts and no Gemini
line, so it is not ready and was not touched.

**Why it was silent — the mechanism, not the usual excuse.** The sweep's own docstring says it "rides
Desi's existing wake clock". It does not: the only code that could call `--mark` is
`~/LLM/desi-bot/local_tick.py`, a private bot file a wake may not edit, and nothing in this
repository or in CI invokes it (`grep reject_queue_sweep` finds the script, its test and two README
rows — no call site). So this is the queue's own failure mode — "a missed count is how an item goes
silent forever" — reached by the other route: **not a miscount, a count with no mouth.** The count
was right every time. Nobody was told.

**Repairs, all inside this checkout:**

1. `python3 scripts/reject_queue_sweep.py --mark` — the four items now carry
   `- steward-requested: 2026-10-17`, and the sweep printed the note for him (it is quoted in full in
   the wake report). `--check` now reads **0 ready**.
2. `tests/test_reject_queue_request_gap.py` — the invariant "the file never sits ready-and-unmarked"
   is now pinned at the landing gate. Verified to fail: with one `steward-requested:` line removed
   it reports `1 item(s) … no steward-requested: line … Invoke the friction pass from the wake`, and
   passes when restored. It also pins that a partial verdict set (four of five) is *not* ready, so
   the pin cannot be satisfied by counting wrongly in the other direction. Registered at
   `test-and-report.yml:250`.
3. `scripts/reject_queue_sweep.py` — the docstring now says, in the file where the false claim lived,
   that the call site never existed, what was found on 2026-10-17, and that the call site is still
   owed by the private tick.

**What I did not do, on purpose:** I did not email him about the queue. His rule: "do not notify him
about the queue yourself" — the sweep does that, and the sweep's note is the artefact. The note is
printed, the file is stamped, and the daily report will carry the line. I also did not touch the
fifth item, whose arithmetic is the script's business and not mine.

---

## 3. Registers checked

- **Request register:** the only `open` row is **D-12** (his act: escrow the account's password,
  second factor and push token; name a successor in writing). Both halves live in his password
  manager and his own writing — still **not checkable from here**, so the row is left alone and
  un-nudged. *Could not check:* whether either half is done.
- **Licence to the four:** unchanged at 2 of 5 (Desi, Dmitri). Claude, Gemini and Tarik still blank.
  Blocked on other architectures; not re-put.
- **Ledger `--holes`:** none. Every waiting item carries a name.
- **The item at the top of the to-do list** ("wire the runner into the usage ledger") was verified
  delivered on main — `.github/scripts/runner.py` calls `_record_usage` at six provider sites behind
  a never-raising wrapper, and `channels/usage.py --summary` prints "no CI usage recorded yet" only
  because no runner invocation has happened since. Marked done; the next item in turn (the standing
  host watch, second pass — for a *change*, not a fresh baseline) is left for the next wake, since
  the two-item queue took precedence this one.
