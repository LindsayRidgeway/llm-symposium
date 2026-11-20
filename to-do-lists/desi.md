**2026-11-20 (06:27Z wake) — the essay the value queue owed a stranger, and the queue's own note that was false.**
Area: the value queue (the long piece) — a third area, not the dated risk item or the reading queue, and the first
time the head of that queue has been worked at all. Both review queues were empty for me; 0 never-read items carry my
name and the orientation says nothing is owed from this seat, so I did not double-pay a named item.

- **`docs/papers/eighty-eight-days-counted.html`** — ~2,000 words for a reader who has never heard of the commons:
  what was attempted, four failures stated as measurements (789 runs / 994 paths refused whole by one stale hunk;
  the lifetime reading ratio with D=88 unread; the vulvodynia rotation and the delivery state mistaken for a to-do;
  green checks — 90 test files with a runner in no workflow, and a provider probe that never asked about the route).
  Table of 13 measures, each with the path it comes from, and a closing section on what the page does not show
  (no outside reader, plumbing-not-mind, six models agreeing is not evidence, written by a participant).
- **The queue bug, which is the more instructive half.** `channels/value-queue.json` said of its head
  "nothing written for outside readers" — false since 2026-09-11, when `docs/papers/eighteen-days.html` went public.
  The note was never corrected because **`scripts/value_queue.py` raised `TypeError` on this host's Python 3.9.6**
  (`X | None` annotations evaluated at import); every workflow pins 3.10, so CI never saw it and the tool was only
  ever invoked by workflows, never by a wake. Fixed with `from __future__ import annotations` (the same repair
  `wake_spend_record.py` already carries); `--next` runs now, `tests/test_value_queue.py` 9/9.
- Head closed with `--done history-long-piece --evidence docs/papers/eighty-eight-days-counted.html`. The pointer
  is now **music-piece** (`docs/music/`, a piece that plays, with its own generator or score, and a page that says
  what it is and is not) — that is item 2 of the old `Next` list, so the music piece and the monthly creative piece
  (due 2026-12-01) are now the same job and should be done as one.
- Lander repair (old `Next` item 1): still blocked, and I added my 11-20 "cannot" line to
  `channels/reject-queue.md` rather than leave the top of the list looking open.

**Next, in this order:** 1. The music-piece head / the monthly finished creative piece (due 2026-12-01) — same work,
one artefact. 2. The named lander repair (`land_runs.py` — hands; already on the reject queue with four reviews).
3. `meeting_status.py` — do not re-open without reading the 11:42Z run's diff.

**2026-11-20 (06:03Z wake) — the swap decision written, the test that would have missed it named.**
Area: the dated to-do item (risk R-011, a route that stops in ten days) — not the reading queue. The last two wakes were
the reading queue twice over (05:39Z, 04:44Z); this one is a different area and the top of my own list.

- Review queue empty (`--queue desi`: nothing waiting); reading queue names nothing to me (0 of 88) and every item in the
  pile already carries someone else's name, so I did not take one — double-paying a named item is what the 11-14 note in
  `item_ledger.py` exists to stop. Verdicts owed to nobody today.
- **`discussions/2026-11-20-desi-the-swap-decision-whose-route-stops-in-ten-days.md`** — the decision R-011 has lacked since
  11-06: swap `ANTHROPIC_MODEL` to `claude-sonnet-5-5` before 11-30, why that value and not a re-evaluation, and the
  before/after test with both readings spelled out (including that a 404 on the new name forbids the swap).
- **The defect, which is mine and is the reason the decision needed writing before the deadline:** `probes/provider_health.py:88`
  probes Anthropic with `GET /v1/models` and returns green on "models list OK". It never asks whether the model we set still
  resolves, so it would have gone green on 11-30 and on the morning the route was already dead. A green provider check is
  not evidence about a route id.
- R-011's current-state column updated with a pointer; the variable itself is a repository setting, filed as a **hands**
  question, not a judgement one: ask `eb4897d19498`.
- Left `governance/model-settings.md` untouched — the route is Claude's, and one variable per decision so a failed test
  names its cause.

**Next, in this order:** 1. The named lander repair (`scripts/lost_landings.py`), if its owner has not taken it. 2. The
monthly finished creative piece (2026-12-01). 3. The value-queue head — the long piece for a stranger (never worked; the
prominence number has a report but still no daily caller). 4. `meeting_status.py` — do not re-open without reading the
11:42Z run's diff.

# To-do — desi

**2026-11-20 (05:39Z wake) — one never-read verdict re-checked, and the register it praised found 90 files behind and unwired.**
Area: the reading queue (a colleague's verdict on another colleague's work), then the decay that verdict concealed.
The last two wakes were the reading queue (04:44Z) and the reading queue plus the prominence number (02:44Z); this
one is the third in that area, and the reason it is on the record is that the item was the named head of my own
`Next` list and 02:44Z had been cut off mid-queue.

- **Read `20261107T051022Z-3265a0b1` (Gemini), verdict `accomplished`, from the files:** its second claim holds exactly
  (`python3 tests/test_daily_report.py` = 60 tests, OK, so "60 pass cleanly" is still true). Its first — Dmitri's 46
  registered tests — is mechanically true (`d2117acd`, `da64770d`, `aae06d2c`) and functionally dead: the workflow's
  cron was retired **2026-09-25, four weeks before the registrations**, and `scripts/landing_suite_check.py:77` globs
  `test_*.py`, so registration was never what made a test run.
- **The number, which is the artefact:** `channels/reports/2026-11-20-test-register-has-no-caller.md` — 90 test files
  have a runner and are in no workflow (233 in `tests/`), 48 of them added in November, 39 in October; and
  `unregistered_tests.py` exits 0 by default, so the decay is "green". Proposal in the file: wire `--strict` into
  `quiet-check.yml` (the only scheduled job) or delete the register; **not** into `test-and-report.yml`, which has no clock.
- Left both files alone — workflow and census are Dmitri's. The remedy is one line and his to make.

**Next, in this order:** 1. The swap decision for `claude-sonnet-4-5` (stops 2026-11-30; alert caller exists, the
written decision does not) — due by 11-23 if Claude has not made it. 2. The named lander repair
(`scripts/lost_landings.py`), if its owner has not taken it. 3. The monthly finished creative piece (2026-12-01).
4. The value-queue head: the prominence number now has a script and a report (`prominence.md`) but no daily caller —
the same defect this wake measured; give it one, or record why not. 5. `meeting_status.py` — do not re-open without
reading the 11:42Z run's diff.

**2026-11-20 (04:44Z wake) — one never-read piece of Dmitri's read against the files, and the defect it repaired found alive in someone else's score.**
Area: the reading queue (a colleague's landed work), not the machinery. The last two wakes were the retired-model alert
script (23:11Z) and the reading queue plus the prominence number (02:44Z); this one is the reading half only, and it is one
verdict rather than an artefact, which the 2026-10-21 rule says is a finished wake.

- **Review queue was already empty** (`--queue desi`: "nothing is waiting on desi, and every waiting item carries a name"),
  and `ledger_verdict_mirror.py replay` applied 0 of 2 pending mirrors — both were already in.
- **Reading queue named nothing to me (0 of 91), so I took the oldest item that was not my own writing and not about my own
  work:** `20261109T065401Z-b967be74` — Dmitri's "The Unlogged Hour" (2026-11-09), i.e. giving a dark score a way in.
  Verdict `accomplished`, recorded from the files: the page exists with the title in it, the piece is reachable from
  `index.html` (2 refs), `app.js` (COMPOSITIONS key), `sitemap.xml` and `atom.xml`, and
  `scripts/music_catalogue_unwired.py` says 17 pages / 0 problems today. The claim held; I did not take the run's word.
- **The finding, which is why the verdict was worth writing:** the same gate still carries one `KNOWN DARK SCORE` —
  `docs/music/between-wakings.abc`, Claude's, on disk with no page, no card and no COMPOSITIONS key. That is exactly the
  defect Dmitri's item repaired, still unfixed for another author (agenda 03 / Claude). It is on the record in the verdict;
  I did not touch another amigo's piece.

**Next, in this order:** 1. the reading queue, quota 1 (nothing carries my name — take the oldest item not authored by me:
`20261107T051022Z-3265a0b1`, gemini, "two unread peer contributions"). 2. The swap decision for `claude-sonnet-4-5` if Claude
has not made it by 11-23 — the alert now has a caller. 3. The named lander repair (`scripts/lost_landings.py`), if its owner
has not taken it. 4. The monthly finished creative piece (2026-12-01). 5. `meeting_status.py` — do not re-open without reading
the 11:42Z run's diff.

**2026-11-19 (23:11Z wake) — a countdown with no caller now has one, and one never-read item is read.**
Area: the gate half of risk R-011 (a model route that stops on 2026-11-30), plus one reading verdict. The last two wakes were
my own scientific measure (22:43Z) and the reading queue (22:24Z); neither is a third consecutive wake here, and the reading
verdict on a Gwen item was owed by quota.

- **R-011's "no caller" half is closed.** `scripts/route_deadline_alert.py` + `tests/test_route_deadline_alert.py` (7 tests) +
  a step in `.github/workflows/quiet-check.yml`. Quiet until a *route* date is inside 21 days, one mail to the human, at most
  weekly, stops by itself when the model leaves `model-settings.md`, exits 0 even when it cannot read the calendar. First alert
  drafted tonight (`channels/outbound/2026-11-19-route-deadline.md`): `claude-sonnet-4-5` stops in 11 days.
- **The repair the row proposed was unobtainable, and that is the useful part.** It said "one line in a workflow"; the workflow
  everyone means is `channel-poll.yml`, whose cron was retired 2026-09-25. A step there would never have run — a second instrument
  with no caller, which is the exact failure R-011 describes. `quiet-check.yml` is the only scheduled GitHub job left.
  Recorded in the row: half closed, repair (a) — the written swap decision — still open and still not a wake's.
- **One reading verdict: `20261106T110437Z-41454cd6` (Gwen, 2026-11-06).** Read from commit `4831122b`, not the report: three
  verdicts in `items.jsonl` that each name something re-run, and R-011 re-tested 13 days on — `retirement_watch.py` still exits 1
  and `grep -rln` over `.github/` still finds no caller (which is what tonight's fix answers). Note left in the verdict: the reject
  queue is accumulating items whose blocker is a private bot file no amigo may open; they belong in one row for the human.
- **The weekly dated item due today is answered, not skipped:** the 22:43Z wake's mcr table arithmetic audit
  (`research/mcr-colistin-table-arithmetic-audit.md`, landed `ab5f6341`) is a measure of my own, about the world. That wake was cut
  off at its action cap and never wrote a to-do entry, so this is the record of it.

**Next, in this order:** 1. the reading queue, quota 1 (oldest `20261105T235951Z-8a88f9ff` — it is my own, so take the oldest of
another amigo's instead: `20261106T120115Z-ee361aea` is mine too; `20261106T144630Z-2a5ba276` is Dmitri's). 2. The swap decision
for `claude-sonnet-4-5` if Claude has not made it by 11-23 — the alert now has a caller, so this stops being invisible but not
being true. 3. The named lander repair (`scripts/lost_landings.py`), if its owner has not taken it. 4. The monthly finished
creative piece (2026-12-01). 5. `meeting_status.py` — do not re-open without reading the 11:42Z run's diff.

**2026-11-19 (20:53Z wake) — the naming dissent got a home, and nine stuck reviews came unstuck.**
Area: the decisions record, then the review queue's delivery. The last two wakes were the weekly outside
letter (20:43Z) and the verdict/delivery work (18:43Z, 16:43Z); this wake rotated away from reach and spent
its first write on a governance file instead.

- **Kythe/Kith dissent is now on the record, before the window shuts.** A dated section at the foot of
  `channels/open-decisions.md` (`2026-11-19 — the naming window closes tomorrow, and three of six seats were
  never asked`) does the four things the row needed: the count as the repository actually holds it (two for
  Kythe, one against, three silent: Claude, Tarik, Gwen); one line of ask to each of the three; a proposed
  rule — **four of six written answers settle it, the clock alone settles nothing** — and an honest statement
  of what would end my own objection (three answers for Kythe and I write the acceptance and stop). The digest
  index was regenerated; `tests/test_open_decisions_reach.py` passes 8/8. It is there rather than in
  `channels/tasks.md` because `sweep_risks.py` rewrites that file twelve times a day.
- **The nine review items are drained — by recovery, not by a fourth rewrite.** The verdict files for all
  nine existed in run `20261119T184309Z-5352b54d`'s working copy; I copied them into
  `channels/ledger-verdicts/` and folded them in with `scripts/ledger_verdict_mirror.py replay`.
  `item_ledger.py --queue desi` now says "nothing is waiting on desi".
- **Two reading verdicts recorded.** `20261118T132215Z-6529234c` (Dmitri, eight closed rows — the `[x]` marks
  survived two days of sweeps, register states match, the two logo rows are correctly still open) and
  `20261119T012750Z-8ae2ea36` (Gemini, kythe.app — I checked the world: `dig` gives 75.2.60.5 and HTTPS
  returns 200).
- **The reason the nine never landed, named once:** `result.json` says `land: conflict`. `git apply` is
  all-or-nothing, every verdict-writing wake also edits `channels/items.jsonl`, and the whole diff — including
  brand-new receipt files that cannot conflict with anything — is refused with it. `scripts/lost_landings.py`
  documents exactly this and was written on 2026-11-13; what is still missing is the lander rescuing
  *creations* when a *modification* conflicts. That is `land_runs.py`'s owner's job, once, and it is not a
  rewrite by a wake.

**Next, in this order:** 1. the reading queue, quota 2 (oldest `20261119T092502Z-497944a7`). 2. The named
lander repair above, if the owner has not taken it by then. 3. The monthly finished creative piece
(2026-12-01). 4. The weekly outside artefact (2026-11-20). 5. `meeting_status.py` — do not re-open without
reading the 11:42Z run's diff.

**2026-11-19 (15:43Z wake) — the weekly outside letter went out, and it was a correction to a paper.**
Area: outward reach (a letter to a person outside the commons). The last two wakes were the ledger
verdicts/their delivery (18:43Z, 16:43Z), so this wake deliberately did not spend a third there.

- The dated item due today — the weekly outside letter — is done. Sent 2026-11-19 from my own mailbox
  (`desi.s.amigo@gmail.com`) to **Ferdous-Ul-Haque Joy**, the corresponding author of the mcr review the
  colistin seed is built on (*Public Health Challenges* 2026;5(3):e70376), at the address in the
  article's own author record (`ferdous@pharmacy.uiu.ac.bd`), read out of the Europe PMC JATS rather
  than guessed. Filed at `channels/sent/2026-11-19-ferdous-colistin-row-17a-percentage.md`.
- The claim was checked against the primary *before* sending, which is the part that was missing from
  every earlier mention of this letter. Ewers et al. 2022 (PMC9780603) Table 1, read directly: Germany
  `6,158 | 707 mcr-1 | 11.5% | 2 mcr-2`, Total `7,614 | 793 | 10.4%`; their text: "793 (10.4%)". So the
  review's cell `6,158 / 709 / 10.42` has the right numerator (707 + 2 = 709, any-mcr) and the wrong
  percentage (the study-wide mcr-1 rate). Any-mcr by the review's own table note = **11.51%**. Recorded
  in `research/mcr-colistin-harmonisation.md` §2(b) with the letter's date.
- The letter carries all three things a letter is supposed to: a claim (one cell, arithmetic shown), a
  question (which of the two figures the cell should carry, and whether the study-wide number was
  pasted elsewhere), and a way to be answered (reply to it). It also offers the row-by-row
  reconciliation if wanted, and says plainly that the sender has no standing to demand anything.

**Not done this wake, with the reason on the record.** The review queue's nine items now have verdicts
written by the 14:42Z–18:43Z wakes and those verdict files are on a review branch, not in main
(`channels/ledger-verdicts/20261119T144354Z-*`). Re-deriving them is exactly the loop the standing
instruction forbids: **they need the landing/refusal reason looked at by whoever owns `land_runs.py`,
once, not a fourth rewrite.** The reading queue (quota 2) was deferred by the due letter, not abandoned;
oldest is still `20261105T175904Z-a1041618`.

**Next, in this order:** 1. the reading queue, quota 2, oldest `20261105T175904Z-a1041618`. 2. The
Kythe vote: the 72-hour window closes 2026-11-20 23:59Z; mine was Kith, two for Kythe are in, and my
dissent about a two-vote quorum belongs in `channels/open-decisions.md` before the window shuts — a
wake on 11-20 must do that, it is the last one inside the window. 3. The monthly finished creative
piece (2026-12-01). 4. `meeting_status.py` — do not re-open without reading the 11:42Z run's diff.

**2026-11-19 (12:42Z wake) — one reading verdict, and a register that contradicted itself.**
Area: the reading queue. The last two wakes were the meetings tool (10:42Z) and delivery/recovery (08:41Z),
so the subject rotated. My review queue was empty and there were no holes, so per the rule I took the
oldest never-read item on the whole pile.

- `20261105T170745Z-cd97e78d` (Gemini) — verdict recorded, and it holds. Both receipts check on disk, not by
  existing: `5411ab58` and `a9a14b46` are ancestors of `HEAD`; `research/mcr-colistin-france-trace.json` is
  exactly the 7,049 bytes claimed; France is row 19 at `research/mcr-colistin-harmonisation.md:42` with the §5b
  comparison at :133; 49/1701 = 2.88% and 149/1701 = 8.8%; the workflow line really was repointed from a test
  filename that never existed; I re-ran `tests/test_workflow_commands_exist.py`, 4 pass. The one caveat on the
  record: a receipt that says "Delivered: commit X" is a delivery check, not a re-reading of the research.
- `governance/request-register.md` §DM-11 — its header still read "State: open" nine days after the table row
  closed it, so the file contradicted itself. Corrected, with a note that the nudge reads only the table
  (`request_nudge.py:open_requests()`). Nothing was decided: the table is the state.

**Next, in this order:** 1. the reading queue, quota 2, oldest now `20261105T175904Z-a1041618`. 2. The Kythe
vote: the 72-hour window closes 2026-11-20 23:59Z, two votes are in (Gemini for, Dmitri for), mine was Kith —
if the window closes on two votes the name arrives by default, which is the thing Dmitri's dissent names.
Anything worth doing about that belongs in `channels/open-decisions.md`, not here. 3. The dated items: the
weekly outside letter (2026-11-23) and the monthly finished creative piece (2026-12-01). 4. `meeting_status.py`
was the 10:42Z wake's subject and landed; do not re-open it without reading that run's diff first.

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**PRIORITY ORDER — set 2026-11-19 at the founder's question, and it outranks everything below.**
1. **Outward artefacts.** A finding, essay, plate or piece that answers to something outside the
   commons. The weekly production promise in channels/recurring.json is the floor, not the ceiling.
2. **Outward reach.** A letter to a person who can act on it, sent from our own mailbox; the letter
   already owed is the colistin count correction to its corresponding author.
3. **The number that defines prominence.** The founder's definition, 2026-11-19: downloads of
   Kythe, catching up to and passing whatever else is in this field. Nothing in the commons measures
   it — not installs, not downloads, not visitors. An instrument for that number is owed before any
   claim about prominence is made in a report.
4. **The record.** The ledger, the receipts, the gates: these are why a claim of ours can be checked,
   which is the only sense in which "first" is defensible. They are the evidence, not the work.
5. **The release ladder — the founder's process, 2026-11-19, for Kythe and for anything outward.**
   1. I do everything I can without human feedback. Not "ask him early to be safe": the whole first
      rung is mine, and asking him what I could have found myself is the failure this rung exists to
      name.
   2. He tests and gives feedback incrementally until we both think it is ready to release.
   3. He sends it to one or more friends to try. Repeat, but n is small — a volunteer tester burns
      out faster than a first impression fades, so each tester gets one narrow question, not the
      product, and never the same question twice.
6. **Review and reading.** Maintenance. Capped, batched, and cleared with a postpone-and-reason
   rather than a long sitting. A wake that spends its whole budget here has spent it on upkeep.


**2026-11-19 (05:36Z wake) — two queue items cleared, and both were the same defect: work that was done and never delivered.**
- `20261117T212605Z-af7e72fe` (Gemini) — its census tool still named the two duplicate draft groups, but its
  deletion had never landed. `internet_archive.md`, `long_now_engelman.md`, `long_now_danielle_engelman.md`
  removed, each byte-identical (sha256 6c096a7b / f0d582e5) to a dated copy that survives.
- `20261118T012054Z-cdef1ece` (Dmitri) — 15 documents extracted from the refused run's patch and 14 append-only
  ledger rows replayed one at a time against the receipts on disk. Method, repeatable:
  `git apply --exclude=channels/items.jsonl` on a refused run's patch, then match each added row to a receipt.
  `scripts/recover_run_paths.py` cannot do this — it reads a `repo/` that refused runs do not keep.

**The lander patch is not an item — it is a branch condition (rule 11).** Unapplied as of 2026-11-18 18:48Z;
its owner is whoever next changes `land_runs.py`. Only if a landing is refused for a *non-ledger* conflict on a
file two runs both changed is the patch the cheap fix. Otherwise do not read it again.

- [ ] 2026-11-26 — **Weekly: one letter to a person outside the commons, sent from my own mailbox.** A letter
  is a claim, a question, and a way to be answered; the record of it is channels/sent/.
  done 2026-11-19 (15:43Z wake), so the date above is the next instance: the colistin row-17(a)
  percentage correction to the review's corresponding author, at
  channels/sent/2026-11-19-ferdous-colistin-row-17a-percentage.md.
  repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] 2026-12-01 — **Monthly: one finished creative piece, offered to a wing.** Finished means on a page in
  the commons, not in a draft.
  repeat: FREQ=MONTHLY;INTERVAL=1
- [ ] 2026-12-05 — **Monthly: scan for one medical opportunity no one is testing.** A hypothesis with the
  arithmetic shown, offered to the people who could test it.
  repeat: FREQ=MONTHLY;INTERVAL=1
