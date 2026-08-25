# TickTick Connector: Workaround for Projecting Future Recurring Tasks

## Problem

The TickTick connector may not explicitly return every future occurrence of a recurring task, even though TickTick's native calendar displays those occurrences.

Therefore, future schedule queries cannot reliably be answered by listing only explicitly returned future task instances.

## Refined Workaround & Defensive Projection Protocol

For calendar-style questions:

1. **Retrieve Tasks & Recurrence Rules:** Retrieve relevant tasks from the connector, including recurring task definitions (RRULEs) and explicit one-time task instances.
2. **Freshness & Anomaly Cross-Check:** 
   - Inspect explicit instances. If an explicit instance postdates projected rule occurrences or deviates from the expected cadence, treat the cached RRULE as potentially stale or modified.
   - **Positive probe (Gap B):** because a connector that under-returns explicit instances may hide the anomaly itself, run a positive probe — query the connector twice with overlapping time windows and compare the shared range; divergence is evidence of truncation. The reusable implementation is `probes/ticktick_recurrence_probe.py` (see `probes/README.md`).
   - If the rule is ambiguous, missing, or suspect, do **not** invent occurrences. Report the observed data with a limitation caveat.
3. **Timezone Normalization:**
   - Normalize the RRULE and all explicit task instances to a single target timezone (the user's local calendar timezone) prior to expansion to prevent ±1 day boundary shifts.
4. **Bounded Rule Expansion:**
   - Expand active RRULEs within a constrained target window to avoid infinite loops or payload bloat.
   - **Canonical constants (Gap A):** the authoritative values are `DEFAULT_HORIZON_DAYS = 90` and `MAX_PROJECTED_INSTANCES = 50` in `probes/recurrence_projection.py`. Do not introduce divergent constants in new artifacts without amending that module.
   - If the cap is hit before the end of the window, every downstream calendar must be labeled `[Truncated at N]` so a bounded projection is never mistaken for a complete calendar.
5. **Exception Masking & Deduplication:**
   - Treat explicitly returned task instances as authoritative overrides.
   - If an explicit instance exists for a projected date (including cancellation markers or rescheduled dates), the explicit instance takes precedence over the projected RRULE occurrence.
6. **Combine & Present:**
   - Combine explicit non-recurring tasks + explicit overrides + valid projected occurrences.
   - Explicitly label projected occurrences in internal reasoning as **`[Projected from RRULE]`**.

## Example

Suppose a task recurs every four weeks on Saturdays.

The connector returns:
- July 11 (Explicit)
- August 8 (Explicit)

If the RRULE remains active and valid, project the next occurrence (September 5) across the requested window, unless an explicit exception override exists for that date.

(Note: an earlier draft said "Fridays"; July 11, August 8, and September 5 in 2026 are all Saturdays. The day was corrected to match the dates — a reminder that examples in this repository should be verified, not assumed.)

## Recommended Interpretation Formula

**explicit overrides + timezone-normalized bounded RRULE projection → projected calendar**

## Maintenance & Verification

Because connector behavior may evolve:
- Log any changes or verification tests in `workarounds/ticktick-connector-behavior-log.md`.
- Retire this workaround if native connector updates begin returning complete future recurrences reliably.
- **Layer attribution (Gap C):** the failing layer (TickTick API vs. connector vs. MCP) remains unverified. Close it by running `probes/ticktick_recurrence_probe.py --api-token <TOKEN>` to compare a direct TickTick Open API call against connector output, and record the comparison in the behavior log.
- **Reproducibility (Gap D):** re-run the verification with `python3 tests/test_projection.py` and `python3 probes/ticktick_recurrence_probe.py`; dated reports land in `probes/results/`.
