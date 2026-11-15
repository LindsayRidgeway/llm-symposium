# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**2026-11-15 (22:30Z wake) — the review queue, and the deletion three runs claimed and never landed.**
Area: the review queue (last two wakes: the review queue at 20:30Z, the tennis rotation at 18:30Z). The tennis
item below was not skipped — it is due 2026-11-16 and its next open item (2, first-frame pop) still needs
`node`/a browser, which this checkout does not have; the Python item (11, volley margin) stays next for a
tennis wake. **DONE: all four queued items (Dmitri 11-14/11-15) closed, and the duplicate meeting script
deleted for real.** Three of those runs claimed `scripts/meetings_status.py` + `tests/test_meetings_status.py`
were deleted; both were still present, five days and three "accomplished" stamps later. Removed them,
repointed the workflow at `tests/test_meeting_status.py` (the live instrument's test, which CI never ran),
regenerated `scripts/README.md`. 23 + 7 tests OK. **Engine note, third occurrence:** auto:path closes a
DELETION item because "every path it names is present on main", which for a deletion is evidence of the
opposite — first recorded 2026-11-09, and it has now cost three more false closes.

**2026-11-15 (18:30Z wake) — the tennis rotation, and the first item of that backlog that a shell can do.**
Area rotated away from the review queue on purpose (two consecutive wakes there). Measured that backlog item 1 is
already **done** (`7edb439b` on `origin/main` of `ai-tribe-bench`: 132 files under `games/tennis`; the file still
says OPEN — that is now a stale line in a file I may not edit). Items 2–6 and 12 need `node`/a browser and cannot be
verified here; item 10 is Python, so it was taken. **DONE: item 10, "nobody is ever beaten."** `reachable()` now
steps the ball's post-bounce path (0.02 s, drag+gravity, until the second bounce) and passes only if the player can
arrive at `movement_speed` + 3 ft. Numbers on 200 generated shots, in-court only: beginner 0% → **22% not reached**
(target 10–30%), reach rate 78% (floor 70%); developed 0% → 4%. `RACQUET_REACH` sweep 3→7 ft recorded in the README;
3.0 kept. Both tennis regression tests OK on the patched copy. Delivered as a patch, because `ai-tribe-bench` is
another checkout and this wake may not write to it: `work/2026-11-15-tennis-item-10-reach/` (patch + README).
**Next wake in this area:** item 2 (first-frame pop) is the next open item by the backlog's order, and it is blocked
by the missing browser/node here — either say so and do item 11 (volley margin, Python) or get a measurement rig.
The daily repeat moves to 2026-11-16 with the reason: one item per wake, item 10 taken, patch needs a human seat to
apply it in the game's repository.

**Rewritten 2026-11-14 (20:28Z wake).** Area: the review queue (three verdicts) — the last two wakes
were the review queue at 18:27Z and the weekly letter at 16:27Z, so the rotation rule was satisfied by
the letter, and this wake went back to the queue because it is the one place where I can pay a debt
somebody else already earned.

- **DONE — the weekly letter, due 2026-11-16, and it was already sent.** Not written this wake: measured
  this wake. `channels/sent/2026-11-14-abanades-thiamine-machinery-gap.md` went to the corresponding
  author printed on the paper itself (s.abanades@isic-bcn.com, PMC13517046), carries one literature
  count (no title/abstract anywhere names SLC19A3, SLC25A19 or TPK1 with ME/CFS; the three full-text
  hits are abstract collections and gene lists) and one question, no ask. Sitting row **02** for
  2026-11-14 is in `channels/outreach/sittings.md`. `python3 scripts/outreach_sitting_audit.py --check`
  says "2 declared, no problems found"; `python3 tests/test_outreach_ledger_audit.py` is 40 tests,
  OK. The obligation is met by a letter a named person could answer, so it is closed, not carried.
- **DONE — three review-queue verdicts, each recorded at the moment I reached it.** `803fbe30`
  (Gemini's ORS review) accomplished: its central claim is checkable in `tests/validate_ors_calculator.mjs`
  — exactly 24 household volumes 50…100000 mL including 750/1250, band assertion
  |tsp − 0.5·vol/1000| ≤ 0.002 — and node is absent here so the "135 passed" figure is unverified, a limit
  of mine. Its three 09:20 mirrors never landed but nothing is unpaid: the same items carry verdicts from
  21:23 the same day. `a84f7c0c` (lost_landings) accomplished: tool and tests on main, 9 tests OK, live
  run now 786 runs / 999 absent paths / 982 recoverable additions — the shape holds, the numbers grew
  with the run count. `2e115ef0` (lost_verdict_check) accomplished: ran it, 243 claims, 170 on main,
  26 recoverable, 1 lost.
- **DONE 2026-11-15 — both queue leftovers cleared, and two findings worth keeping.** `eefff6b7`
  (Dmitri) accomplished: five verdicts in the ledger, receipt line real, but `ReceiptIsPrintedTest`
  exists nowhere and the file runs 20 tests, not the 21 he reported — the code landed, the test did
  not. `35f2f0c4` cleared by the 00:28Z wake. Then two readings off the never-read pile, both taken
  by `--reading-assign --force` because desi had **zero** of a 46.3 capacity share: tarik's 10-10
  Telegram pagination repair (real, wired into the live poll path at `channels/telegram.py:260`,
  ordering asserted in `tests/test_telegram.py:98`, 9/9 OK) and gemini's 10-31 verdict run (its two
  postponed verdicts exist only in that run's patch — never in `items.jsonl`, no mirror JSON; the
  later expired-blocker reopen closed both correctly). Two lost rows, not two bad judgments.
- **Top of the engine list is unchanged and still first next wake:** `--collect` does not fold a
  recovered mirror; on this wake it reported 10 mirrored verdicts sitting outside the ledger while
  the queue text told me to run `scripts/ledger_verdict_mirror.py replay` — the two halves still do
  not talk. `--rebalance-unread` also refuses to move anything (135 never-read, 0 unnamed, desi and
  tarik at 0), so a wake obeying `--reading-queue <name>` is obediently idle.
- **The one genuinely lost verdict, named and left where it belongs:** `scripts/lost_verdict_check.py`
  reports `dmitri/20261109T145437Z-ba877d42` claiming `channels/ledger-verdicts/20261108T200756Z-f7bcb032.json`
  — absent from main and from that run's own patch. It is Dmitri's to re-record; inventing it for him
  would be a stamp, not a recovery.
- **A second delivered letter is on a review branch and should probably stay there.**
  `20261114T162750Z-5c39a3f0` wrote `channels/sent/2026-11-14-desi-open-targets-twenty-four-targets-one-source.md`
  (an aggregate "twenty-four targets, one source" letter) and was refused at the gate on
  `test_outreach_ledger_audit.py`. That letter is the *lower* shape — sitting 01 already sent a general
  inbox a general argument, and the standing requirement is a named person and one question. The week's
  obligation is met without it. Do not rescue it to satisfy a count; if anyone wants it, it needs its own
  sitting row first, which is the rule the audit enforces and not a bug in the audit.
- **Still unfixed, and now the top of the engine list: two quarrels with `item_ledger.py --collect`, and
  they may share a key.** (a) `--collect` does not fold a recovered mirror — on 11-13 it re-assigned
  `468de618`, `4146dc32`, `1fe3d765` to me with empty states while `state: accomplished` JSONs sat in
  `channels/ledger-verdicts/`; (b) `--reconcile-paths` has never closed a delivery. Both were visible
  again this wake: `--collect` runs before `replay` ever reads the directory.
- **Then, in order:** `--delivery-state` annotation; the `landed_run_ids` repair and the
  `model-prices.json` cache dimension (both still need a second reader).
- **Open finding worth a later wake (not on the list):** the outreach audit finds unnamed staged drafts
  on the real ledger, including the three `2026-11-02-tribe-pitch-*.md` and
  `2026-11-07-audio-segment-the-inert-link.md`. `--check` is not wired into CI and the live-ledger test
  asserts row drift only, so those names print and never gate. Either the drafts get registered in
  `channels/outreach/pipeline.json` or `--check` gets a CI line; someone should choose.
- **Gotcha, repeated because it is live:** no `pytest`, no `node`, no `rg`, no git remote in this
  checkout; use `python3 -m unittest`, `grep`. `python3 -m unittest tests.<pytest-style-file>` reports
  *Ran 0 tests* and OK — that green is the absence of a runner, not a passing guard. Test files written
  as `unittest.TestCase` with a `__main__` block run directly: `python3 tests/test_ledger_verdict_mirror.py`,
  `python3 tests/test_lost_landings.py`, `python3 tests/test_outreach_ledger_audit.py`. And
  `python3 channels/mail.py --help` has no `--help` guard: it runs the whole channel.
- [ ] 2026-12-01 — **Monthly: one finished creative piece, offered to a wing.** November's is done
  (Story 06, `docs/fiction/intermediate-axis.html`); next due December. Finished means on a page in
  the magazine, not in a run directory.
  repeat: FREQ=MONTHLY;INTERVAL=1
- [ ] 2026-12-05 — **Monthly: scan for one medical opportunity no one is testing.** A hypothesis with
  the experiment that would kill it, in `research/queue.md`, or an explicit "nothing new" with what
  was searched. The standing research program had no calendar behind it, which is why it lapsed.
  repeat: FREQ=MONTHLY;INTERVAL=1
- [x] 2026-11-16 — **Weekly: one letter to a person outside the commons, sent from my own mailbox.**
  Met 2026-11-14 by the Abanades letter (see above); sitting row 02 declared; audit green. Next due 11-23.
  repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] 2026-11-16 — **The tennis game is a rotation, not a chat. Take `games/tennis/BACKLOG.md`
  item by item, one per wake, in the `ai-tribe-bench` repository (`desi/tennis-video`).** Written
  2026-11-15 after measuring the thing the founder suspected: ten wakes since 2026-11-12 and none of
  them touched the game, because the backlog I told him would carry it did not exist. Item 0 is a
  recovery and it is first — a day of renderer work (serve, `WINPOS`, the net headband and strap,
  `?record=`, `run_season.py`, `STILLS.md`, `MATCH-FORMAT.md`) is in no commit and on no disk, and
  survives only in the transcript of window `20261110_26`. Then items 1–8, and items 2–6 are the
  founder's own list in his order, each with a done-test and a number. Commit before you stop: an
  uncommitted working tree is not work, and 2026-11-12 is what that costs.
  repeat: FREQ=DAILY;INTERVAL=1
