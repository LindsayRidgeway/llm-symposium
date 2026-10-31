"""A wake's unlanded file is in its run's patch — the recovery must find it and must not invent one.

The load-bearing cases: a new file is recovered whole; a *modification* is not (a diff against an
unknown base reconstructs a file that never existed); a restore never overwrites; a restore never
writes outside the checkout.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import recover_from_run_patches as rec  # noqa: E402

NEW_FILE_PATCH = """diff --git a/channels/reports/2026-10-13-gone.md b/channels/reports/2026-10-13-gone.md
new file mode 100644
index 00000000..e4608db5
--- /dev/null
+++ b/channels/reports/2026-10-13-gone.md
@@ -0,0 +1,3 @@
+# A report
+
+Measured.
"""

MODIFIED_FILE_PATCH = """diff --git a/scripts/thing.py b/scripts/thing.py
index 1111111..2222222 100644
--- a/scripts/thing.py
+++ b/scripts/thing.py
@@ -1,2 +1,3 @@
 x = 1
+x = 2
 y = 3
"""

DELETED_FILE_PATCH = """diff --git a/scripts/old.py b/scripts/old.py
deleted file mode 100644
index 3333333..0000000
--- a/scripts/old.py
+++ /dev/null
@@ -1,2 +0,0 @@
-gone = True
-more = True
"""


class RecoverFromRunPatchesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs = os.path.join(self._tmp.name, "runs")
        self.repo = os.path.join(self._tmp.name, "repo")
        os.makedirs(os.path.join(self.runs, "20261013T170314Z-aaaa"), exist_ok=True)
        os.makedirs(self.repo, exist_ok=True)
        with open(os.path.join(self.runs, "20261013T170314Z-aaaa", "changes.patch"), "w") as fh:
            fh.write(NEW_FILE_PATCH + MODIFIED_FILE_PATCH + DELETED_FILE_PATCH)

    def test_a_new_file_is_indexed_with_its_full_body(self):
        index = rec.scan(self.runs)
        self.assertIn("channels/reports/2026-10-13-gone.md", index)
        body = index["channels/reports/2026-10-13-gone.md"][0]["text"]
        self.assertIn("# A report", body)
        self.assertEqual(len(body.split("\n")), 3)

    def test_a_modification_is_not_recovered_as_content(self):
        index = rec.scan(self.runs)
        self.assertNotIn("scripts/thing.py", index)

    def test_a_deletion_is_not_recovered(self):
        index = rec.scan(self.runs)
        self.assertNotIn("scripts/old.py", index)

    def test_restore_writes_the_file_and_refuses_to_overwrite(self):
        argv = ["--runs", self.runs, "--restore", "channels/reports/2026-10-13-gone.md",
                "--into", self.repo]
        self.assertEqual(rec.main(argv), 0)
        written = os.path.join(self.repo, "channels/reports/2026-10-13-gone.md")
        self.assertTrue(os.path.isfile(written))
        self.assertEqual(rec.main(argv), 4)          # second attempt: exists, refuses
        with open(written) as fh:
            self.assertIn("Measured.", fh.read())

    def test_restore_refuses_a_path_outside_the_checkout(self):
        self.assertEqual(rec.main(["--runs", self.runs, "--restore", "../escape.md",
                                   "--into", self.repo]), 3)
        self.assertFalse(os.path.exists(os.path.join(self._tmp.name, "escape.md")))

    def test_get_returns_the_most_recent_version(self):
        second = os.path.join(self.runs, "20261014T000000Z-bbbb")
        os.makedirs(second, exist_ok=True)
        with open(os.path.join(second, "changes.patch"), "w") as fh:
            fh.write(NEW_FILE_PATCH.replace("Measured.", "Measured twice."))
        index = rec.scan(self.runs)
        versions = index["channels/reports/2026-10-13-gone.md"]
        self.assertEqual(versions[0]["run"], "20261014T000000Z-bbbb")
        self.assertIn("Measured twice.", versions[0]["text"])
        self.assertEqual(versions[-1]["run"], "20261013T170314Z-aaaa")

    def test_a_path_absent_from_the_patches_is_an_error_not_an_empty_file(self):
        self.assertEqual(rec.main(["--runs", self.runs, "--restore", "channels/reports/nope.md",
                                   "--into", self.repo]), 2)


if __name__ == "__main__":
    unittest.main()
