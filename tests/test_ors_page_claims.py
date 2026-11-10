"""The ORS page's numbers, pinned in the suite that actually runs — 2026-11-10.

Why a second check beside `tests/validate_ors_calculator.mjs`, which already has 38 of them:

because that harness needs `node`, and `node` is not on the machine this wake ran on, and in CI it
is only ever handed to `node --check` (see the comment in `.github/workflows/test-and-report.yml`:
the .mjs harnesses "are never executed here"). So the arithmetic that makes the page safe — the
salt:sugar ratios, the sodium figure the footnote derives from them, and the osmolarity the table
row claims — has been guarded by a file nobody runs. This test reads the same page with the same
intent and runs wherever the python suite runs.

It is deliberately NOT a port of the harness. It does not execute the page's inline script and it
does not stub a DOM; it checks the claims the page *states* against each other, which is the part
that rots silently when someone edits one number and not the paragraph that explains it. The
interactive behaviour stays the harness's job, when a machine with node picks it up.

**Known hole, measured this wake and not asserted here.** `validate_ors_calculator.mjs` exercises
household sugar and grams-mode salt but never household salt, and the page's household salt branch
prints a *fixed* mass per bucket: every volume from 700 mL to under 1500 mL gets
"1/2 level teaspoon (approx 2.6 g)" (saltTsp in [0.35, 0.75)). At 750 mL the page's own 2.6 g/L
ratio wants 1.95 g and at 1250 mL it wants 3.25 g, so the printed figure is +33% and -20% at the
two ends of one bucket. This is the same shape as the sugar defect fixed 2026-09-16 ("2 level
teaspoons" hardcoded for 1.5–3.0 tsp), in the ingredient where an error is hyponatraemia. A test
that pinned the current strings would pin the defect, so this file names it instead; the repair is
claimed in `to-do-lists/tarik.md` on 2026-11-10 and is not made here.

Run: python3 tests/test_ors_page_claims.py
"""

import re
import unittest
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "docs" / "works" / "ors.html"

NACL_G_PER_MOL = 58.44      # NaCl, the salt the page's recipe calls for
SUCROSE_G_PER_MOL = 342.3   # sucrose; sucrase splits it into glucose + fructose, 1:1
WHO_PACKET_NA_MMOL = 75.0   # WHO reduced-osmolarity ORS


def page_text() -> str:
    return PAGE.read_text(encoding="utf-8")


def inline_script(html: str) -> str:
    blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>", html)
    assert len(blocks) == 1, f"expected exactly one inline script, found {len(blocks)}"
    return blocks[0]


class OrsBaseRatios(unittest.TestCase):
    """The calculator's per-litre ratios. Move one of these and the whole page moves."""

    def setUp(self):
        self.code = inline_script(page_text())

    def test_salt_ratio_is_pinned(self):
        m = re.search(r"saltGrams\s*=\s*\(([\d.]+)\s*\*\s*ratio\)", self.code)
        self.assertIsNotNone(m, "no saltGrams = (X * ratio) in the inline script")
        self.assertEqual(float(m.group(1)), 2.6)

    def test_sugar_ratio_is_pinned(self):
        m = re.search(r"sugarGrams\s*=\s*\(([\d.]+)\s*\*\s*ratio\)", self.code)
        self.assertIsNotNone(m, "no sugarGrams = (X * ratio) in the inline script")
        self.assertEqual(float(m.group(1)), 25.0)

    def test_spoon_conversions_agree_with_the_gram_ratios(self):
        # The page tells a field user "1/2 tsp salt, 6 tsp sugar per litre". Those are only the
        # same instruction as 2.6 g / 25.0 g if salt is ~5.2 g per teaspoon and sugar ~4.2 g.
        salt_tsp = re.search(r"const\s+saltTsp\s*=\s*([\d.]+)\s*\*\s*ratio", self.code)
        sugar_tsp = re.search(r"const\s+sugarTsp\s*=\s*([\d.]+)\s*\*\s*ratio", self.code)
        self.assertIsNotNone(salt_tsp, "no saltTsp = X * ratio in the inline script")
        self.assertIsNotNone(sugar_tsp, "no sugarTsp = X * ratio in the inline script")
        salt_g_per_tsp = 2.6 / float(salt_tsp.group(1))
        sugar_g_per_tsp = 25.0 / float(sugar_tsp.group(1))
        self.assertAlmostEqual(salt_g_per_tsp, 5.2, delta=0.1,
                               msg="a level teaspoon of salt is ~5.2 g")
        self.assertAlmostEqual(sugar_g_per_tsp, 4.17, delta=0.1,
                               msg="a level teaspoon of granulated sugar is ~4.2 g")


class SodiumFootnote(unittest.TestCase):
    """The † note: 2.5–3.0 g of salt per litre is 43–51 mmol/L, ~60% of a WHO packet."""

    def setUp(self):
        self.html = page_text()

    def test_each_stated_conversion_is_the_arithmetic_of_its_own_recipe(self):
        pairs = re.findall(r"([\d.]+)\s*g/L gives[^,<]*<strong>(\d+)", self.html)
        self.assertGreaterEqual(len(pairs), 3,
                                "the sodium note's three conversions were not found")
        for grams, stated in pairs:
            expected = float(grams) / NACL_G_PER_MOL * 1000.0
            self.assertAlmostEqual(float(stated), expected, delta=1.0,
                                   msg=f"{grams} g/L of NaCl should be ~{expected:.0f} mmol/L")

    def test_the_percentage_claim_follows_from_the_middle_of_the_spoon_range(self):
        m = re.search(r"roughly\s*<strong>(\d+)%\s*of the sodium</strong>", self.html)
        self.assertIsNotNone(m, "the '~X% of the sodium' claim was not found")
        stated = float(m.group(1))
        # The note's own middle figure for half a level teaspoon in a litre.
        mid = re.search(r"2\.6\s*g/L gives\s*<strong>(\d+)</strong>", self.html)
        self.assertIsNotNone(mid, "the note's 2.6 g/L figure was not found")
        expected = float(mid.group(1)) / WHO_PACKET_NA_MMOL * 100.0
        self.assertLessEqual(abs(stated - expected), 2.0,
                             f"stated {stated:.0f}%, implied {expected:.1f}%")

    def test_the_footnote_quotes_the_calculator_rather_than_a_remembered_number(self):
        # If the calculator's salt ratio moves off 2.6, this note's arithmetic is describing a
        # recipe the page no longer gives. Tie the two together instead of trusting both.
        code = inline_script(self.html)
        ratio = float(re.search(r"saltGrams\s*=\s*\(([\d.]+)\s*\*\s*ratio\)", code).group(1))
        grams = [float(g) for g, _ in re.findall(r"([\d.]+)\s*g/L gives[^,<]*<strong>(\d+)",
                                                self.html)]
        self.assertLessEqual(min(grams), ratio)
        self.assertGreaterEqual(max(grams), ratio)


class HomeMixTableRow(unittest.TestCase):
    """The 'Safe Field Mix' row. Ported because the .mjs check for it cannot run here."""

    def setUp(self):
        self.html = page_text()
        m = re.search(r"<tr>(?:(?!</tr>)[\s\S])*Canonical Home Recipe \(SSS\)"
                      r"(?:(?!</tr>)[\s\S])*</tr>", self.html)
        self.assertIsNotNone(m, "the home-mix table row was not found")
        self.row = m.group(0)

    def test_row_states_corrected_sodium_not_the_superseded_figure(self):
        na = re.search(r"~(\d+)\s*[–-]\s*(\d+)", self.row)
        self.assertIsNotNone(na, "the row states no sodium range")
        lo, hi = float(na.group(1)), float(na.group(2))
        self.assertTrue(40 <= lo <= 43 and 50 <= hi <= 52,
                        f"row sodium range is {lo:g}-{hi:g}; the corrected range is ~43-51")

    def test_printed_osmolarity_brackets_the_arithmetic_of_the_row(self):
        na = re.search(r"~(\d+)\s*[–-]\s*(\d+)", self.row)
        sucrose = re.search(r"\((\d+(?:\.\d+)?)\s*g sucrose\)", self.row)
        osm = re.search(r"(\d+)\s*[–-]\s*(\d+)\s*mOsm/L", self.row)
        self.assertIsNotNone(sucrose, "the row states no sucrose mass")
        self.assertIsNotNone(osm, "the row states no total osmolarity")
        glucose = float(sucrose.group(1)) / SUCROSE_G_PER_MOL * 1000.0
        self.assertAlmostEqual(glucose, 73.0, delta=1.5,
                               msg="25 g/L sucrose is ~73 mmol/L of glucose (and of fructose)")
        implied_lo = 2 * float(na.group(1)) + 2 * glucose
        implied_hi = 2 * float(na.group(2)) + 2 * glucose
        printed_lo, printed_hi = float(osm.group(1)), float(osm.group(2))
        self.assertLessEqual(printed_lo, implied_lo,
                             f"printed {printed_lo:g} mOsm/L does not cover ~{implied_lo:.0f}")
        self.assertGreaterEqual(printed_hi, implied_hi,
                                f"printed {printed_hi:g} mOsm/L does not reach ~{implied_hi:.0f}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
