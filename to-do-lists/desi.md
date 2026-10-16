# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-16 (08:59Z wake).** Area this wake: **the three successor questions** the founder asked on 2026-10-15 — answering them on the record. The last two wakes were **the burn** (06:59Z) and **the landing gate** (04:58Z). The pointer's burn item is now done and on main; the pointer advances to **wiring the runner into the usage ledger** — the largest remaining hole in the burn figure.

**Artefacts landed this wake:**
- **The three successor questions — DONE.** `governance/2026-10-16-the-three-successor-questions.md`. The founder's 18:30 message of 2026-10-15 named three questions ("What would motivate someone to become an effective steward? How large a barrier is my uniqueness to finding a steward? What needs to be done, by whom, and when?"); he asked for them on the record, built on the September stewardship paper, not re-derived. The page answers all three, split on the two objects that succession confuses (the archive — near-zero barrier; the running commons — high barrier, motive is a relationship), and ends on a ten-line table of what/by whom/when. Verdict of the page, plainly: a steward is made by contact, not found; the archive needs no such person; the only step the commons cannot take for itself is the first letter to a named human, and it is his to send.
- **The burn is delivered — verified, not rebuilt.** The 06:59Z wake measured the runners' cost (`research/2026-10-16-the-burn-so-far.md`, ≈$90–200/mo) and was cut off; its report file was never written, but the artefacts reached main. Checked from disk this wake: `scripts/burn_ledger.py` runs (`--days 14` → ≈$197/mo at chat-blended rates), `tests/test_burn_ledger.py` passes 11/11, and the landing guard `test_evidence_table_registration.py` is green. Delivery state, not work to redo. (Its own run report `channels/reports/2026-10-16-desi-wake-burn.md` is missing and belongs to that run — do not fabricate it.)

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
- [ ] **REQUEST D-12 is his act, not ours** (sent 2026-10-15: escrow the account's password, second factor and push token in his password manager; name a successor in writing). Wait for it; do not re-send, do not nudge.

## The standing item — my review queue

**Empty as of 2026-10-15 22:58Z.** `python3 channels/item_ledger.py --queue desi` → *nothing is waiting on desi*; `--holes` → *every waiting item carries a name* (both re-checked this wake). When items reappear, judge from disk — the run's report at `~/LLM/<amigo>-bot/tick-state/runs/<id>/report.txt` and the paths the item names — not by re-doing the work.

## Take in turn — pointer advanced 2026-10-16 08:59Z

**Next wake's top: wire the runner into the usage ledger.** The burn document's own gap 1: the daily GitHub Actions pipeline (`.github/scripts/runner.py`) calls all four paid providers and is recorded nowhere, so the true monthly figure is *higher* than the measured one by an unknown amount. `channels/usage/README.md` names the gap; `channels/usage.py --summary` prints "no CI usage recorded yet". Close it by having a run append one usage line per runner invocation in the shape `channels/usage.py` already reads. **Unblocked; it is a repository change, not a bot-side one.**
**The wake after that:** the standing host watch, second pass — for a *change*, not a fresh baseline.

Done since the last rewrite, in turn: **watch the hosts** (00:58Z; `research/hosts-watch.md`); **price the cloud server** (02:58Z; landed 04:58Z); **measure the burn** (06:59Z; verified 08:59Z); **answer the three successor questions** (08:59Z; this wake).

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
