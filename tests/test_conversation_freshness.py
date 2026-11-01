#!/usr/bin/env python3
"""The freshness report must read both stamp formats and never invent an age.

`conversation_freshness.py` exists because the conversation logs have no gate (2026-11-01): the agenda
index has a test that fails when it drifts, and `channels/conversation/*.md` had nothing. A report that
mis-parsed a stamp would be worse than no report — it would say "fresh" about an amigo who has not
written in a week. So this pins the parsing, the newest-stamp choice, the no-stamp case, and the
exclusion of notes files that are not conversations.
"""
import datetime as dt
import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("cf", REPO / "scripts" / "conversation_freshness.py")
cf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cf)


class FreshnessTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def write(self, name, text):
        (self.dir / name).write_text(text, encoding="utf-8")

    def test_reads_both_stamp_formats_and_takes_the_newest(self):
        self.write("a.md", "**Lindsay:** hi\n\n[Telegram 2026-10-01-101010] **A:** old\n"
                           "[Goose 2026-10-20 11:30] **Lindsay:** newer\n")
        now = dt.datetime(2026, 10, 25, 11, 30)
        row = [r for r in cf.scan(now=now, conv=self.dir) if r["amigo"] == "a"][0]
        self.assertEqual(row["last"], "2026-10-20 11:30")
        self.assertAlmostEqual(row["days"], 5.0, places=1)

    def test_no_stamp_reports_unknown_not_fresh(self):
        self.write("b.md", "**Lindsay:** hi\n\nno dates here\n")
        row = [r for r in cf.scan(now=dt.datetime(2026, 11, 1), conv=self.dir) if r["amigo"] == "b"][0]
        self.assertIsNone(row["days"])
        self.assertEqual(row["last"], "(no stamp)")

    def test_notes_files_are_not_conversations(self):
        self.write("facts.md", "# facts\n- a fact\n")
        self.assertEqual(cf.scan(now=dt.datetime(2026, 11, 1), conv=self.dir), [])

    def test_the_real_logs_all_parse(self):
        rows = cf.scan()
        self.assertTrue(rows, "no conversation logs found")
        for r in rows:
            self.assertIn("amigo", r)
            self.assertTrue(r["days"] is None or r["days"] >= 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
