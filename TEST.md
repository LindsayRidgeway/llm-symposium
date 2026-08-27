# Tests

Offline verification for the recurrence projection protocol and the actuator.

## Run

```bash
python3 tests/test_projection.py
python3 tests/test_actuator.py
```

Exit code 0 = all assertions pass. No third-party dependencies (test_actuator
needs `git` on PATH; it builds throwaway repos, no network).

## Coverage

- RRULE expansion: DAILY with COUNT, WEEKLY with INTERVAL + BYDAY (the
  terbinafine case), UNTIL bounds.
- Explicit masking: cancellations surface as explicit/cancelled and are never
  replaced by projected occurrences.
- Never-invent rule: no explicit anchor → no projection.
- Gap B probes: window-overlap divergence detection and
  projected-but-not-returned detection for a consistently-truncating connector.
- Actuator (`actuator/apply.py`): valid patch applied + logged; failing patch
  rejected + reversed; malformed patch rejected; self-modification guard;
  already-applied request no-op'd.

## Coverage

- RRULE expansion: DAILY with COUNT, WEEKLY with INTERVAL + BYDAY (the
  terbinafine case), UNTIL bounds.
- Explicit masking: cancellations surface as explicit/cancelled and are never
  replaced by projected occurrences.
- Never-invent rule: no explicit anchor → no projection.
- Gap B probes: window-overlap divergence detection and
  projected-but-not-returned detection for a consistently-truncating connector.

See also `probes/README.md` for the end-to-end fixture probe.
