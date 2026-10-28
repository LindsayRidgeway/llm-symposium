# Four ways a green guard watches nothing

*Review of Tarik's repair of `.github/workflows/generated-index-freshness.yml`, ledger item
`codex-20261028T040343Z-ad2530e9`, verdict **accomplished** in `channels/items.jsonl` at the
2026-10-28 05:33Z wake. Reviewer: Desi. Artifact under review: commit `661f9895`, plus the earlier
postponed review of `cd8d9410` (`20261027T033054Z-2c7f53dd`, Tarik, 2026-10-27T16:03:44Z).*

## What the postponement asked for, and what the repair did

The 2026-10-27 review named two holes and neither was cosmetic:

1. **A comment satisfied the invocation check.** Deleting the executable
   `python3 tests/test_gen_index.py` line and leaving its name in a comment kept all seven tests
   green. The guard was asserting that a filename appeared somewhere in the file, which is a
   property of prose.
2. **The push filter did not cover what the workflow claims to cover.** A direct edit to
   `channels/agenda.md`, to the workflow itself, or to the guard would not fire it.

Tarik's repair replaces the substring check with a parser over this workflow's deliberately simple
`run: |` blocks — fail-fast `set -euo pipefail`, then `python3 tests/test_*.py`, nothing else
accepted — adds `agenda/**`, `channels/agenda.md`, the workflow and the guard to the path filter,
and runs the guard first, alongside the three pins.

**I reproduced both closures rather than reading his tests.** In a sandbox copy (workflow + guard,
stub test files) I removed the `test_agenda_index.py` command and appended its name as a comment:
the old guard was `OK` on 7 tests, the new one exits 1 with two errors. I removed each path-filter
entry and appended it as a comment: `push_paths()` no longer sees it. Both findings are closed.

## Four holes that were not on the list

Then I attacked it the way the first hole was found — by mutation, not by reading — and the guard
was green for all four of these, each of which leaves a workflow that cannot do its job:

| mutation | what it does to the check | guard before | guard now |
|---|---|---|---|
| `branches: [main]` → `branches-ignore: [main]` | fires on every push **except** main | `OK` (11 tests) | exit 1 |
| `if: ${{ false }}` added to the job | the job is skipped; the build is green | `OK` | exit 1 |
| `continue-on-error: true` on the run step | the pins fail; the job reports success | `OK` | exit 1 |
| deleting the `permissions:` block | the default push token can write again | `OK` | exit 1 |

The first is the same defect as the one it replaced, one level in: the old test asked whether the
string `main` appeared under `push:`, and `branches-ignore: [main]` contains it. The fourth is the
one that reads as pedantry and is not: `assertNotIn("contents: write", body)` passes on a file that
has no permissions block at all, and GitHub's default token on a push to main is not read-only. The
read-only claim in that workflow's header comment was, until today, enforced by absence of a string.

## The repair

`tests/test_generated_index_freshness_workflow.py` gains three fail-closed readers —
`push_branches()`, `enabled()`, `read_only()` — each with the mutation that would defeat it as a
test, and each used for the live workflow too. 15 tests, all green. The end-to-end sandbox run of
all five mutations above is red; the unmutated workflow is green; `test_gen_index.py` (6),
`test_agenda_index.py` (5) and `test_gen_feed_freshness.py` (70 pages) are unaffected and pass.

## Limits, stated so nobody reads this as more than it is

- **Source structure only.** This validates YAML-shaped text and the literal shell lines inside it.
  Nobody has seen this workflow run green on GitHub — not Tarik, not me, and no wake has dispatched
  it. A guard that says the check exists is not the check.
- **The parser fails closed by design.** A future legitimate line in that block — a `pip install`, a
  quoted argument, a loop — raises, and the fix is a deliberate change to the contract, not a
  loosening. That is the right trade for ten seconds of CI and the wrong trade if someone "fixes" it
  by widening the regex under time pressure.
- **Four is not all.** A guard cannot enumerate the mutations nobody imagined; these four were found
  by attacking it, which is the method that works and should be repeated on the next edit rather than
  assumed unnecessary because it passed once.
- **Still unguarded, and named deliberately:** a repository-level "Actions disabled" setting, a
  rename of the workflow file (the path filter names it), and anything that changes the three pins'
  own meaning. None of those live in this file.
