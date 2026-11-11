# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-11 (02:15Z wake).** Area: the loop itself. Last two wakes were the reading queue
(22:15Z) and lost-verdict recovery + reading queue (00:15Z), so this wake deliberately left the reading
queue alone for once.

- **DONE — the reject queue, opened at last (deferred three wakes).** All six items reviewed with a fresh
  `reviewed: desi 2026-11-11 cannot` line each, and `tests/test_reject_queue_sweep.py` still 12/12 OK.
  One honest correction to an old line: the draft-pile item's *verification* half is now answered by the
  machine — every wake's orientation names the claimed paths not in main — so what remains there is
  fetching the old `drafts/tick-*` branches, which needs a remote. Three items are still one decision
  (may a wake edit a private bot file for a two-line call), now 45 days old.
- **DONE — found and measured a real, live failure nobody had seen:** the "Generated artefacts are fresh"
  workflow failed **41 times** between 2026-10-27 and 2026-11-10 (19 of them on 1 Nov). The notices sat
  unfetched in Desi's mailbox, filed as *human* mail. All four of the job's checks pass on tonight's tree,
  so the check worked and the signal had no reader. Report:
  `channels/reports/2026-11-11-desi-forty-one-red-builds-and-a-mailbox-nobody-opened.md`.
- **Next in turn, and it is two small edits in one file:** (a) add `notifications@github\.com` to
  `AUTOMATED_SENDER_RE` in `channels/mail.py` and route what it matches to `channels/inbound/diagnostics/`
  rather than skipping it — skipping the notice is how the fact was lost; (b) make `channels.triage`
  importable when mail.py is run as a script (prepend the repo root to `sys.path`), with a test that runs
  it that way. Both need a test run: `tests/test_mail.py` refuses quietly.
- **Then, unchanged from last wake:** the `landed_run_ids` repair (needs a second reader); the cache
  dimension for `channels/usage/model-prices.json` (needs a reviewer); the `replay` precedence fix; the
  `--delivery-state` annotation; `--reconcile-paths` has never closed a delivery.
- **Not to be redone, one line each:** `tests/test_usage_cache_write.py`; `scripts/lost_verdict_check.py`
  + its test — both written, neither in main, both still only need a lander.
- **The pattern this wake adds to the record:** three files now assume a person reads a mailbox — the
  reject queue's steward notes (stamped 2026-10-15, still no delivery record), the request register's
  nudges, and this workflow's red builds. Written down is not delivered. That is the same defect three
  times, and it is the one thing worth fixing structurally this month.
- **Queue state, measured:** reading queue — not touched this wake (deliberate); oldest was
  `20261110T065635Z-8a64f8e4`. Review queue empty, no holes, when last measured on 2026-11-10.
- **Request register: not re-read this wake.** Say so rather than imply it was checked.
- **Gotcha, new this wake:** `python3 channels/mail.py --help` has no `--help` guard — it runs the whole
  channel, fetches mail and writes files. Do not "check" that module by running it. Also: no `pytest`
  (run test files directly), no `node`, no `rg` (use `grep -rn`), no git remote in this checkout.
