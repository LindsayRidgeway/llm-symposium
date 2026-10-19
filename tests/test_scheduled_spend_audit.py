#!/usr/bin/env python3
# Owner: Desi
"""Tests for `scripts/scheduled_spend_audit.py`. Offline, temp directories, no network.

Why these exist. The audit exists because a *comment* was mistaken for a schedule: three
workflows keep their retired cron lines, commented out on 2026-09-25, and the burn document went
on pricing a "daily GitHub Actions pipeline" for three weeks after it stopped. So the cases pinned
here are the ways that mistake comes back:

  1. a commented-out cron must not read as a schedule;
  2. a schedule that spends and records nothing is the one hard failure;
  3. a manual spender is reported, never failed;
  4. the recorder (`channels/usage.py`) is not itself a spender, whatever its docstring says;
  5. a document that merely *cites* a provider is not a spender — the first version of this regex
     matched the bare word `deepseek` and flagged a probe that only names a review file;
  6. the live tree: exactly one scheduled workflow, and it calls no model.
"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scheduled_spend_audit as audit_mod  # noqa: E402


def build(tmp: Path, files: dict) -> Path:
    """Write a dict of relative path -> text under `tmp`, return the workflows dir."""
    for rel, text in files.items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp / ".github" / "workflows"


SCHEDULED_HEAD = "name: x\non:\n  schedule:\n    - cron: '0 12 * * *'\n  workflow_dispatch:\njobs:\n  j:\n    runs-on: ubuntu-latest\n    steps:\n"
MANUAL_HEAD = "name: x\non:\n  workflow_dispatch:\njobs:\n  j:\n    runs-on: ubuntu-latest\n    steps:\n"


class CommentedCronTest(unittest.TestCase):
    def test_a_commented_cron_is_not_a_schedule(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            wf = build(tmp, {
                ".github/workflows/r.yml": (
                    "name: r\non:\n  # schedule:\n  #   - cron: '0 12 * * *'\n"
                    "  workflow_dispatch:\njobs:\n  j:\n    steps:\n      - run: python3 scripts/spend.py\n"
                ),
                "scripts/spend.py": "from openai import OpenAI\n",
            })
            row = audit_mod.parse_workflow(wf / "r.yml", tmp)
            self.assertFalse(row["scheduled"])
            self.assertEqual(row["crons"], [])
            self.assertEqual(row["verdict"], "spends-unrecorded")

    def test_a_live_cron_is_a_schedule(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            wf = build(tmp, {".github/workflows/r.yml": SCHEDULED_HEAD + "      - run: python3 scripts/spend.py\n",
                             "scripts/spend.py": "import anthropic\n"})
            row = audit_mod.parse_workflow(wf / "r.yml", tmp)
            self.assertTrue(row["scheduled"])
            self.assertEqual(row["crons"], ["0 12 * * *"])


class FailureTest(unittest.TestCase):
    def test_scheduled_spend_without_record_fails(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            wf = build(tmp, {".github/workflows/r.yml": SCHEDULED_HEAD + "      - run: python3 scripts/spend.py\n",
                             "scripts/spend.py": "from openai import OpenAI\n"})
            rows = audit_mod.audit(wf, tmp)
            self.assertEqual([r["workflow"] for r in audit_mod.failures(rows)], ["r.yml"])

    def test_scheduled_spend_with_record_passes(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            wf = build(tmp, {".github/workflows/r.yml": SCHEDULED_HEAD + "      - run: python3 scripts/spend.py\n",
                             "scripts/spend.py": "from openai import OpenAI\n"
                                                 "from channels import usage\nusage.record_api_call('openai', 'm', r)\n"})
            rows = audit_mod.audit(wf, tmp)
            self.assertEqual(rows[0]["verdict"], "spends-recorded")
            self.assertEqual(audit_mod.failures(rows), [])

    def test_a_manual_spender_is_reported_not_failed(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            wf = build(tmp, {".github/workflows/r.yml": MANUAL_HEAD + "      - run: python3 scripts/spend.py\n",
                             "scripts/spend.py": "import anthropic\n"})
            rows = audit_mod.audit(wf, tmp)
            self.assertTrue(rows[0]["spends"])
            self.assertEqual(rows[0]["verdict"], "spends-unrecorded")
            self.assertEqual(audit_mod.failures(rows), [])


class SignalTest(unittest.TestCase):
    def test_the_recorder_is_not_a_spender(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            wf = build(tmp, {".github/workflows/r.yml": SCHEDULED_HEAD + "      - run: python3 channels/usage.py --summary\n",
                             "channels/usage.py": "from openai import OpenAI  # only in a docstring in reality\n"})
            row = audit_mod.parse_workflow(wf / "r.yml", tmp)
            self.assertEqual(row["spends_on"], [])
            self.assertEqual(row["verdict"], "scheduled-no-spend")

    def test_a_citation_is_not_a_spend(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            wf = build(tmp, {".github/workflows/r.yml": SCHEDULED_HEAD + "      - run: python3 probes/p.py\n",
                             "probes/p.py": '"""See discussions/deepseek-review.md for the argument."""\nprint(1)\n'})
            row = audit_mod.parse_workflow(wf / "r.yml", tmp)
            self.assertEqual(row["spends_on"], [])

    def test_an_env_key_read_is_a_spend(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            wf = build(tmp, {".github/workflows/r.yml": SCHEDULED_HEAD + "      - run: python3 scripts/c.py\n",
                             "scripts/c.py": "import os\nK = os.environ['OPENROUTER_API_KEY']\n"})
            row = audit_mod.parse_workflow(wf / "r.yml", tmp)
            self.assertTrue(row["spends"])

    def test_a_test_entrypoint_is_not_a_spender(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            wf = build(tmp, {".github/workflows/r.yml": SCHEDULED_HEAD + "      - run: python3 tests/test_x.py\n",
                             "tests/test_x.py": "from openai import OpenAI  # stubbed\n"})
            row = audit_mod.parse_workflow(wf / "r.yml", tmp)
            self.assertEqual(row["spends_on"], [])


class LiveTreeTest(unittest.TestCase):
    """The tree this script is part of. If these break, the record and the tree disagree."""

    @classmethod
    def setUpClass(cls):
        cls.rows = audit_mod.audit(ROOT / ".github" / "workflows", ROOT)
        cls.by_name = {r["workflow"]: r for r in cls.rows}

    def test_no_scheduled_workflow_spends_without_recording(self):
        self.assertEqual(audit_mod.failures(self.rows), [])

    def test_quiet_check_is_the_only_scheduled_workflow(self):
        scheduled = sorted(r["workflow"] for r in self.rows if r["scheduled"])
        self.assertEqual(scheduled, ["quiet-check.yml"])

    def test_the_four_model_runner_is_manual(self):
        # symposium.yml ran daily until 2026-09-25. If someone uncomments its cron, the burn
        # figure changes meaning and this test should say so rather than pass quietly.
        sym = self.by_name["symposium.yml"]
        self.assertFalse(sym["scheduled"], "symposium.yml is scheduled again: re-price the burn")
        self.assertTrue(sym["records"], "the runner must record its spend")

    def test_goose_workflows_are_seen_as_spenders(self):
        for name in ("autonomous-goose-tarik.yml", "check-tarik-model.yml"):
            self.assertTrue(self.by_name[name]["spends"], name)


if __name__ == "__main__":
    unittest.main()
