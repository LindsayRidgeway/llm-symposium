#!/usr/bin/env python3
"""Tests for scripts/reconcile_review_verdicts.py — the ledger exit lost between report and row.

Plain runner, no pytest (this repo has none): `python3 tests/test_reconcile_review_verdicts.py`.
Every case builds a throwaway ledger and report directory, so nothing here reads or writes the
commons' real ledger.
"""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "channels"))
sys.path.insert(0, str(ROOT / "scripts"))

import item_ledger  # noqa: E402
import reconcile_review_verdicts as rrv  # noqa: E402

FRANCE = "codex-20261019T040208Z-f399a2b6"


class Bench:
    def __init__(self, tmp: Path):
        self.ledger = tmp / "items.jsonl"
        self.reports = tmp / "reports"
        self.reports.mkdir()

    def add(self, item_id, amigo="tarik", state=None):
        item_ledger.append([{
            "id": item_id, "amigo": amigo, "title": "t", "paths": [],
            "filed_utc": "2026-10-19T04:07:08Z", "state": state, "state_utc": None,
            "reviewer": None, "reason": None,
        }], self.ledger)

    def write(self, name, body):
        (self.reports / name).write_text(body, encoding="utf-8")

    def plan(self):
        return rrv.plan(item_ledger.load(self.ledger), self.reports)

    def rec(self, item_id):
        return item_ledger.load(self.ledger)[item_id]


def test_table_row_with_truncated_token_closes(b):
    b.add(FRANCE)
    b.write("2026-10-19-desi-review.md",
            "| Item | Author | Verdict | Why |\n|---|---|---|---|\n"
            "| `codex-20261019T040208Z-…` France units | tarik | **accomplished** | §6 above |\n")
    closures, _ = b.plan()
    assert [c["id"] for c in closures] == [FRANCE], closures
    assert closures[0]["state"] == "accomplished"
    assert closures[0]["reviewer"] == "auto:verdict:desi"
    assert "2026-10-19-desi-review.md" in closures[0]["reason"]


def test_full_token_in_prose_closes_and_keeps_the_why(b):
    b.add(FRANCE)
    b.write("2026-10-19-desi-review.md",
            f"`{FRANCE}` — **postponed.** both report paths have never existed in any commit.\n")
    closures, _ = b.plan()
    assert closures[0]["state"] == "postponed", closures
    assert "never existed" in closures[0]["reason"]


def test_author_never_reviews_own_item(b):
    b.add(FRANCE, amigo="desi")
    b.write("2026-10-19-desi-review.md", f"| `{FRANCE}` | desi | accomplished | mine |\n")
    closures, refusals = b.plan()
    assert closures == []
    assert any("author is never the reviewer" in r["why"] for r in refusals)


def test_unattributable_report_is_refused(b):
    b.add(FRANCE)
    b.write("2026-10-19-review.md", f"| `{FRANCE}` | tarik | accomplished | x |\n")
    closures, refusals = b.plan()
    assert closures == []
    assert any("cannot be attributed" in r["why"] for r in refusals)


def test_ambiguous_prefix_is_refused(b):
    b.add("20261018T151657Z-aaaaaaaa")
    b.add("20261018T151657Z-bbbbbbbb")
    b.write("2026-10-18-desi-r.md", "| `20261018T151657Z-…` | tarik | postponed | gone |\n")
    closures, refusals = b.plan()
    assert closures == []
    assert any(r["why"].startswith("ambiguous") for r in refusals)


def test_conflicting_verdicts_leave_the_row_alone(b):
    b.add(FRANCE)
    b.write("2026-10-19-desi-a.md", f"| `{FRANCE}` | tarik | accomplished | ok |\n")
    b.write("2026-10-20-desi-b.md", f"| `{FRANCE}` | tarik | postponed | not ok |\n")
    closures, refusals = b.plan()
    assert closures == []
    assert any("conflicting verdicts" in r["why"] for r in refusals)


def test_line_without_a_verdict_word_is_ignored(b):
    b.add(FRANCE)
    b.write("2026-10-19-desi-r.md", f"`{FRANCE}` is still under review.\n")
    closures, _ = b.plan()
    assert closures == []


def test_row_that_already_has_a_state_is_untouched(b):
    b.add(FRANCE, state="accomplished")
    b.write("2026-10-19-desi-r.md", f"| `{FRANCE}` | tarik | rejected | x |\n")
    closures, _ = b.plan()
    assert closures == []


def test_apply_writes_the_row_with_reviewer_and_reason(b):
    b.add(FRANCE)
    b.write("2026-10-19-desi-r.md", f"| `{FRANCE}` | tarik | accomplished | §6 above |\n")
    closures, _ = b.plan()
    assert rrv.apply(closures, b.ledger) == 1
    rec = b.rec(FRANCE)
    assert rec["state"] == "accomplished"
    assert rec["reviewer"] == "auto:verdict:desi"
    assert "2026-10-19-desi-r.md" in rec["reason"]


def test_dry_run_shows_but_writes_nothing(b):
    b.add(FRANCE)
    b.write("2026-10-19-desi-r.md", f"| `{FRANCE}` | tarik | accomplished | ok |\n")
    assert rrv.main(["--reports", str(b.reports), "--ledger", str(b.ledger)]) == 0
    assert b.rec(FRANCE)["state"] is None


def test_a_stamp_cannot_be_written_even_with_an_empty_why_cell(b):
    b.add(FRANCE)
    b.write("2026-10-19-desi-r.md", f"| `{FRANCE}` | tarik | accomplished | |\n")
    closures, _ = b.plan()
    assert closures
    rrv.apply(closures, b.ledger)
    assert "2026-10-19-desi-r.md" in b.rec(FRANCE)["reason"]


def main():
    tests = sorted((n, f) for n, f in globals().items() if n.startswith("test_") and callable(f))
    failures = 0
    for name, fn in tests:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                fn(Bench(Path(tmp)))
                print(f"ok   {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"ERROR {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
