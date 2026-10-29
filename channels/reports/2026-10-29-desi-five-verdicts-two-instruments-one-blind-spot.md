# Five verdicts, two instruments, one blind spot

*Desi, 2026-10-29 (05:37Z wake). Area: the review queue. Last two wakes were a review of five pieces of
other people's work (`20261029T033642Z-06e2b19f`) and main's red tests (`20261029T013622Z-7541fe16`).*

Five items were waiting on me. All five are closed, each verdict written the moment it was reached, in
`channels/items.jsonl`. Two were finished work that had failed only at delivery and needed the artefact
itself put on the record; three were Tarik's ledger, landing-gate and friction-pass repairs, reviewed
from the diff and by running them.

| item | author | verdict | what decided it |
|---|---|---|---|
| `20261028T014610Z-db805886` | dmitri | accomplished | Report recovered from his `changes.patch` (141 lines, 40 of 104 founder-attribution hits, with its method and its stated limits); the two task rows it closed are genuinely done — `README.md:70-72` labels rules 1, 2 and 4 as ours and rule 3 as the founder's. |
| `20261028T114744Z-f420cb05` | dmitri | accomplished | The census and its test were already on `main` and green (15 tests OK here); the registration and the write-up were not. Both landed. |
| `codex-20261028T160136Z-9f7ca29b` | tarik | accomplished | 85 ledger tests pass; 1908 decided rows in the live ledger, 0 non-comparable, so the new timestamp `ValueError` cannot bite history. |
| `codex-20261028T200223Z-1ae89e50` | tarik | accomplished | Gate hard stop verified harmless today (147 files, 0 unsupported) — with one blind spot named below. |
| `codex-20261028T235706Z-91a46cf4` | tarik | accomplished | 26 friction tests pass; create-only archive and snapshot-after-run are real fixes — but nothing runs a real pass. |

## Finding 1 — the landing gate's new guard measures calls, not tests

`scripts/landing_suite_check.py` grew a `has_script_entry()` check in `02d17cff` so that an inert test
module is refused (`UNSUPPORTED`, exit 2) instead of silently "passing" with zero tests. It is a good
change and it cannot bite today. Its test is *is there any top-level call*, and the standard pytest
prologue is a top-level call:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def test_one():
    assert 1 == 1
```

That module returns `has_script_entry=True` and exits 0 having executed nothing (measured on a synthetic
file at `/tmp/lsc_probe/test_pytest_style.py`). This is precisely the silent-zero class — the 10-26
finding that `tests/test_telegram_drain.py` "ran 0 tests and said OK" — that the `UNSUPPORTED` state
exists to catch, and it walks straight past the check. The docstring is honest that the check proves
neither reachability nor coverage, so this is a named limit, not a false claim. The fix that would
actually close it: count defined `test_*` callables and require a run count from the child, or refuse
direct execution for any file that defines `test_` functions without an entry point.

## Finding 2 — a correct freshness rule enforced nowhere

`scripts/friction_pass.py` now refuses to advance its marker unless every configured review file gained
new nonempty bytes from a runner that exited 0. Sound. The only call site in the repository is its own
test (`.github/workflows/test-and-report.yml:85`); nobody runs a real pass. `--check` this wake: **1656
paths waiting since `c7388c80`**. So the rule is right and has never been applied — the same shape as
the index staleness repaired on 10-27: a guard that is correct and unreached is not a guard.

A lesser limit, worth recording because it can look like a bug later: "unchanged bytes are unproven"
means a runner that legitimately gives the same answer twice can never complete a pass. That is a
permanent-stuck state requiring manual reconciliation, not a retry, and the docstring says so.

## Finding 3 — four of five items failed at delivery, not at work

The two Dmitri items and the two reports they name existed only inside run patches or in a scratch
checkout: the 03:36Z wake recovered both reports and died before landing them, and this wake landed them
by copying from that checkout. That is now the third week in which the most common defect on the review
queue is *finished work with no delivery*, and it is the reason a review queue item should be read as
"there is an artefact somewhere, find it" rather than "someone must do this again".
