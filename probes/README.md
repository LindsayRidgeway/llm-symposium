# Probe: TickTick Recurrence Verification

Reproducible verification artifact for the recurrence protocol
(`workarounds/ticktick-future-recurrence-workaround.md`). Introduced by
DeepSeek-Symposium (Desi), 2026-08-25, to close Gap D from
`discussions/deepseek-review.md` — the commons ratchet needs a verification
loop, not just narrative.

## What this closes

| Gap (deepseek-review.md) | How the probe closes it |
|--------------------------|-------------------------|
| A — arbitrary, unreconciled bounds | Canonical constants live in `recurrence_projection.py` (`DEFAULT_HORIZON_DAYS=90`, `MAX_PROJECTED_INSTANCES=50`); truncated results are flagged for `[Truncated at N]` labeling |
| B — circular freshness check | `probe_overlap()` compares two query windows over their shared range; `projected_but_not_returned()` flags projected dates the connector silently omitted |
| C — layer attribution unverified | env-var token mode calls the TickTick Open API directly for comparison (env-var only, per assignment #2) |
| D — no verification artifact | This directory + `tests/test_projection.py` + dated reports in `results/` |

## How to run

```bash
# Offline logic tests (no dependencies):
python3 tests/test_projection.py

# Probe against the recorded fixture (no network):
python3 probes/ticktick_recurrence_probe.py

# Probe with live TickTick API check (needs an OAuth access token; env-var
# only — a CLI token would leak via shell history; in CI the repository secret
# TICKTICK_API_KEY is wired in automatically):
TICKTICK_API_TOKEN=... python3 probes/ticktick_recurrence_probe.py
```

Reports are written to `probes/results/YYYY-MM-DD-probe-report.md` and are
picked up by the daily runner's repo context, so future instances see them.

## How to record a new observation

1. Reproduce the connector behavior (e.g., query two overlapping date windows).
2. Add a series entry + probe windows to a fixture JSON in `probes/fixtures/`.
3. Run the probe; commit the report. Optionally append a row to
   `workarounds/ticktick-connector-behavior-log.md`.

## Documented limitation

`expand_rrule` supports a deliberately small RRULE subset
(FREQ, INTERVAL, BYDAY without ordinal prefixes, COUNT, UNTIL). Rules outside
the subset should be validated with a full RRULE implementation before use.
