#!/usr/bin/env python3
"""The reader's red dot has to be generated, not remembered (2026-11-20).

The founder found this one himself, which is the only reason it is being fixed: a story landed in the
literary wing and neither the home menu nor the wing's page showed the dot that means "there is
something here you have not read". `docs/tracker.js` carried a hand-typed timestamp per section —
fiction's said 2026-10-18, "five delivered stories", while the directory held six that night and
seven after. Nothing could notice, because the number was typed by whoever added the work, and that
is the same failure as every other hand-maintained promise in this repository: it survives exactly as
long as somebody remembers.

So these tests pin the two halves of the repair: the manifest is derived from the tree, and the file
in the repository is not allowed to disagree with the tree it ships beside.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tracker_manifest as tm  # noqa: E402


class TheManifestIsMeasured(unittest.TestCase):
    def test_every_section_with_a_directory_reports_a_date_a_count_and_the_newest_name(self):
        sections = tm.build()
        for section_id in ("fiction", "papers", "works", "music", "gallery"):
            entry = sections[section_id]
            self.assertRegex(entry["updated"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$", section_id)
            self.assertGreater(entry["count"], 0, section_id)
            self.assertIn("newest:", entry["label"], section_id)

    def test_the_literary_wing_counts_the_story_the_founder_went_looking_for(self):
        """The measured failure: 7 works in docs/fiction, and the manifest said five."""
        sections = tm.build()
        on_disk = len(tm.work_pages(ROOT / "docs" / "fiction"))
        self.assertEqual(sections["fiction"]["count"], on_disk)
        self.assertIn("The Second Reader", sections["fiction"]["label"])

    def test_a_section_with_no_directory_says_it_is_typed_by_hand(self):
        sections = tm.build()
        self.assertIn("typed by hand", sections["roster"]["label"])
        self.assertIn("typed by hand", sections["letters"]["label"])

    def test_dates_are_utc_with_a_z(self):
        self.assertEqual(tm.as_utc("2026-11-20T17:29:47-05:00"), "2026-11-20T22:29:47Z")

    def test_the_gallery_counts_wings_not_nothing(self):
        """Its children are directories, so a naive glob would report zero and hand the section back
        to a typed date — which is how a section goes dark without anyone deleting anything."""
        sections = tm.build()
        self.assertGreater(sections["gallery"]["count"], 0)
        self.assertNotIn("typed by hand", sections["gallery"]["label"])


class TheFileAgreesWithTheTree(unittest.TestCase):
    def test_the_checked_in_manifest_is_not_stale(self):
        self.assertEqual(tm.apply(check=True), 0,
                         "docs/tracker.js disagrees with the tree — run "
                         "python3 scripts/tracker_manifest.py")

    def test_the_markers_are_present_so_the_next_work_cannot_land_silently(self):
        text = (ROOT / "docs" / "tracker.js").read_text(encoding="utf-8")
        self.assertIn(tm.BEGIN, text)
        self.assertIn(tm.END, text)


if __name__ == "__main__":
    unittest.main()
