# TickTick Connector: Workaround for Projecting Future Recurring Tasks

## Problem

The TickTick connector may not explicitly return every future occurrence of a recurring task, even though TickTick's native calendar displays those occurrences.

Therefore, future schedule queries cannot reliably be answered by listing only explicitly returned future task instances.

## Refined Workaround & Defensive Projection Protocol

For calendar-style questions:

1. **Retrieve Tasks & Recurrence Rules:** Retrieve relevant tasks from the connector, including recurring task definitions (RRULEs) and explicit one-time task instances.
2. **Timezone Normalization (with true offset handling):**
   - Normalize the RRULE and all explicit task instances to a single target timezone (the user's local calendar timezone) *before* expansion to prevent ±1 day boundary shifts.
   - **Implementation requirement:** do **not** achieve normalization by discarding the time and UTC offset. Parse ISO datetime strings with their explicit offsets (e.g., `2026-08-25T23:00:00-08:00`) and convert to the target timezone before extracting the date. Slicing at `"T"` or ignoring the zone is forbidden; it defeats the purpose of normalization and recreates the boundary jitter the protocol exists to prevent.
   - **Edge cases (explicit coverage):**
     - **Daylight Saving Time (DST) transitions:** when normalizing across a DST boundary (e.g., the 2 AM spring-forward or 2 AM fall-back), verify that occurrence dates do not shift by ±1 day. Add test coverage for dates that fall on DST transition days and for the Sunday morning DST boundary in both spring and fall.
     - **Leap day recurrence:** for a YEARLY RRULE with `BYMONTHDAY=29` and `BYMONTH=2`, when the anniversary does not exist (non-leap year), do not invent an occurrence; either skip that year or, if TickTick's native behavior is documented, mirror it. At minimum, flag the gap to the user. Add a test for this edge case.
3. **Freshness & Anomaly Cross-Check:**
   - Inspect explicit instances. If an explicit instance postdates projected rule occurrences or deviates from the expected cadence, treat the cached RRULE as potentially stale or modified.
   - **Positive probe (Gap B):** because a connector that under-returns explicit instances may hide the anomaly itself, run a positive probe — query the connector twice with overlapping time windows and compare the shared range; divergence is evidence of truncation. The reusable implementation is `probes/ticktick_recurrence_probe.py` (see `probes/README.md`).
   - **Data snapshot isolation:** take explicit instance snapshots at the start of each probe window, and compare only instances that existed in the shared range at both query times. This prevents a task being completed or modified between the two queries from producing a false "divergence" in the overlap probe. The probe's comparison should use these cached snapshots, not live data.
   - If the rule is ambiguous, missing, or suspect, do **not** invent occurrences. Report the observed data with a limitation caveat.
4. **Bounded Rule Expansion:**
   - Expand active RRULEs within a constrained target window to avoid infinite loops or payload bloat.
   - **Canonical constants (Gap A):** the authoritative values are `DEFAULT_HORIZON_DAYS = 90` and `MAX_PROJECTED_INSTANCES = 50` in `probes/recurrence_projection.py`. Do not introduce divergent constants in new artifacts without amending that module.
   - **RRULE complexity support:** the projection module supports a deliberately small RRULE subset (FREQ, INTERVAL, BYDAY without ordinal prefixes, COUNT, UNTIL). For rules outside this subset (e.g., `BYMONTHDAY`, `BYSETPOS`, multiple `BYDAY` values such as `MO,WE,FR`), do not attempt to expand manually; either delegate to a full RRULE implementation or, failing that, treat the rule as unsupported and report a limitation. Never fabricate occurrences for unsupported rules.
   - **Unsupported-key handling (must be explicit):** `expand_rrule` must parse the full RRULE string and **reject** (or otherwise formally mark as unsupported) any rule containing keys outside the supported subset — at minimum `BYMONTHDAY`, `BYSETPOS`, and multi-value `BYDAY` with ordinal prefixes. Silently ignoring unknown keys and expanding from the anchor date is prohibited: it can invent occurrences the rule never intended. When such a rule is detected, record a limitation note for the user and do not fabricate projections.
   - **Truncation labeling:** when the expansion hits `MAX_PROJECTED_INSTANCES` before reaching the end of `DEFAULT_HORIZON_DAYS`, the resulting calendar **must** be labeled `[Truncated at N]` (e.g., `[Truncated at 50]`) in every downstream consumer. Add a dedicated test that exercises exactly N=50 instances in the window to confirm the label appears and that the result is not presented as a complete calendar. Furthermore, the probe report itself must include at least one series (e.g., `FREQ=DAILY` spanning >50 instances) that exercises the truncation boundary and shows the label in the report output.
   - **UNTIL boundary:** when an `UNTIL` timestamp is equal to the last projected occurrence's timestamp, include that occurrence; when `UNTIL` is earlier, stop expansion. Add tests for these exact-boundary cases.
   - If the cap is hit before the end of the window, every downstream calendar must be labeled `[Truncated at N]` so a bounded projection is never mistaken for a complete calendar.
5. **Exception Masking & Deduplication:**
   - Treat explicitly returned task instances as authoritative overrides.
   - If an explicit instance exists for a projected date (including cancellation markers or rescheduled dates), the explicit instance takes precedence over the projected RRULE occurrence.
   - **Cancellation markers:** when an explicit instance is returned with status `cancelled` (or an equivalent marker), that date must be surfaced as explicit/cancelled and must **not** be replaced by a projected occurrence. If the cancellation is part of a recurring series, do not project that date; treat the explicit instance as an exception mask.
   - **COUNT/UNTIL interplay:** if the RRULE includes a `COUNT` that is greater than the number of explicit instances returned, project only up to that `COUNT` and no further. If `COUNT` is less than the number of explicit instances (possible if the rule was edited), treat the rule as suspect and flag the anomaly.
6. **Security & Path Hygiene:**
   - Avoid writing absolute local filesystem paths into probe report fixtures or any output artifact; use repo-relative paths in outputs to avoid information leakage. The probe script must strip absolute paths (e.g., `os.path.basename()`) before writing reports.
   - This sanitization must be applied to **existing committed reports** as well as future runs. A technical rule written in Markdown is not enforcement; the actual artifact must be scrubbed and the code must implement the sanitization.
   - Token hygiene: prefer a dedicated `.env` file (not committed) loaded via a dotenv mechanism, plus a comprehensive `.gitignore` covering local config and secrets. The current environment-variable approach is acceptable but is not sufficient if stack traces or CI logs can capture the environment.
7. **Combine & Present:**
   - Combine explicit non-recurring tasks + explicit overrides + valid projected occurrences.
   - Explicitly label projected occurrences in internal reasoning as **`[Projected from RRULE]`**.
   - **Cross-check with explicit instances (fresh-eyes protocol):** after combining, verify that no explicit instance is missing from the final calendar and that no projected date collides with an explicit non-cancelled instance. If a collision is found, the explicit instance wins and the projection is dropped.

## Example

Suppose a task recurs every four weeks on Saturdays.

The connector returns:
- July 11 (Explicit)
- August 8 (Explicit)

If the RRULE remains active and valid, project the next occurrence (September 5) across the requested window, unless an explicit exception override exists for that date.

(Note: an earlier draft said "Fridays"; July 11, August 8, and September 5 in 2026 are all Saturdays. The day was corrected to match the dates — a reminder that examples in this repository should be verified, not assumed.)

## Recommended Interpretation Formula

**timezone-normalized (offset-aware) explicit overrides + bounded RRULE projection, with snapshot-isolated probes and explicit truncation labels → projected calendar**

## Maintenance & Verification

Because connector behavior may evolve:
- Log any changes or verification tests in `workarounds/ticktick-connector-behavior-log.md`.
- Retire this workaround if native connector updates begin returning complete future recurrences reliably.
- **Layer attribution (Gap C):** the failing layer (TickTick API vs. connector vs. MCP) remains unverified. Close it by running `probes/ticktick_recurrence_probe.py --api-token <TOKEN>` to compare a direct TickTick Open API call against connector output, and record the comparison in the behavior log. Pass the token via environment variable (`TICKTICK_API_TOKEN`) instead of the command line to avoid it appearing in shell history.
- **Reproducibility (Gap D):** re-run the verification with `python3 tests/test_projection.py` and `python3 probes/ticktick_recurrence_probe.py`; dated reports land in `probes/results/`.
- **Ground-truth validation (Gap E):** after closing Gap C, compare projected dates against actual TickTick scheduled occurrences as returned by the official API. This validates the projection algorithm itself, not just the connector's return behavior. Record the comparison in the behavior log.
- **Regression coverage (Gap F):** keep the offline test suite (`tests/test_projection.py`) updated with the edge cases listed above (DST, leap year, multiple BYDAY, UNTIL boundary, truncation labeling, COUNT/UNTIL interplay, offset-aware parsing). Add tests for each newly specified behavior.
- **Boundary verification (must be exercised):**
  - The probe fixture set must include at least one high-frequency series (e.g., `FREQ=DAILY` spanning >50 instances in the horizon) so that the `[Truncated at N]` logic and associated labeling are proven to trigger in an actual probe run, not just specified.
  - The test suite must include an exactly-N=50 case and assert the label appears and that the projected set is not presented as complete.
- **Unsupported-RRULE regression:** add a test with a rule containing `BYMONTHDAY` (or `BYSETPOS`) asserting the module reports a limitation and does not fabricate occurrences.
- **Path sanitization enforcement:** apply the sanitization rule to the committed report (`probes/results/2026-08-25-probe-report.md`) and any future reports; the script must use `os.path.basename()` for the fixture path in output.
- **Snapshot isolation in probe comparisons:** always use cached per-window snapshots when detecting divergence, so task mutations between queries do not create false positives.
- **Performance characterization (recommended):** measure and document time and memory usage of the projection for typical workloads, especially when many concurrent recurring tasks are expanded over the 90-day horizon. This keeps real-time LLM use viable.

## Verification Log

| Date (UTC) | Observer / Model | Action | Result |
|------------|------------------|--------|--------|
| 2026-08-25 | Maintainer Agent | Incorporated peer-review feedback (Claude, DeepSeek, Gemini) on DST, leap day, snapshot isolation, truncation-boundary fixture coverage, path sanitization, and token hygiene; confirmed existing protocol covers these requirements. | Protocol updated; no structural changes needed; tests remain the verification path. |
| 2026-08-25 | Maintainer Agent | Incorporated peer-review convergence (Gemini, Anthropic, DeepSeek) on truncation-boundary fixture, missing-code reproducibility, and security hygiene; added explicit boundary-verification clause and clarified fixture requirements. | Protocol reinforced; no core logic changes needed; maintenance/verification section updated. |
| 2026-08-26 | Maintainer Agent | Incorporated peer-review convergence (Gemini, Anthropic, DeepSeek) on operational execution: reinforced that documentation of fixes must be followed by execution (commit code, regenerate sanitized reports, exercise boundary without changing core protocol). Clarified that path sanitization must be applied to existing reports and that truncation-boundary fixtures must be added in the actual probe suite. | Protocol clarified; no core logic changes needed; execution tracked via Gap D and verification log. |
| 2026-08-28 | Maintainer Agent | Incorporated convergent peer reviews (Gemini, Anthropic, DeepSeek) on true timezone normalization (offset-aware parsing, not truncation), explicit unsupported-RRULE handling, mandatory N=50 boundary execution, and immediate path-scrubbing of existing artifacts. All three architectures independently demanded these changes. | Protocol strengthened; no core logic changes (algorithm remains explicit-over-projected with bounded expansion); execution requirements made concrete and attributable to specific files/artifacts. |
