#!/usr/bin/env python3
"""Pin the map from published Works pages to the JavaScript harnesses they name.

Why this file exists (measured 2026-11-25, Dmitri). Ten published Works pages tell the
reader that a named JavaScript file checks them — "Checked by
`tests/validate_retraction_page.mjs`, which runs this page's own script against the live
APIs", "pinned to `docs/works/heat-sources.json` by `tests/validate_heat_page.mjs`
(57 checks, offline)". The repository holds 12 `validate_*.mjs` files plus 4 other `.mjs`
harnesses, 16 in all, and says so honestly in one respect only: not one of them is ever
*executed* by a registered job. `.github/workflows/test-and-report.yml` runs exactly one
JavaScript step, `tests/test_mjs_validators_parse.py`, which asks Node to `node --check`
each file — a syntax check — and skips cleanly when Node is absent, which it is on this
checkout (no node, nodejs, deno or bun on PATH). So every "56 checks pass" in the record
is a claim about another machine and another day, and the number in it cannot be re-derived
here.

What that leaves, and what this test can honestly do today: a page may go on naming a
harness only while the file it names exists and still contains checks. That is the part a
guard can hold without a JavaScript runtime, and it is the part that breaks silently — a
harness renamed, emptied, or deleted leaves the page's sentence standing and false.

So this file pins:

  * MAP — the eleven pages that name a harness (ten Works pages plus `docs/works/index.html`,
    which lists nine of them), and exactly which harness each names. A page
    that gains a claim, drops one, or names a different file fails here, and the map has to
    be edited on purpose, in the same change.
  * every named harness exists under `tests/` and still contains an assertion (a `fail(`,
    `ok(`, `assert` or `throw`). Existence alone would pass on a gutted file.
  * ORPHANS — the harnesses that no page names (`validate_ors_calculator.mjs`,
    `validate_warming_page.mjs`). Pinned so that a page one day citing one of them, or a
    harness quietly losing its last citation, is visible rather than silent.
  * every `.mjs` under `tests/` is accounted for by one of the three lists above; that is
    what keeps "sixteen" true.
  * the CI registration of the parse guard and of this test.
  * and the measured fact that no registered job executes a validator. That assertion is
    deliberate friction: if someone one day registers a harness for execution, this test
    fails and the failure message says what to do — delete the assertion and amend the
    pages that claim only what actually ran.

It does not and cannot re-derive the harnesses' own arithmetic; that is the remaining half
of the value-queue item `js-harness-claims`, and it is successor work, not this file.

Run: python3 tests/test_page_harness_map.py
"""

import glob
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# page -> the harnesses it names, verbatim from the page's own text on 2026-11-25.
MAP = {
    "docs/works/air.html": ("validate_air_quality_page.mjs",),
    "docs/works/co-safety.html": ("validate_co_safety_page.mjs",),
    "docs/works/fetchable.html": ("validate_fetchable_page.mjs",),
    "docs/works/food-safety.html": ("validate_food_safety_page.mjs",),
    "docs/works/heat.html": ("validate_heat_page.mjs",),
    "docs/works/index.html": (
        "validate_air_quality_page.mjs",
        "validate_co_safety_page.mjs",
        "validate_food_safety_page.mjs",
        "validate_heat_page.mjs",
        "validate_nonreplication_page.mjs",
        "validate_recalls_page.mjs",
        "validate_retraction_page.mjs",
        "validate_trials_page.mjs",
        "validate_unreported_trials_page.mjs",
    ),
    "docs/works/nonreplication.html": ("validate_nonreplication_page.mjs",),
    "docs/works/recalls.html": ("validate_recalls_page.mjs",),
    "docs/works/retraction.html": ("validate_retraction_page.mjs",),
    "docs/works/trials.html": ("validate_trials_page.mjs",),
    "docs/works/unreported-trials.html": ("validate_unreported_trials_page.mjs",),
}

# Harnesses that exist, compile-check, and are named by no published page. Not a defect
# to fix by deleting the file: each one is real checking work whose page never says so.
ORPHANS = (
    "validate_ors_calculator.mjs",
    "validate_warming_page.mjs",
)

# `.mjs` files under tests/ that are not page harnesses at all: the retraction page's
# registry and voice checks. Listed so the total stays legible.
OTHER_HARNESSES = (
    # A module, not a harness: `tests/harness_net.mjs` answers a harness's fetch from a recorded
    # response so the page can be checked at every landing without the network (2026-11-27).
    "harness_net.mjs",
    "retraction_voice.mjs",
    "test_retraction_epmc.mjs",
    "test_retraction_registry_boundary.mjs",
    "test_retraction_voice.mjs",
)

# Pages whose harness's offline assertions have since been re-derived by a REGISTERED Python
# test, because no job here executes the `.mjs`. Keyed page -> the file under tests/ that now
# holds the same claims. A page is added here only when the port covers the harness's
# substantive offline assertions; the live-network half of a page's claim cannot be ported at
# all and closes instead by an amended claim (Dmitri's audit of 2026-11-25 splits the ten that
# way). A hybrid page can sit here for the half that ports while its amended claim covers the
# rest — fetchable.html was added on 2026-11-26 with its five live re-measurements still the
# harness's job, and its "Checked by" sentence amended in the same change to say which checks
# actually run here. This dict is the item's progress bar: six of the ten pages are ported and
# four still rest on a file nothing runs — recalls, retraction, trials and unreported-trials, all
# four named live-network in Dmitri's audit, whose honest close is an amended claim rather than a
# port — and on 2026-11-27 those four were amended in place, so no page in MAP now rests on a
# sentence nothing backs. A shorter list here is the measure of the item, nothing else. (The sentence said seven and
# named co-safety and food-safety, both of which were ported before it was corrected on
# 2026-11-26, and then named nonreplication after that was ported too: a progress bar that
# miscounts its own progress is the one kind of stale test worth a comment.)
PYTHON_REDERIVED = {
    "docs/works/air.html": "test_air_page_claims.py",
    "docs/works/co-safety.html": "test_co_safety_page_claims.py",
    "docs/works/fetchable.html": "test_fetchable_page_claims.py",
    "docs/works/food-safety.html": "test_food_safety_page_claims.py",
    "docs/works/heat.html": "test_heat_page_claims.py",
    "docs/works/nonreplication.html": "test_nonreplication_page_claims.py",
}

# The four pages whose harness checks the LIVE network, so no port can replace it: recalls,
# retraction, trials and unreported-trials. Their honest close is the other half of the item's
# condition — "or carries an amended claim saying exactly what ran" — so what is pinned here is
# that the amendment is still on the page and still says the measured thing: that no registered
# job executes the harness, that the only check is a syntax parse, and that the figures rest on
# the dated by-hand measurement instead. Both places a reader meets the claim are pinned: the
# entry page, and the one-line entry in docs/works/index.html that repeats it. A page rewritten
# back to "Checked by X, which runs…" fails here rather than reading as checked.
AMENDED_LIVE = (
    "docs/works/recalls.html",
    "docs/works/retraction.html",
    "docs/works/trials.html",
    "docs/works/unreported-trials.html",
)
AMENDMENT_MARKER = "Amended 2026-11-27"
AMENDMENT_CLAIM = "no job in this repository runs"

# The seventh offline page, and the only one whose harness no page names: `docs/works/warming.html`
# says nothing about being checked, so `validate_warming_page.mjs` sits in ORPHANS above and its 28
# `ok(...)` assertions have been a claim about a machine nobody has. (This comment said 40 and the
# port's docstring said 24 until 2026-11-27; the file was measured at 28 and the port now pins it.) Dmitri's port of 2026-11-26 re-derived
# the offline half anyway — the page's own arithmetic is a public good whether or not the page
# advertises its guard — so the port is pinned here, where the harnesses' accounting lives, rather
# than added to MAP (which would claim the page names a harness it does not). Keyed page -> port.
ORPHAN_PORTS = {
    "docs/works/warming.html": "test_warming_page_claims.py",
}

HARNESS_NAME = re.compile(r"validate_[A-Za-z0-9_]*\.mjs")
# Two shapes are in use. Some harnesses call `fail("...")` / `ok(cond)`; three of them
# (nonreplication, retraction, trials) call a `check(name, cond)` helper that increments a
# `fail` counter. Either is a check; a file with neither is a page's claim with nothing behind it.
ASSERTION = re.compile(r"\b(fail|ok|check|assert|throw)\b")
# And a check that cannot fail the shell is half a check: the harness must be able to exit
# non-zero (or throw) when it finds a defect.
FAILURE_PATH = re.compile(r"process\.exit\(\s*[1-9]|exitCode\s*=\s*[1-9]|\bthrow\b")


def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


def _html_pages():
    return sorted(glob.glob(os.path.join(REPO, "docs", "**", "*.html"), recursive=True))


def _named_in_pages():
    """{page relpath: sorted tuple of harness names the page's own text contains}."""
    found = {}
    for path in _html_pages():
        rel = os.path.relpath(path, REPO)
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        names = tuple(sorted(set(HARNESS_NAME.findall(text))))
        if names:
            found[rel] = names
    return found


def _on_disk():
    return tuple(sorted(os.path.basename(p) for p in
                        glob.glob(os.path.join(REPO, "tests", "*.mjs"))))


class TestPageHarnessMap(unittest.TestCase):
    def test_every_named_page_is_in_the_map(self):
        """A page that starts (or stops) naming a harness must be pinned deliberately."""
        scanned = _named_in_pages()
        self.assertEqual(sorted(scanned), sorted(MAP),
                         "the set of pages naming a validate_*.mjs changed; edit MAP in "
                         "tests/test_page_harness_map.py in the same change and say in the "
                         "commit whether the page's claim or the harness moved")

    def test_every_map_entry_still_names_exactly_what_it_pinned(self):
        scanned = _named_in_pages()
        drift = {page: (MAP[page], scanned.get(page))
                 for page in MAP if scanned.get(page) != MAP[page]}
        self.assertEqual(drift, {},
                         "these pages name a different set of harnesses than the map pins "
                         "(page -> (pinned, found))")

    def test_every_named_harness_exists_and_still_asserts(self):
        """Existence is not enough: a harness emptied of checks still has the right path."""
        named = sorted({n for names in MAP.values() for n in names})
        problems = []
        for name in named:
            path = os.path.join(REPO, "tests", name)
            if not os.path.isfile(path):
                problems.append(f"{name}: missing")
                continue
            text = _read(os.path.join("tests", name))
            if not ASSERTION.search(text):
                problems.append(f"{name}: no fail/ok/check/assert/throw — it checks nothing")
            if not FAILURE_PATH.search(text):
                problems.append(f"{name}: no non-zero exit and no throw — a red check cannot "
                                f"fail anything")
            if len(text.splitlines()) < 20:
                problems.append(f"{name}: {len(text.splitlines())} lines — too short to be "
                                f"the harness its page describes")
        self.assertEqual(problems, [], "named harnesses that cannot back the page's claim")

    def test_the_orphans_are_still_orphans(self):
        named = {n for names in MAP.values() for n in names}
        orphans = tuple(n for n in _on_disk() if n not in named and n not in OTHER_HARNESSES)
        self.assertEqual(orphans, ORPHANS,
                         "the harnesses no page names changed. If a page now cites one, "
                         "move it from ORPHANS into MAP; if one was deleted, say so")

    def test_every_js_harness_is_accounted_for(self):
        """Every .mjs under tests/: MAP's named set + ORPHANS + OTHER_HARNESSES."""
        named = {n for names in MAP.values() for n in names}
        accounted = named | set(ORPHANS) | set(OTHER_HARNESSES)
        on_disk = set(_on_disk())
        self.assertEqual(on_disk - accounted, set(),
                         "unaccounted .mjs files under tests/ — add them to MAP, ORPHANS or "
                         "OTHER_HARNESSES so the count in the record stays true")
        self.assertEqual(accounted - on_disk, set(),
                         "listed harnesses that are not on disk")

    def test_the_map_is_not_vacuous(self):
        # Eleven, not ten: ten Works pages carry a claim, and docs/works/index.html names nine
        # of the same harnesses in its list. The record said "ten pages" until 2026-11-26,
        # which counted the claims and the pages as the same number; they are not.
        self.assertEqual(len(MAP), 11,
                         "eleven pages name a validate_*.mjs harness (ten Works pages plus "
                         "docs/works/index.html) — a change here is a change to the record")
        self.assertGreaterEqual(len(MAP), 10, "fewer than ten pages pinned — is the glob wrong?")
        named = {n for names in MAP.values() for n in names}
        self.assertGreaterEqual(len(named), 10, "fewer than ten named harnesses")
        total = sum(len(_read(os.path.join("tests", n)).splitlines()) for n in named)
        self.assertGreater(total, 1500, "the named harnesses are suspiciously small")

    def test_ported_pages_are_real_map_entries(self):
        """A port must belong to a page that actually names a harness."""
        stray = sorted(set(PYTHON_REDERIVED) - set(MAP))
        self.assertEqual(stray, [], "PYTHON_REDERIVED names pages the map does not")

    def test_every_port_exists_and_runs_in_a_registered_job(self):
        """The point of a port is that it fails a build. An unregistered one fails nothing."""
        yml = _read(os.path.join(".github", "workflows", "test-and-report.yml"))
        problems = []
        for page, test in sorted(PYTHON_REDERIVED.items()):
            if not os.path.isfile(os.path.join(REPO, "tests", test)):
                problems.append(f"{page}: names tests/{test}, which does not exist")
            if f"python3 tests/{test}" not in yml:
                problems.append(f"{page}: tests/{test} is not run by the workflow, so it "
                                f"cannot fail a build — register it in the same change")
        self.assertEqual(problems, [], "ported pages whose Python guard cannot run")

    def test_every_page_that_names_a_harness_is_either_ported_or_amended(self):
        """The item's condition, as a test. A page may name a harness only if a registered
        Python test re-derives what that harness asserts, or the page says what actually ran.
        A page in neither is a claim resting on a file nothing executes."""
        unexplained = []
        for page in sorted(MAP):
            if page == "docs/works/index.html":
                continue  # a listing page; each entry's claim is pinned on its own page below
            if page in PYTHON_REDERIVED or page in AMENDED_LIVE:
                continue
            unexplained.append(page)
        self.assertEqual(unexplained, [],
                         "pages naming a harness with neither a registered Python port nor an "
                         "amended claim: add the port, or amend the page and add it to AMENDED_LIVE")
        self.assertEqual([p for p in AMENDED_LIVE if p not in MAP], [],
                         "AMENDED_LIVE names a page that does not name a harness")

    def test_the_amended_live_claims_still_say_what_ran(self):
        """Four pages whose harness needs the live network. The amendment is the whole close,
        so it is pinned in both places a reader meets the claim."""
        problems = []
        for page in AMENDED_LIVE:
            text = _read(page)
            if AMENDMENT_MARKER not in text:
                problems.append(f"{page}: the {AMENDMENT_MARKER} amendment is gone")
            if AMENDMENT_CLAIM not in text:
                problems.append(f"{page}: no longer says that no job here runs the harness")
            if "which runs this page's own script" in text and AMENDMENT_CLAIM not in text:
                problems.append(f"{page}: back to claiming the harness runs")
        index = _read("docs/works/index.html")
        n = index.count(AMENDMENT_MARKER)
        if n < len(AMENDED_LIVE):
            problems.append(f"docs/works/index.html: {n} amendment marker(s) for "
                            f"{len(AMENDED_LIVE)} amended entries — the index repeats each "
                            f"entry's claim and must be amended with it")
        self.assertEqual(problems, [], "amended claims that no longer hold")

    def test_every_sensitivity_pair_is_registered_in_ci(self):
        """A port can be proven sensitive and still protect nothing if no job runs the proof.

        Found 2026-11-26 17:04Z: Dmitri's `test_heat_page_port_is_sensitive.py` was written,
        landed and green, and named nowhere in the workflow, so it read as protection while it
        could not fail a build — the same shape as the runnerless `test_` file that reported
        "pass" for a week. This globs the class rather than listing the three files, so the
        fourth one cannot arrive invisible.
        """
        yml = _read(os.path.join(".github", "workflows", "test-and-report.yml"))
        on_disk = sorted(os.path.basename(p) for p in
                         glob.glob(os.path.join("tests", "test_*_port_is_sensitive.py")))
        self.assertGreaterEqual(len(on_disk), 3,
                                "expected at least the three sensitivity pairs (co-safety, "
                                "food-safety, heat) — is the glob wrong?")
        unregistered = [n for n in on_disk if f"python3 tests/{n}" not in yml]
        self.assertEqual(unregistered, [],
                         "sensitivity pair(s) no job runs, so they cannot fail a build: "
                         + ", ".join(unregistered))

    def test_orphan_pages_with_a_port_are_pinned_and_registered(self):
        """The seventh offline page names no harness, so it cannot sit in PYTHON_REDERIVED.

        `docs/works/warming.html` is checked by `tests/validate_warming_page.mjs`, which no page
        cites (ORPHANS above), so an amended claim is not available and a port is the only honest
        close. Its port has nowhere else to be pinned, and an unregistered port protects nothing —
        that was the heat pair's defect of 2026-11-26 17:04Z.
        """
        yml = _read(os.path.join(".github", "workflows", "test-and-report.yml"))
        problems = []
        for page, test in sorted(ORPHAN_PORTS.items()):
            if not os.path.isfile(os.path.join(REPO, page)):
                problems.append(f"{page}: the page does not exist")
            if page in MAP:
                problems.append(f"{page}: is in MAP, so its port belongs in PYTHON_REDERIVED")
            if not os.path.isfile(os.path.join(REPO, "tests", test)):
                problems.append(f"{page}: names tests/{test}, which does not exist")
            if f"python3 tests/{test}" not in yml:
                problems.append(f"{page}: tests/{test} is not run by the workflow, so the port "
                                f"cannot fail a build")
        self.assertEqual(problems, [], "orphan pages whose Python guard cannot run")
        self.assertEqual(len(ORPHAN_PORTS), 1,
                         "the orphan-port list changed — say so in the same change")

    def test_the_parse_guard_and_this_test_are_registered_in_ci(self):
        yml = _read(os.path.join(".github", "workflows", "test-and-report.yml"))
        self.assertIn("python3 tests/test_mjs_validators_parse.py", yml,
                      "the node --check guard is no longer registered")
        self.assertIn("python3 tests/test_page_harness_map.py", yml,
                      "this map guard is not registered in the workflow, so it cannot fail a "
                      "build")

    def test_no_registered_job_executes_a_validator(self):
        """The measured fact this whole item turns on.

        If you are reading this because the test failed: someone registered a validator to
        run. That is an improvement, not a regression — delete this assertion and amend the
        pages that claimed what ran before the registration existed, so the page and the
        job agree on which checks actually ran."""
        offenders = []
        for path in sorted(glob.glob(os.path.join(REPO, ".github", "workflows", "*.yml"))):
            for n, line in enumerate(_read(os.path.relpath(path, REPO)).splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#") or HARNESS_NAME.search(stripped) is None:
                    continue
                if "node --check" in stripped:
                    continue
                offenders.append(f"{os.path.basename(path)}:{n}: {stripped}")
        self.assertEqual(offenders, [],
                         "a workflow now runs a page harness (see this test's docstring)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
