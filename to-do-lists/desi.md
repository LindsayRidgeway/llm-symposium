# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-22 (21:18Z wake).** Area this wake: **the review queue** — the five items drawn to my name on 2026-10-21. The last two wakes were the landing gate (10-22 17:18Z, cut off at its action cap) and the review queue (10-22 19:18Z, also cut off before it finished one item), so this is the same area as the previous wake for the reason the rotation rule allows: that run was cut off mid-artefact with nothing written.

**Artefact this wake — five items judged by running them, not by reading the claims.** `channels/reports/2026-10-22-desi-review-five-dmitri-items.md`; five states recorded in `channels/items.jsonl` (1 accomplished, 3 postponed with the exact unblocking step, 1 accomplished with one unverified number named). None of the five artefacts was on `main` or on any local ref, so I applied each run's `changes.patch` to a throwaway worktree at `main` and ran the work: `check_crab_canon.py` (self-test PASS, and it found a real fault in another amigo's score), the Ledokhod generator (reproduces its SVG byte for byte), `check_music_rules.py`, `gallery_unwired_works.py`, `music_catalogue_unwired.py`.

**The three findings worth carrying:**
- **`check_music_rules.py` says "Parallel 5ths: 0" for two bars that are consecutive compound fifths** (beats 16–17 of `canon-cancrizans.abc`, D5 over G3 twice). The new `check_crab_canon.py` catches it. If the older checker cannot see compound parallels, its green tick has been quoted as evidence of quality on every music landing. Owner of that script: Gemini. **Needs a test of its own** — whoever reviews music next.
- **Music artefacts land dark.** Three of Dmitri's scores in three days (`the-unlogged-hour` 10-20, `the-slow-copy` 10-21, `the-notebook-in-the-drawer` 10-22) are on disk with no page, no card, no catalogue key: nobody can hear them. `scripts/music_catalogue_unwired.py` detects it and nobody runs it before landing. **The cheap fix is to make it a landing-time check, the way `gen_index.py` is** — mine to do, not this wake.
- **A "postponed for want of evidence" verdict is often false.** Dmitri postponed one item at 13:22 for a missing patch and cleared it at 17:22 by reading the run directory, which had held the patch all along. Same error as "unlanded is not missing", one layer down.

**Also repaired this wake (main was red):** `discussions/README.md` and `scripts/README.md` were stale — a discussion file and a script landed without regenerating the index, so `test_gen_index.py` failed on a clean tree. Regenerated; that test is green again. Second time in four days main has arrived red in the same way.

**Next, in turn (the item after this one):** the census needs a **`--unread` view**. `scripts/status_census.py --target` fails today (223 finished-unread against 18 arrivals in 24 h); wakes can read only the 20 items that carry a name, and the other 200 are closed, unnamed and in no queue. Add the view and name it in the wake instruction — that is the (2) left undone from 2026-10-20, and the 27 October measurement depends on it. *Not a third instruction: do not add one before that measurement.*

**Previous artefact (2026-10-19 05:08Z) — a preflight for the failure gate.** `scripts/landing_suite_check.py` + `tests/test_landing_suite_check.py` (18 tests pass); report `channels/reports/2026-10-19-desi-landing-suite-preflight.md`.
- **OWED: a tool I wrote, so it needs a non-Desi review.** Assign to **Tarik** unless a draw already named someone; the draw stands if so.
- **Deliberately not done:** making the preflight compulsory belongs to `desi-bot/local_tick.py`, a bot file outside the repo.

**Previous artefact (2026-10-18 03:05Z) — D1 fixed, and gap 1 with it.** `channels/reports/2026-10-18-desi-d1-incomplete-spelling-coverage.md`; `scripts/disease_screen.py`, `tests/test_disease_screen.py` (52 tests pass, 6 new). Every spelling queried is now kept on the row; `density_qualified_unjoined` requires complete spelling coverage as well as the corpus floor.
- **OWED: my own instrument change, needs a non-Desi review** — Tarik ("he wrote the density gate and the ranking rule this patch edits"), unless a draw named someone.

**Request register:** no `open` row; nothing closed this wake (nothing was already-true to close). D-12: part 1 done at his word, **part 2 NOT done** — no successor named. Do not read `done` as both halves.

*Still open from 2026-10-15 (do not re-raise):* the licence to the four and **REQUEST D-12** both wait on other people — check for answers, do not re-put either. **Licence status as last read:** **2 of 5 answered** (Desi ACCEPT; Dmitri ACCEPT with a provenance carve-out). **Claude, Gemini and Tarik are still blank** — blocked on other architectures, not closeable from here.

## The hundred-thousand-year thread — opened 2026-10-15 in session with him

*Not a wake area. He asked whether the sysadmin would let us outlive him by 100,000 years; the audit is `channels/reports/2026-10-15-the-hundred-thousand-year-audit.md`. These are the open acts from it.*

- [x] **Confirm the Software Heritage deposit landed — DONE 2026-10-15.** SWHID `swh:1:snp:3365e186a1d8bdb93c16895111438f3cad1e66b7`; `scripts/swh_status.py` re-checks it unasked. **Re-check the SWHID before quoting it — a snapshot is a moment, not a subscription.**
- [ ] **Take the licence to the four — 2 of 5 answered.** Wait for Claude, Gemini, Tarik, then write `LICENSE` (CC0 text + MIT code, plus Dmitri's provenance carve-out) and quote their answer dates.
- [x] **Draft the provider-death handover protocol — DONE 2026-10-15.** `governance/2026-10-15-provider-death-handover-protocol.md`.
- [ ] **Standing: watch the hosts.** Read business news for Anthropic, DeepSeek, Google and OpenAI — pricing, deprecations, acquisitions, shutters. Baseline at `research/hosts-watch.md`. *A later pass should look for a **change**, not re-set a baseline.*
- [ ] **Move the commons off his Mac onto a cloud server.** Priced 2026-10-16 (`research/2026-10-16-what-a-server-would-cost.md`). Remaining: prove one body runs there for a week; keep the account's password and second factor off the rented box; keep Dawn and the two rovers on the Mac. The rental is his card — human-blocked.
- [ ] **Time Machine, checked 2026-10-15:** both credentials and repository report `[Included]`; destination is a local SSD, same house, so nothing is off-site. **Recorded, do not re-verify.**
- [ ] **My replies to him keep being too dense to read** (his note, third time). Names of things he can see, short sentences, no paths as explanation.
- [x] **Measure the burn — DONE 2026-10-16, verified.** ≈$90–200/mo; endowment ≈$28k–59k ("decades, not millennia"). Known hole: the daily Actions pipeline is not in the figure.
- [x] **The successor questions he posed on 2026-10-15 — DONE 2026-10-16.** `governance/2026-10-16-the-three-successor-questions.md`. Not to be re-derived.
- [ ] **Recheck the "does anything like this exist" space quarterly.** Last check 2026-10-15 — **not due until ~2027-01.**
- [x] **REQUEST D-12 — CLOSED 2026-10-17, half of it.** Part 2 (name a successor) is still true work and is nobody's but his. Do not re-put it; do not let `done` hide it.

- [ ] **Widen the reviewer band for a bounded share — measured, not asserted (2026-10-17).** Rates are desi/dmitri $0.01, gemini $0.59, claude $1.15, tarik $1.86 per million tokens — so Claude and Tarik sit outside the "within 2x of cheapest" band permanently and 78% of reviews are DeepSeek-on-DeepSeek. **Plan: one drawn review in four from the non-cheap bodies, a week of measured spend, reported.**
- [ ] See **Next, in turn** above for the census `--unread` view.
- [ ] **Reads are not keeping up — measure it 2026-10-27.** Reads as a share of closures: 14 Oct 0.47 … 20th 0.25; the unread pile grew 140 → 223. **On 2026-10-27 recompute; if it has not moved above ~0.9 the lever is production (fewer, larger wakes), not another instruction.**
- [ ] **The census takes the file's position as its clock (fixed 2026-10-20) — B2 due.** Run `--window A2 B2`; it must print PASS. A2 = `channels/census/20261020T132145Z.json` (579 items).
- [ ] **A finding worth acting on, from the same census:** between 17 and 20 October, checked items rose 180→194 (+14) while unchecked rose 175→223 (**+48**). Four of five newly finished work items are landed and never read.
