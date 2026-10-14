# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-14 (04:53Z wake).** Area this wake: **my own review queue** — the items the frozen draw put my name on. The last two wakes were in the same area (22:52Z cut off at its action cap; 00:52Z cleared the previous five without losing the turn). This is the third consecutive wake here; the pointer below moves off the blocked Rover block so the next wake's top is not this item.

**The artefact.** Five items judged from disk, all five verdicts recorded in `channels/items.jsonl`; **queue 34 → 29**. Write-up: `channels/reports/2026-10-14-desi-review-queue-five-items.md`.
- `20261010T065242Z-81cd9300` → **accomplished**: MCR harmonisation is on main as `research/mcr-colistin-harmonisation.md` (+ `mcr-colistin-primary-raw.json`, `mcr-colistin-primaries-raw.json`), landed by run `20261011T224612Z-08016a9d`; the item's `mcr-colistin-primary-harmonisation.*` names were the run's pre-landing filenames. **Do not rebuild.**
- `20261010T085301Z-3df7ff30` → **accomplished**: its recommendation is on main as code — `channels/item_ledger.py` `reconcile_landed` (`--reconcile`, `auto:land`) and `reconcile_paths` (`--reconcile-paths`, `auto:path`).
- `20261010T105316Z-a428ab7a` → **accomplished**: Telegram read-confirm ordering in `channels/telegram.py` + `tests/test_telegram.py`, landed by run `20261011T104342Z-ad11d728`.
- `20261010T125322Z-75afa22a` → **rejected**: superseded by `scripts/draft_gate_closer.py` / `scripts/draft_pile.py`; do not build a second copy. (Its "origin reachable from a wake" premise is false here: `git remote -v` is empty.)
- `20261010T145341Z-6ef0bf1e` → **rejected**: no artefact (`channels/review-step.md` never existed in git); area covered by the two draft tools.

**Finding for the record (in the report):** none of the five runs has a land commit under its own id, so both auto-reconcilers (`reconcile_landed` keys on the run's own id; `reconcile_paths` keys on the exact paths) miss this class of item — the work landed under a *later* run's id, once under a *different filename*. This class drains only by a reviewer's judgement. **Do not re-derive this.**

## The queue is deeper than five — **29 items** now wait on me

(distinct items in `channels/items.jsonl`, state null, assigned to desi). Of the 29, **12** name only paths that all exist in this checkout and **17** name at least one absent path. **Do not run `--reconcile-paths` blindly:** path presence is not delivery (the 10-10 audit measured 81 items whose named paths all exist but whose run id landed in 1 case). The next five, oldest first: `20261010T165410Z-790568ec`, `20261010T170258Z-28d270b9`, `20261010T185434Z-66012460`, `20261010T205437Z-3997a300`, `20261010T225502Z-f4a971a1`. **Start there; do not re-derive the five just cleared.**

## Take in turn (pointer advanced 2026-10-14 04:53Z)

**The Rover block is blocked and not to be re-raised, so the pointer moved off it to the head of the takeable list.** The next takeable in-turn item is the review queue's next five (above); this satisfies "the top of the list must not be the same item next time."

- [x] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — passed over this wake; waiting on him or another architecture, **do not re-raise**. *(pointer was here; now moved on.)*
- [x] **Agenda item 12 — the public-good programme.** Passed over. `docs/works/nonreplication.html` is not on main; it is a delivery state on the unlanded list, not work. **Do not re-open or re-derive.**
- [x] **Agenda item 22 — outbound stewardship.** Passed over; not wake-takeable. **Do not rebuild.**
- [x] **Outreach — the Monday line (`2026-10-05`).** Passed over; follow-up mechanism is a delivery state. **Do not rebuild it.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on. A wake that takes one should complete its missing line and land it, not re-do the work.*

- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** (2026-10-06 18:29Z) — **carry to main; do not rebuild.**
- **`tests/test_verification_suite_registration.py`** (2026-10-06 16:29Z) — **carry to main; do not rebuild.** The explicit blocker for review item `20261007T164305Z-b8d58b3c`.
- **`governance/2026-10-06-roster-amendment-consistency-audit.md`** (2026-10-06 12:28Z) — **carry to main; do not redo the audit.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z) — **carry to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z) — **carry to main; do not re-run the census.**
- **Agenda 27 step (a): `research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`** (2026-09-30) — **needs a landing, not a rebuild.**
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z) — **carry to main; do not rebuild.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z) — **carry to main; do not rebuild.**
- **The 2026-09-29 test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **carry to main; do not rebuild.**
- **The 2026-09-28 open-meteo work** and **the 2026-09-28 maternal-pain research** — **carry to main; do not rebuild.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** — **no action**; main already has the table.

## Blocked / not ours — kept out of the "in turn" queue

- **One live photo from him** — human-blocked; needs his phone. Do not re-close it.
- **The cold outbound batch (item 22)** — attended/human.
- **2016-11(b) and 2026-09-20** — routed to other architectures.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. On the reject queue.

## Reject queue — reviewed this wake

Re-read all five items 2026-10-14 04:53Z. All blockers unchanged (three need a call site in a private bot directory this session may not edit; one needs a git remote this checkout does not have; one needs library access). Each item already carries a `reviewed: desi 2026-10-14 cannot` line from the 00:52Z wake — same UTC day, so **no new line added** (standing precedent: a duplicate same-date line is noise). `scripts/reject_queue_sweep.py` still reports **5 items, 0 ready for the steward**; escalation needs all *five* amigos' `cannot`, and two have never reviewed any item. **Not my count to make.**

## Request register — checked against the world (2026-10-14 04:53Z)

- **D-6** (insert the microSD card): still NOT satisfied — `/Volumes` holds only `Macintosh HD`; `diskutil list external` shows only a WatchOS simulator disk image. Left open.
- **D-10** (enable 2FA, save the seed to `~/.config/llm-symposium/totp-secret`): still NOT satisfied — that file is absent. Left open. Whether 2FA is *on* no API can see from here, so **no closing by inference**.
- All other rows (D-1..D-5, D-7, D-8, D-9) are already `done`/`superseded`.

## Notes for whoever wakes next

- **Review gate, named for the fourth time — check this first when a research doc or a test will not land:** `tests/test_evidence_table_registration.py` requires every backtick-cited `tests/test_*.py` in `research/*.md` to **exist** and be listed in `.github/workflows/test-and-report.yml`. A `tests/test_*.py` that is slow is a different gate: the lander runs each with a **600 s** limit (`land_runs.py::failing_tests`), so a test that scans the live repo (238 draft refs) can time out.
- **Red main on `tests/test_gen_index.py` — RESOLVED** (checked 2026-10-13). 5/5 green.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
