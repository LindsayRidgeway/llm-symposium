#!/usr/bin/env python3
"""Tests for scripts/declutter_audit.py.

Two kinds of thing are asserted here. First, that the detectors work at all. Second —
and this is the reason the file exists — that the intent table is *class-scoped*, which
it was not in the auditor's first working draft.

The bug it guards against: INTENDED was a flat path→reason map, and the "docs/" entry
meant "served pages are reached by URL, not by a relative link." That is true. Applied
globally it also exempted every JPEG under docs/ from the EXACT detector, and the
auditor reported "0 duplicates" while ~4 MB of byte-identical gallery images sat in the
tree. An intent declared for one class must not suppress another.

Run: python3 tests/test_declutter_audit.py
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = importlib.util.spec_from_file_location(
    "declutter_audit", os.path.join(REPO, "scripts", "declutter_audit.py"))
da = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(da)


class TestIntentScoping(unittest.TestCase):
    def test_docs_is_exempt_from_orphan(self):
        self.assertIsNotNone(da.is_intended("docs/works/trials.html", "orphan"))

    def test_docs_is_not_exempt_from_exact(self):
        """The regression. A duplicate image under docs/ is a duplicate."""
        self.assertIsNone(da.is_intended(
            "docs/gallery/impressionism/studies/tarik/abcdef.jpg", "exact"))

    def test_a_declared_duplicate_is_exempt_from_exact(self):
        self.assertIsNotNone(da.is_intended(
            "docs/gallery/sumi-e/generate-tarik-interval.py", "exact"))

    def test_marker_files_are_dynamic_references(self):
        for path in ("runs/2026-09-17", "runs/1999-01-01", ".gitkeep"):
            self.assertIsNotNone(da.is_intended(path, "orphan"), path)

    def test_every_intent_entry_has_a_reason_with_a_date(self):
        for key, (classes, why) in da.INTENDED.items():
            self.assertTrue(classes, key)
            self.assertRegex(why, r"^20\d\d-\d\d-\d\d — ", key)


class TestDetectorsOnFixtures(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", self.dir], check=True)
        self._old = da.REPO
        da.REPO = self.dir

    def tearDown(self):
        da.REPO = self._old
        subprocess.run(["rm", "-rf", self.dir], check=True)

    def w(self, path, text, binary=False):
        full = os.path.join(self.dir, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb" if binary else "w") as fh:
            fh.write(text.encode() if binary else text)
        subprocess.run(["git", "-C", self.dir, "add", path], check=True)

    def test_exact_finds_byte_identical_files(self):
        self.w("a/x.jpg", "SAME", binary=True)
        self.w("b/x.jpg", "SAME", binary=True)
        self.w("c/y.jpg", "OTHER", binary=True)
        files = da.tracked()
        blobs = {f: da.read(f) for f in files}
        groups = da.find_exact(files, blobs)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0][2], ["a/x.jpg", "b/x.jpg"])

    def test_exact_ignores_empty_files(self):
        """Empty files are markers, not content."""
        self.w("a/empty", "")
        self.w("b/empty", "")
        files = da.tracked()
        blobs = {f: da.read(f) for f in files}
        self.assertEqual(da.find_exact(files, blobs), [])

    def test_near_groups_into_clusters_not_pairs(self):
        """Three mutually-similar documents are one finding, not three."""
        body = ("the commons records its own reasons in the record itself " * 90)
        for name in ("a.md", "b.md", "c.md"):
            self.w(name, "# %s\n\n%s" % (name, body))
        files = da.tracked()
        blobs = {f: da.read(f) for f in files}
        clusters = da.find_near(files, blobs)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0][0], 3)

    def test_near_ignores_short_documents(self):
        """At 120 words this returned 46 Gemini chat logs as one 'duplicate'."""
        self.w("a.md", "hello there friend " * 40)
        self.w("b.md", "hello there friend " * 40)
        files = da.tracked()
        blobs = {f: da.read(f) for f in files}
        self.assertEqual(da.find_near(files, blobs), [])

    def test_dangling_finds_broken_relative_links_only(self):
        self.w("doc.md", "[gone](nowhere/missing.md) [ok](https://x.test/y) "
                         "[fine](other.md)")
        self.w("other.md", "# other\n")
        files = da.tracked()
        blobs = {f: da.read(f) for f in files}
        self.assertEqual(da.find_dangling(files, blobs), [("doc.md", "nowhere/missing.md")])

    def test_orphan_scope_excludes_terminal_records(self):
        self.w("news/2026-01-01-something.md", "# news\n\n" + "word " * 200)
        files = da.tracked()
        blobs = {f: da.read(f) for f in files}
        self.assertEqual(da.find_orphans(files, blobs), [])


class TestAgainstTheRealRepository(unittest.TestCase):
    def test_report_renders_and_writes_nothing_in_stdout_mode(self):
        out = subprocess.run(
            [sys.executable, os.path.join(REPO, "scripts", "declutter_audit.py"), "--stdout"],
            capture_output=True, text=True, cwd=REPO, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("# Declutter audit", out.stdout)
        self.assertIn("What this audit cannot see", out.stdout)

    def test_it_does_not_mutate_the_tree(self):
        """The DRIFT detector re-runs generators. It must put the tree back."""
        before = subprocess.check_output(["git", "-C", REPO, "status", "--porcelain"])
        subprocess.run([sys.executable, os.path.join(REPO, "scripts", "declutter_audit.py"),
                        "--quiet"], capture_output=True, cwd=REPO, timeout=600)
        after = subprocess.check_output(["git", "-C", REPO, "status", "--porcelain"])
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
