"""`--postpone-expired`: does a postponed row ever get looked at again?

The gap these tests guard, filed as a to-do item on 2026-11-02 after a measured case: four items
postponed on 2026-10-31 were unblocked by files landing at 03:56Z and 07:56Z on 11-01, and stayed
`postponed` for two days because every automatic pass in `item_ledger.py` filters on the item being
in W. A postponement is a decision, so nothing revisits it — which is right for the ledger and wrong
for the reader, who is told the commons is blocked on work that arrived a day ago.

The property that matters most here is the negative one: this pass prints and never writes. The
last two tests check that against the module and against the real ledger file, byte for byte.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from channels import item_ledger as il  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"


def _row(**kw):
    row = {
        "amigo": "dmitri",
        "id": "20261031T022537Z-20f65972",
        "filed_utc": "2026-10-31T02:25:37Z",
        "state": "postponed",
        "state_utc": "2026-11-01T01:01:58Z",
        "reviewer": "gemini",
        "reason": "absent from main",
        "scope": "internal",
        "source": "derived",
        "title": "a title",
        "paths": ["channels/items.jsonl"],
    }
    row.update(kw)
    return row


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "channels" / "reports").mkdir(parents=True)
        self.path = self.root / "items.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, *rows):
        with open(self.path, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")

    def test_a_blocker_that_has_arrived_is_reported_expired(self):
        (self.repo / "scripts" / "recover_from_run_patches.py").write_text("# x\n")
        self.write(_row(reason="Examined checkout: scripts/recover_from_run_patches.py is absent "
                              "from main. Postponed pending recovery."))
        rows = il.postpone_expired(self.path, repo=self.repo)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "expired")
        self.assertEqual(rows[0]["present"], ["scripts/recover_from_run_patches.py"])
        self.assertEqual(rows[0]["absent"], [])

    def test_a_blocker_that_has_not_arrived_is_not_reported_expired(self):
        self.write(_row(reason="scripts/never_landed.py and tests/test_never_landed.py are absent."))
        rows = il.postpone_expired(self.path, repo=self.repo)
        self.assertEqual(rows[0]["status"], "still-blocked")
        self.assertIn("scripts/never_landed.py", rows[0]["absent"])

    def test_half_a_blocker_is_partial_and_names_both_halves(self):
        (self.repo / "channels" / "reports").mkdir(parents=True, exist_ok=True)
        (self.repo / "channels" / "reports" / "2026-10-31-dmitri-green.md").write_text("x\n")
        self.write(_row(reason="channels/reports/2026-10-31-dmitri-green.md and "
                              "scripts/still_absent.py are absent from main."))
        rows = il.postpone_expired(self.path, repo=self.repo)
        self.assertEqual(rows[0]["status"], "partial")
        self.assertEqual(rows[0]["present"], ["channels/reports/2026-10-31-dmitri-green.md"])
        self.assertEqual(rows[0]["absent"], ["scripts/still_absent.py"])

    def test_a_postponement_that_names_no_path_is_unmeasurable_not_dropped(self):
        self.write(_row(reason="waiting for a human decision about the register"))
        rows = il.postpone_expired(self.path, repo=self.repo)
        self.assertEqual(len(rows), 1, "a row with no stated blocker must still be shown")
        self.assertEqual(rows[0]["status"], "unmeasurable")

    def test_prose_that_is_not_a_repo_path_is_not_counted_as_one(self):
        present, absent = il.blockers_named(
            "the script.py was refused, see https://example.com/x/y.py and/or notes", self.repo)
        self.assertEqual((present, absent), ([], []),
                         "a bare filename or a URL is not a claim about this checkout")

    def test_only_postponed_rows_are_rechecked(self):
        (self.repo / "scripts" / "a.py").write_text("x\n")
        self.write(_row(id="i1", state="accomplished", reason="scripts/a.py landed"),
                   _row(id="i2", state="rejected", reason="scripts/a.py should never be done"),
                   _row(id="i3", state="postponed", reason="scripts/a.py is absent"))
        rows = il.postpone_expired(self.path, repo=self.repo)
        self.assertEqual([r["id"] for r in rows], ["i3"])

    def test_hours_skips_a_row_postponed_moments_ago(self):
        self.write(_row(reason="scripts/a.py is absent",
                        state_utc="2026-11-02T17:40:00Z"))
        self.assertEqual(il.postpone_expired(self.path, repo=self.repo, hours=12), [])
        self.assertEqual(len(il.postpone_expired(self.path, repo=self.repo, hours=0)), 1)

    def test_the_pass_writes_nothing_back_to_the_ledger(self):
        (self.repo / "scripts" / "a.py").write_text("x\n")
        self.write(_row(reason="scripts/a.py is absent"))
        before = self.path.read_bytes()
        il.postpone_expired(self.path, repo=self.repo)
        self.assertEqual(self.path.read_bytes(), before,
                         "postpone_expired must not append: an expired blocker is evidence, not "
                         "a verdict, and stamping accomplished here is the 2026-10-09 stamp")

    def test_the_cli_prints_and_leaves_the_real_ledger_untouched(self):
        before = LEDGER.read_bytes()
        old = sys.argv
        try:
            sys.argv = ["item_ledger.py", "--postpone-expired"]
            code = il.main()
        finally:
            sys.argv = old
        self.assertEqual(code, 0)
        self.assertEqual(LEDGER.read_bytes(), before,
                         "running the pass on the real ledger must not change a byte of it")


if __name__ == "__main__":
    unittest.main()
