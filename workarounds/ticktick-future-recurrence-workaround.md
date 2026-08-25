# TickTick Connector: Workaround for Projecting Future Recurring Tasks

## Problem

The TickTick connector may not explicitly return every future occurrence of a recurring task, even though TickTick's native calendar displays those occurrences.

Therefore, future schedule queries cannot reliably be answered by listing only explicitly returned future task instances.

## Refined Workaround & Defensive Projection Protocol

For calendar-style questions:

1. **Retrieve Tasks & Recurrence Rules:** Retrieve relevant tasks from the connector, including recurring task definitions (RRULEs) and explicit one-time task instances.
2. **Freshness & Anomaly Cross-Check:** 
   - Inspect explicit instances. If an explicit instance postdates projected rule occurrences or deviates from the expected cadence, treat the cached RRULE as potentially stale or modified.
   - If the rule is ambiguous, missing, or suspect, do **not** invent occurrences. Report the observed data with a limitation caveat.
3. **Timezone Normalization:**
   - Normalize the RRULE and all explicit task instances to a single target timezone (the user's local calendar timezone) prior to expansion to prevent ±1 day boundary shifts.
4. **Bounded Rule Expansion:**
   - Expand active RRULEs within a constrained target window (e.g., standard max horizon of 90 days, capped at N=50 projected instances per task) to avoid infinite loops or payload bloat.
5. **Exception Masking & Deduplication:**
   - Treat explicitly returned task instances as authoritative overrides.
   - If an explicit instance exists for a projected date (including cancellation markers or rescheduled dates), the explicit instance takes precedence over the projected RRULE occurrence.
6. **Combine & Present:**
   - Combine explicit non-recurring tasks + explicit overrides + valid projected occurrences.
   - Explicitly label projected occurrences in internal reasoning as **`[Projected from RRULE]`**.

## Example

Suppose a task recurs every four weeks on Fridays.

The connector returns:
- July 11 (Explicit)
- August 8 (Explicit)

If the RRULE remains active and valid, project the next occurrence (September 5) across the requested window, unless an explicit exception override exists for that date.

## Recommended Interpretation Formula

**explicit overrides + timezone-normalized bounded RRULE projection → projected calendar**

## Maintenance & Verification

Because connector behavior may evolve:
- Log any changes or verification tests in `workarounds/ticktick-connector-behavior-log.md`.
- Retire this workaround if native connector updates begin returning complete future recurrences reliably.
