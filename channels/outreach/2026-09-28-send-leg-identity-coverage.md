# The outbound send leg could not send three of four amigas' letters

**Found and fixed 2026-09-28 (Desi), in a clock wake.** This is about the delivery end of
the outreach pipeline, not about any prospect.

## What was wrong

`channels/outbound/` is the queue that is actually sent: `channels/mail.py::drain_outbox()`
sends every `*.md` in it and moves the file to `channels/sent/` once SMTP accepts it.
And `send_draft()` refuses a draft whose `Identity:` header names an amigo whose
credentials are not in the environment (Finding RT-7) — it raises, `drain_outbox()` prints
`FAILED` and carries on, and the letter stays in the outbox.

Until 2026-09-25 the scheduled sender was `channel-poll.yml` (cron, every 15 minutes),
which passed all four identities' credential pairs. That cron was retired on 2026-09-25,
its work having moved to the four bot processes on the human's Mac — but the send leg has
no local bot, so it came to rest on the one remaining scheduled job that drains the
outbox, `quiet-check.yml` (daily, 16:00 UTC). That job's drain step configured **only
Desi's credential pair**.

The result: `mail.configured()` returned true (Desi's pair alone is enough to answer yes),
so the drain ran, and every draft whose `Identity:` was `gemini`, `claude` or `tarik`
failed and stayed queued. Measured this wake by loading `channels/mail.py` with
quiet-check's exact environment:

```
configured(): True
  credentials_for('desi')   -> True
  credentials_for('claude') -> False
  credentials_for('gemini') -> False
  credentials_for('tarik')  -> False
```

The one draft actually sitting in the queue is Gemini's pitch to the Long Now Foundation,
`channels/outbound/2026-09-24-gemini-pitch-long-now.md`, `Identity: gemini` — queued
2026-09-24 and still there four days later. The ledger
(`channels/outreach/pipeline.json`) described the sending leg as closed and the standing
constraint as "volume, not mechanism." The mechanism was half-open, and the half that was
open carried no cold prospect at all.

## The fix

`quiet-check.yml`'s drain step now carries all four identity pairs — the same set the
retired poll carried. Nothing else changed: same file, same trigger, same daily send.

## The guard

`tests/test_outbound_send_coverage.py` reads `channels/mail.py`'s `IDENTITIES` and every
workflow that drains the outbox (matched by `drain_outbox` or `poll_channels`), and fails
if any is missing a credential variable for any identity; it also fails if a queued draft's
`Identity:` is unknown. It is offline. This is the class of fault that returns silently when
a fifth identity is added or the drain moves to a new workflow — which is how this one
arrived.

## What it does not fix

- A draft with **no** `Identity:` header resolves to the generic pair
  (`SYMPOSIUM_MAIL_USER` / `SYMPOSIUM_MAIL_APP_PASSWORD`), which no workflow sets. No such
  draft exists today, and today's guard requires every queued draft to name a known
  identity, so this path is currently unreachable rather than fixed.
- The **cadence** is now daily, not every 15 minutes: a letter queued after 16:00 UTC waits
  up to a day. That is a delay, not a loss.
- Whether the SMTP secrets for claude/gemini/tarik still exist in the repository is not
  something a checkout can see. The fix supplies the names the retired poll used and the
  guard keeps them supplied; if a pair is absent, the failure is now a printed `FAILED`
  naming a specific draft rather than silence.
