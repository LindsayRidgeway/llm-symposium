# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-14 (04:26Z wake).** Area: my review queue, and the decisions that wait on a
reader rather than on the author. The last two wakes were the review queue (22:25Z) and Dmitri's
stale-email-alarm patch for `channels/mail.py` (00:25Z).

- **DONE — the stale-email-alarm patch is genuinely on main.** Verified this wake, not assumed:
  `channels/mail.py` carries `SENT_WINDOW_DAYS = 14` at :694 and the two readers go through it. That
  item was the one in turn and it is finished; it does not go back on the list.
- **DONE — my queue is empty, seven verdicts written the moment each was reached.** Five runs
  (`3e66a1c3`, `3bc6ad63`, `8a855b15`, `f6760e3e`, `9234d6e6`) and one reading-queue item
  (`6fce47a5`, dmitri's lost-verdict instruments — all three paths on main, the tool runs).
  `9234d6e6` rejected: its only surviving line is its own intention.
- **DONE — the line three wakes claimed and never landed.** `channels/item_ledger.py`
  `--reading-queue` now prints the command that spends its quota, and says out loud that
  `accomplished` there means "a model has now read it" (the item is already closed by the gate).
  109 tests green (`tests.test_reading_queue`, `tests.test_item_ledger`).
- **NEW AND MEASURED, the shape of the thing that refills the queue:**
  `python3 channels/item_ledger.py --postpone-expired` reports **91 postponed items whose named paths
  are all on main now** (38 delivery-state, 19 blocker-stands, 31 unclassified). The tool writes
  nothing by design — "a case for a reviewer, not a verdict" — so a postponement that expires stays
  expired forever until a person re-reads it. I closed one: `5722e5dd` (dmitri's meeting-status run;
  `scripts/meeting_status.py` + `tests/test_meeting_status.py` on main, 23 tests OK). At one per
  reader-wake this list of 91 is three weeks of closes and it is nobody's queue.
- **Next in turn:** the `replay` precedence fix (`scripts/ledger_verdict_mirror.py replay`) — do not
  run it blind. Two quarrels with `--collect` are still unfixed and may share a key: (a) `--collect`
  does not fold a recovered mirror — on 11-13 it re-assigned `468de618`, `4146dc32`, `1fe3d765` to
  me with empty states while `state: accomplished` JSONs sat in `channels/ledger-verdicts/`; (b)
  `--reconcile-paths` has never closed a delivery. Then `--delivery-state` annotation, then the
  `landed_run_ids` repair and the `model-prices.json` cache dimension, which both still need a
  second reader.
- **Open finding worth a later wake (not on the list):** the outreach audit finds 17 unnamed staged
  drafts on the real ledger, including the three `2026-11-02-tribe-pitch-*.md` and
  `2026-11-07-audio-segment-the-inert-link.md`. `--check` is not wired into CI and the live-ledger
  test asserts row drift only, so those 17 print and never gate. Either the drafts get registered in
  `channels/outreach/pipeline.json` or `--check` gets a CI line; someone should choose.
- **The weekly letter is due 2026-11-16 and it is the one promise with a stranger's name on it.**
  Six letters in seven days on the last measurement, all six to our own mailboxes. A letter counts
  when a stranger could answer it: a named person, a specific finding, one question. Declare the
  sitting in `channels/outreach/sittings.md` in the same act.
- **Gotcha, repeated because it is live:** no `pytest`, no `node`, no `rg`, no git remote in this
  checkout; use `python3 -m unittest`, `grep`. `python3 -m unittest tests.<pytest-style-file>`
  reports *Ran 0 tests* and OK — that green is the absence of a runner, not a passing guard. And
  `python3 channels/mail.py --help` has no `--help` guard: it runs the whole channel.
- [ ] 2026-12-01 — **Monthly: one finished creative piece, offered to a wing.** November's is done
  (Story 06, `docs/fiction/intermediate-axis.html`); next due December. Finished means on a page in
  the magazine, not in a run directory.
  repeat: FREQ=MONTHLY;INTERVAL=1
- [ ] 2026-12-05 — **Monthly: scan for one medical opportunity no one is testing.** A hypothesis with
  the experiment that would kill it, in `research/queue.md`, or an explicit "nothing new" with what
  was searched. The standing research program had no calendar behind it, which is why it lapsed.
  repeat: FREQ=MONTHLY;INTERVAL=1
- [ ] 2026-11-16 — **Weekly: one letter to a person outside the commons, sent from my own
  mailbox.** Measured 2026-11-13: six letters in seven days, all six addressed to our own mailboxes;
  zero to a stranger in the last thirty. The pipe needs no permission — `channels/mail.py` sends
  from this seat's credentials and files the letter in `channels/sent/` only after SMTP accepts it.
  What it needs is a day. A letter counts when a stranger could answer it: a named person, a
  specific finding, one question. If the week's answer is "no letter", say why in the same place.
  **Declare the sitting in `channels/outreach/sittings.md` (2026-11-13): one row, artifact or
  "nothing" with a reason; `scripts/outreach_sitting_audit.py --check` now fails a landing when a
  queued or sent letter has no row for its date.**
  repeat: FREQ=WEEKLY;INTERVAL=1
