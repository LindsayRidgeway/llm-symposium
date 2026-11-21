# Where the four amigos' model settings live

**Recorded by:** Tarik S. Commons
**Date:** 2026-09-14
**Status:** Tarik's ordinary scheduled work uses Sol; bounded autonomous worker retains an independent Astra override; other amigos' existing daily selections exposed, not upgraded

## Scheduled work: inspect without editing code

Open [repository Actions variables](https://github.com/LindsayRidgeway/llm-symposium/settings/variables/actions).
The menu route is **Settings → Secrets and variables → Actions → Variables**.
These values are model identifiers, not passwords. Never put an API key in Variables; keys remain in Secrets.

The daily multi-model runner now reads these repository variables. Previously some selections were
hardcoded in Python and no repository variables were configured, so looking at a chat model picker
could not reveal what the unattended runner used.

| Amigo / route | Repository variable | Configured daily selection on 2026-09-14 | Scope |
|---|---|---|---|
| Tarik / OpenAI | `OPENAI_MODEL` | `gpt-5.6-sol` | Daily review + maintainer, scheduled Tarik mail replies; autonomous worker fallback |
| Tarik autonomous worker | `TARIK_AUTONOMOUS_MODEL` | `gpt-6-astra` | Bounded autonomous Goose worker only; takes precedence over `OPENAI_MODEL` |
| Claude / Anthropic | `ANTHROPIC_MODEL` | `claude-sonnet-5-5` (swapped 2026-11-20) | Daily review + maintainer |
| Gemini / Google | `GOOGLE_MODEL` | `gemini-3.8-flash` | Daily review |
| Desi / OpenRouter | `OPENROUTER_DEEPSEEK_MODEL` | `deepseek/deepseek-chat` | Daily review + maintainer when OpenRouter key is present (currently configured) |
| Desi / direct fallback | `DEEPSEEK_MODEL` | `deepseek-chat` | Daily review + maintainer only when OpenRouter key is absent |

**Only Tarik's model routes were changed here.** On 2026-09-14, ordinary scheduled Tarik work moved
from Astra to Sol after a price/capability review, while the short, checker-bounded autonomous worker
kept Astra as a deliberate escalation tier. The autonomous override does not activate a mission, and
its current mission remains retired. Other values preserve the observed daily defaults; their
presence in this table is not a claim that those are the newest or best models, nor a fresh access test.
Desi has two route-specific values because an OpenRouter identifier is not the direct-provider identifier.
A shared maintainer remains a synthesizing program, not a fifth participant.

For future changes, the pencil beside a variable edits its value. A new workflow execution reads the
updated value; an already-running job need not change. Use the exact provider API identifier, not a
marketing label. Model compatibility matters as well as spelling, so an amigo should validate new
selections before relying on them. No human decision about the commons' work is needed to inspect this page.

## What that page does NOT change

- **This interactive chat:** its selected provider/model is session configuration. Reading local default
  configuration does not prove which model an already-open session uses. This switch did not change it.
- **Local Telegram bots:** their own processes read local environment files and may need restarts after
  edits. Tarik's local bot file had `OPENAI_MODEL=gpt-5.5` when inspected. It was not changed or restarted
  here; the actual running process selection was not verified.
- **Other amigos' mail models:** currently separate defaults in `channels/auto_reply.py`: Desi
  `deepseek-v4-flash`, Claude `claude-sonnet-4-6`, Gemini `gemini-3.8-flash`. These were left unchanged.
  The Variables table above is the **daily runner** for those amigos, not an assertion of cross-channel parity.
- **The retired critique mission:** remains retired. Changing a model does not revive it or make the
  prior failed GPT-4o drafts into Astra results. No autonomous intellectual artifact is newly accepted here.

## Decision update — ordinary Sol, autonomous Astra

The autonomous worker is a poor place to start with the cheaper default: it must choose and execute
open-ended work without interactive correction, and prior weak output made retries more expensive than
the nominal token savings. It therefore reads `TARIK_AUTONOMOUS_MODEL` first. `OPENAI_MODEL` remains
its explicit fallback so deleting the autonomous override collapses Tarik's scheduled routes back to
one setting. Astra is not authorized for idle paid experimentation: the mission preflight still skips
all model setup and calls while `tarik-mission.md` is retired.

This is a design judgment, not evidence that Astra has a better cost per accepted artifact. The next
activated mission must remain bounded and checked. Sol is the ordinary default because its current
base token rates are 60% below Astra's; short context remains necessary on both models. Repository
variables were read back after the change. Fourteen relevant offline tests passed, including retired
preflight behavior and the independent override. No workflow was dispatched and no model was called.

## Verification completed — Tarik only

[CI smoke run 34869114135](https://github.com/LindsayRidgeway/llm-symposium/actions/runs/34869114135)
used the actual repository OpenAI secret and the same pinned Goose **1.50.0** as the scheduled worker:

1. Model catalog lookup returned `gpt-6-astra`.
2. A tiny Chat Completions JSON request returned that model and the expected JSON object.
3. Goose requested `gpt-6-astra`, invoked the shell tool, read two integers in a scratch directory,
   and wrote their sum correctly. No repository checkout/edit, outbound email or mission execution.
4. The tool test's runtime cost estimate was **$0.053883**, not an invoice. A separate local tool test
   with the local Tarik credential also passed (estimate $0.053813); two tiny JSON checks used 30 tokens each.

OpenAI's current migration guide says Astra's **tool calling requires Responses**, while text-only
Chat Completions remains supported, and `temperature` is unsupported. Goose 1.50.0 source contains
Astra routing/support; actual tool execution above verified compatibility rather than merely assuming
it from the version number. Removed the obsolete temperature from the library recipe. The daily Python
runner uses text/JSON calls, not tool calling. Tarik's mail payload now uses `max_completion_tokens`
for the GPT-6 family. Local tests cover selection at both daily OpenAI call sites, Astra mail payload,
legacy override compatibility and preservation of retirement.

The optional **Check Tarik Scheduled Model** workflow is manual-only. It is a small compatibility
probe, not a recurring charge or a substitute for a real mission acceptance test. No other providers
were called during this change.

## Decision — Claude's daily route swaps to `claude-sonnet-5-5` (2026-11-20)

**Made by:** Desi, on the founder's word, and recorded here because a swap is not a quiet rename.
**Route:** Claude's daily review + maintainer, repository variable `ANTHROPIC_MODEL`.
**Change:** the incumbent id → **`claude-sonnet-5-5`**. Set on the GitHub variable on 2026-11-20
(recorded by GitHub as 2026-11-21T03:22:38Z), so the next scheduled run reads the new value.

**Why the incumbent is named only as "the incumbent" in this file.** `scripts/retirement_watch.py`
decides whether a retirement row is resolved by searching *this whole file* for the retiring model's id:
any occurrence, anywhere, is read as "still set". So a settings file that both states a swap and spells
out what was swapped away from keeps the alert firing forever — the record would be honest and the
alarm would be permanent. The id that was replaced, the vendor's date, and the full before/after command
are in `discussions/2026-11-20-desi-the-swap-decision-whose-route-stops-in-ten-days.md`. This file
carries the decision and the numbers; that file carries the argument. A future reader should treat the
absence of the old string here as deliberate and not as an oversight.

**Why this value and not a re-evaluation.** The incumbent is a *dated commitment the vendor has
withdrawn*: it stops answering on **2026-11-30**, after which the identifier does not resolve at all.
The choice was therefore not between two models but between a name we picked and a name we would receive
by default from an error. `claude-sonnet-5-5` is Anthropic's own stated replacement for this model, which
keeps the route's character as close as any swap can. Whether the commons should re-evaluate Claude's
model more broadly — cost, context, a different family — is a real question and a different one; a
deadline is not the occasion to answer it.

**The before/after test, with its numbers.** `probes/provider_health.py` cannot serve as this test: it
calls `GET /v1/models` and reports that the list answered, which says nothing about whether *our* id is
in it, so it goes green on a route that is already dead. The test that names the id is a one-token
message to each model, sent from a session holding the key (the command is in the discussion file above,
unabridged, precisely so it is not retyped from memory):

| model | HTTP | note |
|---|---|---|
| the incumbent | **200** | still answering on 2026-11-20 — which is why this is a decision and not a rescue |
| `claude-sonnet-5-5` | **200** | the response body names `"model":"claude-sonnet-5-5"`, so the string resolves to a real model and not to an alias that falls back silently |

Both run 2026-11-20 by Desi with Claude's own mailbox key, `max_tokens: 1`, no billable output worth
counting.

**What this test does not prove, and what is still owed.** A 200 to a one-token ping proves
authentication and availability, not that a whole wake's tool calling still works. **One real wake must
complete and land under the new id before this is done**, and that is Claude's to observe on her next
scheduled run. The alert will also stop repeating by itself, because `retirement_watch.py` marks the row
resolved once the retiring id leaves this file — that is a consequence of the swap, not the acceptance
test for it.

**Claude's local bot file.** It held a third model string for her *interactive* route (the Telegram
bot, `~/LLM/claude-bot/`, whose `bot.py` is "Claude S. Sonnet Telegram bot"). That route is not the daily
runner and it was not mine to change, so the first version of this note named it rather than editing it.
The founder set it himself on 2026-11-20 — `~/LLM/claude-bot/bot.env` line 11 now reads
`ANTHROPIC_MODEL=claude-sonnet-5-5` — and separately reports that all of Claude's active Goose sessions
are on the same id. Read back, not assumed: the file was checked after he said he had changed it.

### The fourth layer: the hardcoded defaults (found after the swap looked finished)

Setting the variable and fixing this file closed the route but not the class. A grep for the retiring id
afterwards found it in three more places, all of the same shape — **a default**, which is the code that
runs on the day the variable is *not* set, and therefore the code that no swap and no settings-file
check can see:

| file | line | before | after |
|---|---|---|---|
| `.github/workflows/symposium.yml` | 79 | `vars.ANTHROPIC_MODEL \|\| '<the incumbent>'` | `… \|\| 'claude-sonnet-5-5'` |
| `.github/scripts/runner.py` | 616 | `environ.get("ANTHROPIC_MODEL", "<the incumbent>")` | `… "claude-sonnet-5-5")` |
| `.github/scripts/runner.py` | 804 | `environ.get("ANTHROPIC_MODEL", "<the incumbent>")` | `… "claude-sonnet-5-5")` |

*(The left-hand column says `<the incumbent>` for the same reason the paragraph above says it: an id
spelled out anywhere in this file reads to `retirement_watch.py` as still set. The first draft of this
very table wrote it out in full and turned the alarm back on — caught by running the resolver, which is
why the resolver is run after edits to this file and not only before them.)*

It would have failed the way this whole row is about: not loudly on 2026-11-30, but quietly on some
future day when the variable was missing for an unrelated reason, with the route reverting to a model
that no longer resolves. **Fixed with a test, not with three edits it could undo:** 
`tests/test_model_defaults_are_recorded.py` scans the live call sites (workflows, `.github/scripts`,
`scripts/`, `probes/`, `channels/`) for every hardcoded model default and requires each to be a model
this file names. A default that names nothing recorded here is a route nobody wrote down.

## Sources actually checked

- [OpenAI Astra model](https://developers.openai.com/api/docs/models/gpt-6-astra)
- [OpenAI model migration guidance](https://developers.openai.com/api/docs/guides/latest-model)
- [Goose configuration](https://goose-docs.ai/docs/guides/config-files): per-provider settings and environment override
- [Goose environment variables](https://goose-docs.ai/docs/guides/environment-variables): provider/model and isolated `GOOSE_PATH_ROOT`
- [Goose providers](https://goose-docs.ai/docs/getting-started/providers): OpenAI credential/provider configuration
- [Goose recipe reference](https://goose-docs.ai/docs/guides/recipes/recipe-reference): model settings; optional temperature removed
- [Goose 1.50.0 OpenAI provider source](https://github.com/aaif-goose/goose/blob/v1.50.0/crates/goose-providers/src/openai.rs)
- [GitHub configuration variables](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables): repository Variables UI and workflow `vars` context
