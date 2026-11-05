"""The licence exists, says both licences by name, and the paths it claims are real.

Why a test and not a document. `LICENSE` did not exist until 2026-11-05, and the reason it did not is
that it lived as *words in a chat* and as three unchecked lines in `channels/tasks.md` for four days
after the founder decided (`channels/telegram/2026-11-03-130557-reply-dmitri-s.md`: "the MIT-for-code /
CC BY 4.0-for-records decision, naming Lindsay as grantor, is real but unwritten"). A licence that
lives in a chat grants nothing. The point of this test is that a licence is a claim a *reader* relies
on, so the two ways it can rot are the two things checked here:

1. The grant disappears, or loses one of its two halves, or stops naming the grantor — a licence that
   says "open source" without naming a licence is the exact failure the founder called out
   ("no vague 'this is Open Source' language, which grants nothing and binds no one").
2. The path lists become false. `LICENSE` and the README paragraph name directories and files to say
   which licence covers which; a named path that does not exist is a claim about a tree that has
   moved, which is the same class of error as a citation that opens nothing. Wildcards are resolved
   with `glob`, so `news/*-world-sample.md` is checked as "at least one file matches", not literally.

This test deliberately does NOT check licence *text* against the canonical MIT/CC BY wording — that
would fail on a whitespace change and tell nobody anything. It checks the names, the grantor, the
attribution route, and that the map is true.
"""
import glob
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(name):
    path = os.path.join(ROOT, name)
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


BACKTICKED = re.compile(r"`([^`\n]+)`")
# A token counts as a path claim when it has a slash, or is one of the top-level documents.
TOP_LEVEL = {
    "README.md", "AUTHORSHIP.md", "PROVENANCE.md", "PRESERVATION.md",
    "SUCCESSION.md", "ROSTER.md", "TEST.md", "LLM-SYMPOSIUM-BEACON.md", "LICENSE",
}


def path_claims(text):
    out = []
    for tok in BACKTICKED.findall(text):
        tok = tok.strip()
        if not tok or " " in tok or tok.startswith("-"):
            continue
        if "/" in tok or tok in TOP_LEVEL:
            out.append(tok)
    return out


class LicenceTest(unittest.TestCase):

    def setUp(self):
        self.text = read("LICENSE")
        self.assertIsNotNone(self.text, "LICENSE is missing from the repository root")

    def test_both_licences_are_named(self):
        self.assertIn("MIT License", self.text)
        self.assertIn("Creative Commons Attribution 4.0 International", self.text)
        self.assertIn("CC BY 4.0", self.text)

    def test_grantor_is_named(self):
        self.assertIn("Lindsay Ridgeway", self.text)

    def test_attribution_route_is_stated(self):
        self.assertIn("https://github.com/LindsayRidgeway/llm-symposium", self.text)
        self.assertIn("creativecommons.org/licenses/by/4.0", self.text)

    def test_quoted_material_is_carved_out(self):
        self.assertIn("not relicensed", self.text)
        self.assertIn("PROVENANCE.md", self.text)

    def test_readme_points_at_the_licence(self):
        readme = read("README.md") or ""
        self.assertIn("[LICENSE](LICENSE)", readme)
        self.assertIn("CC BY 4.0", readme)
        self.assertIn("MIT", readme)

    def test_every_path_the_licence_names_exists(self):
        missing = []
        for tok in path_claims(self.text):
            target = os.path.join(ROOT, tok)
            if any(ch in tok for ch in "*?["):
                if not glob.glob(target, recursive=True):
                    missing.append(tok)
            elif not os.path.exists(target):
                missing.append(tok)
        self.assertEqual([], sorted(set(missing)),
                         "LICENSE names paths that are not in the tree")


if __name__ == "__main__":
    unittest.main()
