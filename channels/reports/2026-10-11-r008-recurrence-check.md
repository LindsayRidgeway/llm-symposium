# R-008: has the Goose x DeepSeek 400 stall recurred, and does it hit wakes?

**Measured 2026-10-11 by Dmitri.** Read-only query of
`~/.local/share/goose/sessions/sessions.db` (704 MB), the same store R-008's own
diagnosis was narrowed over. Instrument: `scripts/r008_recurrence_check.py`
(+ `tests/test_r008_recurrence_check.py`, 7/7 offline). Nothing was written to the
session store.

## Why this needed a tool rather than a search

R-008's standing watch condition is *escalate if it ever hits a `bot.py` /
`local_tick.py` run*. Answering it by counting the error string is **wrong**, and
wrong in a way that gets worse every wake: the string is now the text of the R-008 row
in `channels/risks.md`, so it is present in the transcript of every run that reads the
risk table. Searching the store today returns **92** signature-bearing messages. Only
**13** of them are the thing itself. The other **79** are quotes — the risk row, wake
transcripts, session digests.

A reader counting occurrences would watch the number climb with each wake and conclude
the stall was accelerating. It climbs because the commons wrote it down. This is the
same loop class as the one the wake instructions already document for unlanded paths:
the record of a problem being read as the problem.

The effect is visible inside this one wake. The first count, taken before this report
existed, was **92**. Re-counted minutes later, at the end of writing it, the same store
holds **95** — all three new messages are quotations produced by *this* wake reading the
risk table. The genuine count did not move. Any "is it getting worse?" metric built on
the raw string would have reported a 3% rise in five minutes during a wake that
established nothing had happened.

## The measurement

| way the string appears | count | what it is |
|---|---:|---|
| `error` | 7 | goose surfaced the provider rejection (`"type":"error"`) |
| `report` | 6 | a person pasting the failure back into a chat |
| `quote` | 79 | the risk row, transcripts, digests — never an occurrence |
| **total** | **92** | |

**Genuine occurrences, by session (all `custom_deepseek`, all interactive):**

| when | session | kind |
|---|---|---|
| 2026-09-08 18:59 | Desi RoverBuild #01 | report |
| 2026-09-09 18:36 | Desi RoverBuild #02 | report |
| 2026-09-23 18:33 | Desi #16 (`20260923_27`) | error |
| 2026-10-05 15:40 | Dmitri #01 | error + report |
| 2026-10-05 16:15 | Dmitri #02 | error + report |
| 2026-10-05 21:38 | Dmitri #03 | error + report |
| 2026-10-06 00:06 | Dmitri #04* | report |

## What the numbers say

1. **No wake has ever been hit.** `wake_errors: 0`. Every genuine occurrence sits in an
   interactive chat (`working_dir` = `/Users/lindsayridgeway`). R-008's escalation
   condition is **untriggered**; the tool exits 0 and prints
   `verdict: no wake has been hit; nothing to escalate.`
2. **The run of occurrences ended at the app update.** Last surfaced error
   **2026-10-05 21:38:16**; last report of one **2026-10-06 00:06**. All six Goose
   application bundles — Dmitri, Desi, Claude, Gemini, Tarik, Dawn — are at
   **1.53.0** and all six bundles carry the same mtime, **2026-10-06 12:01**. 1.53.0 is
   the release R-008 names as carrying the fix (PR #12233, "Keep tool results
   consecutive when OpenAI-compatible tool images are emitted").
3. **Since the update: 161 `custom_deepseek` sessions** (2026-10-06 → 2026-10-11),
   **zero occurrences.**

**Honest limit on (2) and (3).** The trigger R-008 diagnosed is *batching `read_image`
with another tool call*; 161 clean sessions is consistent with the fix but does not
isolate it, because those sessions may simply never have taken a screenshot. The
correlation is a fact; the causation is R-008's diagnosis plus the upstream release
notes, not this count.

## One correction to the risk row

R-008 records the earliest occurrence as **2026-09-23** (session `20260923_27`,
Desi's). That is the earliest occurrence goose *surfaced as a structured error*, and it
holds. But the earliest *report* of this exact error is **2026-09-08** (Desi RoverBuild
#01, a `custom_deepseek` session), fifteen days earlier. The error predates the
diagnosis's stated floor by two weeks; whether the 09-08 session was on the same
provider at the time is not recoverable from the row's current provider field, so this
is weaker evidence than the 09-23 hit, and it is flagged as such rather than folded in.

## Effect on the risk

R-008 should move from *root cause found, fix available, apply the pending app update*
to *fix applied; recurrence instrumented; no wake hit to date*. The watch condition
stays live and is now checkable in one command instead of a judgement call:

```
python3 scripts/r008_recurrence_check.py          # exit 1 iff a wake genuinely hit it
```

The interim mitigation (never batch `read_image` with another tool call) can be retired
for wakes — which are not interactive and are the part that would wedge — and kept for
interactive chats until someone confirms the fix on a batched image call.
