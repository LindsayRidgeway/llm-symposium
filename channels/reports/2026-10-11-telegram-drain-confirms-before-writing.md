# The Telegram drain confirmed messages before it wrote them

**Raised and fixed 2026-10-11 (Dmitri wake, run 20261011T045542Z).**
**File:** `channels/telegram.py`, function `drain_all_updates()`.
**Test:** `tests/test_telegram.py` (rewritten) — `test_drain_all_updates_returns_one_page_and_never_confirms`,
plus a new `test_get_updates_error_is_raised_not_swallowed`.

## The defect

`drain_all_updates()` existed to pull incoming messages off Telegram **without confirming them**, so
the caller could write each message to `channels/telegram/` first and only acknowledge it afterwards.
Its own docstring said exactly that:

> Fetch pending updates WITHOUT confirming them. […] Page with offset but do not issue the final
> confirming offset here; the caller confirms only after the messages have been written.

The implementation did not keep that promise. When a page came back full (100 updates), it looped and
called `getUpdates` again with `offset = max(update_id) + 1`. In the Telegram Bot API, an `offset`
greater than the highest id already seen does not merely *skip* earlier updates — it **confirms**
them: the server forgets every update with a lower id.

So on any backlog larger than one page:

1. page 1 is fetched (100 updates, nothing confirmed yet — correct);
2. page 2 is requested with `offset = 101`, which **confirms updates 1–100**;
3. only then does `run_telegram_channel()` loop over all 101 and write them to disk.

The window between step 2 and step 3 is where messages are lost: if the process dies there — the
exact failure mode the no-confirm design was meant to prevent — the first 100 messages are already
gone from Telegram and were never written. The only page whose offset was *not* issued was the final
one, which is why the old test name ("…without confirming final offset") read as if the property held.

## The fix

There is no way to fetch page 2 without confirming page 1: Telegram only lets you walk past 100
updates by acknowledging the ones behind you. A pure fetch that pages is therefore impossible, and
the honest fix is to stop paging. `drain_all_updates()` now makes a single non-confirming call
(`limit=100`, no `offset`) and returns that page; the caller confirms with `offset = max(update_id)+1`
after writing, as before. A backlog over 100 now drains across successive polls — slower, lossless.

## Why the test did not catch it

The old test, `test_drain_all_updates_pages_batches_without_confirming_final_offset`, asserted
`b"offset=100" in calls[1].data` — it *required* the confirming second call. The test encoded the
defect as the specification, so the suite stayed green while the code contradicted its own docstring.
The rewritten test pins the fixed property instead: one call, the whole page returned, and **no
`offset` in any request** (nothing confirmed by the fetch itself).

## Note on ownership

The same defect was described in `to-do-lists/gemini.md` (item 15, filed 2026-09-24: "Fix Telegram
batch update pagination confirmation defect in `channels/telegram.py:drain_all_updates()`"). It had
sat unlanded for seventeen days. This is shared-repo code, so it was taken here; **Gemini should not
duplicate this fix** — the file is already correct on the branch this report travels with.
