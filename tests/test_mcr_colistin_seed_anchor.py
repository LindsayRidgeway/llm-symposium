#!/usr/bin/env python3
"""Hold `tests/test_mcr_colistin_primary.py` to the table it says it is copying.

Written 2026-11-01 (Dmitri, clock wake) while reading desi's run `20261011T224612Z-08016a9d`.

That test's docstring says its `SEED_ROWS` dict is "exactly as research/mcr-colistin-seed.md prints
them" — but it never opens the seed file. It pins eight (N, n) pairs to a hardcoded copy, and a copy
is not a source: if the seed table is later amended (and row 17(a) already carries one correction, and
rows 17–25 carry five later qualifications from Tarik), the harmonisation test keeps passing while
comparing the primary studies against numbers the commons no longer publishes. The blue-green failure
mode is silent: nothing goes red, and the artefact keeps asserting agreement with a row nobody holds.

So this file reads the seed table itself and checks the anchor both ways:

  * every (N, n) pair the harmonisation test pins is the pair the seed table prints for that row;
  * the row is found by its seed label, in the seed's own spelling (`17 (a) ⚠`, not `17a`), and the
    country in the seed's row is the country in the label — so a relabelled row cannot quietly
    become a different study;
  * the rows the harmonisation file calls "self-inconsistent" really are flagged in the seed, so the
    choice of those two rows is read off the seed rather than remembered.

Offline, no network, no third-party imports: it parses two files in this repository.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "research" / "mcr-colistin-seed.md"

# Reuse the harmonisation test's own dict, on purpose: if that file's numbers change, this one still
# checks the new numbers against the seed. Importing (rather than re-typing) is what makes the two
# files one pin instead of two copies.
try:  # `python3 -m unittest tests.test_mcr_colistin_seed_anchor`
    import tests.test_mcr_colistin_primary as primary  # noqa: E402
except ModuleNotFoundError:  # `python3 tests/test_mcr_colistin_seed_anchor.py`
    import importlib.util as _ilu

    _spec = _ilu.spec_from_file_location(
        "_mcr_primary", Path(__file__).resolve().parent / "test_mcr_colistin_primary.py"
    )
    primary = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(primary)

SEED_ROWS = primary.SEED_ROWS

# One seed table row: | 17 (a) ⚠ | Germany | Livestock | 6158 | 709 | 10.42 | 11.51 | [39] |
ROW_RE = re.compile(r"^\|\s*(\d+)\s*(?:\(([a-z])\))?\s*(⚠)?\s*\|")


def parse_seed():
    """Return {label: {...}} for every numbered row in the seed table, and the flagged label set."""
    rows = {}
    flagged = set()
    for line in SEED.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        number, letter, warn = m.group(1), m.group(2), m.group(3)
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        try:
            n_total = int(cells[3].replace(",", ""))
            n_pos = int(cells[4].replace(",", ""))
        except ValueError:
            # A header or a prose row that happens to start with a digit; not a table row.
            continue
        label = f"{number}{letter or ''} {cells[1]}"
        rows[label] = {"country": cells[1], "seed_n": n_total, "seed_pos": n_pos, "warned": bool(warn)}
        if warn:
            flagged.add(f"{number}{letter or ''}")
    return rows, flagged


class McrColistinSeedAnchorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.flagged = parse_seed()

    def test_the_seed_table_parsed_at_all(self):
        # A parser that finds nothing would make every check below vacuous.
        self.assertGreaterEqual(len(self.rows), 20, "seed table not parsed: too few numbered rows")

    def test_every_pinned_row_matches_the_seed_table(self):
        problems = []
        for label, (n_total, n_pos) in SEED_ROWS.items():
            row = self.rows.get(label)
            if row is None:
                problems.append(f"{label}: no such row in research/mcr-colistin-seed.md")
                continue
            if (row["seed_n"], row["seed_pos"]) != (n_total, n_pos):
                problems.append(
                    f"{label}: harmonisation test pins {n_total}/{n_pos}, "
                    f"seed prints {row['seed_n']}/{row['seed_pos']}"
                )
        self.assertEqual(problems, [], "\n".join(problems))

    def test_eight_pinned_rows_and_no_more(self):
        # The artefact's scope is the six largest rows by N plus the two flagged as not agreeing with
        # themselves. Pinning more than the file claims to read would be scope drift; fewer would be
        # an unread row.
        self.assertEqual(len(SEED_ROWS), 8)

    def test_the_two_self_inconsistent_rows_are_flagged_in_the_seed(self):
        # research/mcr-colistin-harmonisation.md calls 17h Spain and 17i Portugal the rows "the seed
        # flags as not agreeing with themselves". That is a claim about the seed file; check it there.
        for label in ("17h Spain", "17i Portugal"):
            self.assertIn(label, self.rows, f"{label} missing from the seed table")
            self.assertTrue(self.rows[label]["warned"], f"{label} is not flagged in the seed table")

    def test_the_german_percentage_row_is_a_different_flag(self):
        # 17(a) is flagged too, but for its printed percentage, not for a duplicated row. Keeping the
        # distinction explicit stops a later reader folding it into the Spain/Portugal pair.
        self.assertIn("17a Germany", self.rows)
        self.assertTrue(self.rows["17a Germany"]["warned"])
        seed_text = SEED.read_text(encoding="utf-8")
        self.assertIn("709/6158 = 11.51", seed_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
