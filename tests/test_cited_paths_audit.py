"""The census must sort a citation into the class that decides whether it is a defect.

Three cases carry the whole argument, so they are pinned: a dated evidence path that is absent
is a claim nobody can check (`dated`); the same absence in a register of unlanded work is the
register doing its job (`register`); a placeholder or a bare filename is neither (`other` or
not a citation at all).
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import cited_paths_audit as audit  # noqa: E402


class CitedPathsAuditTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_a_dated_evidence_path_that_is_absent_is_a_claim(self):
        self._write("channels/reports/2026-10-17-x.md",
                    "Measured from `channels/reports/2026-10-16-gone.md` yesterday.\n")
        res = audit.audit(self.root)
        self.assertEqual(res["counts"]["dated"], 1)
        self.assertEqual(res["by_class"]["dated"][0]["target"],
                         "channels/reports/2026-10-16-gone.md")
        self.assertEqual(res["counts"]["register"], 0)

    def test_the_same_absence_in_a_register_is_not_a_defect(self):
        self._write("to-do-lists/someone.md",
                    "- `channels/reports/2026-10-16-gone.md` — needs a merger.\n")
        res = audit.audit(self.root)
        self.assertEqual(res["counts"]["register"], 1)
        self.assertEqual(res["counts"]["dated"], 0)

    def test_placeholders_and_bare_names_are_not_citations(self):
        self._write("notes.md",
                    "`channels/usage/price-band-YYYY-MM.json` and `local_tick.py`\n"
                    "`…-targets.json` and `https://example.org/a.md`\n")
        res = audit.audit(self.root)
        self.assertEqual(sum(res["counts"].values()), 0)

    def test_a_path_that_does_exist_is_never_reported(self):
        self._write("channels/reports/2026-10-16-here.md", "body\n")
        self._write("notes.md", "`channels/reports/2026-10-16-here.md`\n")
        res = audit.audit(self.root)
        self.assertEqual(sum(res["counts"].values()), 0)

    def test_docstring_and_comment_citations_are_read_from_code(self):
        self._write("scripts/thing.py",
                    "# Measured in `channels/reports/2026-10-16-gone.md`.\nprint(1)\n")
        res = audit.audit(self.root)
        self.assertEqual(res["counts"]["dated"], 1)


    def test_a_test_string_is_a_fixture_but_a_test_comment_is_a_claim(self):
        self._write("tests/test_thing.py",
                    "# Measured in `channels/reports/2026-10-16-gone.md`.\n"
                    "NAME = `channels/reports/2026-10-16-fake.md`\n")
        res = audit.audit(self.root)
        targets = [r["target"] for r in res["by_class"]["dated"]]
        self.assertEqual(targets, ["channels/reports/2026-10-16-gone.md"])


if __name__ == "__main__":
    unittest.main()
