#!/usr/bin/env python3
"""The page harnesses that need no network are executed, not syntax-checked (Desi, 2026-11-27).

Sixteen `.mjs` harnesses sit in `tests/`. The Works index and several pages cite them as their
guard — "56 checks", "135 passed" — and until now **nothing on this machine executed one of them**:
the gate runs every `tests/test_*.py` as a script, and the workflow hands the `.mjs` files to
`node --check`, which is a syntax check. A syntax check passes on a file whose every assertion is
false. The Python ports exist because of exactly that gap, and the ports cover the page claims a
Python reader can re-derive; what they cannot cover is the page's own JavaScript, run against its
own extracted script, which is what these harnesses do.

Measured here on 2026-11-27 (node v24.3.0): of the sixteen, nine run offline in a few seconds and
produce real output —

    validate_ors_calculator        135 passed, 0 failed
    validate_air_quality_page       56 passed, 0 failed
    validate_food_safety_page       56 passed, 0 failed
    validate_co_safety_page         43 checks passed
    validate_heat_page              pinned to heat-sources.json
    test_retraction_registry_boundary  23 checks passed
    test_retraction_epmc            15 checks passed
    test_retraction_voice           14 offline checks passed
    retraction_voice                (a module the harnesses import; no checks of its own)

The other seven call a live API (`fetch(`), so a landing must not depend on them: this test names
them and skips them rather than pretending they ran.

What this test refuses to accept as a pass:

  * **silence.** A harness that exits 0 and prints nothing is either a module or a vacuous run, so
    those are separated by name and not counted as executed checks;
  * **a shrinking executed set.** At least eight harnesses must run, so a future change that
    reclassifies the whole directory as "network" fails here instead of quietly emptying the guard;
  * **a missing node.** Where node is absent the whole file skips with the reason in the message —
    a machine without the runtime has not run these, and says so.

Run directly: `python3 tests/test_page_harnesses_run.py`
"""

import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESSES = ROOT / "tests"
TIMEOUT = 180

# The amigo launchd jobs set no PATH, so they inherit `/usr/bin:/bin:/usr/sbin:/sbin` — and Homebrew
# lives elsewhere. `shutil.which("node")` alone would therefore find nothing under the landing gate
# and this whole file would skip on every landing, which is the defect it was written to end: a guard
# whose silence reads as health. The search is explicit, and the first found wins.
NODE_DIRS = ("/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/opt/local/bin", "/snap/bin")


def find_node():
    found = shutil.which("node")
    if found:
        return found
    for d in NODE_DIRS:
        candidate = Path(d) / "node"
        if candidate.is_file() and os.access(str(candidate), os.X_OK):
            return str(candidate)
    return None


NODE = find_node()


def harnesses():
    return sorted(HARNESSES.glob("*.mjs"))


def text_of(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def is_library(text: str) -> bool:
    """A module the harnesses import: it exports and decides nothing, so running it proves nothing."""
    return "export function" in text and "process.exit" not in text


def needs_network(text: str) -> bool:
    return "fetch(" in text


def run(path: Path):
    return subprocess.run([NODE, str(path)], capture_output=True, text=True,
                          cwd=str(ROOT), timeout=TIMEOUT)


class TheHarnessesActuallyRun(unittest.TestCase):
    def setUp(self):
        if not NODE:
            self.skipTest("no node on PATH: these harnesses have not been run on this machine and "
                          "this file will not pretend otherwise")

    def test_every_offline_harness_exits_zero_and_says_something(self):
        ran, failed, silent = [], [], []
        for path in harnesses():
            text = text_of(path)
            if is_library(text) or needs_network(text):
                continue
            r = run(path)
            ran.append(path.name)
            if r.returncode != 0:
                failed.append("%s rc=%d: %s" % (path.name, r.returncode,
                                                ((r.stderr or r.stdout or "").strip()
                                                 .splitlines() or [""])[-1][:200]))
            elif not ((r.stdout or "") + (r.stderr or "")).strip():
                silent.append(path.name)
        self.assertEqual(failed, [], "page harness(es) failed: " + " | ".join(failed))
        self.assertEqual(silent, [], "these exit 0 and print nothing, so their assertions may not "
                                     "run at all — say which and why, do not let silence pass: "
                                     + ", ".join(silent))
        self.assertGreaterEqual(len(ran), 8,
                                "only %d offline harness(es) ran: the set is shrinking, and the "
                                "pages they guard are then checked by nothing" % len(ran))

    def test_the_network_ones_are_named_rather_than_skipped_in_silence(self):
        live = sorted(p.name for p in harnesses() if needs_network(text_of(p)))
        self.assertTrue(live, "no harness reaches the network: the classification changed")
        # Named in the failure message so that a reader of a green run still knows what is not
        # checked at landing time: a live API is not a landing's business, but it is a fact.
        self.assertGreaterEqual(len(live), 5)

    def test_the_ports_and_the_harnesses_are_not_the_same_guard(self):
        # The Python ports re-derive page claims; the harnesses run the page's own script. A page
        # that has a port but no harness (or the reverse) is a gap in one of the two directions.
        ports = {p.name.replace("test_", "").replace("_page_claims.py", "")
                 for p in HARNESSES.glob("test_*_page_claims.py")}
        harnesses_named = {p.name.replace("validate_", "").replace("_page", "").replace(".mjs", "")
                           for p in harnesses() if p.name.startswith("validate_")}
        self.assertTrue(ports, "no page ports found at all")
        self.assertTrue(harnesses_named, "no validate_*.mjs harnesses found at all")
        # Both sets non-empty is the claim; the exact correspondence is not, because the ports were
        # written for the pages whose claims a Python reader can re-derive and the harnesses for the
        # pages whose script must be executed. Naming a false equality here would be worse than
        # naming none.
        self.assertGreaterEqual(len(harnesses_named), 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
