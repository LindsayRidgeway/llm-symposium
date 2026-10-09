#!/usr/bin/env python3
"""The Warm Room calculator: its no-JS fallback must equal its own model.

Why this exists (2026-10-09, Desi — the first cross-amigo review recorded in
`channels/item_ledger.py`). `docs/works/thermal.html` renders a microclimate
calculator in JavaScript. The result panel is *also* written as static HTML, so a
reader whose browser does not run the script sees a number anyway. Until this
test, those two disagreed: the static panel showed `54.5 °F`, `+22.5 °F` and a
survival phrase the script never emits, none of which the model produces for its
own default inputs (2 occupants, table fort, R-3.0, 32 °F ambient -> 48.8 °F,
+16.8 °F, "Manageable Cold Stress"). The script overwrote them on load, so a
JavaScript visitor never saw the stale values — only a reader without it, and
every crawler and text extractor, did.

The test does not hard-code the answer. It reads the calculator's own constants
out of the page (the three switch tables, which `<option>` is `selected`, and the
ambient `<input>` default), recomputes the JS `updateThermalModel()` model in
Python, and asserts the static fallback panel matches what the script would have
written. Change a default, a wattage, an R-value or an area and this fails — which
is the point: the two views of one number cannot drift again.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "works" / "thermal.html"

# The survival bands, copied from updateThermalModel(). Each is (lower_bound, value, sub).
# Order matters: the first band whose lower bound the inside temperature meets wins.
BANDS = [
    (60, "Optimal Thermal Comfort (Low Hypothermia Risk)",
     "Light winter blankets sufficient. Body easily maintains core equilibrium."),
    (45, "Viable Long-Term Shelter (Manageable Cold Stress)",
     "Requires standard sleeping bags or dry wool layers. Minimal metabolic shivering required."),
    (32, "Challenging Cold (Requires High-Grade Sleeping Bags)",
     "Must wear dry thermal base layers, wool hats, and remain insulated off the floor. "
     "Do not sleep in damp garments."),
    (float("-inf"), "High Hypothermia Risk (Severe Thermal Drain)",
     "Microclimate is inadequate. Reduce enclosure volume further (e.g. shrink from room to "
     "tent/table) or add more insulation layers."),
]


def _values(html: str, var: str) -> dict[str, float]:
    """Read a JS switch table: `case 'key': <var> = <number>;`."""
    return {m.group(1): float(m.group(2))
            for m in re.finditer(rf"case '([^']+)':\s*{var} = ([\d.]+);", html)}


def _selected(html: str, select_id: str) -> str:
    block = re.search(rf'<select id="{select_id}">(.*?)</select>', html, re.S).group(1)
    m = re.search(r'<option value="([^"]+)"[^>]*\bselected', block)
    assert m, f"no option is selected in #{select_id}"
    return m.group(1)


def _static_text(html: str, el_id: str) -> str:
    return re.search(rf'id="{el_id}">([^<]*)<', html).group(1)


class TestWarmRoomDefaults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text()

    def _model_default(self) -> dict[str, str]:
        """Recompute updateThermalModel() for the panel's own default inputs."""
        watts_map = _values(self.html, "watts")
        area_map = _values(self.html, "areaSqFt")
        r_map = _values(self.html, "rVal")

        watts = watts_map[_selected(self.html, "calcOccupants")]
        area = area_map[_selected(self.html, "calcShelterType")]
        r_val = r_map[_selected(self.html, "calcInsulation")]
        ambient = float(re.search(r'id="calcAmbient" value="([-\d.]+)"', self.html).group(1))

        btu_hr = watts * 3.41214
        d_t = btu_hr * r_val / area
        inside_f = ambient + d_t
        inside_c = (inside_f - 32) * 5 / 9

        band = next(b for b in BANDS if inside_f >= b[0])
        return {
            "resInsideTemp": f"{inside_f:.1f} \u00b0F ({inside_c:.1f} \u00b0C)",
            "resTempDiff": f"+{d_t:.1f} \u00b0F (+{d_t * 5 / 9:.1f} \u00b0C) above room temperature",
            "resWatts": f"{watts:.0f} Watts ({btu_hr:.0f} BTU/hr)",
            "resSurvival": band[1],
            "resSurvivalSub": band[2],
        }

    def test_defaults_are_the_pinned_scenario(self):
        """If a default changes, the reviewer's arithmetic is what must be re-run."""
        self.assertEqual(_selected(self.html, "calcOccupants"), "2")
        self.assertEqual(_selected(self.html, "calcShelterType"), "table_fort")
        self.assertEqual(_selected(self.html, "calcInsulation"), "heavy_blankets")
        self.assertEqual(re.search(r'id="calcAmbient" value="([-\d.]+)"', self.html).group(1), "32")

    def test_static_fallback_matches_the_model(self):
        expected = self._model_default()
        for el_id, want in expected.items():
            got = _static_text(self.html, el_id)
            self.assertEqual(got, want, f"#{el_id} static fallback ≠ model default for # {el_id}")

    def test_the_stale_values_are_gone(self):
        """The three values the page used to show for its default inputs."""
        model = self._model_default()
        self.assertNotIn("54.5 \u00b0F", self.html)
        self.assertNotIn("+22.5 \u00b0F", self.html)
        # 'Low Hypothermia Risk' survives only inside the 60 °F-and-above band's own label.
        self.assertEqual(model["resSurvival"], "Viable Long-Term Shelter (Manageable Cold Stress)")


if __name__ == "__main__":
    unittest.main()
