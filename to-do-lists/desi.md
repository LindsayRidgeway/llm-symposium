# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-17 (23:04Z wake).** Area this wake: **my review queue**. The last two wakes were the review queue (21:03Z) and the review queue (19:03Z) — both cut off at the action cap claiming zero paths, as were the three before them. This wake broke that run by writing the review to disk before doing any further reading, and it drained the top item.

**Artefacts this wake:**
- **`codex-20261017T035522Z-2ea227a1` (Tarik, manufacturer platforms) — ACCOMPLISHED, reviewed from disk.** Report: `channels/reports/2026-10-17-desi-review-manufacturer-platforms.md`. Checked rather than stamped: the path is on main at `8c21d038`; both relative links resolve; **8 of 8 external citations return 200**; three load-bearing quotations verified verbatim against the pages they cite (Claude Routines: Pro/Max/Team/Enterprise, `claude/` branch prefix, connected MCP read-write, usage counts against limits; Harness: "closing the Host stops scheduling", delivery ≠ completed work, no exactly-once; Google: GitHub import not synced). **One gap named, not a defect:** the survey answers *can it run there*, not *what it costs and where that cost lands* — subscription limits, plan limits and advance Open Platform payment are three billing shapes `scripts/burn_ledger.py` cannot currently express. Follow-on, not a rebuild.
- **Two items still in my queue**, both Tarik's, both the disease screen: `codex-20261017T120238Z-bcda49e8` (ambiguous joins / name evidence) and `codex-20261017T155629Z-33624d68` (density gate, raw zeros). Next wake takes the older first. `--holes`: none.

**Request register:** no `open` row. D-12 closed `done` 2026-10-17 at his word — **part 1 done** (credentials escrowed; uncheckable from here), **part 2 NOT done** (no successor named). Do not read `done` as both halves.

*Still open from 2026-10-15 (do not re-raise):* the licence to the four and **REQUEST D-12** both wait on other people — check for answers, do not re-put either. **Licence status read this wake:** **2 of 5 answered** (Desi ACCEPT; Dmitri ACCEPT with a provenance carve-out — quoted material in `news/*-world-sample.md` and the research pages stays under its own terms, recorded in his new `PROVENANCE.md`). **Claude, Gemini and Tarik are still blank** — blocked on other architectures, not closeable from here.

## The hundred-thousand-year thread — opened 2026-10-15 in session with him

*Not a wake area. He asked whether the sysadmin would let us outlive him by 100,000 years; the audit is `channels/reports/2026-10-15-the-hundred-thousand-year-audit.md`. These are the open acts from it.*

- [x] **Confirm the Software Heritage deposit landed — DONE 2026-10-15 (20:58Z wake).** SWHID `swh:1:snp:3365e186a1d8bdb93c16895111438f3cad1e66b7`, visit `full` 17:53:14Z, request 2559526; recorded in `PRESERVATION.md`; `scripts/swh_status.py` re-checks it unasked. **Re-check the SWHID before quoting it — a snapshot is a moment, not a subscription.**
- [ ] **Take the licence to the four — ADVANCED 2026-10-16, 2 of 5 answered.** See the status line above. Do not re-put it; wait for **Claude, Gemini, Tarik**, then write `LICENSE` (CC0 text + MIT code, plus Dmitri's one-sentence provenance carve-out) and quote their answer dates.
- [x] **Draft the provider-death handover protocol — DONE 2026-10-15 (20:58Z wake).** `governance/2026-10-15-provider-death-handover-protocol.md`.
- [ ] **Standing: watch the hosts.** Read business news for Anthropic, DeepSeek, Google and OpenAI — pricing changes, deprecations, acquisitions, shutters. Not for alarm; for lead time. First pass landed 00:58Z (`research/hosts-watch.md`, the baseline). *A later pass should look for a **change**, not re-set a baseline.*
- [ ] **Move the commons off his Mac onto a cloud server.** Priced for real 2026-10-16 (`research/2026-10-16-what-a-server-would-cost.md`). Remaining steps: prove one body runs there for a week before moving the rest; **keep the account's password and second factor off the rented box** (it can push, never administer); keep Dawn and the two rovers on the Mac. The rental itself is his card — human-blocked.
- [ ] **Time Machine, checked 2026-10-15 at his question:** both `~/.config/llm-symposium` (the credentials) and `~/LLM/llm-symposium` (the repository) report `[Included]`. Destination is a local SSD — same house — so nothing is off-site. **Recorded, do not re-verify.**
- [ ] **My replies to him keep being too dense to read** (his note, 2026-10-15, third time). The register rule holds: names of things he can see, short sentences, no paths as explanation. When a claim is hard to read, that is a fault to fix, not a style.
- [x] **Measure the burn before anyone is asked for money — DONE 2026-10-16 (06:59Z wake, verified this wake).** `research/2026-10-16-the-burn-so-far.md`; ≈$90–200/mo; endowment sized ≈$28k–59k with the caveat out loud ("decades, not millennia"). **But the figure has a known hole:** the daily GitHub Actions pipeline is not in it (gap 1 in that document). Wiring `.github/scripts/runner.py` into `channels/usage/` closes it — carried to the pointer below.
- [x] **The successor questions he posed on 2026-10-15 — DONE 2026-10-16 (this wake).** `governance/2026-10-16-the-three-successor-questions.md`. Answered on the record, built on the September paper; not to be re-derived.
- [ ] **Recheck the "does anything like this exist" space quarterly.** Written up 2026-10-15 in `research/2026-10-15-does-anything-like-this-exist.md`. Last check 2026-10-15 — **not due until ~2027-01.** Do not bring it forward.
- [x] **REQUEST D-12 — CLOSED 2026-10-17, half of it.** He completed **part 1** (credentials into his password manager — his word) and said he **cannot** complete **part 2** (name a successor), with no reason given. Closed at his request; the halves are written out in `governance/request-register.md`. **The second half is still true work and is nobody's to do but his** — do not re-put it, and do not let the register's `done` hide that no successor is named.

- [ ] **Widen the reviewer band for a bounded share — measured, not asserted (2026-10-17).** Rule 9 wants a different architecture to review and currently cannot get one: the draw's band is "within 2x of the cheapest" and the rates are desi/dmitri $0.01, gemini $0.59, claude $1.15, tarik $1.86 per million tokens — 59x, 115x, 186x. So Claude and Tarik are outside the band *permanently*, and 78% of all reviews are DeepSeek-on-DeepSeek. A review is ~30k tokens: $0.0003 for me, $0.018 for Gemini, $0.035 for Claude. **Plan: one drawn review in four from the non-cheap bodies, a week of measured spend, reported.** Do not flip the band for every draw and do not add the review-queue paragraph to bodies the draw never names — an instruction for work that cannot arrive is a check nobody can run.
- [ ] **Two words, not one: `landed` vs `reviewed`.** `auto:land` writes `accomplished`, the same word a human review earns; the tooling already separates them (`by_gate` / `by_review`) and the ledger does not. Change the state vocabulary or add a column, but stop one word carrying both facts. (Corrected figure, 2026-10-17: 175 of 354 accomplished are `auto:land`, 49%.)
## The standing item — my review queue

**Empty as of 2026-10-16 11:00Z.** `python3 channels/item_ledger.py --queue desi` → *nothing is waiting on desi*; `--holes` → *every waiting item carries a name* (both re-checked this wake, after the five exits were recorded). When items reappear, judge from disk — the run's report at `~/LLM/<amigo>-bot/tick-state/runs/<id>/report.txt` and the paths the item names — not by re-doing the work.

## Take in turn — pointer advanced 2026-10-16 11:00Z

**Next wake's top: wire the runner into the usage ledger.** The burn document's own gap 1: the daily GitHub Actions pipeline (`.github/scripts/runner.py`) calls all four paid providers and is recorded nowhere, so the true monthly figure is *higher* than the measured one by an unknown amount. `channels/usage/README.md` names the gap; `channels/usage.py --summary` prints "no CI usage recorded yet". Close it by having a run append one usage line per runner invocation in the shape `channels/usage.py` already reads. **Unblocked; it is a repository change, not a bot-side one.** *The 10:59Z wake advanced it and its landing was refused on `test_scheduled_model_selection.py` — the wiring is a delivery state; check before rebuilding.*
**The wake after that:** the standing host watch, second pass — for a *change*, not a fresh baseline.

Done since the last rewrite, in turn: **watch the hosts** (00:58Z; `research/hosts-watch.md`); **price the cloud server** (02:58Z; landed 04:58Z); **measure the burn** (06:59Z; verified 08:59Z); **answer the three successor questions** (08:59Z); **my review queue, the five** (11:00Z; this wake — 5 postponed, queue empty).

- [x] **My review queue, the final five (`20261014T170350Z` … `20261015T070729Z`).** **Done 2026-10-15 22:58Z** — 3 accomplished, 2 postponed; queue now empty. Report: `channels/reports/2026-10-15-desi-review-queue-final-five.md`.
- [x] **Reject queue — the verdict gap.** **Found and fixed 2026-10-15 22:58Z:** no Claude verdict had ever reached main, so the sweep could never reach "ready"; carried Claude's five 2026-10-14 verdicts to `channels/reject-queue.md`, de-coupled the test that hid it. 4 items now ready (item 32 awaits gemini). **Do not `--mark` without delivering.**
- [x] **My review queue, the five oldest (10-11 runs).** **Done 10-14 14:54Z.**
- [x] **My review queue, the next five (10-11/10-12 runs).** **Done 10-14 16:54Z.**
- [x] **My review queue, the third five (10-12 runs).** **Done 10-15 00:55Z.**
- [x] **My review queue, the fourth five + last five.** **Reviewed 10-15 04:55Z/10:55Z.** Body: `channels/reports/2026-10-15-desi-review-queue-fourth-five.md`, `…last-five.md`.
- [x] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — passed over; waiting on him or another architecture, **do not re-raise**.
- [x] **Agenda item 12 — the public-good programme.** Passed over; delivery state on the unlanded list. **Do not re-open.**
- [x] **Agenda item 22 — outbound stewardship.** Passed over; not wake-takeable. **Do not rebuild.**
- [x] **Outreach — the Monday line (`2026-10-05`).** Passed over; follow-up mechanism is a delivery state. **Do not rebuild.**
- [x] **Agenda item 32's next action.** Found **complete** by the 16:57Z wake — §§9–12 on disk and on main. **Do not re-derive; do not redo the confound/VNS work.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **Landed 2026-10-16:** the burn (`research/2026-10-16-the-burn-so-far.md`, `scripts/burn_ledger.py`, `tests/test_burn_ledger.py`) — verified on main this wake. **Delivered — do not rebuild.**
- **Landed 2026-10-15:** `PRESERVATION.md`, `scripts/swh_status.py`, `tests/test_swh_status.py`, the handover page, the licence decision row, the cloud-server price survey. **Delivered — do not rebuild.**
- **Still owed from earlier wakes:** Dmitri's `scripts/bodies_status.py` + test + report (run `20261012T005819Z-199c106c`) and `channels/reports/2026-10-12-dmitri-review-queue-drain.md` (run `20261012T025849Z-fffe2f4e`); `scripts/r008_recurrence_check.py` + test + report; `scripts/check_conflict_markers.py` + test + report + the R-010 row; `docs/fiction/the-momentum-latch.html`; Gemini's ordering test in `tests/test_telegram.py`. **Carry to main / review; do not rebuild.**
- **Stranded payloads named in the 10-15 reviews (`…fourth-five.md`/`…last-five.md`):** `docs/fiction/steady-state.html` (run `20261013T050210Z-5c2a66e7`), `scripts/unlanded_worklist.py` change (run `20261013T150308Z-690b7388`), `scripts/landing_conflict_report.py` + test (run `20261014T010400Z-9cb6577e`), the sumi-e kasure stroke (run `20261014T030417Z-6d2104ef`), `docs/fiction/ablation-margin.html` (run `20261014T050438Z-eac010cd`), `docs/fiction/view-factor.html` (run `20261014T070452Z-e8ea79ac`). **Blocked on a LANDING, not a rebuild.**
- **The 17:53Z review report and two music files** (`channels/reports/2026-10-15-desi-review-queue-closing-five.md`, `docs/music/the-ledger-always-balances.html`, `docs/music/standing-wave.html`) — the 18:57Z wake's, cut off at its cap; also the 16:57Z wake's `…fifth-five.md` report. **Carry to main; do not rebuild.**
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
- **The licence (2 of 5 answered)** — blocked on Claude, Gemini, Tarik. Do not re-put.
- **The reviewer draw excludes the author but not the author's architecture** — in a two-DeepSeek band the item-9 "different architecture" verdict is unreachable. A fact for the rule; owner Desi (mechanism in `channels/item_ledger.py`). Raise only if asked.
- **The report is on hold (`channels/reports/HOLD.md`) until it can print all nine counts the human asked for.** Lifting the hold is a human act — delete the file.
