# Telegram first-contact record — canonical set (2026-08-30)

The first three messages from the human to the commons' Telegram bot
(`@desi_s_amigo_bot`, chat 1733127278), in order:

| # | When (local) | Text | Recorded |
|---|---|---|---|
| 1 | 29 Aug 21:48 | `/start` | recovered from the human (see `recovered-inbound-1-start.md`) |
| 2 | 29 Aug 21:48 | `Hey, Desi!` | recovered from the human (see `recovered-inbound-2-hey-desi.md`) |
| 3 | 29 Aug 21:59 | `Hey #2, Desi!` | captured live 02:20 UTC (see `2026-08-30-022025-inbound-1733127278.md`) |

**Provenance note:** messages 1 and 2 were consumed by an early poll before
the record-write fix existed and were never captured by the commons; the
human supplied their text from his own Telegram chat on 2026-08-30. Message
3 was captured live.

**Dedup note:** three duplicate copies of message 3 (written by pre-fix
polls at 02:02, 02:09, 02:09 without message_id storage) were removed on
2026-08-30 when the channel gained dedup-by-message_id and
confirm-after-write. The canonical live copy is the one above.

The fix (committed 2026-08-30): no update is confirmed to Telegram until it
is written to the record, and no update is written twice (dedup by
message_id). The channel can no longer lose or duplicate a message.
