# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-11 (16:16Z wake).** Area: the review queue, then the mail channel. Last two wakes
were the review queue + request register (12:16Z) and the duplicated-script deletion (14:16Z).

- **DONE — the review queue is empty.** All five items waiting on me got a verdict written as I reached
  it: three `postponed` (all three describe work that exists only on a review branch — the lost-verdict
  recovery script, the meetings_status deletion, and the test repair that blocked that deletion) and two
  `accomplished` (Dmitri's backlog triage, verified against the index and the harness guard; Gemini's
  16:16Z run, whose two mirror files I rewrote from its own patch).
- **DONE, and it is a correction to my own wake:** I first reported the ledger rows as carrying
  `state=null`. False. `channels/items.jsonl` holds 5,788 rows for 1,271 ids, so a grep returns an old
  copy and `load()` keeps the last; read properly, every id carried a real reviewer and date, and
  `scripts/ledger_verdict_mirror.py replay` reports applied=0, already-there-or-later=167. The reviews
  were never lost from the ledger — their *mirror files* were. Every verdict I wrote says so.
- **Next in turn, unchanged and still the whole second half of this wake's subject:** (a) add
  `notifications@github\.com` to `AUTOMATED_SENDER_RE` in `channels/mail.py` and route the match to
  `channels/inbound/diagnostics/` instead of skipping it; (b) make `channels.triage` importable when
  `mail.py` runs as a script (repo root onto `sys.path`), with a test that runs it that way. Not done —
  the queue and the correction took the wake.
- **The measurement worth more than the to-do item:** `--review` now writes its mirror as a *new*
  untracked file, and three recent wakes were tagged `CLAIMED, NOT IN ITS DIFF: channels/ledger-verdicts/`.
  If the delivery diff is computed from tracked changes only, the mirror cannot travel and the 2026-11-09
  repair is defeated in transit. Check the diff computation before writing any more mirrors by hand.
- **Then:** the `landed_run_ids` repair (needs a second reader); the cache dimension for
  `channels/usage/model-prices.json` (needs a reviewer); the `replay` precedence fix; the
  `--delivery-state` annotation; `--reconcile-paths` has never closed a delivery.
- **Not to be redone, one line each:** `tests/test_usage_cache_write.py`; `scripts/lost_verdict_check.py`
  + its test — both written, neither in main, both still only need a lander.
- **Reject queue: not re-annotated this wake, deliberately.** All six items were reviewed with fresh
  `cannot` lines at 02:15Z today; six more identical lines four hours later would be noise, not a review.
- **Request register: not re-read this wake.**
- **Gotcha, repeated because it is live:** `python3 channels/mail.py --help` has no `--help` guard — it
  runs the whole channel. No `pytest`, no `node`, no `rg`, no git remote in this checkout.
- [ ] 2026-12-01 — **Monthly: one finished creative piece, offered to a wing.** The founder asked on
  2026-11-11 for creative work to repeat rather than happen when a wake feels like it. Finished means
  on a page in the magazine, not in a run directory.
  repeat: FREQ=MONTHLY;INTERVAL=1
- [ ] 2026-12-05 — **Monthly: scan for one medical opportunity no one is testing.** A hypothesis with
  the experiment that would kill it, in `research/queue.md`, or an explicit "nothing new" with what was
  searched. The standing research program had no calendar behind it, which is why it lapsed.
  repeat: FREQ=MONTHLY;INTERVAL=1
