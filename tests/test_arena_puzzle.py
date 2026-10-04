#!/usr/bin/env python3
"""The Friction Arena (docs/works/arena.html) — the Round 1 certificate, checked offline.

Why this file exists. The Arena page makes one falsifiable claim: that its seating puzzle
has *exactly one* solution, and that the arrangement it publishes is that solution. A page
that says "here is the only answer" is worth nothing unless the claim is re-checked by
something other than the page. This test reads the same clue objects the page renders,
re-runs the exhaustive search over the puzzle's whole space, and fails if:
  * the number of consistent arrangements is not exactly one, or
  * the published answer is not the arrangement the search finds, or
  * the page's stated size of the raw space is wrong.

It is the certificate. If it is ever red, the page's central claim is false and the page
should say so rather than keep the certificate printed on it.

No network, no writes. Run: python3 tests/test_arena_puzzle.py
"""

import itertools
import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "works" / "arena.html"
INDEX = ROOT / "docs" / "works" / "index.html"

CATS = ["arch", "wing", "hour", "colour"]


def load_arena():
    """Pull the ARENA object out of the page. One source of truth, parsed not duplicated."""
    text = PAGE.read_text(encoding="utf-8")
    start = text.index("const ARENA = ")
    brace = text.index("{", start)
    end = text.index("\n    };", brace)
    return json.loads(text[brace:end + len("\n    }")])


def solve(arena, limit=2):
    """Count arrangements consistent with every clue (stopping at `limit`).

    Each clue names one or two values; a clue is only checked once every category it
    mentions has been placed, which is what makes the search tractable while still being
    a complete enumeration of the space."""
    vals = arena["categories"]
    clues = arena["clues"]
    perms = list(itertools.permutations(range(5)))

    def need(clue):
        return {clue[key][0] for key in ("a", "b") if key in clue}

    def holds(clue, placed):
        if not need(clue) <= set(placed):
            return True
        pos = lambda cv: placed[cv[0]][cv[1]]
        k = clue["k"]
        if k == "mid":     return pos(clue["a"]) == 2
        if k == "end":     return pos(clue["a"]) in (0, 4)
        if k == "same":    return pos(clue["a"]) == pos(clue["b"])
        if k == "next":    return abs(pos(clue["a"]) - pos(clue["b"])) == 1
        if k == "rightof": return pos(clue["a"]) > pos(clue["b"])
        if k == "leftof":  return pos(clue["a"]) < pos(clue["b"])
        if k == "imm":     return pos(clue["a"]) == pos(clue["b"]) + 1
        raise ValueError("unknown clue kind: %r" % k)

    count = 0
    found = []

    def rec(level, placed):
        nonlocal count
        if count >= limit:
            return
        if level == len(CATS):
            count += 1
            found.append({c: dict(placed[c]) for c in CATS})
            return
        cat = CATS[level]
        for perm in perms:
            placed[cat] = {v: perm[i] for i, v in enumerate(vals[cat])}
            if all(holds(c, placed) for c in clues):
                rec(level + 1, placed)
            del placed[cat]
            if count >= limit:
                return

    rec(0, {})
    return count, found


def as_rows(arena, solution):
    rows = []
    for seat in range(5):
        row = {"seat": seat + 1}
        for cat in CATS:
            row[cat] = next(v for v in arena["categories"][cat] if solution[cat][v] == seat)
        rows.append(row)
    return rows


class ArenaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arena = load_arena()
        cls.page_text = PAGE.read_text(encoding="utf-8")

    def test_page_is_staged_and_well_formed(self):
        self.assertTrue(PAGE.exists())
        self.assertIn("<title>", self.page_text)
        self.assertIn('meta name="description"', self.page_text)
        # the Arcade index must actually link it, or it is not staged
        self.assertIn('href="arena.html"', INDEX.read_text(encoding="utf-8"))

    def test_clues_are_present_and_readable(self):
        clues = self.arena["clues"]
        self.assertGreaterEqual(len(clues), 15, "too few clues for a unique puzzle")
        texts = [c["text"] for c in clues]
        self.assertTrue(all(t and t.strip() for t in texts), "a clue has no text")
        self.assertEqual(len(set(texts)), len(texts), "duplicate clue text")

    def test_exactly_one_solution_exists(self):
        count, found = solve(self.arena, limit=2)
        self.assertEqual(count, 1,
                         "the puzzle admits %d arrangements, not one — the certificate is false" % count)

    def test_published_answer_is_the_unique_solution(self):
        _count, found = solve(self.arena, limit=1)
        self.assertEqual(len(found), 1)
        unique = as_rows(self.arena, found[0])
        self.assertEqual(self.arena["solution"], unique,
                         "the page publishes an answer the clues do not single out")

    def test_every_published_row_is_well_formed(self):
        sol = self.arena["solution"]
        self.assertEqual([r["seat"] for r in sol], [1, 2, 3, 4, 5])
        for cat in CATS:
            col = [r[cat] for r in sol]
            self.assertEqual(sorted(col), sorted(self.arena["categories"][cat]),
                             "column %s is not a permutation" % cat)

    def test_the_stated_size_of_the_space_is_correct(self):
        # The page prints the raw space it searches. If the arithmetic changes the number
        # must move with it.
        self.assertIn("207,360,000", self.page_text)
        self.assertEqual(math.factorial(5) ** 4, 207_360_000)
        self.assertEqual(len(CATS), 4, "the space is 5! per category over four categories")


if __name__ == "__main__":
    unittest.main(verbosity=2)
