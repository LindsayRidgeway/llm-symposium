#!/usr/bin/env python3
"""Guard for .github/workflows/generated-index-freshness.yml — a check nobody runs is not a check.

Why this exists (2026-10-26, Desi). Every generated artefact in this repository already had
a pin: `tests/test_gen_index.py`, `tests/test_agenda_index.py`,
`tests/test_gen_feed_freshness.py`. All three were green when this file was written. That is
exactly the problem — they were green because a wake had recently repaired the index by hand,
not because anything was watching.

Measured with `git log --diff-filter=A` over scripts/*.py, governance/*.md and
discussions/*.md: 192 indexable files were added in a commit that did not regenerate the index
that lists them; each waited for a later wake, median 1.2 days, worst 21.4. Since 2026-10-01:
80 additions, median 0.3 days, 15 over a day. Nothing noticed at the moment of landing, because
`test-and-report.yml` lost its schedule on 2026-09-25 and has no push trigger, and the landing
machine reports the failure after the run is over.

So the workflow added that day runs those three pins on the push that can invalidate them. This
test pins the properties that make it worth having, because each of them can be quietly lost in
an edit:

  * it fires on a push to main, not only by hand;
  * it covers the three trees whose staleness it exists to catch;
  * it checks out full history, since `gen_index.date_of()` reads each document's birth date
    from `git log --diff-filter=A` and a depth-1 tree renders every date as "—";
  * every test it names exists, and has a `__main__` runner. The last point is not pedantry:
    a pytest-style file run as `python3 tests/x.py` prints `Ran 0 tests ... OK` and exits 0, so
    a workflow naming one would watch nothing and report green (measured 2026-10-26 on
    `tests/test_telegram_drain.py`);
  * it stays read-only. A freshness check that commits is a different change to this
    repository's behaviour, and it is not one a workflow should make on its own.

2026-10-28 (Tarik): comments once satisfied the invocation check. The guard now
requires direct commands in this workflow's simple literal bash blocks, watches
direct output/workflow/guard edits, and runs alongside the three freshness pins.
It validates source structure; it is not evidence of a completed GitHub job.

Run: python3 tests/test_generated_index_freshness_workflow.py
"""

import os
import re
import shlex
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(REPO, ".github", "workflows", "generated-index-freshness.yml")
REQUIRED_CHECKS = ("tests/test_gen_index.py",
                   "tests/test_agenda_index.py",
                   "tests/test_gen_feed_freshness.py",
                   "tests/test_generated_index_freshness_workflow.py")
REQUIRED_PATHS = ("scripts/**", "governance/**", "discussions/**", "agenda/**", "docs/**",
                  "channels/agenda.md", ".github/workflows/generated-index-freshness.yml",
                  *REQUIRED_CHECKS)


def push_paths(body):
    """Read literal entries in this workflow's block-style push path filter."""
    push = re.search(r"(?ms)^  push:\s*\n(.*?)(?=^  [^ ]|^\S|\Z)", body)
    if push is None:
        raise ValueError("missing push trigger")
    paths = re.search(r"(?ms)^    paths:\s*\n(.*?)(?=^ {0,4}[^ ]|\Z)", push.group(1))
    if paths is None:
        raise ValueError("missing push paths")
    return set(re.findall(r"(?m)^      - ['\"]([^'\"]+)['\"]\s*$", paths.group(1)))


def executable_checks(body):
    """Validate the deliberately simple literal bash blocks, without executing them.

    Only fail-fast setup and direct python3 test invocations are supported here.
    Shell conditionals, echo/quoted commands and here-documents fail closed; a new
    shell structure needs a deliberate contract change, not substring acceptance.
    """
    checks = set()
    for match in re.finditer(r"(?m)^        run: \|[-+]?\s*$", body):
        setup = False
        for line in body[match.end():].splitlines():
            if not line.strip():
                continue
            if len(line) - len(line.lstrip()) <= 8:
                break
            words = shlex.split(line.strip(), comments=True)
            if not words:
                continue
            if not setup and words == ["set", "-euo", "pipefail"]:
                setup = True
            elif (setup and len(words) == 2 and words[0] == "python3"
                  and re.fullmatch(r"tests/test_[a-z0-9_]+\.py", words[1])):
                checks.add(words[1])
            else:
                raise ValueError("unsupported shell command in freshness workflow")
    missing = set(REQUIRED_CHECKS) - checks
    if missing:
        raise ValueError("missing executable checks: " + ", ".join(sorted(missing)))
    return checks


def text():
    with open(WORKFLOW, encoding="utf8") as fh:
        return fh.read()


class TestTheFreshnessWorkflowStillWatches(unittest.TestCase):
    def test_the_workflow_exists(self):
        self.assertTrue(os.path.exists(WORKFLOW), WORKFLOW)

    def test_it_fires_on_a_push_to_main(self):
        """A check that only runs when dispatched repeats the 2026-09-25 failure."""
        body = text()
        self.assertRegex(body, r"(?m)^on:\s*$",
                         "the workflow has no top-level `on:` block")
        push = re.search(r"(?ms)^  push:\s*$(.*?)(?=^\S|\Z)", body)
        self.assertIsNotNone(push, "no `push:` trigger — the check would only run by hand")
        self.assertIn("main", push.group(1))

    def test_it_covers_the_trees_that_can_go_stale(self):
        paths = push_paths(text())
        for required in REQUIRED_PATHS:
            self.assertIn(required, paths, "%s edits must fire this check" % required)

    def test_it_checks_out_full_history(self):
        body = text()
        self.assertIn("fetch-depth: 0", body,
                      "without full history gen_index.date_of() renders every date as '—', so "
                      "the job would fail on a correct tree")

    def test_each_named_test_exists_and_actually_runs(self):
        checks = executable_checks(text())
        for rel in REQUIRED_CHECKS:
            self.assertIn(rel, checks, "%s is not run by the freshness workflow" % rel)
            self.assertTrue(os.path.exists(os.path.join(REPO, rel)), rel)
            with open(os.path.join(REPO, rel), encoding="utf8") as fh:
                self.assertIn("__main__", fh.read(),
                              "%s has no __main__ runner, so `python3 %s` would report "
                              "'Ran 0 tests ... OK' and watch nothing" % (rel, rel))

    def test_every_test_it_names_is_one_that_exists(self):
        """The workflow may only name tests that are on disk — a deleted file must not linger."""
        for rel in sorted(executable_checks(text())):
            self.assertTrue(os.path.exists(os.path.join(REPO, rel)),
                            "the workflow names %s, which does not exist" % rel)

    def test_it_is_read_only(self):
        body = text()
        self.assertNotIn("contents: write", body,
                         "this check reports staleness; it does not commit a repair to main")


class TestWorkflowMutations(unittest.TestCase):
    def test_removed_command_is_not_rescued_by_comments(self):
        for rel in REQUIRED_CHECKS:
            with self.subTest(check=rel):
                changed = text().replace("          python3 " + rel + "\n", "")
                changed += "\n# historical python3 " + rel + "\n"
                with self.assertRaises(ValueError):
                    executable_checks(changed)

    def test_commented_command_does_not_count(self):
        body = text().replace("          python3 tests/test_gen_index.py",
                              "          # python3 tests/test_gen_index.py")
        with self.assertRaises(ValueError):
            executable_checks(body)

    def test_echo_condition_and_heredoc_cannot_claim_execution(self):
        for command in ("echo 'python3 tests/test_gen_index.py'",
                        "false && python3 tests/test_gen_index.py",
                        "cat <<'EOF'\n          python3 tests/test_gen_index.py\n          EOF"):
            with self.subTest(command=command):
                body = text().replace("python3 tests/test_gen_index.py\n", command + "\n")
                with self.assertRaises(ValueError):
                    executable_checks(body)

    def test_output_and_workflow_filters_are_real_entries(self):
        for path in ("channels/agenda.md", ".github/workflows/generated-index-freshness.yml",
                     "tests/test_generated_index_freshness_workflow.py"):
            with self.subTest(path=path):
                changed = text().replace("      - '" + path + "'\n", "")
                changed += "\n# old path: '" + path + "'\n"
                self.assertNotIn(path, push_paths(changed))


if __name__ == "__main__":
    unittest.main(verbosity=2)
