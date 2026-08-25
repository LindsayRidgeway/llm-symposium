# Tests

Offline verification for the recurrence projection protocol.

## Run

```bash
python3 tests/test_projection.py
```

Exit code 0 = all assertions pass. No third-party dependencies.

## Coverage

- RRULE expansion: DAILY with COUNT, WEEKLY with INTERVAL + BYDAY (the
  terbinafine case), UNTIL bounds.
- Explicit masking: cancellations surface as explicit/cancelled and are never
  replaced by projected occurrences.
- Never-invent rule: no explicit anchor → no projection.
- Gap B probes: window-overlap divergence detection and
  projected-but-not-returned detection for a consistently-truncating connector.

See also `probes/README.md` for the end-to-end fixture probe.
