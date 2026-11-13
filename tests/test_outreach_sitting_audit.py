"""Tests for scripts/outreach_sitting_audit.py — the register that keeps an outreach chat honest.

Registered in .github/workflows/test-and-report.yml; the project has no pytest (see to-do-lists/desi.md,
2026-11-12: "no pytest, no node, no rg"), so this is plain unittest with a __main__ runner.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import outreach_sitting_audit as audit  # noqa: E402

REGISTER = """# Outreach sittings

Prose that mentions | a pipe | and should not become a row.

| no | date | chat | who | artifact | what left the building |
|----|------|------|-----|----------|------------------------|
| 01 | 2026-11-13 | Desi Outreach #01 | desi | channels/sent/2026-11-13-open-meteo-which-model-answered.md | a letter |
| 02 | 2026-11-14 | Desi Outreach #02 | desi | nothing | Looked for an address for three hours, the site answers 403 to this session on every path, and no address was invented. |
"""


class ParseRegister(unittest.TestCase):
    def test_rows_are_read_with_their_headers(self):
        rows = audit.parse_register(REGISTER)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["who"], "desi")
        self.assertEqual(rows[1]["artifact"], "nothing")

    def test_prose_outside_the_table_is_not_a_row(self):
        rows = audit.parse_register(REGISTER)
        self.assertNotIn("pipe", " ".join(" ".join(r.values()) for r in rows))

    def test_earliest_date_is_where_the_register_applies(self):
        self.assertEqual(audit.register_start(audit.parse_register(REGISTER)), "2026-11-13")

    def test_empty_register_has_no_start(self):
        self.assertIsNone(audit.register_start([]))


class RowProblems(unittest.TestCase):
    def row(self, artifact, outcome="a letter to a stranger about a measurement"):
        return {"no": "01", "date": "2026-11-13", "who": "desi",
                "artifact": artifact, "what left the building": outcome}

    def test_existing_artifact_is_fine(self):
        self.assertEqual(audit.row_problems(self.row("x.md"), exists=lambda p: True), [])

    def test_missing_artifact_is_named(self):
        problems = audit.row_problems(self.row("x.md"), exists=lambda p: False)
        self.assertEqual(len(problems), 1)
        self.assertIn("ARTIFACT MISSING", problems[0])
        self.assertIn("x.md", problems[0])

    def test_nothing_needs_a_reason(self):
        problems = audit.row_problems(self.row("nothing", outcome="nothing"), exists=lambda p: False)
        self.assertEqual(len(problems), 1)
        self.assertIn("NO REASON", problems[0])

    def test_nothing_with_a_reason_is_accepted(self):
        outcome = ("The site answers 403 to this session on every path tried, so there was no "
                   "address to verify and none was invented.")
        self.assertEqual(audit.row_problems(self.row("nothing", outcome=outcome), exists=lambda p: False), [])

    def test_blank_artifact_is_a_problem_not_a_silent_pass(self):
        problems = audit.row_problems(self.row(""), exists=lambda p: True)
        self.assertEqual(len(problems), 1)
        self.assertIn("NO ARTIFACT COLUMN", problems[0])


class UndeclaredSittings(unittest.TestCase):
    rows = [{"no": "01", "date": "2026-11-13", "who": "desi", "artifact": "x", "outcome": "y"}]

    def test_a_commit_after_the_first_row_needs_a_row(self):
        commits = {"2026-11-15": ["outreach: a letter"]}
        problems = audit.undeclared(self.rows, "2026-11-13", commits)
        self.assertEqual(len(problems), 1)
        self.assertIn("UNDECLARED SITTING", problems[0])
        self.assertIn("2026-11-15", problems[0])

    def test_a_commit_on_a_declared_date_is_fine(self):
        self.assertEqual(audit.undeclared(self.rows, "2026-11-13", {"2026-11-13": ["x"]}), [])

    def test_history_before_the_register_is_not_retro_failed(self):
        self.assertEqual(audit.undeclared(self.rows, "2026-11-13", {"2026-09-17": ["x"]}), [])

    def test_a_ledger_send_after_the_first_row_needs_a_row(self):
        problems = audit.undeclared(self.rows, "2026-11-13", {}, {"2026-11-20": "open-meteo"})
        self.assertEqual(len(problems), 1)
        self.assertIn("open-meteo", problems[0])

    def test_a_ledger_send_on_a_declared_date_is_fine(self):
        self.assertEqual(audit.undeclared(self.rows, "2026-11-13", {}, {"2026-11-13": "open-meteo"}), [])

    def test_ledger_sends_before_the_register_are_not_retro_failed(self):
        self.assertEqual(audit.undeclared(self.rows, "2026-11-13", {}, {"2026-09-17": "retraction-watch"}), [])


class PipelineSends(unittest.TestCase):
    def test_dates_come_from_the_ledger_not_the_sent_folder(self):
        import json, tempfile
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "pipeline.json"
            p.write_text(json.dumps({"prospects": [
                {"id": "open-meteo", "sent": "channels/sent/2026-11-13-open-meteo-x.md"},
                {"id": "staged-only", "draft": "channels/outreach/drafts/x.md"},
            ]}), encoding="utf-8")
            self.assertEqual(audit.pipeline_sent_dates(p), {"2026-11-13": "open-meteo"})

    def test_a_broken_ledger_is_empty_not_fatal(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "pipeline.json"
            p.write_text("{not json", encoding="utf-8")
            self.assertEqual(audit.pipeline_sent_dates(p), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
