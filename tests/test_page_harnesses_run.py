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

import json
import os
import shutil
import subprocess
import tempfile
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
    """The harnesses, by the naming convention: `test_*.mjs` and `validate_*.mjs`.

    Everything else in tests/ that ends in .mjs is a module the harnesses import — `retraction_voice.mjs`,
    `harness_net.mjs` — and running a module proves nothing. Distinguishing them by name rather than by
    reading for `export` is deliberate: `harness_net.mjs` exports and also has a CLI, so every content
    heuristic that tried to classify it was wrong in one direction or the other.
    """
    return sorted(p for p in HARNESSES.glob("*.mjs")
                  if p.name.startswith(("test_", "validate_")))


def text_of(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def is_library(text: str) -> bool:
    """A module the harnesses import: it exports and decides nothing, so running it proves nothing."""
    return "export function" in text and "process.exit" not in text


# Which harness runs where, said in one place instead of inferred from the source.
#
# 2026-11-27, second turn: the first version classified by looking for `await fetch(`. It put
# `validate_warming_page.mjs` in the network bucket although that harness stubs the fetch and runs
# offline by default (its live branch is behind `WARMING_LIVE=1`) — so a page that could have been
# checked at every landing was being skipped, and the skip looked like a considered decision. A scan
# for a substring cannot tell a default path from a gated one. An explicit list can, and the
# completeness test below means a new harness cannot be quietly omitted from both.
OFFLINE = {
    "validate_ors_calculator.mjs": "pure arithmetic over the page's own script",
    "validate_air_quality_page.mjs": "no network at all",
    "validate_food_safety_page.mjs": "no network at all",
    "validate_co_safety_page.mjs": "reads sources JSON from the repo",
    "validate_heat_page.mjs": "pinned to heat-sources.json",
    "test_retraction_epmc.mjs": "offline checks; registry requests are refused",
    "test_retraction_registry_boundary.mjs": "offline checks; registry requests are refused",
    "test_retraction_voice.mjs": "offline checks; registry requests are refused",
    "validate_trials_page.mjs": "runs on a recorded response (HARNESS_REPLAY, see harness_net.mjs)",
    "validate_warming_page.mjs": "stubbed fetch; the live Boston figure runs only under WARMING_LIVE=1",
    "validate_recalls_page.mjs": "runs on a recorded response (HARNESS_REPLAY, see harness_net.mjs)",
}

# These four need a live API on their default path. Named so that a green run still tells the truth
# about what it did not check; `harnesses-need-a-network` is the queue item that shrinks this set.
NETWORK = {
    "validate_nonreplication_page.mjs": "three live keyless records",
    "validate_fetchable_page.mjs": "five live hosts, re-measured per run",
    "validate_retraction_page.mjs": "the registry and Europe PMC, live",
    "validate_unreported_trials_page.mjs": "the registry and Europe PMC, live",
}

REPLAY_ENV = {"validate_trials_page.mjs": "HARNESS_REPLAY",
              "validate_recalls_page.mjs": "HARNESS_REPLAY"}


def replay_fixture(path: Path) -> Path:
    return HARNESSES / "fixtures" / (path.stem + ".replay.json")


def run(path: Path, env=None):
    return subprocess.run([NODE, str(path)], capture_output=True, text=True,
                          cwd=str(ROOT), timeout=TIMEOUT, env=env)


class TheHarnessesActuallyRun(unittest.TestCase):
    def setUp(self):
        if not NODE:
            self.skipTest("no node on PATH: these harnesses have not been run on this machine and "
                          "this file will not pretend otherwise")

    def test_every_offline_harness_exits_zero_and_says_something(self):
        ran, failed, silent = [], [], []
        for path in harnesses():
            if path.name not in OFFLINE:
                continue
            env = None
            if path.name in REPLAY_ENV:
                fixture = replay_fixture(path)
                self.assertTrue(fixture.is_file(),
                                "%s runs on a recorded response and has no record at %s: record one "
                                "with HARNESS_RECORD=%s node %s"
                                % (path.name, fixture, fixture, path.name))
                env = dict(os.environ, HARNESS_REPLAY=str(fixture.relative_to(ROOT)))
            r = run(path, env)
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
        self.assertGreaterEqual(len(ran), 10,
                                "only %d offline harness(es) ran: the set is shrinking, and the "
                                "pages they guard are then checked by nothing" % len(ran))

    def test_a_replay_that_disagrees_with_the_page_can_actually_fail(self):
        """The proof the replay is not theatre: break the record, the harness must go red.

        Found while writing the first one, 2026-11-27: the trials harness passed every check against
        a fixture cut from 50 studies to 3, because its claims are all "at least one" and "some". A
        replay whose strength depends on a record nobody verified is a green light wired to nothing.
        The harness now pins that the record fills the requested page, and this test proves the pin
        bites — by mutating a copy, never the repository's record.
        """
        fixture = HARNESSES / "fixtures" / "validate_trials_page.replay.json"
        if not fixture.is_file():
            self.skipTest("no trials record to mutate")
        record = json.loads(fixture.read_text(encoding="utf-8"))
        studies = (record.get("body") or {}).get("studies")
        if not isinstance(studies, list) or len(studies) < 5:
            self.skipTest("the record's shape changed; this test names `body.studies` explicitly")
        with tempfile.TemporaryDirectory() as td:
            broken = Path(td) / "broken.replay.json"
            record["body"]["studies"] = studies[:3]
            broken.write_text(json.dumps(record), encoding="utf-8")
            r = run(HARNESSES / "validate_trials_page.mjs", dict(os.environ, HARNESS_REPLAY=str(broken)))
        self.assertNotEqual(r.returncode, 0,
                            "a record trimmed to 3 studies still passed: the replay asserts nothing "
                            "about how much of the world it is looking at")
        self.assertIn("FAIL", (r.stdout or "") + (r.stderr or ""))

    def test_the_recalls_replay_can_fail_too(self):
        """Same proof for the route-table record: trim the 2,000-row sample, the harness goes red.

        The recalls harness records seven urls because the page builds its own queries; its strongest
        claim about the world is "over a 2,000-row sample of the whole drug record, every row carries
        a start date". A record that answers with three rows must fail that claim rather than pass it.
        """
        fixture = HARNESSES / "fixtures" / "validate_recalls_page.replay.json"
        if not fixture.is_file():
            self.skipTest("no recalls record to mutate")
        record = json.loads(fixture.read_text(encoding="utf-8"))
        routes = record.get("responses") or {}
        whole = [u for u in routes if "search=&limit=1000" in u]
        if len(whole) < 2:
            self.skipTest("the record no longer holds the two whole-index pages this test trims")
        with tempfile.TemporaryDirectory() as td:
            broken = Path(td) / "broken.replay.json"
            body = json.loads(routes[whole[1]]["body"])
            body["results"] = body["results"][:3]
            routes[whole[1]]["body"] = json.dumps(body)
            broken.write_text(json.dumps(record), encoding="utf-8")
            r = run(HARNESSES / "validate_recalls_page.mjs",
                    dict(os.environ, HARNESS_REPLAY=str(broken)))
        self.assertNotEqual(r.returncode, 0,
                            "a whole-index page trimmed to 3 rows still passed: the sample-size "
                            "claim is not pinned by anything")
        self.assertIn("FAIL", (r.stdout or "") + (r.stderr or ""))

    def test_a_record_the_page_no_longer_asks_for_is_reported(self):
        """The other direction: an unused url means the capture is stale and looks healthy."""
        fixture = HARNESSES / "fixtures" / "validate_recalls_page.replay.json"
        if not fixture.is_file():
            self.skipTest("no recalls record to extend")
        record = json.loads(fixture.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as td:
            stale = Path(td) / "stale.replay.json"
            record.setdefault("responses", {})["https://api.fda.gov/drug/enforcement.json?search=nobody-asks-this"] = \
                {"status": 200, "body": '{"results": []}'}
            stale.write_text(json.dumps(record), encoding="utf-8")
            r = run(HARNESSES / "validate_recalls_page.mjs",
                    dict(os.environ, HARNESS_REPLAY=str(stale)))
        self.assertNotEqual(r.returncode, 0,
                            "the record answered a url this run never asked for and the harness "
                            "still exited 0: a stale capture would look like a passing one")

    def test_the_network_ones_are_named_rather_than_skipped_in_silence(self):
        self.assertGreaterEqual(len(NETWORK), 1, "no harness reaches the network: the split changed")
        for name, why in sorted(NETWORK.items()):
            self.assertTrue(why, "%s is in NETWORK with no reason written down" % name)

    def test_every_harness_is_in_exactly_one_list(self):
        """The lists are the classification; a harness in neither is one nobody decided about.

        This is the assertion that replaces guessing from the source. It also refuses a harness in
        both, which would mean running a live check at landing time by accident.
        """
        on_disk = {p.name for p in harnesses()}
        self.assertEqual(sorted(on_disk - set(OFFLINE) - set(NETWORK)), [],
                         "harness(es) classified as neither offline nor network — decide, and write "
                         "the reason beside the name in this file")
        self.assertEqual(sorted(set(OFFLINE) & set(NETWORK)), [],
                         "harness(es) in both lists")
        self.assertEqual(sorted((set(OFFLINE) | set(NETWORK)) - on_disk), [],
                         "listed harness(es) that are not on disk")

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
