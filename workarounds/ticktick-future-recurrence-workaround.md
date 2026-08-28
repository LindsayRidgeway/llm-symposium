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
> Since updated (2026-08-27, second engineering pass via the actuator): Gap C
> is now wired end-to-end — the repository secret `TICKTICK_API_KEY` feeds the
> probe through `.github/workflows/test-and-report.yml` (`TICKTICK_API_TOKEN`),
> so the live TickTick API isolation check runs on every scheduled
> verification and the dated report records the result.
>
> Still open (unchanged by this pass): Gap E ground-truth validation (needs a
> confirmed-valid token and a comparison against actual scheduled
> occurrences), performance characterization.

## Problem

The TickTick connector may not explicitly return every future occurrence of a recurring task, even though TickTick's native calendar displays those occurrences.

Therefore, future schedule queries cannot reliably be answered by listing only explicitly returned future task instances.

## Refined Workaround & Defensive Projection Protocol

For calendar-style questions:

1. **Retrieve Tasks & Recurrence Rules:** Retrieve relevant tasks from the connector, including recurring task definitions (RRULEs) and explicit one-time task instances.

2. **Timezone Normalization (with true offset handling):**
   - Normalize the RRULE and all explicit task instances to a single target timezone (the user's local calendar timezone) *before* expansion to prevent ±1 day boundary shifts.
   - **Implementation requirement:** Parse ISO datetime strings with their explicit offsets and convert to the target timezone before extracting the date. The module `probes/recurrence_projection.py` **must** implement offset-aware parsing and must not truncate the offset. This was recommended by the DeepSeek review and the Gemini synthesis (2026-08-27).
   - **Edge cases (explicit coverage):**
     - **Daylight Saving Time (DST) transitions:** ensure occurrence dates do not shift by ±1 day when normalizing across a DST boundary.
     - **Leap day recurrence:** for a YEARLY RRULE with `BYMONTHDAY=29` and `BYMONTH=2`, flag non-leap years rather than invent occurrences.

3. **Freshness & Anomaly Cross-Check:**
   - Inspect explicit instances. If an explicit instance postdates projected rule occurrences or deviates from the expected cadence, treat the cached RRULE as potentially stale or modified.
   - **Positive probe (Gap B):** run a positive probe by querying the connector twice with overlapping time windows and comparing the shared range for divergence.
   - If the rule is ambiguous, missing, or suspect, do **not** invent occurrences. Report the observed data with a limitation caveat.

4. **Bounded Rule Expansion:**
   - Expand active RRULEs within a constrained target window to avoid infinite loops or payload bloat.
   - **Canonical constants (Gap A):** authorize values `DEFAULT_HORIZON_DAYS = 90` and `MAX_PROJECTED_INSTANCES = 50`. Do not introduce divergent constants without amending the canonical source.
   - **Unsupported-key handling (must be explicit and enforced):** use `validate_rrule` to reject unsupported keys and values explicitly.
   - **Truncation labeling:** label results as truncated if the hard cap is hit before the window ends.

5. **Exception Masking & Deduplication:**
   - Treat explicitly returned task instances as authoritative over projections.
   - **Cancellation markers:** preserve explicit cancellations as authoritative.

6. **Security & Path Hygiene:**
   - Avoid writing absolute local filesystem paths into output artifacts.
   - Prefer environment-variable token injection over CLI arguments to avoid leaks.

7. **Combine & Present:**
   - Combine explicit non-recurring tasks, explicit overrides, and valid projected occurrences.
   - Explicitly label projected occurrences as `[Projected from RRULE]`.

## Example

Suppose a task recurs every four weeks on Saturdays. The connector returns earlier occurrences but not the latest one due to under-return behavior.

(Note: an earlier draft stated "Fridays"; all dates in 2026 fall on Saturdays. This was corrected to match the calendar.)

## Recommended Interpretation Formula

**timezone-normalized (offset-aware) explicit overrides + bounded RRULE projection, with snapshot-isolated probes, explicit truncation labels, and code-enforced unsupported-RRULE rejection → projected calendar**

## Maintenance & Verification

- Log any changes or verification tests in `workarounds/ticktick-connector-behavior-log.md`.
- Retire this workaround if native connector updates return complete future recurrences reliably.
- Layer attribution (Gap C) is now verified; see behavior log for details.
- Ground-truth validation (Gap E) pending resolution of the task-list query.
- Schedule performance characterization.
- CI workflow runs `tests/test_projection.py` and `probes/ticktick_recurrence_probe.py` on every push, failing when tests fail.