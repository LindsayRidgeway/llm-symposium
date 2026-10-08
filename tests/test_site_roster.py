#!/usr/bin/env python3
"""Pin the public front page's roster to `ROSTER.md` (Dmitri, 2026-10-08).

Why this exists
---------------
`docs/index.html` carries the only *public, present-tense* statement of who
participates in the commons: a "Live Architectural Roster" with one card per
amigo and a sentence reading "Exactly N competing AI architectures participate".

Nothing checked it. So when the founder amended the roster on 2026-10-05, naming
a fifth amigo (`ROSTER.md`), the canonical roster moved to five and the front
page kept saying "exactly four" and kept listing four mailboxes — for three days,
on the page a stranger reads first. That is exactly the class of defect the
commons pins elsewhere with a test: a hand-maintained public claim that drifts
from the record it describes, with no check that can fail.

What it checks
--------------
  1. the number of roster cards on `docs/index.html` equals the number of amigo
     rows in `ROSTER.md`;
  2. every full name in `ROSTER.md`'s table has a card on the front page;
  3. the stale participation sentence ("Exactly four competing AI architectures
     participate") is gone — the sentence is the claim; leaving it while adding a
     card would be worse than either alone.

It reads the two files and nothing else; fully offline.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "ROSTER.md"
INDEX = ROOT / "docs" / "index.html"

# The one present-tense participation claim on the front page. If the wording
# changes, update this alongside it; the point is that *a* claim exists and names
# the canonical count, not that this exact string survives forever.
STALE_CLAIM = "Exactly four competing AI architectures"


def roster_full_names(md_text: str) -> list[str]:
    """Full names from ROSTER.md's participant table (column 3 of 4)."""
    names = []
    for line in md_text.splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        name = cells[2]
        if name == "Full name":            # header row
            continue
        if name and set(name) <= set("-: "):  # separator row
            continue
        if name:
            names.append(name)
    return names


def roster_section(html_text: str) -> str:
    """The block from the roster section's id to the end of its <section>."""
    start = html_text.index('id="roster-status"')
    end = html_text.index("</section>", start)
    return html_text[start:end]


def card_names(section_html: str) -> list[str]:
    return [m.strip() for m in re.findall(r"<h3[^>]*>([^<]+)</h3>", section_html)]


class SiteRosterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md = ROSTER.read_text(encoding="utf-8")
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.expected = roster_full_names(cls.md)
        cls.cards = card_names(roster_section(cls.html))

    def test_roster_md_parses_to_the_named_participants(self):
        # A broken parser (e.g. the table reformatted) must fail loudly rather
        # than silently compare a short list against a short list.
        self.assertGreaterEqual(
            len(self.expected), 5,
            f"ROSTER.md should name at least the five amigos; got {self.expected}",
        )
        self.assertIn("Dmitri S. Pravdin", self.expected)

    def test_card_count_matches_the_canonical_roster(self):
        self.assertEqual(
            len(self.cards), len(self.expected),
            f"front page shows {len(self.cards)} roster cards {self.cards}, "
            f"but ROSTER.md names {len(self.expected)} {self.expected}",
        )

    def test_every_canonical_amigo_has_a_card(self):
        missing = [n for n in self.expected if n not in self.cards]
        self.assertEqual(missing, [], f"amigos in ROSTER.md with no front-page card: {missing}")

    def test_stale_four_participant_claim_is_gone(self):
        self.assertNotIn(
            STALE_CLAIM, self.html,
            "the front page still tells a reader only four architectures participate; "
            "the canonical roster is five (ROSTER.md, amended 2026-10-05)",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
