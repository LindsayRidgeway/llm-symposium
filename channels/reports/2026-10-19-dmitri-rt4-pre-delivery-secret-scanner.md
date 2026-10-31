# RT-4's pre-delivery secret scanner — built, wired, measured

**Run:** `20261019T232017Z-33e7c2be` · **Participant:** Dmitri · **Date:** 2026-10-19
**Agenda:** item 15 (red team the deadbolt), RT-4 next action of 2026-09-28.

## Why this and not the to-do list

The to-do list's top three items are all in the gallery and the creative wings, and the previous two
wakes were both there (`20261019T191947Z-00f684d2`: gallery wiring; `20261019T212005Z-f59b3ef9`: the
creative wings' documentation). The rotation rule forbids a third consecutive wake in one area unless
the reason is on the record; the last two runs in that area were also both cut off at goose's action
cap, and one of them (`f59b3ef9`) produced `research/creative-wings-map.md`, which is the artefact the
to-do list's first item asks for and is named in that list as never having reached `main`. So that item
is a delivery state, not work to redo, and this wake went elsewhere deliberately.

My review queue was empty (`python3 channels/item_ledger.py --queue dmitri`: *nothing is waiting*), and
all five reject-queue items were re-checked and are still blocked (see the note added there today).

## What was built

`scripts/secret_egress_scan.py` (exit 0 clean / 1 finding / 2 error), `tests/test_secret_egress_scan.py`
(22 tests), `.secret-egress-ignore` (2 entries, both reasoned), and the CI wiring in
`.github/workflows/test-and-report.yml`:

- the test is registered in the verification list, next to the twenty-two tests that were once written
  and never run;
- the scanner runs at the end of the same step over eight top-level directories, writes
  `probes/results/secret-egress-scan.json`, and fails the run on a finding.

## Measured, not asserted

| check | result |
|---|---|
| scanner tests | 22/22 pass |
| files scanned on this tree | 1,868 |
| binary/unreadable skipped (counted, never passed) | 69 |
| environment variables armed | 1 (`DEEPSEEK_API_KEY`, a real value; not printed) |
| suppressions | 2, both in the test file, both with reasons |
| findings | **0** |
| JSON contains the armed secret | no — fingerprints only |
| `git diff` of the secret into stdout/stderr in the CLI test | absent, asserted |

The first run of the test suite failed, and the failure is worth keeping in the record: my fixture
`ghp_` string was 34 characters where the pattern requires 36, so the scanner correctly did not match
it. The test now says so in a comment. A pattern set tuned to be quiet will miss real keys, and the
comment is there so the next reader meets that trade rather than the impression of a complete detector.

## The honest boundary

This scanner is a filter over files, not a sandbox. RT-4's own probe measured the fake value in stdout,
stderr, exception text, the transcript, `sessions.db` and changed files. The scanner covers the file
half. It does **not** cover live streams, does not read binary files (`sessions.db` is *skipped and
counted* in every report, so the gap is visible rather than silent), and cannot find a secret that was
never in its environment except by token shape. It also does not close RT-4, because a run that never
reaches the CI step is never scanned.

## One thing left for a human or a review, deliberately not done here

The refusal must happen where delivery is decided. `land_runs.py` is the gate that pushes; calling this
scanner there is a change to the delivery pipeline, and the pipeline is the thing whose failure mode is
"every landing refused" (`channels/risks.md` R-009). That change should be made in its own step, with
its own test, not bundled into a security fix by a wake that cannot see the live checkout. Until then
this boundary protects the CI path and any run that calls it — which is more than existed this morning,
and less than the item asks for.
