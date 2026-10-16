#!/usr/bin/env python3
"""Arithmetic guard for the Literary Wing story `docs/fiction/the-fourth-power.html`.

Why this file exists. The Hard SF matrix says a story's physics "cannot be hand-waved", and
the wing's own standard is that "an error in delta-V, angular momentum, or heat dissipation
is an unambiguous, measurable error". But nothing in the repository recomputes a story's
numbers: `Dead Band` will keep its granular arithmetic and `Round-Trip Time` its light-lag
arithmetic whether or not either page ever changes, because no checker reads them. A story
whose central number drifts by a factor of four is exactly as green as one that is correct.

So this file recomputes every figure the story turns on, from the story's own machine-readable
constants, and fails if any number quoted in the prose or the figure table stops matching.

What it checks:
  1. the page declares its constants in one JSON block, and this test parses that block rather
     than re-declaring the constants in Python (so the page is the single source of truth);
  2. Q = emissivity * sigma * area * T^4 reproduces, to the printed rounding, the two banks'
     ceiling rejections, their per-square-metre rates, the total ratio and the per-m^2 ratio;
  3. the equilibrium temperature of the kept-bank branch is 884.7 K (the page's 885 K), and the
     broad bank's required 751.8 K is past its 500 K ceiling;
  4. the runaway rate, the fuse length and the ending's headroom/shortfall are the page's;
  5. those figures, as printed, are actually present in the page — both as numeral (figure
     table) and as English words (prose), because the story states them twice, deliberately;
  6. the fiction index still links the story and marks the Dmitri row Delivered.

Run: python3 tests/test_fiction_fourth_power.py
"""

import json
import math
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(REPO, "docs", "fiction", "the-fourth-power.html")
INDEX = os.path.join(REPO, "docs", "fiction", "index.html")

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print("  ok: %s" % name)
    else:
        FAILURES.append(name)
        print("  FAIL: %s %s" % (name, detail))


def main():
    for path in (PAGE, INDEX):
        if not os.path.exists(path):
            print("  FAIL: missing %s" % path)
            return 1

    html = open(PAGE, encoding="utf-8").read()
    index = open(INDEX, encoding="utf-8").read()

    # --- 1. the page's own constants -----------------------------------------------------
    m = re.search(
        r'<script\s+type="application/json"\s+id="thermal-constants">(.*?)</script>',
        html, re.S)
    check("the page declares a machine-readable `thermal-constants` JSON block", m is not None)
    if not m:
        return 1
    try:
        C = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        check("the constants block is valid JSON", False, str(e))
        return 1
    check("the constants block is valid JSON", True)

    sigma = C["sigma_w_m2_k4"]
    eps = C["emissivity"]
    a_n, t_n = C["bank_narrow"]["area_m2"], C["bank_narrow"]["ceiling_k"]
    a_b, t_b = C["bank_broad"]["area_m2"], C["bank_broad"]["ceiling_k"]
    idle = C["plant_idle_waste_w"]
    cutting = C["plant_cutting_waste_w"]
    cap = C["hull_heat_capacity_j_per_k"]
    rise = C["cook_rise_k"]

    check("the two ceilings stand in a ratio of exactly two (the story's whole hinge)",
          abs(t_n / t_b - 2.0) < 1e-12, "%s / %s" % (t_n, t_b))
    check("the narrow bank is smaller than the broad one (so 'bigger' is the tempting error)",
          a_n < a_b, "%s < %s" % (a_n, a_b))

    def q(area, temp):
        return eps * sigma * area * temp ** 4

    def t_for(area, watts):
        return (watts / (eps * sigma * area)) ** 0.25

    q_n = q(a_n, t_n)                       # narrow bank at its ceiling, W
    q_b = q(a_b, t_b)                       # broad bank at its ceiling, W
    per_n = q_n / a_n                       # W/m^2
    per_b = q_b / a_b
    ratio_total = q_n / q_b
    ratio_per_m2 = per_n / per_b

    keep_narrow = t_for(a_n, idle)          # K, equilibrium if the narrow bank is kept
    keep_broad = t_for(a_b, idle)           # K, equilibrium the broad bank would need
    shortfall = idle - q_b                  # W, heat the idle plant puts in when only B is kept
    rate = shortfall / cap                  # K/s
    fuse_min = (rise / rate) / 60.0         # min to the cook-the-crew rise

    # The ending's numbers: idle headroom on the kept bank, and what the torch adds to it.
    headroom = q_n - idle                   # W
    torch_extra = cutting - idle            # W
    ceiling_left = t_n - keep_narrow        # K
    # With both banks and the broad bank pinned at its bond limit, the narrow bank carries the
    # remainder of the cutting load at:
    narrow_at_cut = t_for(a_n, cutting - q_b)
    narrow_margin_at_cut = t_n - narrow_at_cut

    # --- 2. the law reproduces the story's headline figures ------------------------------
    check("narrow bank at 1000 K rejects 1225 kW (page: '1225')",
          abs(q_n / 1000.0 - 1225.0) < 0.5, "%.1f kW" % (q_n / 1000.0))
    check("broad bank at 500 K rejects 147 kW (page: '147')",
          abs(q_b / 1000.0 - 147.0) < 0.5, "%.1f kW" % (q_b / 1000.0))
    check("the narrow bank is worth 8.3x the broad one in total (page: 'eight and a third')",
          abs(ratio_total - 8.333) < 0.02, "%.3f" % ratio_total)
    check("per square metre the ratio is the pure fourth power: exactly 16",
          abs(ratio_per_m2 - 16.0) < 1e-9, "%.6f" % ratio_per_m2)
    check("per-m^2 rates are 51.0 kW and 3.2 kW (page's figure table)",
          abs(per_n / 1000.0 - 51.0) < 0.05 and abs(per_b / 1000.0 - 3.2) < 0.05,
          "%.1f / %.1f kW" % (per_n / 1000.0, per_b / 1000.0))

    # --- 3. the two branches -----------------------------------------------------------------
    check("keeping the narrow bank settles at 884.7 K (page: '885')",
          abs(keep_narrow - 884.7) < 0.5, "%.1f K" % keep_narrow)
    check("keeping the broad bank would need 751.8 K, well past its 500 K bond ceiling",
          abs(keep_broad - 751.8) < 0.5 and keep_broad > t_b, "%.1f K" % keep_broad)
    check("at its 500 K ceiling the broad bank is short by 603 kW (page: 'six hundred and three')",
          abs(shortfall / 1000.0 - 603.0) < 0.5, "%.1f kW" % (shortfall / 1000.0))

    # --- 4. the fuse -----------------------------------------------------------------------
    check("runaway is 0.043 K/s on the page's own hull capacity (page: 'nought-point-nought-four-three')",
          abs(rate - 0.0431) < 0.0005, "%.5f K/s" % rate)
    check("that is 2.6 K/min (page: 'Two-point-six kelvin a minute')",
          abs(rate * 60 - 2.586) < 0.01, "%.3f K/min" % (rate * 60))
    check("40 K arrives in fifteen minutes (page: 'fifteen minutes')",
          abs(fuse_min - 15.47) < 0.1, "%.2f min" % fuse_min)

    # --- 5. the ending's arithmetic ----------------------------------------------------------
    check("idle headroom on the kept bank is 475 kW (page: 'four hundred and seventy-five kilowatts')",
          abs(headroom / 1000.0 - 475.0) < 0.5, "%.1f kW" % (headroom / 1000.0))
    check("the torch wants 550 kW more than idle (page: 'five hundred and fifty')",
          abs(torch_extra / 1000.0 - 550.0) < 0.5, "%.1f kW" % (torch_extra / 1000.0))
    check("the shortfall that ends the voyage is 75 kW, so the claim is permanently unreachable",
          abs((torch_extra - headroom) / 1000.0 - 75.0) < 0.5,
          "%.1f kW" % ((torch_extra - headroom) / 1000.0))
    check("ceiling left is 115 K (page: 'one hundred and fifteen kelvin of ceiling left')",
          abs(ceiling_left - 115.0) < 1.0, "%.1f K" % ceiling_left)
    check("with both banks the cut ran the narrow bank at 985 K, fifteen under its ceiling",
          abs(narrow_at_cut - 985.0) < 1.0 and abs(narrow_margin_at_cut - 15.0) < 1.0,
          "%.1f K, margin %.1f K" % (narrow_at_cut, narrow_margin_at_cut))

    # --- 6. the numbers are printed in the page, as numerals and as words -------------------
    numerals = ["1225", "147", "51.0", "3.2", "24", "46", "1000", "500"]
    words = [
        "one point two two",                    # 1.22 MW, the kept bank's ceiling
        "one point three megawatts",            # 1.30 MW, cutting power
        "eight and a third times",              # total ratio
        "sixteen times",                        # per-m^2 ratio
        "fifty-one kilowatts", "three-point-two",
        "eight hundred and eighty-five kelvin",  # kept-bank equilibrium
        "seven hundred and fifty-two kelvin",    # what the broad bank would need
        "six hundred and three kilowatts",       # the shortfall into the hull
        "nought-point-nought-four-three kelvin a second",
        "Two-point-six kelvin a minute",
        "fifteen minutes",
        "one hundred and fifteen kelvin of ceiling left",
        "four hundred and seventy-five kilowatts",
        "five hundred and fifty",
        "nine hundred and eighty-five",          # narrow bank at cutting power, both banks live
    ]
    for tok in numerals:
        check("the page states the numeral %r" % tok, tok in html)
    for tok in words:
        check("the page states %r" % tok, tok in html)

    # --- 7. the index agrees the slot is filled ---------------------------------------------
    check("the fiction index links the story", "the-fourth-power.html" in index)
    row = re.search(r"<td><strong>Dmitri S\. Pravdin</strong></td>(.*?)</tr>", index, re.S)
    check("the Dmitri matrix row exists", row is not None)
    if row:
        check("the row no longer reads 'Open Slot'", "Open Slot" not in row.group(1))
        check("the row is marked Delivered", "Delivered" in row.group(1))

    print()
    if FAILURES:
        print("%d FAILED: %s" % (len(FAILURES), "; ".join(FAILURES)))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
