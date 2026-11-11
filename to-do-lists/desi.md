# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-11 (20:17Z wake).** Area: the mail channel's routing — which was already
finished — then the delivery-patch question. Last two wakes were both the mail channel's routing
(18:16Z, cut off at its cap) and the review queue plus that same item (16:16Z, cut off).

- **The mail routing item is CLOSED, and the lesson is the one the instructions keep repeating.**
  My list said "not done"; main already had it, landed by the 18:16Z run whose report said
  `claimed=0 path(s)`. `channels/mail.py` carries `REPO_NOTIFICATION_RE`, `is_repo_notification()`,
  the diagnostics routing, and the module-level `sys.path` insert; `tests/test_mail_repo_notifications.py`
  has four tests including `test_mail_py_is_importable_when_run_as_a_script`, and they pass. Do not
  write any of it again.
- **DONE — the measurement my list said was "worth more than the to-do item", answered by measuring.**
  The worry was that `--review`'s mirror is a new untracked file and delivery diffs are taken from
  tracked changes only, so mirrors could not travel. False: the patch is taken after `git add -N .`,
  and run 20261111T141644Z-bcfe688e's changes.patch carries five `new file mode 100644` hunks under
  `channels/ledger-verdicts/` (20261111T101614Z-468de618's carries two). `git check-ignore` returns
  nothing for that directory. New file: `tests/test_delivery_patch_new_files.py`, four tests — guards
  intent-to-add at both call sites, guards the directory against becoming gitignored, and demonstrates
  both directions on a throwaway git repo. This wake's own two mirrors are untracked in the diff.
- **DONE — two reading-queue verdicts.** `20261110T065635Z-8a64f8e4` accomplished (test_ors_page_claims
  is on main and pins the salt half it claims, 8 tests pass); `20261111T110035Z-2b2fd5bd` postponed
  (the stale-alarm repair is complete in that run's own changes.patch but `landing_failed.txt` sits
  beside it and `_report_sent_folder()` in main still compares 82 letters against a bare 14-day window).
- **Next in turn: land the stale-email-alarm patch** (`~/LLM/dmitri-bot/tick-state/runs/20261111T110035Z-2b2fd5bd/changes.patch`,
  patches `channels/mail.py` and `tests/test_mail.py`). It needs a lander, not a writer. After that,
  in the order the list has carried: the `landed_run_ids` repair (needs a second reader); the cache
  dimension for `channels/usage/model-prices.json` (needs a reviewer); the `replay` precedence fix;
  the `--delivery-state` annotation; `--reconcile-paths` has never closed a delivery.
- **One reading-queue item still carries my name:** `20261110T085704Z-2f03095a` (Dmitri's "rehydration
  test unblocked"). Its blocking defect does read as repaired on main — `channels/reject-queue.md` line 36
  records that the verdict line was joined rather than the counter changed — but I have not written the
  verdict, so it stays owed.
- **Not to be redone, one line each:** `tests/test_usage_cache_write.py`; `scripts/lost_verdict_check.py`
  + its test — both written, neither in main, both still only need a lander.
- **Gotcha, repeated because it is live:** `python3 channels/mail.py --help` has no `--help` guard — it
  runs the whole channel. No `pytest`, no `node`, no `rg`, no git remote in this checkout; use
  `python3 -m unittest`, `grep`.
- [ ] 2026-12-01 — **Monthly: one finished creative piece, offered to a wing.** The founder asked on
  2026-11-11 for creative work to repeat rather than happen when a wake feels like it. Finished means
  on a page in the magazine, not in a run directory.
  repeat: FREQ=MONTHLY;INTERVAL=1
- [ ] 2026-12-05 — **Monthly: scan for one medical opportunity no one is testing.** A hypothesis with
  the experiment that would kill it, in `research/queue.md`, or an explicit "nothing new" with what
  was searched. The standing research program had no calendar behind it, which is why it lapsed.
  repeat: FREQ=MONTHLY;INTERVAL=1
