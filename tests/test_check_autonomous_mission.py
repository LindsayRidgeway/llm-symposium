#!/usr/bin/env python3
"""Offline git integration tests: no model calls, fake drafts only."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_autonomous_mission.py"
spec = importlib.util.spec_from_file_location("mission_check", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
TARGET = "discussions/2026-09-13-tarik-peer-critique-eighteen-days.md"


class MissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.artifacts = self.root / "artifacts"
        self.artifacts.mkdir()
        self.mission = self.root / "mission.md"
        self.mission.write_text(f"**Required artifact path:** `{TARGET}`\n- Minimum 900 words.\n")
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        (self.repo / "README.md").write_text("# Fixture\n")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], text=True)

    def draft(self, n=920):
        # Padding is a test fixture, NOT evidence that word count proves quality.
        text = "# Fixture\n\n**Author:** Tarik S. Commons  \n**Date:** 2026-09-13  \n**Status:** Test only\n\n"
        path = self.repo / TARGET
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + ("fixture " * n).strip() + " \n")
        return path

    def check(self):
        return m.check(self.repo, self.mission, self.base, self.artifacts)

    def test_empty_diff_fails(self):
        r = self.check()
        self.assertFalse(r["ok"])
        self.assertIn("required artifact", " ".join(r["errors"]))

    def test_state_only_fails(self):
        path = self.repo / "to-do-lists/tarik.md"
        path.parent.mkdir()
        path.write_text("# Done\n")
        self.assertFalse(self.check()["ok"])

    def test_untracked_draft_normalized_and_preserved(self):
        path = self.draft()
        original = path.read_bytes()
        r = self.check()
        self.assertTrue(r["ok"], r)
        self.assertTrue(r["normalized"])
        self.assertEqual((self.artifacts / "mission-original.md").read_bytes(), original)
        self.assertTrue(path.read_text().endswith("fixture\n"))
        self.assertIn("Commons  \n", path.read_text())  # intentional hard break
        self.assertIn(TARGET, (self.artifacts / "changes.patch").read_text())

    def test_staged_draft_detected(self):
        self.draft()
        self.git("add", ".")
        self.assertTrue(self.check()["ok"])

    def test_short_draft_fails_even_if_metadata_good(self):
        self.draft(60)
        r = self.check()
        self.assertFalse(r["ok"])
        self.assertIn("900", " ".join(r["errors"]))
        self.assertTrue((self.artifacts / "mission-original.md").exists())

    def test_simple_frontmatter_metadata_accepted(self):
        path = self.draft()
        path.write_text("---\ntitle: Fixture\nauthor: Tarik\ndate: 2026-09-13\nstatus: Draft\n---\n# Fixture\n" + "word " * 920 + "\n")
        self.assertTrue(self.check()["ok"])

    def test_missing_metadata_rejected(self):
        path = self.draft()
        path.write_text("# Fixture\n" + "word " * 950)
        self.assertFalse(self.check()["ok"])

    def test_valid_artifact_cannot_smuggle_workflow_change(self):
        self.draft()
        path = self.repo / ".github/workflows/escape.yml"
        path.parent.mkdir(parents=True)
        path.write_text("# unexpected\n")
        r = self.check()
        self.assertFalse(r["ok"])
        self.assertIn("unexpected changed", " ".join(r["errors"]))

    def test_existing_document_is_not_renormalized(self):
        self.draft()
        before = "# Fixture\nchange \n"
        (self.repo / "README.md").write_text(before)
        self.check()
        self.assertEqual((self.repo / "README.md").read_text(), before)

    def test_symlink_target_rejected(self):
        path = self.repo / TARGET
        path.parent.mkdir(parents=True)
        path.symlink_to(self.repo / "README.md")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.check()

    def test_traversal_rejected(self):
        self.mission.write_text("**Required artifact path:** `../outside.md`\n- Minimum 900 words.\n")
        with self.assertRaises(ValueError):
            self.check()

    def test_accepted_artifact_is_not_regenerated(self):
        self.draft()
        self.git("add", ".")
        self.git("commit", "-qm", "accepted")
        self.base = self.git("rev-parse", "HEAD").strip()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.check()

    def test_normalizer_is_idempotent_and_keeps_code(self):
        text = "hello \nline   \n```txt\ncode \n```\n    indented \nend"
        clean = m.normalize_markdown(text)
        self.assertEqual(clean, "hello\nline  \n```txt\ncode \n```\n    indented \nend\n")
        self.assertEqual(m.normalize_markdown(clean), clean)

    def test_cli_report_written_on_failure(self):
        result = subprocess.run(["python3", str(SCRIPT), "--repo", str(self.repo),
                                 "--mission", str(self.mission), "--base", self.base,
                                 "--artifacts", str(self.artifacts)], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads((self.artifacts / "mission-check.json").read_text())["ok"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
