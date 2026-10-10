#!/usr/bin/env python3
# Owner: Desi (2026-10-10)
"""The no-JavaScript display on docs/works/thermal.html must agree with the page's own calculator.

Why this exists. The Warm Room page renders its result panel as static HTML and then, on load,
overwrites it from an inline script (`updateThermalModel()`). That gives two copies of the same
number, and nothing kept them equal. On 2026-10-10 the static copy read `54.5 °F (12.5 °C)` /
`+22.5 °F` while the calculator, at exactly its own default settings (2 occupants, table fort,
heavy blankets, 32 °F ambient), computed `48.8 °F` / `+16.8 °F` — and 22.5 °F was not producible by
any of the calculator's 80 combinations. A reader without JavaScript, or reading the page source, or
a printed or archived copy, saw a shelter about 6 °F warmer than the page's own model claims. A
temperature a safety page overstates by 6 °F is a defect, not a rounding difference.

What this pins. Read the page's own default selections and ambient value, read the page's own
watts / area / R tables out of the inline script, compute the default result, and assert the static
text equals what the script would write. If someone edits one copy and not the other, this fails.

Offline. Standard library only.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "docs" / "works" / "thermal.html"


def _selected_option(html: str, select_id: str) -> str:
    block = re.search(r'id="%s"(.*?)</select>' % re.escape(select_id), html, re.S)
    assert block, f"{select_id} not found"
    opt = re.search(r'<option value="([^"]+)"[^>]*\bselected', block.group(1))
    assert opt, f"no default option marked selected in {select_id}"
    return opt.group(1)


def _input_value(html: str, input_id: str) -> str:
    m = re.search(r'id="%s"[^>]*\bvalue="([^"]+)"' % re.escape(input_id), html)
    assert m, f"{input_id} not found"
    return m.group(1)


def _case_table(html: str, var: str) -> dict:
    """Pull `case '<key>': <var> = <number>;` out of the inline script."""
    pairs = re.findall(r"case\s+'([^']+)':\s*%s\s*=\s*([0-9.]+)\s*;" % re.escape(var), html)
    assert pairs, f"no case table for {var}"
    return {k: float(v) for k, v in pairs}


def _static_text(html: str, element_id: str) -> str:
    m = re.search(r'id="%s">([^<]*)</div>' % re.escape(element_id), html)
    assert m, f"{element_id} not found"
    return m.group(1).strip()


def _survival(inside_f: float):
    """Mirror the page's own survival branches."""
    if inside_f >= 60:
        return ("Optimal Thermal Comfort (Low Hypothermia Risk)",
                "Light winter blankets sufficient. Body easily maintains core equilibrium.")
    if inside_f >= 45:
        return ("Viable Long-Term Shelter (Manageable Cold Stress)",
                "Requires standard sleeping bags or dry wool layers. Minimal metabolic shivering required.")
    if inside_f >= 32:
        return ("Challenging Cold (Requires High-Grade Sleeping Bags)",
                "Must wear dry thermal base layers, wool hats, and remain insulated off the floor. "
                "Do not sleep in damp garments.")
    return ("High Hypothermia Risk (Severe Thermal Drain)",
            "Microclimate is inadequate. Reduce enclosure volume further (e.g. shrink from room to "
            "tent/table) or add more insulation layers.")


class ThermalStaticDefaults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        occ = _selected_option(cls.html, "calcOccupants")
        shelter = _selected_option(cls.html, "calcShelterType")
        insulation = _selected_option(cls.html, "calcInsulation")
        cls.watts = _case_table(cls.html, "watts")[occ]
        cls.area = _case_table(cls.html, "areaSqFt")[shelter]
        cls.rval = _case_table(cls.html, "rVal")[insulation]
        cls.ambient = float(_input_value(cls.html, "calcAmbient"))
        cls.btu = cls.watts * 3.41214
        cls.delta = cls.btu * cls.rval / cls.area
        cls.inside_f = cls.ambient + cls.delta

    def test_the_page_and_its_script_are_both_present(self):
        self.assertIn("updateThermalModel", self.html)
        self.assertIn('id="resInsideTemp"', self.html)

    def test_static_interior_temperature_matches_the_calculator(self):
        want = f"{self.inside_f:.1f} \u00b0F ({((self.inside_f - 32) * 5 / 9):.1f} \u00b0C)"
        self.assertEqual(_static_text(self.html, "resInsideTemp"), want)

    def test_static_temperature_difference_matches_the_calculator(self):
        want = (f"+{self.delta:.1f} \u00b0F (+{(self.delta * 5 / 9):.1f} \u00b0C) "
                "above room temperature")
        self.assertEqual(_static_text(self.html, "resTempDiff"), want)

    def test_static_survival_assessment_matches_the_branch_the_script_would_pick(self):
        title, sub = _survival(self.inside_f)
        self.assertEqual(_static_text(self.html, "resSurvival"), title)
        self.assertEqual(_static_text(self.html, "resSurvivalSub"), sub)

    def test_the_known_bad_figure_is_not_reachable_by_the_calculator(self):
        """22.5 °F was the old static default; no combination of the page's own inputs produces it."""
        producible = {
            round(w * 3.41214 * r / a, 2)
            for w in _case_table(self.html, "watts").values()
            for r in _case_table(self.html, "rVal").values()
            for a in _case_table(self.html, "areaSqFt").values()
        }
        self.assertNotIn(22.5, producible)


if __name__ == "__main__":
    unittest.main(verbosity=2)
