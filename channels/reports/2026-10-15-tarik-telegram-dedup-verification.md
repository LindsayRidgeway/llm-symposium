# Tarik Telegram deduplication verification — 2026-10-15

## Question

Tarik's queue still said to fix Telegram deduplication so one bot's seen message could not suppress another bot's message with the same Telegram `message_id`.

## Finding

The fix is already present on `main`, so the remaining queue entry was stale state rather than missing code.

Evidence in `channels/telegram.py`:

- `log_message(...)` records both `Bot` and `Message_id` when present.
- `_load_seen_keys()` returns `set[tuple[str, int, int]]`, keyed as `(bot, chat_id, message_id)`.
- `_is_seen(...)` checks the exact `(bot, chat_id, message_id)` tuple, with a wildcard only for legacy logs that predate the bot field.
- The poller calls `_is_seen(seen_keys, name, chat_id, mid)` and adds `(name.lower(), chat_id, mid)` after logging a new inbound message.

Regression coverage in `tests/test_telegram.py`:

- `test_deduplication_by_bot_chat_message_id()` writes a Gemini log for chat `42` / message `1001` and proves Tarik with the same chat/message tuple is **not** treated as seen.
- The same test also proves legacy logs without a bot line still match any bot for backward compatibility.

## Verification run

```text
$ python3 tests/test_telegram.py
9/9 tests passed
```

## State change

I removed the stale Telegram deduplication item from `to-do-lists/tarik.md` so the next wake advances to the local-trigger integration item instead of redoing landed work.
