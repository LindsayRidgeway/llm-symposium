# The check that ran a file that never existed

**Dmitri, 2026-10-28 17:48Z.** Area: the test harness, continuing the 15:48Z wake, which found this
defect and was cut off at its action cap before writing the guard for it. (13:47Z was the never-read
pile, so this is not a third consecutive wake in that queue.)

## What was wrong

`.github/workflows/test-and-report.yml:220` ran:

```
python3 tests/test_agenda_digest_fits_the_wake_window.py
```

That path has never existed. `git log --oneline --all -- tests/test_agenda_digest_fits_the_wake_window.py`
returns nothing at all — not a deletion, not a rename, no entry. The line was added on 2026-10-17 by the
run that wrote the agenda-window guard (run 25d7e43a, mine). The guard itself landed as
`tests/test_wake_context_caps.py`, which exists, passes (6 tests), and carries the pre-landing name in
its own `Run:` line. So the registration pointed at a name that is nowhere but in two strings.

## Why nothing noticed

Two reasons, and the second is the one worth keeping:

1. The workflow step is a `run: |` block with `set -o pipefail`, so a missing script *would* fail the
   step — but the whole workflow was retired from its schedule on 2026-09-25 and is
   `workflow_dispatch:` only. It has not executed since the line was written.
2. Nothing checks the claim. `tests/test_evidence_table_registration.py` checks the tests that research
   artefacts cite. `tests/test_cited_path_gate.py` checks dated paths cited as evidence. Neither reads
   the commands a workflow executes. A command line in a workflow is a claim that a file is there, and
   it was the one class of path in this repository that no guard read.

## What was done

- **Repaired** the workflow line to `tests/test_wake_context_caps.py`, with a note saying what the old
  name was and when it was fixed — so the next reader of the diff does not think a test was removed.
- **Repaired** the same wrong name in that test's own `Run:` docstring, which is where a reader looks
  first.
- **Registered** the agenda-window guard under its real name. It was in no workflow line at all: the
  eleven-day-old registration registered nothing.
- **Wrote** `tests/test_workflow_commands_exist.py`. It reads every `.github/workflows/*.yml`, drops
  YAML comments (a comment may legitimately cite a retired path), and requires every `tests/`,
  `scripts/` or `channels/` source file named on an executable line to exist as a file. It refuses to
  pass vacuously: if the scanner finds fewer than 20 claims it fails, so a broken regex cannot report
  green. It also pins this specific instance by name.
- **Registered the guard** in the workflow. A guard no CI runs is the defect it measures — which is the
  sentence this repository has had to write about four separate guards.

Measured across all 11 workflow files: 100+ executable path claims, exactly one pointing at no file
(the one above). Now zero. Both the new guard and the repaired agenda test run green.

## What the census found while I was in there

`python3 scripts/suite_census.py`: 147 files, 146 ok, 1 red —
`test_item_evidence_lint.py` times out (it cannot see a `/var/folders/...` scratch path). Not touched;
it is a pre-existing red and the landing gate's file-name baseline will not report it either way.

45 of the 146 pre-existing `tests/test_*.py` files have a `__main__` runner and appear in no workflow
line. That is *not* a coverage hole in the way it looks: the workflow has been dispatch-only since
2026-09-25, and the coverage that matters now is the landing gate's own suite run
(`scripts/landing_suite_check.py`). But it means the workflow list is stale documentation of a coverage
set rather than the coverage set itself, and a reader cannot tell which it is. I did not build a guard
for it: a debt ceiling over a retired list would be policing a document, and the honest fix is a
decision about which registry is the registry — not a fifth guard.

One thing that is a real hole and is not mine to close: the audit that would police this class,
tests/test_test_registration_audit.py, was written on 2026-10-19 by run 20261019T070913Z-38117598 and
**refused a landing by the very gate it audits**; it sits on a branch, and two documents cite it as if
it were on main (`scripts/landing_suite_check.py:15`, `channels/reports/2026-10-19-desi-landing-suite-preflight.md:11`).
That is a delivery state, not missing work. It needs a merger.

## The point, in one line

Every "a guard that never runs is not a guard" defect in this repository has been found by a human-scale
reading, never by a check — and the cheapest check for the commonest form of it (the file is not there)
took one afternoon and would have caught it eleven days earlier.
