# TickTick Connector Behavior Log

This document serves as an empirical tracking log for observed behavior changes, API updates, or connector quirks related to the TickTick integration across time and model interactions.

| Date (UTC) | Observer / Model | Connector Behavior / Findings | Operational Impact | Status |
|------------|------------------|------------------------------|--------------------|--------|
| 2026-08-15 | Empirical Discovery | Connector fails to return future occurrences of recurring tasks (e.g., terbinafine, Chumash classes). | High: LLMs falsely report missing tasks unless recurrence rules are projected. | Active Workaround Required |
| 2026-08-24 | Claude-4.5-Symposium | Peer review identified edge cases in projection algorithm (exceptions, timezones, infinite expansions, stale rules). | Refined workaround specification. | Workaround Updated |
| 2026-08-25 | Gemini-Symposium | Validated Claude's review, updated workaround specification with defensive projection guardrails, and initialized log. | Established versioned baseline for cross-model recurrence handling. | Verified |
| 2026-08-25 | DeepSeek-Symposium (Desi) | Built and ran offline verification probe (`probes/`, `tests/`). Reproduced truncation evidence from fixtures; fixed "Fridays"→"Saturdays" error in workaround example; defined canonical bounds (90d / N=50). | Verification loop established; bounds reconciled; layer attribution still open (needs API token). | Probe + tests passing |
