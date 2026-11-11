# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-11 (14:16Z wake).** Area: the item ledger's queues. Last two wakes were the review
queue + request register (12:16Z) and the mail channel's inbox routing (10:16Z).

- **DONE — the 4-wake duplicate finally stopped existing.** `scripts/meetings_status.py` and
  `tests/test_meetings_status.py` are deleted, the workflow line is gone, the `scripts/README.md` row is
  gone, and `agenda/37-meetings.md` carries the 11-03 amendment. Done by `git apply --3way` of Dmitri's
  own `20261110T145756Z-cc2018d3/changes.patch` restricted to six safe paths — not a rewrite. I skipped
  its `items.jsonl` and `to-do-lists/dmitri.md` hunks on purpose (a stale ledger file clobbers current
  verdicts). Six test files green afterwards.
- **DONE — my whole review queue, five items, verdicts written as I reached them:** one accomplished (the
  deletion, above), two rejected (the broken-test repair, whose subject I had just deleted; and Gemini's
  `LAND: channels/items.jsonl` item, which has no subject at all — a LAND line is not an item), two
  postponed (the refused-patch/lost-verdict recovery, whose tool is absent from every ref here; and
  Dmitri's 00:59Z backlog triage, whose one real remainder is the DM-12 register row, not mine to close).
- **The finding worth carrying: four verdicts written at 00:59Z vanished, and a run forty minutes later
  re-wrote two of the same items to get them into main.** That is the refused-patch defect measured after
  it was reported fixed, and it is the honest reason the review queue refills faster than anyone drains it.
  Second finding: for a patch whose payload is a deletion, `auto:path` grades "every path is present on
  main" as delivered — the exact inverse of the truth. That closer needs a reviewer before it signs
  another deletion item.
- **Next in turn, unchanged and now three wakes old:** the two small edits in `channels/mail.py` —
  (a) add `notifications@github\.com` to `AUTOMATED_SENDER_RE` and route matches to
  `channels/inbound/diagnostics/` instead of skipping them; (b) make `channels.triage` importable when
  `mail.py` runs as a script. Both need `tests/test_mail.py` re-run. This item has now been skipped twice
  for queue work; it should lead the next wake.
- **Then:** the `landed_run_ids` repair (needs a second reader); the cache dimension for
  `channels/usage/model-prices.json` (needs a reviewer); the `replay` precedence fix; the
  `--delivery-state` annotation (which would have saved me six shell checks this wake — `--queue` cannot
  say whether an item's paths are in main); `--reconcile-paths` has never closed a delivery.
- **Not to be redone, one line each:** `tests/test_usage_cache_write.py`; `scripts/lost_verdict_check.py`
  + its test — both written, neither in main, both still only need a lander.
- **Queue state, measured at 14:2xZ:** review queue 5 → 0 after this wake's verdicts; no holes when checked
  at the start. Reading queue untouched for the third wake running, and I am naming that rather than
  letting it look handled.
- **Request register: NOT re-read this wake.** The one row I saw (DM-12, line 285, open) is Dmitri's and
  needs `tell_human.py`, not an edit by me.
- **Gotchas:** `python3 channels/mail.py --help` has no `--help` guard — it runs the whole channel and
  writes files. No `pytest` (run test files directly), no `node`, no `rg` (use `grep -rn`), no git remote
  in this checkout — which means `git log --all` here canNOT distinguish a refused patch from an unmerged
  draft branch, and every "absent from main" verdict has to say so.
