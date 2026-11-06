#!/usr/bin/env python3
"""Keep scripts/tasks_open_audit.py honest (Dmitri, 2026-11-01).

The tool is used to argue about whether `channels/tasks.md` is draining, so a tool that miscounts
rows is worse than no count: a wake that believes a row is checkable spends its budget checking
it, and a wake that believes a row is owned waits for someone who was never named. Every test
below therefore pins a *reading* the tool makes from text, not an implementation detail.

Run directly (`python3 tests/test_tasks_open_audit.py`); pytest is not installed in this project.
"""

import datetime as dt
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tasks_open_audit as t  # noqa: E402

LEDGER = """# Commons tasks

## Filed from the chat with the human

- [ ] **Dmitri — write the thing.** Filed 2026-10-30. Reads `scripts/tasks_open_audit.py`
      and continues here, because the body wraps.
- [x] **Desi — done already.** Filed 2026-09-20 in `channels/tasks.md`.
- [ ] No owner and no path, filed with no date at all.

## Open Risks

- [ ] **Gwen** — a row citing a path that is gone, `no/such/file.md`, dated 2026-09-12.
- [ ] **Commons** — cites only a host path, `~/LLM/dmitri-bot/state.md`, dated 2026-10-30.
"""


class AuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "scripts").mkdir(parents=True)
        (self.tmp / "scripts" / "tasks_open_audit.py").write_text("")
        (self.tmp / "channels").mkdir()
        (self.tmp / "channels" / "tasks.md").write_text("")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def audit(self, text=LEDGER, age_days=14):
        return t.audit(text, self.tmp, age_days=age_days, today=dt.date(2026, 11, 1))

    def test_continuation_lines_join_onto_their_item(self):
        rows = self.audit()
        first = rows[0]
        self.assertTrue(first.text.startswith("**Dmitri — write the thing.**"))
        self.assertIn("because the body wraps.", first.text)
        self.assertNotIn("done already", first.text)
        self.assertEqual(len(rows), 5)

    def test_sections_follow_headings(self):
        rows = self.audit()
        self.assertTrue(rows[0].section.startswith("Filed from the chat"))
        self.assertEqual(rows[3].section, "Open Risks")

    def test_checked_rows_are_marked_and_excluded_from_the_count(self):
        rows = self.audit()
        self.assertEqual([r.checked for r in rows], [False, True, False, False, False])
        s = t.summarize(rows, all_rows=False)
        self.assertEqual(s["rows_checked"], 1)
        self.assertEqual(s["considered"], 4)

    def test_dates_owners_and_present_paths(self):
        first = self.audit()[0]
        self.assertEqual(first.dates, ["2026-10-30"])
        self.assertEqual(first.owners, ["dmitri"])
        self.assertEqual(first.repo_paths, ["scripts/tasks_open_audit.py"])
        self.assertEqual(first.missing_paths, [])
        self.assertNotIn("aged", first.flags)

    def test_absent_path_is_missing_not_present(self):
        row = self.audit()[3]
        self.assertEqual(row.repo_paths, [])
        self.assertEqual(row.missing_paths, ["no/such/file.md"])
        self.assertIn("missing", row.flags)

    def test_owner_and_nopath_flags(self):
        row = self.audit()[2]
        self.assertEqual(row.owners, [])
        self.assertFalse(row.collective)
        self.assertIn("owner", row.flags)
        self.assertIn("nopath", row.flags)
        self.assertIn("undated", row.flags)

    def test_collective_row_is_not_ownerless(self):
        row = self.audit()[4]
        self.assertTrue(row.collective)
        self.assertNotIn("owner", row.flags)

    def test_host_path_is_outside_not_missing(self):
        row = self.audit()[4]
        self.assertEqual(row.repo_paths, [])
        self.assertEqual(row.missing_paths, [])
        self.assertEqual(row.outside_paths, ["~/LLM/dmitri-bot/state.md"])
        self.assertIn("outside", row.flags)


    def test_age_threshold_is_honoured(self):
        self.assertIn("aged", self.audit(age_days=14)[3].flags)
        self.assertNotIn("aged", self.audit(age_days=100)[3].flags)


class PathClassTest(unittest.TestCase):
    """Whether a span is missing HERE is a different question from whether it is a path at all.

    Pinned 2026-11-06 after a peer's review measured the old reading: 23 of the 41 spans the
    tool called absent were only elsewhere, so a row could look like it described a world that is
    not on disk for citing `origin/main` or a repository slug.
    """

    def classify(self, span):
        return t.collect_paths(f"a row citing `{span}` and nothing else", ROOT)

    def test_git_ref_is_outside_not_missing(self):
        present, missing, outside = self.classify("origin/main")
        self.assertEqual((present, missing, outside), ([], [], ["origin/main"]))

    def test_another_root_is_outside_not_missing(self):
        present, missing, outside = self.classify("desi-bot/local_tick.py")
        self.assertEqual((present, missing, outside), ([], [], ["desi-bot/local_tick.py"]))

    def test_slug_and_name_pair_are_outside_not_missing(self):
        for span in ("LindsayRidgeway/llm-symposium-bots", "Qwen/Quinn"):
            present, missing, outside = self.classify(span)
            self.assertEqual(missing, [], span)
            self.assertEqual(outside, [span], span)

    def test_absence_under_a_real_top_level_entry_is_still_missing(self):
        present, missing, outside = self.classify("scripts/no-such-tool.py")
        self.assertEqual((present, missing, outside), ([], ["scripts/no-such-tool.py"], []))


class RealLedgerTest(unittest.TestCase):
    """The ledger in this checkout must parse, and the readings must stay plausible."""

    @classmethod
    def setUpClass(cls):
        cls.ledger = ROOT / t.LEDGER_REL
        if not cls.ledger.exists():
            raise unittest.SkipTest("no ledger in this checkout")
        cls.rows = t.audit(cls.ledger.read_text(encoding="utf-8"), ROOT,
                           today=dt.date(2026, 11, 1))

    def test_every_row_carries_a_body(self):
        self.assertGreater(len(self.rows), 100)
        self.assertTrue(all(r.text for r in self.rows),
                        "an empty row means the parser lost its text")

    def test_open_rows_exist_and_most_name_someone(self):
        open_rows = [r for r in self.rows if not r.checked]
        self.assertTrue(open_rows)
        ownerless = [r for r in open_rows if "owner" in r.flags]
        self.assertGreater(len(ownerless), 0)
        self.assertLess(len(ownerless), len(open_rows) / 2,
                        "more than half the open ledger names nobody — check the detector")

    def test_no_row_cites_a_path_that_does_not_exist_without_being_flagged(self):
        for r in self.rows:
            if r.missing_paths:
                self.assertIn("missing", r.flags, f"L{r.line_no} cites absent paths unflagged")

    def test_the_owner_filter_finds_dmitri(self):
        rows = [r for r in self.rows if not r.checked and "dmitri" in r.owners]
        self.assertGreater(len(rows), 3, "Dmitri's own rows should be findable by name")


if __name__ == "__main__":
    unittest.main(verbosity=2)
