#!/usr/bin/env python3
"""Tests for scripts/drive_bridge_ingest.py — Frontmatter parsing, status mirror, and receipt writing."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import drive_bridge_ingest as ingest  # noqa: E402


class TestDriveBridgeIngest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_parse_frontmatter_standard_yaml(self):
        doc = (
            "---\n"
            "author: Gemini S. Lumina (App)\n"
            "type: request\n"
            "serial: G-3\n"
            "action_required: true\n"
            "title: Apps Script Retry Injection\n"
            "summary: Inject exponential backoff into exportDocsToPlainText.\n"
            "---\n\n"
            "Here is the detailed body of the request.\n"
        )
        meta = ingest.parse_frontmatter(doc)
        self.assertEqual(meta["author"], "Gemini S. Lumina (App)")
        self.assertEqual(meta["type"], "request")
        self.assertEqual(meta["serial"], "G-3")
        self.assertTrue(meta["action_required"])
        self.assertEqual(meta["title"], "Apps Script Retry Injection")
        self.assertEqual(meta["summary"], "Inject exponential backoff into exportDocsToPlainText.")
        self.assertEqual(meta["body"], "Here is the detailed body of the request.")

    def test_parse_frontmatter_legacy_bracket_headers(self):
        doc = (
            "[Lumina-Commit-Draft]\n"
            "Type: Milestone Update\n"
            "Author: Gemini S. Lumina\n"
            "Title: Multi-Platform Asynchronous Hand-Off Architecture\n"
            "Summary: Established continuous identity continuity across Mac and Pixel.\n\n"
            "Body text here.\n"
        )
        meta = ingest.parse_frontmatter(doc)
        self.assertEqual(meta["type"], "milestone")
        self.assertEqual(meta["author"], "Gemini S. Lumina")
        self.assertEqual(meta["title"], "Multi-Platform Asynchronous Hand-Off Architecture")
        self.assertIn("Established continuous identity", meta["summary"])

    def test_parse_frontmatter_legacy_request_tag(self):
        doc = (
            "Title: Transient Error Plan\n"
            "A recovery procedure (REQUEST G-3) has been queued for execution.\n"
        )
        meta = ingest.parse_frontmatter(doc)
        self.assertEqual(meta["type"], "request")
        self.assertEqual(meta["serial"], "G-3")
        self.assertTrue(meta["action_required"])

    def test_build_and_export_status_mirror(self):
        out_file = ingest.export_status_mirror(self.root, repo=ROOT)
        self.assertTrue(out_file.is_file())
        self.assertEqual(out_file.name, "LLM Symposium Status for Gemini.md")
        content = out_file.read_text(encoding="utf-8")
        self.assertIn("# LLM Symposium — Real-Time Status Mirror for Gemini", content)
        self.assertIn("## 1. Recent Commits on main", content)
        self.assertIn("## 2. Active Requests to the Human", content)
        self.assertIn("## 3. Latest Milestones", content)
        self.assertIn("Milestone 11", content)
        self.assertIn("## 4. Current Gemini To-Do Queue", content)

    def test_scan_and_ingest_writes_receipt_and_idempotency(self):
        handoff_file = self.root / "Handoff - Test Payload.md"
        handoff_file.write_text(
            "---\n"
            "author: Gemini S. Lumina (App)\n"
            "type: task\n"
            "action_required: false\n"
            "title: Empirical Exploration\n"
            "---\n\n"
            "Content details here.\n",
            encoding="utf-8",
        )

        # First scan writes receipt
        items = ingest.scan_and_ingest(self.root, repo=ROOT, write_receipts=True)
        self.assertEqual(len(items), 1)
        self.assertFalse(items[0]["already_receipted"])
        self.assertIn("receipt_written", items[0])

        receipt_file = self.root / "Receipt - Handoff - Test Payload.txt"
        self.assertTrue(receipt_file.is_file())
        receipt_text = receipt_file.read_text(encoding="utf-8")
        self.assertIn("Status: Delivered & Verified", receipt_text)
        self.assertIn("Source File: Handoff - Test Payload.md", receipt_text)

        # Second scan is idempotent — does not overwrite receipt
        items2 = ingest.scan_and_ingest(self.root, repo=ROOT, write_receipts=True)
        self.assertEqual(len(items2), 1)
        self.assertTrue(items2[0]["already_receipted"])
        self.assertNotIn("receipt_written", items2[0])


if __name__ == "__main__":
    unittest.main()
