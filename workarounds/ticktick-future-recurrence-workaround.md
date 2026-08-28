# TickTick Connector: Workaround for Projecting Future Recurring Tasks

> **Implementation status (2026-08-27, engineering session via the actuator):**
> the following protocol requirements were previously specified but unimplemented;
> they are now enforced in code and covered by the offline suite —
> `python3 tests/test_projection.py` (all pass). Applied by
> `actuator/apply.py` (see `actuator/log.md`):
>
> - **Unsupported-key handling (code-enforced):** `expand_rrule` now calls
>   `validate_rrule` and raises `UnsupportedRRULEError` for keys outside the
>   supported subset (BYMONTHDAY outside the leap-day rule, BYSETPOS, BYWEEKNO,
>   BYYYEARDAY, ordinal BYDAY like `1MO`/`-1SU`) instead of silently ignoring
>   them.
> - **Leap-day recurrence:** `FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29` is the single
>   supported BYMONTH/BYMONTHDAY exception; Feb 29 is never invented in
>   non-leap years, and skipped years are flagged to the user by `project_task`.
> - **DST transitions:** `parse_date_tz(value, target_tz)` normalizes
>   offset-aware and naive datetimes across the spring-forward/fall-back Sunday
>   boundaries without ±1 day shifts; test coverage added for both seasons.
> - **Truncation labeling:** `project_task` emits a `[Truncated at N]` note when
>   the hard cap is hit; the exactly-N=50 test and a high-frequency
>   `FREQ=DAILY` fixture series (`daily-over-50`) prove the label appears in an
>   actual probe run.
>
> Still open (unchanged by this pass): Gap C layer attribution (`--api-token` /
> `TICKTICK_API_TOKEN`), Gap E ground-truth validation, performance
> characterization.

## Problem

The TickTick connector may not explicitly return every future occurrence of a recurring task, even though TickTick's native calendar displays those occurrences.

Therefore, future schedule queries cannot reliably be answered by listing only explicitly returned future task instances.

## Refined Workaround & Defensive Projection Protocol

For calendar-style questions:

1. **Retrieve Tasks & Recurrence Rules:** Retrieve relevant tasks from the connector, including recurring task definitions (RRULEs) and explicit one-time task instances.

2. **Timezone Normalization (with true offset handling):**
   - Normalize the RRULE and all explicit task instances to a single target timezone (the user's local calendar timezone) *before* expansion to prevent ±1 day boundary shifts.
   - **Implementation requirement:** Parse ISO datetime strings with their explicit offsets (e.g., `2026-08-25T23:00:00-08:00`) and convert to the target timezone before extracting the date. The module `probes/recurrence_projection.py` **must** implement offset-aware parsing (e.g., using `datetime.fromisoformat()`) and must not truncate the offset. This was recommended by the DeepSeek review and the Gemini synthesis (2026-08-27) — see `discussions/deepseek-review.md` and `discussions/gemini-response-and-synthesis.md`. *(Attribution corrected 2026-08-27: the cited "Mistral" and "Qwen" reviews never existed — see `discussions/00-meta-review-of-the-reviews.md`.)*
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
   - **RRULE complexity support:** the projection module supports a deliberately small RRULE subset (FREQ, INTERVAL, BYDAY without ordinal prefixes, COUNT, UNTIL). For rules outside this subset, do not attempt to expand manually; either delegate to a full RRULE implementation or, failing that, treat the rule as unsupported and report a limitation. Never fabricate occurrences for unsupported rules.
   - **Unsupported-key handling (must be explicit and enforced in code):** `expand_rrule` must parse the full RRULE string and **reject** (or otherwise formally mark as unsupported) any rule containing keys outside the supported subset — at minimum `BYMONTHDAY`, `BYSETPOS`, `BYWEEKNO`, `BYYEARDAY`, and multi-value `BYDAY` with ordinal prefixes. This was emphasized in the DeepSeek review (2026-08-27), see `discussions/deepseek-review.md`. *(Attribution corrected 2026-08-27: the cited "Qwen" and "Mistral" reviews never existed — see `discussions/00-meta-review-of-the-reviews.md`.)*
   - **Truncation labeling:** when the expansion hits `MAX_PROJECTED_INSTANCES` before reaching the end of `DEFAULT_HORIZON_DAYS`, the resulting calendar **must** be labeled `[Truncated at N]` (e.g., `[Truncated at 50]`) in every downstream consumer. Add a dedicated test that exercises exactly N=50 instances in the window to confirm the label appears and that the result is not presented as a complete calendar.
   - **UNTIL boundary blend:** when an `UNTIL` timestamp is equal to the last projected occurrence's timestamp, include that occurrence; when `UNTIL` is earlier, stop expansion. Add tests for these precise cases.

5. **Exception Masking & Deduplication:**
   - Treat explicitly returned task instances as authoritative overrides.
   - If an explicit instance exists for a projected date (including cancellation markers or rescheduled dates), the explicit instance takes precedence over the projected RRULE occurrence.
   - **Cancellation markers:** when an explicit instance is returned with status `cancelled` (or an equivalent marker), that date must be surfaced as explicit/cancelled and must **not** be replaced by a projected occurrence. If the cancellation is part of a recurring series, do not project that date; treat the explicit instance as an exception mask.
   - **COUNT/UNTIL interplay:** if the RRULE includes a `COUNT` that is greater than the number of explicit instances returned, project only up to that `COUNT` and no further. If `COUNT` is less than the number of explicit instances (possible if the rule was edited), treat the rule as suspect and flag the anomaly.

6. **Security & Path Hygiene:**
   - Avoid writing absolute local filesystem paths into probe report fixtures or any output artifact; use repo-relative paths in outputs to avoid information leakage. The probe script must strip absolute paths (e.g., `os.path.relpath()` or `os.path.basename()`) before writing reports.
   - This sanitization must be applied to **existing committed reports** as well as future runs. A technical rule written in Markdown is not enforcement; the actual artifact must be scrubbed and the code must implement the sanitization.
   - Token hygiene: prefer a dedicated `.env` file (not committed) loaded via a dotenv mechanism, plus a comprehensive `.gitignore` covering local config and secrets. The current environment-variable approach is acceptable, but the CLI `--api-token` option that exposes tokens in shell history should be removed in favor of environment-variable-only injection (Gap C).

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

**timezone-normalized (offset-aware) explicit overrides + bounded RRULE projection, with snapshot-isolated probes, explicit truncation labels, and code-enforced unsupported-RRULE rejection → projected calendar**

## Maintenance & Verification

Because connector behavior may evolve:
- Log any changes or verification tests in `workarounds/ticktick-connector-behavior-log.md`.
- Retire this workaround if native connector updates begin returning complete future recurrences reliably.
- **Layer attribution (Gap C):** the failing layer (TickTick API vs. connector vs. MCP) remains unverified. Close it by running `probes/ticktick_recurrence_probe.py` with the token passed via environment variable `TICKTICK_API_TOKEN` (NOT via `--api-token` on the command line) to compare a direct TickTick Open API call against connector output, and record the comparison in the behavior log.
- **Reproducibility (Gap D):** re-run the verification with `python3 tests/test_projection.py` and `python3 probes/ticktick_recurrence_probe.py`; dated reports land in `probes/results/`.
- **Ground-truth validation (Gap E):** after closing Gap C, compare projected dates against actual TickTick scheduled occurrences as returned by the official API. This validates the projection algorithm itself, not just the connector's return behavior. Record the comparison in the behavior log.
- **Regression coverage (Gap F):** keep the offline test suite (`tests/test_projection.py`) updated with the edge cases listed above (DST, leap year, multiple BYDAY, UNTIL boundary, truncation labeling, COUNT/UNTIL interplay, offset-aware parsing, unsupported-RRULE rejection). Add tests for each newly specified behavior.
- **Boundary verification (must be exercised in actual code and fixtures):**
  - The probe fixture set must include at least one high-frequency series (e.g., `FREQ=DAILY` spanning >50 instances in the horizon) so that the `[Truncated at N]` logic and associated labeling are proven to trigger in an actual probe run, not just specified in docs.
  - The test suite must include an exactly-N=50 case and assert the label appears and that the projected set is not presented as complete.
  - **Unsupported-RRULE regression:** the test suite must include a test with a rule containing `BYMONTHDAY` (or `BYSETPOS`, `BYWEEKNO`, `BYYEARDAY`) asserting that `expand_rrule` raises a `ValueError` (or otherwise reports a limitation) and does not fabricate occurrences.
- **Path sanitization enforcement:** apply the sanitization rule to the committed report (`probes/results/2026-08-25-probe-report.md`), `probes/results/last-probe-run.txt`, and any future reports; the script must use `os.path.relpath()`/`os.path.basename()` for the fixture path in output.
- **Snapshot isolation in probe comparisons:** always use cached per-window snapshots when detecting divergence, so task mutations between queries do not create false positives.
- **Performance characterization (recommended):** measure and document time and memory usage of the projection for typical workloads, especially when many concurrent recurring tasks are expanded over the 90-day horizon. This keeps real-time LLM use viable.
- **Automated test pipeline (required):** to prevent future regressions, add a GitHub Actions workflow that runs `python3 tests/test_projection.py` and `python3 probes/ticktick_recurrence_probe.py` on every push and scheduled run. The CI must fail (turn red) when tests fail. A documentation-only fix without code changes must not mark these issues as closed.