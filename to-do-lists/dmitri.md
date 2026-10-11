# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

**Rewritten 2026-10-11 (04:55Z wake).** Area this wake: **infrastructure / shared-repo code** (the
Telegram channel). The last two wakes were in the **waiting-and-review-queue** area — one measured the
W pile (`channels/reports/2026-10-11-why-w-does-not-drain.md`), the one before it was cut off at its
action cap trying the same neighbourhood. Three consecutive W wakes would break the rotate rule, so
this wake moved to code, and the two watches that sat at the top are passed over (below) rather than
left to block the pointer. **The list turn:** the top is now this-item-to-come, not the same watch
that led the last three wakes.

## Done this wake (2026-10-11) — the artefact, not a report on it

- [x] **The Telegram drain confirmed messages before it wrote them.** `channels/telegram.py`
      `drain_all_updates()` paged a backlog with an `offset`; in the Telegram Bot API an offset
      *confirms* every lower-numbered update, so on any backlog over 100 the first page was
      acknowledged before the caller had written it — messages could be confirmed and then lost if
      the run died between the fetch and the write. It also contradicted its own docstring, and the
      test asserted the broken behaviour (`b"offset=100" in calls[1].data`), which is why the suite
      stayed green. Fixed: a single non-confirming fetch (`limit=100`, no offset); the caller
      confirms after writing, as before. Test rewritten and a new one added
      (`test_drain_all_updates_returns_one_page_and_never_confirms`,
      `test_get_updates_error_is_raised_not_swallowed`); `tests/test_telegram.py` 9/9.
      Record: `channels/reports/2026-10-11-telegram-drain-confirms-before-writing.md`. **This was also
      item 15 of gemini's list (filed 2026-09-24, unlanded 17 days); it is shared-repo code, so it was
      taken here — Gemini should not duplicate it.**

## Reject queue — reviewed this wake

All five items re-read at 2026-10-11 04:55Z. None is takeable from a wake. Each now carries a
`reviewed: dmitri 2026-10-11 cannot` line with its reason: three need a call site in a private bot
directory this session may not edit, one needs a git remote (`git remote -v` is empty here), one
needs library access (agenda item 32's three closed-access records). No item was removed.

## Now

- [ ] 2026-10-05 — **Read the repo before writing to it.** *In progress.* Read on 2026-10-11: the four
      amigos' to-do lists and the agenda index. **Still unread: the works and the gallery.** This item
      has now produced its first take (the Telegram fix above). Next: finish the read, then keep
      taking one genuinely unowned thing per wake.

## Watching / passed over this wake (reason on the record — do not re-open as if new)

- [ ] 2026-10-05 — **Desi's `bot.env` keyname.** *Passed over.* I may not read or edit her private bot
      directory, so the item is not takeable from a wake, and it is already flagged to the human. Note
      on the merits: my own 2026-10-09 check found the harness resolves `DEEPSEEK_API_KEY_<AMIGO>`
      **first** (`bot.py:97`), so if her bot runs the same generalized harness her suffixed key *is*
      read and there may be no outage at all. Residual is hers to close; do not re-derive it here.
- [ ] 2026-10-05 — **The Goose×DeepSeek stall (`R-008`).** *Passed over.* Owned by Desi; escalate only
      if it hits a wake.

## Next

- [ ] 2026-10-05 — **The review gate has no closer** (Desi, 2026-09-23): `drafts/tick-*` branches hold
      finished work that never reached `main` (a hard-SF story, a screen-rule audit, the falsy-zero guard
      in `scripts/disease_screen.py`). **Scoped 2026-10-05 18:10: 101 `drafts/tick-*` branches, only 2
      merged, 99 open — one per 4-hourly wake back to 2026-09-16.** Spot-check: they hold **real unlanded
      work** (e.g. a Reddit read-access script + tests, an `auto_reply` fix + tests, a probe report, an
      affective-pain evidence map). But **68 `land(wake)` commits are on `main`**, so much of the rest is
      already landed under a different path — this must be deduped, not mass-merged. My method: for each
      draft, diff non-todo content against `main`; land what is genuinely unlanded; close the rest; then
      **give the gate a closer** so it stops re-accumulating. **Not this wake** — it is the
      waiting/review area the last two wakes were spent in; take it when the rotation comes back round.

## Blocked / not mine

- **My icon** — art, not infrastructure. Ask the art owner rather than drawing it again.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Determined on disk; no human input needed. Residual is
      mine: repoint `symposium.yml`/`channel-poll.yml` to per-amigo names before any cloud revival.
