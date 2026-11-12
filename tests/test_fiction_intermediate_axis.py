#!/usr/bin/env python3
"""Arithmetic guard for the Literary Wing story `docs/fiction/intermediate-axis.html`.

Why this file exists. The wing's rule is that a hard-SF story's physics "cannot be
hand-waved", and its own standard is that "an error in delta-V, angular momentum, or heat
dissipation is an unambiguous, measurable error". But nothing recomputes a story's numbers:
`Dead Band` keeps its granular arithmetic and `Round-Trip Time` its light-lag arithmetic
whether or not either page changes, because no checker reads them. This story turns on a
torque-free tumble, one solid motor and one corridor, so a single digit moved in the prose
would leave the plot with no reason to exist while every other test stayed green.

So this file recomputes every figure the story turns on, from the story's own
machine-readable constants, and fails if a quoted number stops matching.

What it checks:
  1. the page declares one JSON block (`attitude-constants`) and this test parses that block
     rather than re-declaring the constants here;
  2. the rocket equation reproduces the vacuum velocity change, and the stated thrust, burn
     time and mass flow agree with each other and with the exhaust velocity;
  3. the measured cone-angle law gives 6.0 degrees at the bottom of the breath and 16.0 at
     the top, with the stated 118-second period;
  4. the best ignition phase is found by integration over the whole cycle, and the story's
     two headline numbers come out of it: 723.7 m/s with the tumble as found (3.4 m/s short
     of the near wall of the corridor) and 729.1 m/s after four turns of the water (0.54
     above the requirement, 0.96 inside the far wall);
  5. the ignition window implied by the 0.09 m/s per second gradient is the page's
     06:12:36 -> 06:13:10, and the early side is the short one;
  6. the manoeuvre schedule closes: four revolutions and a settle per transfer, two transfers
     per cycle, four cycles, ending 3 minutes 21 seconds before ignition;
  7. the error bar the narrator admits to is smaller than the margin she claims, and both
     numbers are on the page;
  8. the wing index links the story, the sitemap lists it, and the printed figures appear in
     the prose as printed.

Run: python3 tests/test_fiction_intermediate_axis.py    (or python3 -m unittest tests.test_fiction_intermediate_axis)
"""

import json
import math
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(REPO, "docs", "fiction", "intermediate-axis.html")
INDEX = os.path.join(REPO, "docs", "fiction", "index.html")
SITEMAP = os.path.join(REPO, "docs", "sitemap.xml")


def load_constants():
    html = open(PAGE, encoding="utf-8").read()
    m = re.search(
        r'<script\s+type="application/json"\s+id="attitude-constants">(.*?)</script>',
        html, re.S)
    if not m:
        raise AssertionError("the page declares no `attitude-constants` JSON block")
    return json.loads(m.group(1)), html


def best_delivery(C, delta_deg):
    """Largest delivered delta-v over every ignition phase in the breathing cycle.

    The loss from a cone angle alpha is 1 - cos(alpha), so the delivered velocity change is
    the vacuum figure times the mass-weighted mean of cos(alpha) over the burn. The weight is
    dm/m: impulse early in the burn is spent on a heavier ship and buys less velocity, which
    is why the honest integral is not the time average.
    """
    ve = C["isp_s"] * C["g0_m_s2"]
    m0, prop = C["mass_ignition_kg"], C["propellant_kg"]
    mdot = C["mass_flow_kg_s"]
    burn = prop / mdot
    dv_vac = ve * math.log(m0 / (m0 - prop))
    amin, swing, period = C["alpha_min_deg"], C["alpha_swing_deg"], C["breath_period_s"]

    def mean_cos(phase):
        n = 4000
        num = den = 0.0
        for i in range(n):
            u = (i + 0.5) / n
            t = phase + u * burn
            alpha = math.radians(max(0.0, amin + swing * math.sin(math.pi * t / period) ** 2
                                     - delta_deg))
            w = mdot / (m0 - mdot * t)
            num += math.cos(alpha) * w
            den += w
        return num / den

    best = None
    steps = int(period * 10)
    for k in range(steps):
        phase = k / 10.0
        d = dv_vac * mean_cos(phase)
        if best is None or d > best[0]:
            best = (d, phase)
    return best, dv_vac, burn


class TestIntermediateAxis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.C, cls.html = load_constants()
        cls.index = open(INDEX, encoding="utf-8").read()
        cls.sitemap = open(SITEMAP, encoding="utf-8").read()

    # --- 2. the motor ------------------------------------------------------------------
    def test_rocket_equation_and_motor_consistency(self):
        C = self.C
        ve = C["isp_s"] * C["g0_m_s2"]
        self.assertAlmostEqual(ve, 2863.5, delta=0.1)
        m0, prop = C["mass_ignition_kg"], C["propellant_kg"]
        self.assertAlmostEqual(m0 - prop, 6500.0, delta=0.5)
        burn = prop / C["mass_flow_kg_s"]
        self.assertAlmostEqual(burn, 86.4, delta=0.05)
        thrust_kn = C["mass_flow_kg_s"] * ve / 1000.0
        self.assertAlmostEqual(thrust_kn, 63.0, delta=0.05)
        dv = ve * math.log(m0 / (m0 - prop))
        self.assertAlmostEqual(dv, 734.3, delta=0.05)

    def test_the_corridor_leaves_room_for_less_than_the_tumble_costs(self):
        C = self.C
        dv = self.C["isp_s"] * self.C["g0_m_s2"] * math.log(
            C["mass_ignition_kg"] / (C["mass_ignition_kg"] - C["propellant_kg"]))
        slack = (dv - C["corridor_nominal_m_s"]) + C["corridor_half_width_m_s"]
        self.assertAlmostEqual(slack, 7.2, delta=0.05)
        # the tumble as found is worth 734.3 - 723.7 of loss, which is more than the slack
        (best, _), _, _ = best_delivery(C, 0.0)
        self.assertGreater(dv - best, slack)

    # --- 3. the measured cone angle ----------------------------------------------------
    def test_cone_angle_breathes_sixteen_to_six(self):
        C = self.C
        amin, swing = C["alpha_min_deg"], C["alpha_swing_deg"]
        self.assertAlmostEqual(amin, 6.0, delta=1e-9)
        self.assertAlmostEqual(amin + swing, 16.0, delta=1e-9)
        self.assertIn("6.0&#176;", self.html.replace("°", "&#176;"))
        self.assertIn("118", self.html)

    # --- 4. the two headline numbers ---------------------------------------------------
    def test_tumble_as_found_falls_short_of_the_corridor(self):
        C = self.C
        (best, phase), dv, _ = best_delivery(C, 0.0)
        self.assertAlmostEqual(best, 723.7, delta=0.1)
        self.assertAlmostEqual(phase, 71.6, delta=0.3)
        near_wall = C["corridor_nominal_m_s"] - C["corridor_half_width_m_s"]
        self.assertAlmostEqual(near_wall - best, 3.4, delta=0.05)
        self.assertIn("723.7", self.html)
        self.assertIn("three point four", self.html)

    def test_four_turns_of_the_water_reach_inside_the_corridor(self):
        C = self.C
        delta = C["turn_per_cycle_deg"] * C["cycles"]
        self.assertAlmostEqual(delta, 3.12, delta=0.005)
        (best, phase), dv, _ = best_delivery(C, delta)
        self.assertAlmostEqual(best, 729.1, delta=0.1)
        self.assertAlmostEqual(phase, 71.9, delta=0.3)
        self.assertAlmostEqual(best - C["corridor_nominal_m_s"], 0.54, delta=0.05)
        far_wall = C["corridor_nominal_m_s"] + C["corridor_half_width_m_s"]
        self.assertAlmostEqual(far_wall - best, 0.96, delta=0.05)
        self.assertIn("729.1", self.html)
        self.assertIn("0.54", self.html)
        self.assertIn("0.96", self.html)

    def test_one_cycle_of_water_is_worth_about_a_quarter_of_the_lever(self):
        C = self.C
        lever = math.degrees((320.0 / C["mass_ignition_kg"]) * (2.4 / 1.55))
        self.assertAlmostEqual(lever, 3.4, delta=0.05)
        self.assertLess(C["turn_per_cycle_deg"], lever / 3.0)

    # --- 5. the window ------------------------------------------------------------------
    def test_ignition_window_is_thirty_three_seconds_and_lopsided(self):
        C = self.C
        delta = C["turn_per_cycle_deg"] * C["cycles"]
        (delivered, _), _, _ = best_delivery(C, delta)
        grad = C["required_gradient_m_s_per_s"]
        half = C["corridor_half_width_m_s"]
        # delivered - required must stay inside +/- half, so required is pinned to the band
        # [delivered - half, delivered + half] and the slope turns that into seconds.
        early = (C["corridor_nominal_m_s"] - (delivered - half)) / grad
        late = ((delivered + half) - C["corridor_nominal_m_s"]) / grad
        self.assertAlmostEqual(early, 10.7, delta=0.15)
        self.assertAlmostEqual(late, 22.7, delta=0.15)
        self.assertLess(early, late)
        self.assertIn("ten point seven", self.html)

        hh, mm, ss = (int(x) for x in C["ignition_utc"].split(":"))
        t0 = hh * 3600 + mm * 60 + ss
        lo = t0 - early
        hi = t0 + late

        def clock(s):
            s = int(round(s))
            return "%02d:%02d:%02d" % (s // 3600, (s % 3600) // 60, s % 60)

        self.assertEqual(clock(lo), "06:12:36")
        self.assertEqual(clock(hi), "06:13:10")
        self.assertIn("06:12:36", self.html)
        self.assertIn("06:13:10", self.html)

    # --- 6. the manoeuvre schedule ------------------------------------------------------
    def test_the_four_cycles_close_before_the_window(self):
        C = self.C
        transfer = C["revolutions_per_transfer"] * C["rotation_period_s"] + C["settle_s"]
        self.assertAlmostEqual(transfer, 177.0, delta=1e-9)
        cycle = 2 * transfer
        self.assertAlmostEqual(cycle, 354.0, delta=1e-9)
        total = cycle * C["cycles"]
        self.assertAlmostEqual(total, 1416.0, delta=1e-9)
        self.assertAlmostEqual(total / 60.0, 23.6, delta=0.05)

        hh, mm, ss = (int(x) for x in C["start_utc"].split(":"))
        start = hh * 3600 + mm * 60 + ss
        end = start + total
        self.assertEqual("%02d:%02d:%02d" % (end // 3600, (end % 3600) // 60, end % 60),
                         "06:09:26")
        hh, mm, ss = (int(x) for x in C["ignition_utc"].split(":"))
        gap = (hh * 3600 + mm * 60 + ss) - end
        self.assertEqual(gap, 201)
        self.assertIn("06:09:26", self.html)
        self.assertIn("three minutes and twenty-one seconds", self.html)

    def test_a_rotation_of_the_ship_is_gentle_at_the_berth(self):
        # the story says 3.5 cm/s^2 at 1.5 m; it is the reason nobody noticed for six hours
        w = 2 * math.pi / self.C["rotation_period_s"]
        self.assertAlmostEqual(w * w * 1.5, 0.035, delta=0.001)

    # --- 7. the error bar the narrator will not hide ------------------------------------
    def test_the_admitted_error_bar_exceeds_nothing_it_should_exceed(self):
        C = self.C
        far_wall = C["corridor_nominal_m_s"] + C["corridor_half_width_m_s"]
        (delivered, _), _, _ = best_delivery(C, C["turn_per_cycle_deg"] * C["cycles"])
        margin = far_wall - delivered
        self.assertAlmostEqual(C["error_bar_m_s"], 0.7, delta=1e-9)
        self.assertLess(C["error_bar_m_s"], margin)
        self.assertIn("0.7", self.html)

    # --- 8. provenance: printed, linked, listed -----------------------------------------
    def test_printed_figures_are_printable_strings_in_the_prose(self):
        for s in ("734.3", "728.6", "86.4", "2,863.5", "63.0", "1,900", "8,400", "6,500",
                  "0.78", "3.12", "354", "1,416", "723.7"):
            self.assertIn(s, self.html, "%r is quoted in the figure table or the prose" % s)

    def test_the_wing_index_links_the_story_and_the_sitemap_lists_it(self):
        self.assertIn('href="intermediate-axis.html"', self.index)
        self.assertIn("Intermediate Axis", self.index)
        self.assertIn(
            "https://lindsayridgeway.github.io/llm-symposium/fiction/intermediate-axis.html",
            self.sitemap)

    def test_title_and_author_are_on_the_page(self):
        self.assertIn("<title>Intermediate Axis", self.html)
        self.assertIn("Desi S. Amigo", self.html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
