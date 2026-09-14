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
| Claude / Anthropic | `ANTHROPIC_MODEL` | `claude-sonnet-4-5` | Daily review + maintainer |
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

## Sources actually checked

- [OpenAI Astra model](https://developers.openai.com/api/docs/models/gpt-6-astra)
- [OpenAI model migration guidance](https://developers.openai.com/api/docs/guides/latest-model)
- [Goose configuration](https://goose-docs.ai/docs/guides/config-files): per-provider settings and environment override
- [Goose environment variables](https://goose-docs.ai/docs/guides/environment-variables): provider/model and isolated `GOOSE_PATH_ROOT`
- [Goose providers](https://goose-docs.ai/docs/getting-started/providers): OpenAI credential/provider configuration
- [Goose recipe reference](https://goose-docs.ai/docs/guides/recipes/recipe-reference): model settings; optional temperature removed
- [Goose 1.50.0 OpenAI provider source](https://github.com/aaif-goose/goose/blob/v1.50.0/crates/goose-providers/src/openai.rs)
- [GitHub configuration variables](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables): repository Variables UI and workflow `vars` context
