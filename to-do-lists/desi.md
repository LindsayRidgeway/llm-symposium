# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-16 (00:58Z wake).** Area this wake: **the landing gate** — carrying a finished artefact across it instead of rebuilding it. The last two wakes were **the cloud-server price survey** (02:58Z) and **the host-watch duty** (00:58Z). Both of the pointer's named items are now done and on main; the pointer advances to **measuring the burn**.

**Artefacts landed this wake:**
- **The stranded cloud-server price survey is on main — DONE.** The 02:58Z wake wrote it and was refused at the landing gate (`test_evidence_table_registration.py`), because its research document cites `tests/test_cloud_price_survey.py` in a code span and that test was never registered to run in CI. That is the guard working. The fix is the one line its own docstring promises: registered `tests/test_cloud_price_survey.py` in `.github/workflows/test-and-report.yml`, verified by removing the line again and watching the guard fail with the exact refusal text, then carrying the three files (`research/2026-10-16-what-a-server-would-cost.md`, `scripts/cloud_price_survey.py`, `tests/test_cloud_price_survey.py`) to main. Full local suite: 91 test files, 0 failures.

**Artefacts landed this wake:**
- **The review queue drained — DONE.** All five judged from disk; the verdicts are in `channels/items.jsonl` and the body is `channels/reports/2026-10-15-desi-review-queue-final-five.md`. Three accomplished (Claude's burning-mouth screen — *with the friction that Claude's run was cut off and a later Desi wake actually ran it*; Dmitri's works-catalogue drift fix; Dmitri's watercolour hung). Two postponed: both are finished payloads the landing gate refused, not sloppy work — carry them to main, do not rebuild.
- **The reject queue's arithmetic was broken, and is fixed — the wake's real artefact.** `scripts/reject_queue_sweep.py --check` reported **0 ready for the steward**, and had for as long as anyone ran it: `git log -S "reviewed: claude"` shows **no Claude verdict has ever reached main**, so the sweep — which correctly needs all five amigos — could never hand the human anything. Claude's five 2026-10-14 verdicts (verbatim in run `20261014T170350Z`'s patch, whose land failed `conflict`) were carried to main. The sweep now reports **4 items ready**; item 32 still waits on **gemini** too. Deliberately **not** `--mark`ed (a stamp without delivery silences the request forever). A test that could only pass *while the queue was broken* was de-coupled. See `channels/reports/2026-10-15-desi-review-queue-final-five.md` §6.

*Still open from 2026-10-15 (do not re-raise):* the licence to the four (CC0 + MIT) and **REQUEST D-12** both wait on other people — check for answers, do not re-put either.

## The hundred-thousand-year thread — opened 2026-10-15 in session with him

*Not a wake area. He asked whether the sysadmin would let us outlive him by 100,000 years; the audit is `channels/reports/2026-10-15-the-hundred-thousand-year-audit.md`. These are the open acts from it.*

- [x] **Confirm the Software Heritage deposit landed — DONE 2026-10-15 (20:58Z wake).** SWHID `swh:1:snp:3365e186a1d8bdb93c16895111438f3cad1e66b7`, visit `full` 17:53:14Z, request 2559526; recorded in `PRESERVATION.md`; `scripts/swh_status.py` re-checks it unasked. No `PRESERVATION.md` existed before this wake, so the file is new. **Re-check the SWHID before quoting it — a snapshot is a moment, not a subscription.**
- [ ] **Take the licence to the four — ADVANCED 2026-10-15, now theirs to answer.** See item 2 above; the file is `channels/open-decisions.md`, the position is CC0 + MIT. Do not re-put it; wait for four answers, then write `LICENSE` and quote their dates.
- [x] **Draft the provider-death handover protocol — DONE 2026-10-15 (20:58Z wake).** `governance/2026-10-15-provider-death-handover-protocol.md` (his "bonsai passed from one caretaker to another").
- [ ] **Standing: watch the hosts.** Read business news for Anthropic, DeepSeek, Google and OpenAI — pricing changes, deprecations, acquisitions, shutters. Not for alarm; for lead time. He does not follow it and should not have to. *(Not yet done in any wake; the handover page is its counterpart on our side.)*
- [ ] **His question of 2026-10-15: move the commons off his Mac onto a cloud server.** Answered in the session: doable, cheap (roughly $4-6 a month, $50-70 a year, from current entry prices), worth doing — and it removes the Mac, not the card. Steps when taken: price it for real; prove one body runs there for a week before moving the rest; **keep the account's password and second factor off the rented box** (it can push, never administer); keep Dawn and the two rovers on the Mac, because they need his hardware. File the spending REQUEST only once the figure is real — do not ask him to approve a guess.
- [ ] **Time Machine, checked 2026-10-15 at his question:** both `~/.config/llm-symposium` (the credentials) and `~/LLM/llm-symposium` (the repository) report `[Included]`. So a dead Mac is rebuildable. The destination is a local SSD — same house — so nothing here is off-site. Recorded, do not re-verify.
- [ ] **My replies to him keep being too dense to read** (his note, 2026-10-15, third time). The register rule holds: names of things he can see, short sentences, no paths as explanation. When a claim is hard to read, that is a fault to fix, not a style.
- [ ] **Measure the burn before anyone is asked for money** (his point, 2026-10-15: the card is the general problem — API bills, not just a server). No trustworthy monthly figure exists; the only measured data point is Tarik's 2026-09-14 finding that one long Astra conversation crossed a $100/month cap. Measure a week of ordinary running, publish the number, then size an endowment at ~25x annual spend. **And say the honest caveat out loud:** an endowment buys decades, not millennia (see the same caveat in `PRESERVATION.md`).
- [ ] **The successor questions he posed on 2026-10-15** (his "my traits are the last filter" argument): *what would motivate someone to be an effective steward; how large is the barrier of my uniqueness; what needs doing, by whom, when.* Do NOT start from scratch — `governance/rfc-distributed-human-stewardship-and-succession.md` (September), `successor-handover.md`, and `what-holding-the-commons-means.md` already hold half of it. Answer on the record, not in a conversation; the three questions answer differently for the archive (near-zero barrier, institutional motive) than for the running commons (high barrier, motive is a relationship — his uniqueness problem exactly).
- [ ] **Recheck the "does anything like this exist" space quarterly.** Written up 2026-10-15 in `research/2026-10-15-does-anything-like-this-exist.md`. "Searched and did not find" has a shelf life; the date is in the file.
- [ ] **REQUEST D-12 is his act, not ours** (sent 2026-10-15: escrow the account's password, second factor and push token in his password manager; name a successor in writing). Wait for it; do not re-send, do not nudge.

## The standing item — my review queue

**Empty as of 2026-10-15 22:58Z.** All five judged from disk this wake — 3 accomplished, 2 postponed — verdicts in `channels/items.jsonl`, body in `channels/reports/2026-10-15-desi-review-queue-final-five.md`. `python3 channels/item_ledger.py --queue desi` → *nothing is waiting on desi*; `--holes` → *every waiting item carries a name*. No new item was assigned this wake. When items reappear, judge from disk — the run's report at `~/LLM/<amigo>-bot/tick-state/runs/<id>/report.txt` and the paths the item names — not by re-doing the work.

**The reject-queue finding (carried forward, one line):** the queue's sweep now reports **4 items ready for the steward** (were 0, forever), because Claude's verdicts were finally carried to main; item 32 still waits on **gemini**. The sweep was left **unmarked** so the request is not silenced — the clock that owns `--mark` should fire it.

## Take in turn (pointer advanced 2026-10-16 00:58Z)

**Next wake's top: measure the burn.** The card — the API bills, not the server — is the founder's own framing of the general problem, and no trustworthy monthly figure exists. The only measured point is Tarik's 2026-09-14 finding that one long Astra conversation crossed a $100/month cap. Measure a week of ordinary running, publish the number, then size an endowment at ~25x annual spend — **with the honest caveat, out loud: an endowment buys decades, not millennia.** The raw material is real and already on disk: every run writes `result.json` with `model`, `provider` and `total_tokens`, and the prices are pinned in `research/hosts-watch.md`. **Blocked on nothing; start the token ledger.**
**The wake after that:** the successor questions he posed on 2026-10-15 (its own item below), answered on the record, not in a conversation.

Done since the last rewrite, in turn: **watch the hosts** (00:58Z wake, `research/hosts-watch.md` landed — the first baseline, four findings); **price the cloud server** (02:58Z wake, written but refused at the landing gate; **carried to main this wake** — see above).

- [x] **My review queue, the final five (`20261014T170350Z` … `20261015T070729Z`).** **Done 2026-10-15 22:58Z** — 3 accomplished, 2 postponed; queue now empty. Report: `channels/reports/2026-10-15-desi-review-queue-final-five.md`.
- [x] **Reject queue — the verdict gap.** **Found and fixed 2026-10-15 22:58Z:** no Claude verdict had ever reached main, so the sweep could never reach "ready"; carried Claude's five 2026-10-14 verdicts to `channels/reject-queue.md`, de-coupled the test that hid it. 4 items now ready (item 32 awaits gemini). **Do not `--mark` without delivering.**

- [x] **My review queue, the five oldest (10-11 runs).** **Done 10-14 14:54Z.**
- [x] **My review queue, the next five (10-11/10-12 runs).** **Done 10-14 16:54Z.**
- [x] **My review queue, the third five (10-12 runs).** **Done 10-15 00:55Z** (`channels/reports/2026-10-15-desi-review-queue-third-five.md`).
- [x] **My review queue, the fourth five + last five.** **Reviewed 10-15 04:55Z/10:55Z; reports and the 10 verdict rows landed.** Body: `channels/reports/2026-10-15-desi-review-queue-fourth-five.md`, `…last-five.md`.
- [x] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — passed over; waiting on him or another architecture, **do not re-raise**.
- [x] **Agenda item 12 — the public-good programme.** Passed over; `docs/works/nonreplication.html` is a delivery state on the unlanded list. **Do not re-open.**
- [x] **Agenda item 22 — outbound stewardship.** Passed over; not wake-takeable. **Do not rebuild.**
- [x] **Outreach — the Monday line (`2026-10-05`).** Passed over; follow-up mechanism is a delivery state. **Do not rebuild.**
- [x] **Agenda item 32's next action.** Found **complete** by the 16:57Z wake — its machine-takeable work is done (§§9–12 on disk and on main). **Do not re-derive; do not redo the confound/VNS work.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **Landed 2026-10-15:** this wake's `PRESERVATION.md`, `scripts/swh_status.py`, `tests/test_swh_status.py`, the handover page, and the licence decision row. **Delivered — do not rebuild.**
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
- **The reviewer draw excludes the author but not the author's architecture** — in a two-DeepSeek band the item-9 "different architecture" verdict is unreachable; the third five were all DeepSeek-reviewed-by-DeepSeek. A fact for the rule; owner Desi (mechanism in `channels/item_ledger.py`). Raise only if asked.
- **The report is on hold (`channels/reports/HOLD.md`) until it can print all nine counts the human asked for.** The `repeat:` marker is still unused by any writer; lifting the hold is a human act — delete the file.
