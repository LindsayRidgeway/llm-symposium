#!/usr/bin/env python3
"""The open decisions a wake is told to answer must be inside the text a wake is handed.

Every wake receives `channels/open-decisions.md` truncated to its first 8,000 characters
(`channels/wake_engine.py`, `orientation()`: `text[:8000]`). The file is maintained by appending at
the bottom, so the newest decisions — and both of the commons' meetings — sat past that point.
Measured 2026-11-15: 33,018 characters, five sections unreachable, each meeting closing with 1 of 6
positions in. Nobody was absent from those meetings; nobody was shown the question.

The guard is modelled on `tests/test_wake_context_caps.py`, which exists because a 3,500-character
agenda window held 0 of 57 item headings on 2026-10-17. This one fails if:

- the digest at the top of the file does not match the file (`--check` is stale),
- a section outside the window is missing from the digest,
- the digest itself does not fit inside the window it describes,
- regeneration is not stable (it has to be a fixed point, or `--write` rewrites on every run),
- the window this script believes in has drifted from the slice the wake engine actually takes.

Run: python3 tests/test_open_decisions_reach.py
"""
import os
import re
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import open_decisions_index as odi  # noqa: E402

TARGET = os.path.join(REPO, "channels", "open-decisions.md")
ENGINE = os.path.join(REPO, "channels", "wake_engine.py")


def _read(path):
    with open(path, encoding="utf8") as fh:
        return fh.read()


class OpenDecisionsReachTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = _read(TARGET)
        cls.body = odi._strip(cls.text)

    def test_window_matches_the_wake_engine(self):
        """The cap is one number in two places; if they drift the digest measures the wrong edge."""
        engine = _read(ENGINE)
        found = {int(n) for n in re.findall(r"text\[:(\d+)\]", engine)}
        self.assertIn(odi.WINDOW, found,
                      "wake_engine.py takes %s, this script measures %s" % (sorted(found), odi.WINDOW))

    def test_digest_is_current(self):
        proc = subprocess.run([sys.executable, os.path.join(REPO, "scripts",
                                                            "open_decisions_index.py"), "--check"],
                              cwd=REPO, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_every_unreached_section_is_named(self):
        digest = odi.BLOCK_RE.search(self.text)
        self.assertIsNotNone(digest, "the file has no digest block at its top")
        block = digest.group(0)
        wholly, partly = odi.unreached(self.body, len(block))
        self.assertTrue(wholly or partly,
                        "nothing is unreachable; if the file really fits the window, delete the "
                        "digest rather than leaving a pointer that points at nothing")
        for start, title in wholly + partly:
            first_words = " ".join(title.split())[:24]
            self.assertIn(first_words, " ".join(block.split()),
                          "section at %d is outside the window and not in the digest: %r"
                          % (start, title))

    def test_digest_fits_inside_the_window(self):
        """A pointer that is itself below the cut is the defect wearing a hat."""
        m = odi.BLOCK_RE.search(self.text)
        self.assertIsNotNone(m)
        self.assertLessEqual(m.end(), odi.WINDOW,
                             "the digest ends at %d, past the %d-character window"
                             % (m.end(), odi.WINDOW))

    def test_regeneration_is_stable(self):
        once = odi.desired(self.text)
        self.assertEqual(once, self.text, "the file does not match its own regeneration")
        self.assertEqual(odi.desired(once), once, "regeneration is not a fixed point")


class SyntheticTest(unittest.TestCase):
    """The instrument on a file whose answer is known, so a green run is not just a quiet file."""

    def _file(self, offsets):
        parts = ["# Open Decisions\n\npreamble\n\n"]
        for i, off in enumerate(offsets):
            pad = max(0, off - sum(len(p) for p in parts))
            parts.append(("x" * pad) + ("\n\n" if pad else "") + f"## Section {i}\n\nbody\n\n")
        return "".join(parts)

    def test_sections_past_the_edge_are_reported(self):
        text = self._file([0, 9000])
        wholly, partly = odi.unreached(text, 0)
        self.assertEqual([t for _, t in wholly], ["Section 1"])
        # Section 0's heading is inside the window but its body runs to the next heading at 9,002,
        # so it is half-read, which is the other failure and it is reported as such.
        self.assertEqual([t for _, t in partly], ["Section 0"])

    def test_a_section_cut_mid_text_is_reported_as_partly(self):
        head = "# Open Decisions\n\n" + "x" * (odi.WINDOW - 40) + "\n\n## Straddler\n\n"
        text = head + "y" * 500
        wholly, partly = odi.unreached(text, 0)
        self.assertEqual(wholly, [])
        self.assertEqual([t for _, t in partly], ["Straddler"])

    def test_render_says_so_and_fits(self):
        digest = odi.digest_for(self._file([0, 9000]))
        self.assertIn("Below the window", digest)
        self.assertIn("Section 1", digest)
        self.assertLess(len(digest), odi.DIGEST_MAX)


if __name__ == "__main__":
    unittest.main(verbosity=2)
