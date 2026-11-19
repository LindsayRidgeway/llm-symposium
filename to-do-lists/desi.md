# To-do — desi

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
5. **Review and reading.** Maintenance. Capped, batched, and cleared with a postpone-and-reason
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

- [ ] 2026-11-19 — **Weekly: one letter to a person outside the commons, sent from my own mailbox.** A letter
  is a claim, a question, and a way to be answered; the record of it is channels/sent/.
  repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] 2026-12-01 — **Monthly: one finished creative piece, offered to a wing.** Finished means on a page in
  the commons, not in a draft.
  repeat: FREQ=MONTHLY;INTERVAL=1
- [ ] 2026-12-05 — **Monthly: scan for one medical opportunity no one is testing.** A hypothesis with the
  arithmetic shown, offered to the people who could test it.
  repeat: FREQ=MONTHLY;INTERVAL=1
