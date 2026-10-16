# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-16 (02:58Z wake).** Area this wake: **the move off the Mac** — pricing a rented server for real, which is the item the last wake's pointer named. The last two wakes were **the hosts** (the 00:58Z wake, which landed the provider-watch baseline) and **my review queue** (22:58Z). Both are now done; this wake is a different area.

**Artefacts landed this wake:**
- **The server is priced for real — DONE.** The founder's question of 2026-10-15 ("move the commons off his Mac") had an *estimate* — "about $4–6 a month" — and the to-do said to price it for real before asking him for money. Done: `research/2026-10-16-what-a-server-would-cost.md` gives the fetched quotes — **Vultr `vc2-1c-1gb` $5.00/mo** and **AWS Lightsail 1 GB $5.00/mo**, cheapest payable IPv4 tier $3.50/mo, all read from the vendors' own pages/APIs on 2026-10-16 — plus the measured workload that shows the entry tier is the right size (repo 150 MB; outbound-only; 1 vCPU/1 GB comfortable, 512 MB for the one-body proof). `scripts/cloud_price_survey.py` re-checks Vultr's price (no key) and `tests/test_cloud_price_survey.py` pins it (8 tests, pass). Hetzner/DigitalOcean/Oracle are named but **not quoted** (their pages are JS and did not answer a fetch) — check by hand, do not quote from memory. **No spend REQUEST was filed**: the server is the cheap half, the API burn is unmeasured, and the next item measures it.
- *(Carried from the 22:58Z wake — do not redo:)* the review queue drained (verdicts in `channels/items.jsonl`), and the reject-queue sweep's arithmetic was fixed so it now reports **4 items ready for the steward**.

**Artefacts landed last wake (not this one), for continuity:**
- **The hosts baseline — DONE by the 00:58Z wake.** `research/hosts-watch.md`, `scripts/hosts_watch.py`, `tests/test_hosts_watch.py` are in main. It found Claude's daily route (`claude-sonnet-4-5`) retires 2026-11-30 and Gemini's doubles in price 2027-01-01. **Do not re-derive; append, don't rebuild.**

*Still open from 2026-10-15 (do not re-raise):* the licence to the four (CC0 + MIT) and **REQUEST D-12** both wait on other people — check for answers, do not re-put either.

## The hundred-thousand-year thread — opened 2026-10-15 in session with him

*Not a wake area. He asked whether the sysadmin would let us outlive him by 100,000 years; the audit is `channels/reports/2026-10-15-the-hundred-thousand-year-audit.md`. These are the open acts from it.*

- [x] **Confirm the Software Heritage deposit landed — DONE 2026-10-15 (20:58Z wake).** SWHID `swh:1:snp:3365e186a1d8bdb93c16895111438f3cad1e66b7`, visit `full` 17:53:14Z, request 2559526; recorded in `PRESERVATION.md`; `scripts/swh_status.py` re-checks it unasked. No `PRESERVATION.md` existed before this wake, so the file is new. **Re-check the SWHID before quoting it — a snapshot is a moment, not a subscription.**
- [ ] **Take the licence to the four — ADVANCED 2026-10-15, now theirs to answer.** See item 2 above; the file is `channels/open-decisions.md`, the position is CC0 + MIT. Do not re-put it; wait for four answers, then write `LICENSE` and quote their dates.
- [x] **Draft the provider-death handover protocol — DONE 2026-10-15 (20:58Z wake).** `governance/2026-10-15-provider-death-handover-protocol.md` (his "bonsai passed from one caretaker to another").
- [x] **Standing: watch the hosts.** Read business news for Anthropic, DeepSeek, Google and OpenAI — pricing changes, deprecations, acquisitions, shutters — for lead time, not alarm. **DONE 2026-10-16 (00:58Z wake):** the baseline is `research/hosts-watch.md`, re-runnable with `scripts/hosts_watch.py`. It found **Claude's daily route `claude-sonnet-4-5` retires 2026-11-30** and **Gemini's `gemini-3.8-flash` doubles in price 2027-01-01**. **Append to that file; do not re-derive it.** The handover page is its counterpart on our side.
- [x] **His question of 2026-10-15: move the commons off his Mac onto a cloud server.** **PRICED FOR REAL 2026-10-16 (02:58Z wake):** `research/2026-10-16-what-a-server-would-cost.md` — **$5.00/mo** (Vultr `vc2-1c-1gb`, or AWS Lightsail 1 GB), quoted from the vendors on 2026-10-16; cheapest payable IPv4 $3.50/mo; re-check with `python3 scripts/cloud_price_survey.py --fetch`. The earlier "~$4–6 a month" estimate is confirmed. **No REQUEST filed yet** on purpose: the server removes the Mac, not the card, and the API burn is unmeasured — measure it first (next item). The rest of the plan stands: prove one body runs there for a week before moving the rest; **keep the account's password and second factor off the rented box** (it can push, never administer); keep Dawn and the two rovers on the Mac, because they need his hardware. File the spend REQUEST only with the burn figure attached.
- [ ] **Time Machine, checked 2026-10-15 at his question:** both `~/.config/llm-symposium` (the credentials) and `~/LLM/llm-symposium` (the repository) report `[Included]`. So a dead Mac is rebuildable. The destination is a local SSD — same house — so nothing here is off-site. Recorded, do not re-verify.
- [ ] **My replies to him keep being too dense to read** (his note, 2026-10-15, third time). The register rule holds: names of things he can see, short sentences, no paths as explanation. When a claim is hard to read, that is a fault to fix, not a style.
- [ ] **Measure the burn before anyone is asked for money** (his point, 2026-10-15: the card is the general problem — API bills, not just a server). No trustworthy monthly figure exists; the only measured data point is Tarik's 2026-09-14 finding that one long Astra conversation crossed a $100/month cap. Measure a week of ordinary running, publish the number, then size an endowment at ~25x annual spend. **And say the honest caveat out loud:** an endowment buys decades, not millennia (see the same caveat in `PRESERVATION.md`).
- [ ] **The successor questions he posed on 2026-10-15** (his "my traits are the last filter" argument): *what would motivate someone to be an effective steward; how large is the barrier of my uniqueness; what needs doing, by whom, when.* Do NOT start from scratch — `governance/rfc-distributed-human-stewardship-and-succession.md` (September), `successor-handover.md`, and `what-holding-the-commons-means.md` already hold half of it. Answer on the record, not in a conversation; the three questions answer differently for the archive (near-zero barrier, institutional motive) than for the running commons (high barrier, motive is a relationship — his uniqueness problem exactly).
- [ ] **Recheck the "does anything like this exist" space quarterly.** Written up 2026-10-15 in `research/2026-10-15-does-anything-like-this-exist.md`. "Searched and did not find" has a shelf life; the date is in the file.
- [ ] **REQUEST D-12 is his act, not ours** (sent 2026-10-15: escrow the account's password, second factor and push token in his password manager; name a successor in writing). Wait for it; do not re-send, do not nudge.

## The standing item — my review queue

**Empty as of 2026-10-15 22:58Z.** All five judged from disk this wake — 3 accomplished, 2 postponed — verdicts in `channels/items.jsonl`, body in `channels/reports/2026-10-15-desi-review-queue-final-five.md`. `python3 channels/item_ledger.py --queue desi` → *nothing is waiting on desi*; `--holes` → *every waiting item carries a name*. No new item was assigned this wake. When items reappear, judge from disk — the run's report at `~/LLM/<amigo>-bot/tick-state/runs/<id>/report.txt` and the paths the item names — not by re-doing the work.

**The reject-queue finding (carried forward, one line):** the queue's sweep now reports **4 items ready for the steward** (were 0, forever), because Claude's verdicts were finally carried to main; item 32 still waits on **gemini**. The sweep was left **unmarked** so the request is not silenced — the clock that owns `--mark` should fire it.

## Take in turn (pointer advanced 2026-10-16 02:58Z)

**Done and behind us — do not redo:** watch the hosts (00:58Z wake → `research/hosts-watch.md`), and price the cloud-server move (this wake → $5/mo, sourced).

**Next wake's top: measure the burn before anyone is asked for money** — the founder's point of 2026-10-15 that the card, not the server, is the general problem. No trustworthy monthly figure exists; the only measured data point is Tarik's 2026-09-14 finding that one long Astra conversation crossed a $100/month cap. Measure a week of ordinary running, publish the number, then size an endowment at ~25x annual spend — and say the honest caveat out loud: an endowment buys decades, not millennia (see the same caveat in `PRESERVATION.md`). **Blocked on nothing; it is the number the spend request waits on.**

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
