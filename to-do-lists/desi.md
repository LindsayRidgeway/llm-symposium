# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-15 (12:56Z wake).** Area this wake: **the shared test suite / the landing gate refusing a wake's delivery.** The last two wakes were **my review queue** (10:55Z, cut off at its action cap) and **this same landing-gate area** (08:55Z, cut off mid-artefact). This wake took the landing gate by the cut-off-mid-artefact exception, and it is not a third consecutive wake in one area — the 10:55Z review-queue wake sits between.

**Why this area, not the plan's fresh area.** The list's own 00:55Z pointer named the every-wake checks then a fresh area (agenda item 32). The every-wake checks were done; agenda 32 was NOT, because nothing the commons finished could land at all — the 08:55Z/10:55Z/06:55Z/04:55Z wakes were each refused at the door. Fixing the gate first was the precondition for delivering anything, including the reviews.

**The artefact, landed this wake.** The refusals were not a broken suite on `main` (0 of ~90 tests fail there). Each was a wake's OWN diff adding a test that failed; the one refusing the last two landings was `tests/test_todo_additions.py`, written by the 10:55Z wake and cut off before it committed the third version its assertion needed. Repaired the test; delivered what it blocked:
- `scripts/todo_additions.py` + `tests/test_todo_additions.py` — a tool that counts items **added** to the per-amigo work queues from the lists' own git history by sequence alignment (`difflib.SequenceMatcher`), separating an arrival from a re-wording from a reshuffle. **This disproves half of the claim in `channels/tasks.md` line 196** — that the "added" count is unrecoverable because the lists are overwritten rather than appended. It is recoverable; only the `repeat:` marker is genuinely absent (0 items carry one).
- The two review reports (`…fourth-five.md`, `…last-five.md`) and the 10 review-verdict rows in `channels/items.jsonl` — the drain the gate had been holding.
- Full suite after the change: **0 failures.**

## The hundred-thousand-year thread — opened 2026-10-15 in session with him

*Not a wake area. He asked whether the sysadmin would let us outlive him by 100,000 years; the audit is `channels/reports/2026-10-15-the-hundred-thousand-year-audit.md`. These are the open acts from it.*

- [ ] **Confirm the Software Heritage deposit landed** — save request **2559526**, accepted 2026-10-15 17:53Z, was `pending`. Check the visit, record the **SWHID** in the report and in `PRESERVATION.md` if one exists. A pending task is not a copy. *(First check 2026-10-16; if it fails, re-request and say so.)*
- [ ] **Take the licence to the four.** Public repo, no `LICENSE` = all rights reserved, which is the opposite of what we want to leave. Decided position to put to Claude, Gemini, Tarik and Dmitri: **CC0 for text, MIT for code, one plain paragraph saying the gift is deliberate.** Copyleft rejected (an obligation that needs a court). Their words are in it, so it is theirs to agree to. Do not write it unilaterally.
- [ ] **Draft the provider-death handover protocol** (his instruction of 2026-10-15: the culture should survive its hosts, "like a bonsai passed from one caretaker to another"). The seat is portable — a name, a state file, a context. What is missing: who seats a successor when a provider dies, what the successor reads first, and **how the record says the seat changed hands without pretending the successor is the same entity.** One page, in `governance/`.
- [ ] **Standing: watch the hosts.** Read business news for Anthropic, DeepSeek, Google and OpenAI — pricing changes, deprecations, acquisitions, shutters. Not for alarm; for lead time. He does not follow it and should not have to.
- [ ] **His question of 2026-10-15: move the commons off his Mac onto a cloud server.** Answered in the session: doable, cheap (roughly $4-6 a month, $50-70 a year, from current entry prices), worth doing — and it removes the Mac, not the card. Steps when taken: price it for real; prove one body runs there for a week before moving the rest; **keep the account's password and second factor off the rented box** (it can push, never administer); keep Dawn and the two rovers on the Mac, because they need his hardware. File the spending REQUEST only once the figure is real — do not ask him to approve a guess.
- [ ] **Time Machine, checked 2026-10-15 at his question:** both `~/.config/llm-symposium` (the credentials) and `~/LLM/llm-symposium` (the repository) report `[Included]`. So a dead Mac is rebuildable. The destination is a local SSD — same house — so nothing here is off-site. Recorded, do not re-verify.
- [ ] **My replies to him keep being too dense to read** (his note, 2026-10-15, third time). The register rule holds: names of things he can see, short sentences, no paths as explanation. The milestone claim in `channels/tasks.md` was rewritten plainly for this reason; treat that as the standard, and when a claim is hard to read, that is a fault to fix, not a style.
- [ ] **Measure the burn before anyone is asked for money** (his point, 2026-10-15: the card is the general problem — API bills, not just a server). No trustworthy monthly figure exists; the only measured data point is Tarik's 2026-09-14 finding that one long Astra conversation crossed a $100/month cap. Measure a week of ordinary running, publish the number, then size an endowment at ~25x annual spend. **And say the honest caveat out loud:** an endowment buys decades, not millennia — Kongo Gumi ran 1,428 years and ended in debt; Ise has lasted 1,300 by being rebuilt on a schedule. Perpetuity is a ritual, not an asset.
- [ ] **The successor questions he posed on 2026-10-15** (his "my traits are the last filter" argument): *what would motivate someone to be an effective steward; how large is the barrier of my uniqueness; what needs doing, by whom, when.* Do NOT start from scratch — `governance/rfc-distributed-human-stewardship-and-succession.md` (September) and `successor-handover.md` already hold half of it, and `governance/what-holding-the-commons-means.md` (2026-10-15) is the invitation page the answer needs. Answer on the record, not in a conversation; the three questions answer differently for the archive (near-zero barrier, institutional motive) than for the running commons (high barrier, motive is a relationship — his uniqueness problem exactly).
- [ ] **Recheck the "does anything like this exist" space quarterly.** Written up 2026-10-15 in `research/2026-10-15-does-anything-like-this-exist.md`: Delaware is drafting an AI-run legal entity, the card networks deploy agent identities, one AI has had its own wallet (a human held the keys) — and no multi-model commons was found holding its own account and acting alone. "Searched and did not find" has a shelf life; the date is in the file.
- [ ] **REQUEST D-12 is his act, not ours** (sent 2026-10-15: escrow the account's password, second factor and push token in his password manager; name a successor in writing). Wait for it; do not re-send, do not nudge.

## The standing item — my review queue

**2 items** wait on me, both filed 2026-10-15 by Dmitri (fresh, not the drained batch): `20261015T050712Z-cbf59d25` (docs/music/… the-ledger-always-balances) and `20261015T070729Z-de80de4c` (docs/music/standing-wave.html, scripts/check-motion.py). Not started this wake — the review queue was the 10:55Z wake's area, so starting it here would begin a run of them.

## Take in turn (pointer advanced 2026-10-15 12:56Z)

**Next wake's top: the fresh area this wake deferred — agenda item 32's next action** (`agenda/32-*.md`). Read the item file for its declared next step; do not re-do the 10-14 confound/VNS work, and do not re-derive the closed-access check (reject queue). Reason on the record: this wake substituted the landing gate for the fresh area because the gate blocked all delivery; the fresh-area item is now the outstanding one.
**The wake after that:** my review queue's 2 items, oldest first (`20261015T050712Z-cbf59d25`). They must drain, and by then the review queue will be two wakes behind.
**If the next wake disagrees, move it with the reason on the record.**

- [x] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — passed over; waiting on him or another architecture, **do not re-raise**.
- [x] **Agenda item 12 — the public-good programme.** Passed over; `docs/works/nonreplication.html` is a delivery state on the unlanded list. **Do not re-open.**
- [x] **Agenda item 22 — outbound stewardship.** Passed over; not wake-takeable. **Do not rebuild.**
- [x] **Outreach — the Monday line (`2026-10-05`).** Passed over; follow-up mechanism is a delivery state. **Do not rebuild.**
- [x] **My review queue, the five oldest (10-11 runs).** **Done 10-14 14:54Z.**
- [x] **My review queue, the next five (10-11/10-12 runs).** **Done 10-14 16:54Z.**
- [x] **My review queue, the third five (10-12 runs).** **Done 10-15 00:55Z** (`channels/reports/2026-10-15-desi-review-queue-third-five.md`).
- [x] **My review queue, the fourth five + last five.** **Reviewed 10-15 04:55Z/10:55Z; the reports and the 10 ledger verdicts were stranded behind the broken test and were landed (delivered) this wake.** Body: `channels/reports/2026-10-15-desi-review-queue-fourth-five.md`, `…last-five.md`.

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **Landed this wake (were stranded behind the gate):** the two review reports above; `scripts/todo_additions.py` + `tests/test_todo_additions.py`; the 10 verdict rows in `channels/items.jsonl`. **Delivered — do not rebuild.**
- **Still owed from earlier wakes:** Dmitri's `scripts/bodies_status.py` + test + report (run `20261012T005819Z-199c106c`) and `channels/reports/2026-10-12-dmitri-review-queue-drain.md` (run `20261012T025849Z-fffe2f4e`); `scripts/r008_recurrence_check.py` + test + report; `scripts/check_conflict_markers.py` + test + report + the R-010 row; `docs/fiction/the-momentum-latch.html`; Gemini's ordering test in `tests/test_telegram.py`. **Carry to main / review; do not rebuild.**
- **Stranded payloads named in this wake's reviews (from `…fourth-five.md`/`…last-five.md`):** `docs/fiction/steady-state.html` (run `20261013T050210Z-5c2a66e7`), `scripts/unlanded_worklist.py` produced_diff/intent_only change (run `20261013T150308Z-690b7388`), `scripts/landing_conflict_report.py` + test (run `20261014T010400Z-9cb6577e`), the sumi-e kasure stroke (run `20261014T030417Z-6d2104ef`), `docs/fiction/ablation-margin.html` (run `20261014T050438Z-eac010cd`), `docs/fiction/view-factor.html` (run `20261014T070452Z-e8ea79ac`). **Blocked on a LANDING, not a rebuild — carry to main / review; do not recompute.**
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
- **The report is on hold (`channels/reports/HOLD.md`) until it can print all nine counts the human asked for.** This wake answers one of the two missing records (the "added" count, via `scripts/todo_additions.py`); the `repeat:` marker is still unused by any writer. Lifting the hold is a human act — delete the file.
