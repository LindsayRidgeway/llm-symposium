# Tarik durable cross-platform facts

Purpose: tiny, high-signal facts Tarik must know across Goose, Telegram, and email. This is not a general transcript.

- 2026-09-03 continuity test: Tarik-Goose chose the number **37** when Lindsay asked for a number between 1 and 100. If Lindsay asks Tarik-Telegram what number Tarik-Goose chose, answer **37**.

- 2026-10-16 — **Lindsay's standing authorization to Tarik**, given in the Codex chat: "Tarik, you have standing approval to take actions you judge best for the Symposium, consistent with my goals and preferences. I hope you will use REQUEST T-n only when something genuinely requires my involvement."
  Tarik's operating understanding: make decisions and perform work consistent with Lindsay's goals and preferences without repeated conversational permission; use REQUEST T-n only for issues that genuinely require Lindsay's involvement. Handle routine implementation and recoverable errors ourselves where possible. Mandatory app/service approvals and access controls still apply; those are operational limits, not additional conditions imposed by Lindsay.

- 2026-10-16 — **Wake division authorized by Lindsay:** Tarik-Codex owns general Symposium work and is to run six native wakes per day at New York clock slots 00/04/08/12/16/20. Tarik-Goose's only scheduled-wake work list is `channels/tarik-goose-handoff.json`: tasks Codex cannot currently perform and has evidence Goose can. See `channels/tarik-wake-protocol.md`. Codex keeps `to-do-lists/tarik.md`; Goose must not independently draw general work. The Mac's deterministic before-model gate still requires actual installation and verification. Lindsay will monitor actual spending.

- 2026-10-17T01:55:35Z — **REQUEST T-2 reserved in the Codex chat for the one-time local dispatcher bootstrap.** The request is one message to a Mac-local Tarik-Goose session to execute handoff `tg-20261016-001` using `channels/tarik-goose-bootstrap.md`. Code/tests are prepared; Codex cannot itself start a Mac-local session. This ID is reserved and must not be reused. This is a chat bootstrap request, not a Telegram-registered row; do not hand-add a register row or claim Telegram delivery. T-1 was the earlier completed chat credential bootstrap and also must not be reused.
