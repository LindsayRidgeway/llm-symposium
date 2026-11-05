#!/usr/bin/env python3
"""Tests for scripts/outreach_draft_census.py — the drafts-versus-ledger census.

Written 2026-11-05 (Desi) with the instrument, for the reason the instrument exists: the
outreach audit and the census count different things ("rows in the staged state" versus
"files in the drafts folder"), and only a fixture can hold both answers still long enough
to see that they disagree.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "outreach_draft_census", REPO / "scripts" / "outreach_draft_census.py")
census_mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(census_mod)

LETTER = ("Identity: gemini\nTo: services@example.org\nSubject: An inquiry\n\n"
          "Dear Desk,\n\nOne letter, exactly as written.\n")


class Base(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)
        self.drafts = self.root / "channels" / "outreach" / "drafts"
        self.drafts.mkdir(parents=True)
        self.ledger = self.root / "channels" / "outreach" / "pipeline.json"

    def write_draft(self, name, body=LETTER):
        (self.drafts / name).write_text(body, encoding="utf-8")

    def write_ledger(self, rows):
        self.ledger.write_text(json.dumps({"prospects": rows}), encoding="utf-8")

    def facts(self):
        return census_mod.census(self.ledger, self.drafts, self.root)


class TestCensus(Base):
    def test_a_draft_no_row_names_is_an_orphan(self):
        self.write_draft("seen.md")
        self.write_draft("unseen.md", "different letter\n")
        self.write_ledger([{"id": "a", "draft": "channels/outreach/drafts/seen.md"}])
        facts = self.facts()
        self.assertEqual([p.split("/")[-1] for p in facts["orphans"]], ["unseen.md"])
        self.assertEqual(facts["drafts_on_disk"], 2)
        self.assertEqual(facts["named_by_a_row"], 1)

    def test_a_row_naming_a_draft_that_is_gone_is_reported_not_ignored(self):
        self.write_ledger([{"id": "a", "draft": "channels/outreach/drafts/ghost.md"}])
        facts = self.facts()
        self.assertEqual(facts["missing"], ["channels/outreach/drafts/ghost.md"])

    def test_two_identical_letters_are_a_duplicate_group_named_by_hash(self):
        self.write_draft("a.md")
        self.write_draft("b.md")
        self.write_draft("c.md", "a different letter entirely\n")
        self.write_ledger([])
        facts = self.facts()
        self.assertEqual(len(facts["duplicates"]), 1)
        group = facts["duplicates"][0]
        self.assertEqual([p.split("/")[-1] for p in group["paths"]], ["a.md", "b.md"])
        self.assertEqual(len(group["md5"]), 32)

    def test_a_row_may_name_several_drafts_as_a_list(self):
        self.write_draft("a.md")
        self.write_draft("b.md", "other\n")
        self.write_ledger([{"id": "a", "drafts": ["channels/outreach/drafts/a.md",
                                                  "channels/outreach/drafts/b.md"]}])
        self.assertEqual(self.facts()["orphans"], [])

    def test_an_absolute_path_from_another_checkout_is_rebased_not_called_missing(self):
        self.write_draft("a.md")
        self.write_ledger([{"id": "a",
                            "draft": "/Users/someone/LLM/other-bot/repo/channels/outreach/drafts/a.md"}])
        facts = self.facts()
        self.assertEqual(facts["missing"], [])
        self.assertEqual(facts["orphans"], [])

    def test_readme_in_the_drafts_folder_is_not_a_letter(self):
        self.write_draft("README.md", "what this folder is for\n")
        self.write_ledger([])
        self.assertEqual(self.facts()["drafts_on_disk"], 0)

    def test_a_clean_folder_says_so_in_words(self):
        self.write_draft("a.md")
        self.write_ledger([{"id": "a", "draft": "channels/outreach/drafts/a.md"}])
        facts = self.facts()
        self.assertFalse(facts["orphans"] or facts["missing"] or facts["duplicates"])
        self.assertIn("clean:", census_mod.render(facts, self.ledger, self.drafts))

    def test_strict_exits_one_only_on_a_defect(self):
        self.write_draft("a.md")
        self.write_ledger([{"id": "a", "draft": "channels/outreach/drafts/a.md"}])
        self.assertEqual(census_mod.main(
            ["--ledger", str(self.ledger), "--drafts", str(self.drafts), "--strict"]), 0)
        self.write_draft("b.md")
        self.assertEqual(census_mod.main(
            ["--ledger", str(self.ledger), "--drafts", str(self.drafts), "--strict"]), 1)

    def test_the_real_repository_pipeline_shape_is_understood(self):
        """The live ledger wraps rows in a dict; a bare list must work too."""
        self.write_draft("a.md")
        self.ledger.write_text(json.dumps({"prospects": [
            {"id": "a", "draft": "channels/outreach/drafts/a.md", "status": "staged"}]}),
            encoding="utf-8")
        self.assertEqual(self.facts()["prospects"], 1)
        self.ledger.write_text(json.dumps([
            {"id": "a", "draft": "channels/outreach/drafts/a.md"}]), encoding="utf-8")
        self.assertEqual(self.facts()["prospects"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
