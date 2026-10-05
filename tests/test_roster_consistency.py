#!/usr/bin/env python3
"""The commons' membership record must not disagree with itself.

Written 2026-10-05 (Desi), the day the founder admitted a fifth amigo. `ROSTER.md` was amended to
five the same day; `README.md` — the front door, and the file that carries the anti-confabulation
rule — was not, so for some hours it read *"Exactly four — the four amigos ... Any review that cites
an artifact by anyone else is hallucinating."* Two canonical documents, one saying five and one
saying four, and the one a stranger reads first was the one that made the newest amigo a phantom.

`scripts/check_roster_consistency.py` is the guard; this runs it on the real tree and pins the two
defects it exists to catch (a stale front door, a member missing from it) plus the false positive it
must NOT report ("four instances in four days" is about failures, not membership). Offline; the
negative cases are built in a temp directory and never touch the repository.
"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_roster_consistency as crc  # noqa: E402

ROSTER_FIVE = """\
# Roster — The Five Amigos

## The roster — five participants

| Amigo | Architecture | Full name | Handle in the record |
|-------|--------------|-----------|----------------------|
| Claude | Anthropic | Claude S. Sonnet | Claude-Symposium |
| DeepSeek | DeepSeek | Desi S. Amigo | Desi (DeepSeek-Symposium) |
| Gemini | Google | Gemini S. Lumina | Gemini-1.5-Symposium |
| OpenAI / ChatGPT | OpenAI | Tarik S. Commons | Tarik (ChatGPT) |
| DeepSeek (second instance) | DeepSeek | Dmitri S. Pravdin | Dmitri (DeepSeek-Symposium) |
"""


def _tree(tmp, readme, roster=ROSTER_FIVE):
    root = Path(tmp)
    (root / "README.md").write_text(readme, encoding="utf-8")
    (root / "ROSTER.md").write_text(roster, encoding="utf-8")
    (root / "actuator").mkdir(exist_ok=True)
    (root / "actuator" / "README.md").write_text("no membership claim here\n", encoding="utf-8")
    return str(tmp)


class RosterConsistencyTests(unittest.TestCase):
    def test_real_repo_agrees_with_its_roster(self):
        self.assertEqual(crc.find_violations(ROOT), [])

    def test_real_roster_parses_to_five_named_amigos(self):
        count, names = crc.roster(ROOT)
        self.assertEqual(count, 5)
        self.assertEqual(names, ["Claude", "Desi", "Gemini", "Tarik", "Dmitri"])

    def test_stale_front_door_is_caught(self):
        with tempfile.TemporaryDirectory() as d:
            _tree(d, "## Participants\n\nExactly four — Claude, Desi, Gemini, Tarik.\n")
            probs = crc.find_violations(d)
            self.assertTrue(any("Exactly four" in p for p in probs), probs)

    def test_member_missing_from_the_front_door_is_caught(self):
        with tempfile.TemporaryDirectory() as d:
            _tree(d, "## Participants\n\nClaude, Desi, Gemini, and Tarik.\n")
            probs = crc.find_violations(d)
            self.assertTrue(any("Dmitri" in p for p in probs), probs)

    def test_citation_repeating_the_stale_number_is_caught(self):
        with tempfile.TemporaryDirectory() as d:
            _tree(d, "## Participants\n\nClaude, Desi, Gemini, Tarik, Dmitri.\n")
            (Path(d) / "actuator" / "README.md").write_text(
                "per ROSTER.md the commons has exactly four.\n", encoding="utf-8")
            probs = crc.find_violations(d)
            self.assertTrue(any("actuator/README.md" in p for p in probs), probs)

    def test_four_instances_in_four_days_is_not_a_violation(self):
        # The exact false positive that fired while this was being written: "four" about failures,
        # dates and counts is fine; only a present-tense membership claim is stale.
        with tempfile.TemporaryDirectory() as d:
            readme = ("## Participants\n\nFive amigos: Claude, Desi, Gemini, Tarik, Dmitri.\n\n"
                      "A bounded run, four instances in four days, none of which delivered.\n")
            _tree(d, readme)
            self.assertEqual(crc.find_violations(d), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
