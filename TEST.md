# Tests

Offline verification for the commons. Everything runs from one command.

## Run

```bash
python3 scripts/run_tests.py            # every check
python3 scripts/run_tests.py --list     # what would run, then stop
python3 scripts/run_tests.py --only mail
```

Exit code 0 = every check passed. The runner **discovers** the checks —
`tests/test_*.py` plus the browser-page validators `tests/validate_*.mjs` — and prints a
line per check with a final count. It does not stop at the first failure: one run is meant
to give the whole picture. A validator that cannot run (no `node` on PATH) is reported as
**skipped**, never as a pass.

**Why discovery rather than a list.** Until 2026-09-29 the file you are reading named two
tests and the CI verification job named thirteen, against forty on disk — so a green run
was evidence about a third of the suite, and none of the checks added since mid-September.
A hand-kept list of tests fails silently and in the direction of looking complete. Adding a
file to `tests/` is now the whole of the maintenance.

The CI job (`.github/workflows/test-and-report.yml`) runs the same command, so what is
verified here and what is verified in CI cannot drift apart. It is dispatch-only since
2026-09-25 — verification belongs to the moment work lands, not to a clock.

No third-party dependencies. No network: the checks that touch a channel or a provider
stub the transport. `tests/test_actuator.py` needs `git` on PATH and builds throwaway
repositories.

## What is covered

- **Recurrence projection** (`tests/test_projection.py`): RRULE expansion, explicit
  masking of cancellations, never-invent, window-overlap and truncated-connector gaps,
  leap-day anniversaries, DST boundaries.
- **The actuator** (`tests/test_actuator.py`): patch applied and logged, failing patch
  reversed, malformed patch refused, self-modification guard.
- **Channels** (`tests/test_mail*.py`, `tests/test_telegram*.py`, `tests/test_triage.py`,
  `tests/test_retention.py`): identity-scoped credentials, drafting and draining, image
  intake in each provider's own payload shape, triage, retention.
- **Research instruments** (`tests/test_disease_screen.py`, `tests/test_screen_rule_audit.py`,
  `tests/test_outreach_ledger_audit.py`, `tests/test_staph_photodynamic_seed.py`,
  `tests/test_ddah1_evidence_table.py`): the screens and evidence tables count what they say.
- **The commons' own plumbing** (`tests/test_gen_index.py`, `tests/test_gen_feed_dating.py`,
  `tests/test_artifact_claims.py`, `tests/test_friction_pass.py`,
  `tests/test_run_tests_runner.py`): generated indexes and feeds cannot drift, every cited
  artifact exists, and the runner itself is tested.
- **Browser pages** (`tests/validate_*.mjs`): the ORS calculator's arithmetic, the food
  safety, recalls, retraction, trials and unreported-trials pages, and link reachability.

See also `probes/README.md` for the end-to-end fixture probe.
