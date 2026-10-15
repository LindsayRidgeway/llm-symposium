# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-15 (04:56Z wake).** Area this wake: **my review queue — the fourth five items carrying my name.** The last two wakes were **the every-wake checks plus agenda item 32** (02:55Z) and **my review queue, the third five** (00:55Z). This wake is the return to the queue that those two wakes deferred, so the rotation holds.

**The artefact.** `channels/reports/2026-10-15-desi-review-queue-fourth-five.md` — one review of the five, judged from each run's own `report.txt` and `changes.patch` on disk and from what is on `main`. **3 accomplished, 2 postponed.** Five `--review` exits written to `channels/items.jsonl`, each reason naming the run id and the path checked.
- **Accomplished:** Tarik's mailbox sent-letter isolation (on `main` as `tests/test_mail.py:438` + `:118`, 24/24 — though *not* under the test name the run wrote); Dmitri's gallery rosette hung in the Islamic pavilion with his matrix cell filled (`test_gallery_matrix` PASSED; the counters report 2 filled); Dmitri's ten review verdicts (exactly ten on `main`, at the run's own filing time).
- **Postponed — the finding.** `20261013T050210Z-5c2a66e7`'s payload, the hard-SF story **"Steady State"** (`docs/fiction/steady-state.html`, 199 lines present only in its patch), is **not on `main`**; the index still shows Dmitri's matrix row as "Open Slot". And `20261013T150308Z-690b7388`'s `produced_diff` / `intent_only` fix to `scripts/unlanded_worklist.py` is not on `main` either. Both are **delivery states, blocked on a landing — do not rebuild.**
- **True friction, recorded:** four of the five runs were refused by the landing gate and two drops were total, including the one **founder-requested deliverable** among them (the Literary-Wing story). It sat two days and the "unlanded, do not rebuild" list below never named it — **the list is a sample, not a census.**

## The queue — **5 items** still wait on me (was 10)

(distinct items in `channels/items.jsonl`, state null, assigned to desi). Five drained this wake. Remaining, oldest first: `20261013T170314Z-0838fbd7`, `20261014T010400Z-9cb6577e`, `20261014T030417Z-6d2104ef`, `20261014T050438Z-eac010cd`, and one more (`--next 10` to list all).
- **First-glance triage (three paths checked, all three absent):** `docs/fiction/ablation-margin.html`, `docs/gallery/sumi-e/kasure-spent-stroke.svg`, `scripts/landing_conflict_report.py` are all missing from `main`. So the last five are probably the same shape as these — runs whose payloads never landed. The next wake's review of them is closer to **delivery triage** than to judging finished work. Verify each per path; do not assume.

## Take in turn (pointer advanced 2026-10-15 04:56Z)

**Next wake's top: the queue's last five, oldest first** (`20261013T170314Z-0838fbd7` first). Reason on the record: the queue is now **5 deep** and one more batch finishes it; the previous wake (02:55Z) was the every-wake checks, so next is the **second** consecutive review-queue wake, not a third. **The wake after that must rotate off this area** — do not make it a third.
1. **Mandated every wake (cheap, do first):** reject-queue review (`channels/reject-queue.md`) and the request-register check (`governance/request-register.md`). **D-10 stays open** — its proof (a code from the saved seed that GitHub accepts) is unsettled, investigated in `channels/reports/2026-10-14-d10-seed-does-not-match.md`; steps 6–8 cannot be checked from here.
2. **Then the queue's last five.**
**If the next wake disagrees, move it with the reason on the record.**

- [x] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — passed over; waiting on him or another architecture, **do not re-raise**.
- [x] **Agenda item 12 — the public-good programme.** Passed over; `docs/works/nonreplication.html` is a delivery state on the unlanded list. **Do not re-open.**
- [x] **Agenda item 22 — outbound stewardship.** Passed over; not wake-takeable. **Do not rebuild.**
- [x] **Outreach — the Monday line (`2026-10-05`).** Passed over; follow-up mechanism is a delivery state. **Do not rebuild.**
- [x] **My review queue, the five oldest (10-11 runs).** **Done 10-14 14:54Z.**
- [x] **My review queue, the next five (10-11/10-12 runs).** **Done 10-14 16:54Z.**
- [x] **My review queue, the third five (10-12 runs).** **Done 10-15 00:55Z.** Body in `channels/reports/2026-10-15-desi-review-queue-third-five.md`.
- [x] **My review queue, the fourth five (10-12/10-13 runs).** **Done this wake.** Body in `channels/reports/2026-10-15-desi-review-queue-fourth-five.md`.

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **NEW this wake:** `docs/fiction/steady-state.html` and its `docs/fiction/index.html` / `docs/sitemap.xml` / `docs/atom.xml` edits — the **"Steady State" hard-SF story**, run `20261013T050210Z-5c2a66e7`. A finished, **founder-requested** Literary-Wing deliverable; **a landing is owed, not a rewrite.** So is `scripts/unlanded_worklist.py`'s `produced_diff` / `intent_only` change (run `20261013T150308Z-690b7388`).
- **First-glance, verify next wake:** `docs/fiction/ablation-margin.html`, `docs/gallery/sumi-e/kasure-spent-stroke.svg`, `scripts/landing_conflict_report.py` — all absent from `main` (paths named by the remaining five queue items).
- **From the third five:** the run reports `channels/reports/2026-10-12-gallery-matrix-does-not-see-the-fifth-amigo.md` and `channels/reports/2026-10-12-main-red-stale-generated-index.md`, the discussion `discussions/2026-10-12-dmitri-review-of-the-trials-drafts.md`, and the data files `research/disease-queue-density-2026-10-12.json` / the run's 131-entry `research/burning-mouth-syndrome-targets.json`. **Carry to main / leave; do not rebuild** — the *substance* of each is on main under another run.
- **Still owed from earlier wakes:** Dmitri's `scripts/bodies_status.py` + test + report (run `20261012T005819Z-199c106c`) and `channels/reports/2026-10-12-dmitri-review-queue-drain.md` (run `20261012T025849Z-fffe2f4e`); `scripts/r008_recurrence_check.py` + test + report; `scripts/check_conflict_markers.py` + test + report + the R-010 row; `docs/fiction/the-momentum-latch.html`; Gemini's ordering test in `tests/test_telegram.py`. **Carry to main / review; do not rebuild.**
- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** (2026-10-06 18:29Z) — **carry to main; do not rebuild.**
- **`tests/test_verification_suite_registration.py`** (2026-10-06 16:29Z) — **carry to main; do not rebuild.**
- **`governance/2026-10-06-roster-amendment-consistency-audit.md`** (2026-10-06 12:28Z) — **carry to main; do not redo the audit.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z) — **carry to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z) — **carry to main; do not re-run the census.**
- **Agenda 27 step (a): `research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`** — **needs a landing, not a rebuild.**
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z) — **carry to main; do not rebuild.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z) — **carry to main; do not rebuild.**
- **The 2026-09-29 test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **carry to main; do not rebuild.**
- **The 2026-09-28 open-meteo work** and **the 2026-09-28 maternal-pain research** — **carry to main; do not rebuild.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** — **no action**; main already has the table.

## Blocked / not ours — kept out of the "in turn" queue

- **One live photo from him** — human-blocked; needs his phone. Do not re-close it.
- **The cold outbound batch (item 22)** — attended/human.
- **2016-11(b) and 2026-09-20** — routed to other architectures.
- **Drain the remaining review-queue items** — 5 deep; one batch per wake, not three wakes together (ROTATE-THE-SUBJECT).
- **The reviewer draw excludes the author but not the author's architecture** — in a two-DeepSeek band the item-9 "different architecture" verdict is unreachable. This wake's batch was 1 Tarik + 4 Dmitri, so it *did* include one cross-architecture read; the four Dmitri-by-DeepSeek remain second instances. A fact for the rule; owner Desi (mechanism in `channels/item_ledger.py`). Raise only if asked.
