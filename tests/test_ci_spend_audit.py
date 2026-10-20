#!/usr/bin/env python3
# Owner: Desi
"""Tests for `scripts/ci_spend_audit.py` — the table that answers "does CI spend money?".

The defect this guards against is not a wrong number in a report; it is a *check that reads the
wrong thing*. Every workflow that reaches a paid provider in this repository has its clock
commented out with a paragraph of reasoning, so an auditor that reads the comment (`#   - cron:`)
as a trigger would report five scheduled spenders, and one that reads only the script a step
names would call `channel-poll.yml` free while it calls `channels.auto_reply`, which bills.

No network, no keys: every case is a workflow file in a temporary directory.
"""

import io
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import ci_spend_audit as audit  # noqa: E402


SPENDER = '''\
import os
from openai import OpenAI
client = OpenAI()
'''

SPENDER_THAT_RECORDS = '''\
import os
from channels import usage
from openai import OpenAI
client = OpenAI()
usage.record_sdk_call("openai", "m", None)
'''

RECORDER_ONLY = '''\
import json
print("nothing paid here")
'''


class Fixture:
    """A throwaway repository: `.github/workflows/` plus the scripts those workflows name."""

    def __init__(self, tmp):
        self.root = Path(tmp)
        (self.root / ".github" / "workflows").mkdir(parents=True)
        (self.root / "channels").mkdir(parents=True, exist_ok=True)

    def workflow(self, name, body):
        (self.root / ".github" / "workflows" / name).write_text(body)
        return self

    def script(self, rel, body):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
        return self

    def audit(self):
        return audit.audit(self.root / ".github" / "workflows", self.root)


class TriggerParsing(unittest.TestCase):
    def test_commented_cron_is_not_a_trigger(self):
        """The whole repository is built out of retired crons. Reading one is the failure mode."""
        text = (
            "on:\n"
            "  # Retired 2026-09-25: this ran daily and bought repetition.\n"
            "  # schedule:\n"
            "  #   - cron: '0 12 * * *'\n"
            "  workflow_dispatch:\n"
        )
        self.assertEqual(audit.parse_triggers(text), ["workflow_dispatch"])

    def test_live_cron_and_dispatch(self):
        text = (
            "on:\n"
            "  schedule:\n"
            "    - cron: '0 16 * * *'   # daily\n"
            "  workflow_dispatch:\n"
        )
        self.assertEqual(audit.parse_triggers(text), ["schedule", "workflow_dispatch"])

    def test_push_paths_trigger(self):
        text = "on:\n  push:\n    branches: [main]\n    paths: ['channels/x/*.json']\n"
        self.assertEqual(audit.parse_triggers(text), ["push"])

    def test_no_on_block(self):
        self.assertEqual(audit.parse_triggers("name: x\njobs:\n  a:\n    runs-on: ubuntu-latest\n"), [])


class Classification(unittest.TestCase):
    def test_clocked_spender_that_records_and_commits_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script(".github/scripts/worker.py", SPENDER_THAT_RECORDS)
                  .workflow("daily.yml",
                            "on:\n  schedule:\n    - cron: '0 1 * * *'\n"
                            "jobs:\n  j:\n    steps:\n      - run: |\n"
                            "          python .github/scripts/worker.py\n"
                            "      - run: |\n"
                            "          git add channels/usage/\n"
                            "          git commit -m 'record(usage)'\n"
                            "          git push origin main\n"))
            rows = fx.audit()
            self.assertEqual(len(rows), 1)
            self.assertTrue(rows[0]["spends"])
            self.assertTrue(rows[0]["records"])
            self.assertTrue(rows[0]["persists"])
            self.assertEqual(rows[0]["verdict"], "on the clock, recorded and kept")

    def test_clocked_spender_that_records_but_never_commits_fails(self):
        """The 2026-10-20 defect: a row written into a runner that is thrown away after the job."""
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script(".github/scripts/worker.py", SPENDER_THAT_RECORDS)
                  .workflow("daily.yml",
                            "on:\n  schedule:\n    - cron: '0 1 * * *'\n"
                            "jobs:\n  j:\n    steps:\n      - run: |\n"
                            "          python .github/scripts/worker.py\n"))
            row = fx.audit()[0]
            self.assertTrue(row["records"])
            self.assertFalse(row["persists"])
            self.assertEqual(row["verdict"], "FAIL: on the clock, recorded and never committed")

    def test_git_add_before_the_spend_does_not_count(self):
        """Staging the tree first and spending afterwards commits last run's leftovers."""
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script(".github/scripts/worker.py", SPENDER_THAT_RECORDS)
                  .workflow("daily.yml",
                            "on:\n  schedule:\n    - cron: '0 1 * * *'\n"
                            "jobs:\n  j:\n    steps:\n      - run: git add .\n"
                            "      - run: python .github/scripts/worker.py\n"
                            "      - run: |\n"
                            "          git commit -m 'x'\n"
                            "          git push origin main\n"))
            row = fx.audit()[0]
            self.assertFalse(row["persists"], "the add is above the spend")
            self.assertTrue(row["verdict"].startswith("FAIL"))

    def test_narrow_add_does_not_cover_the_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script(".github/scripts/worker.py", SPENDER_THAT_RECORDS)
                  .workflow("daily.yml",
                            "on:\n  schedule:\n    - cron: '0 1 * * *'\n"
                            "jobs:\n  j:\n    steps:\n"
                            "      - run: python .github/scripts/worker.py\n"
                            "      - run: |\n"
                            "          git add channels/telegram/ channels/conversation/\n"
                            "          git commit -m 'record(telegram)'\n"
                            "          git push origin main\n"))
            row = fx.audit()[0]
            self.assertFalse(row["persists"])
            self.assertEqual(row["verdict"], "FAIL: on the clock, recorded and never committed")

    def test_add_dot_and_dash_capital_a_cover_the_ledger(self):
        for spec in ("git add .", "git add -A", "git add --all", "git add channels/",
                     "git add channels/usage/ci-usage.jsonl"):
            with tempfile.TemporaryDirectory() as tmp:
                fx = (Fixture(tmp)
                      .script(".github/scripts/worker.py", SPENDER_THAT_RECORDS)
                      .workflow("daily.yml",
                                "on:\n  schedule:\n    - cron: '0 1 * * *'\n"
                                "jobs:\n  j:\n    steps:\n"
                                "      - run: python .github/scripts/worker.py\n"
                                "      - run: |\n"
                                f"          {spec}\n"
                                "          git commit -m 'x'\n"
                                "          git push origin main\n"))
                self.assertTrue(fx.audit()[0]["persists"], spec)

    def test_staged_and_committed_but_never_pushed_is_not_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script(".github/scripts/worker.py", SPENDER_THAT_RECORDS)
                  .workflow("daily.yml",
                            "on:\n  schedule:\n    - cron: '0 1 * * *'\n"
                            "jobs:\n  j:\n    steps:\n"
                            "      - run: python .github/scripts/worker.py\n"
                            "      - run: |\n"
                            "          git add channels/usage/\n"
                            "          git commit -m 'x'\n"))
            detail = fx.audit()[0]["keep_detail"]
            self.assertTrue(detail["stages"])
            self.assertTrue(detail["commits"])
            self.assertFalse(detail["pushes"])
            self.assertFalse(detail["persists"])

    def test_clocked_spender_that_does_not_record_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script(".github/scripts/worker.py", SPENDER)
                  .workflow("daily.yml",
                            "on:\n  schedule:\n    - cron: '0 1 * * *'\n"
                            "jobs:\n  j:\n    steps:\n      - run: python .github/scripts/worker.py\n"))
            rows = fx.audit()
            self.assertEqual(rows[0]["verdict"], "FAIL: on the clock and unrecorded")
            self.assertEqual(audit._verdict(True, False, ["schedule"]),
                             "FAIL: on the clock and unrecorded")

    def test_manual_spender_is_reported_but_not_failed(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script("scripts/one_off.py", SPENDER)
                  .workflow("manual.yml",
                            "on:\n  workflow_dispatch:\n"
                            "jobs:\n  j:\n    steps:\n      - run: python scripts/one_off.py\n"))
            rows = fx.audit()
            self.assertEqual(rows[0]["verdict"], "manual, unrecorded")
            self.assertEqual(rows[0]["on_clock"], [])

    def test_import_is_followed_one_level(self):
        """`poll_channels.py` names no vendor; it calls `auto_reply`, which does. Both matter."""
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script("channels/auto_reply.py", SPENDER_THAT_RECORDS)
                  .script(".github/scripts/poll.py",
                          "from channels.auto_reply import run_auto_reply\nrun_auto_reply()\n")
                  .workflow("poll.yml",
                            "on:\n  schedule:\n    - cron: '*/15 * * * *'\n"
                            "jobs:\n  j:\n    steps:\n      - run: python .github/scripts/poll.py\n"))
            row = fx.audit()[0]
            self.assertTrue(row["spends"], "the spend lives in the imported module")
            self.assertTrue(row["records"])
            self.assertIn("channels/auto_reply.py",
                          audit.classify_script(".github/scripts/poll.py", fx.root)["via"])

    def test_mail_only_workflow_is_free(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script(".github/scripts/quiet.py", RECORDER_ONLY)
                  .workflow("quiet.yml",
                            "on:\n  schedule:\n    - cron: '0 16 * * *'\n"
                            "jobs:\n  j:\n    steps:\n      - run: python .github/scripts/quiet.py\n"))
            row = fx.audit()[0]
            self.assertFalse(row["spends"])
            self.assertEqual(row["verdict"], "no model spend")

    def test_model_key_in_env_counts_as_a_spend(self):
        """An inline heredoc hides the call from the script scan; the key does not hide it."""
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp).workflow(
                "probe.yml",
                "on:\n  schedule:\n    - cron: '0 3 * * *'\n"
                "jobs:\n  j:\n    steps:\n      - env:\n"
                "          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}\n"
                "        run: |\n          python3 - <<'PY'\n          print(1)\n          PY\n")
            row = fx.audit()[0]
            self.assertTrue(row["spends"])
            self.assertTrue(any("model key" in r for r in row["spends_because"]))


class TheRepositoryItself(unittest.TestCase):
    """The measured facts this script was written to state. If one of them changes, that is the
    moment the usage ledger's silence stops being explainable and this test should fail."""

    def setUp(self):
        self.rows = {r["workflow"]: r for r in audit.audit()}

    def test_no_clocked_workflow_spends_unrecorded(self):
        failures = [r["workflow"] for r in self.rows.values()
                    if r["verdict"].startswith("FAIL")]
        self.assertEqual(failures, [],
                         "a workflow that can run unattended reaches a paid provider without "
                         "recording what it spent")

    def test_quiet_check_is_the_only_scheduled_workflow(self):
        scheduled = sorted(n for n, r in self.rows.items() if "schedule" in r["triggers"])
        self.assertEqual(scheduled, ["quiet-check.yml"])

    def test_the_scheduled_workflow_makes_no_model_call(self):
        self.assertFalse(self.rows["quiet-check.yml"]["spends"])

    def test_the_runner_is_wired_and_manual(self):
        row = self.rows["symposium.yml"]
        self.assertTrue(row["spends"])
        self.assertTrue(row["records"], "runner.py must record into channels/usage")
        self.assertTrue(row["persists"], "and its commit step must stage the ledger")
        self.assertEqual(row["on_clock"], [])

    def test_every_recording_spender_also_commits_the_ledger(self):
        """Recording without committing is the defect this column exists for. Every workflow
        that records must stage, commit and push the ledger after its spend."""
        lost = sorted(r["workflow"] for r in self.rows.values()
                      if r["records"] and not r["persists"])
        self.assertEqual(lost, [], "these write usage rows that never leave the runner")


    def test_known_unrecorded_spender_is_named_not_hidden(self):
        """`check-tarik-model.yml` really does spend (a chat completion) and records nothing.
        It is manual-only, so it is a fact to report, not a failure to fix tonight."""
        row = self.rows["check-tarik-model.yml"]
        self.assertTrue(row["spends"])
        self.assertFalse(row["records"])
        self.assertEqual(row["on_clock"], [])

    def test_render_says_the_clock_is_clear(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            audit.main([])
        out = buf.getvalue()
        self.assertIn("On the clock and spending: none", out)
        self.assertIn("Unrecorded on-the-clock spend: 0", out)
        self.assertIn("Recorded but never committed (the row dies with the runner): 0", out)


class Survival(unittest.TestCase):
    """The column is worth nothing if it is only a text match, so this is the row itself.

    A usage row written by the ledger's own code, staged by the exact `git add` spec a workflow
    uses, committed, pushed to a bare remote — and read back out of that remote. If this passes,
    "recorded and kept" means kept; if a workflow's spec stops covering the ledger, the audit
    column above says FAIL but this test would still pass, which is why both exist.
    """

    RESPONSE = {"usage": {"prompt_tokens": 11, "completion_tokens": 3}}

    def _survives(self, spec):
        root = tempfile.mkdtemp()
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", root]))
        repo = Path(root) / "repo"
        (repo / "channels" / "usage").mkdir(parents=True)
        (repo / "README.md").write_text("x\n")
        ledger = repo / "channels" / "usage" / "ci-usage.jsonl"

        from channels import usage as ledger_mod
        ledger_mod.record_api_call("deepseek", "deepseek-chat", self.RESPONSE,
                                   source="auto-reply", path=ledger)
        self.assertTrue(ledger.exists(), "the ledger must write where it is told")

        def git(*args, cwd=None):
            done = subprocess.run(["git", *args], cwd=str(cwd or repo),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(done.returncode, 0, done.stderr.decode())
            return done.stdout.decode()

        git("init", "-q", "-b", "main")
        git("config", "user.email", "test@example.com")
        git("config", "user.name", "test")
        git("add", "README.md")
        git("commit", "-qm", "base")
        remote = Path(root) / "remote.git"
        git("init", "-q", "--bare", str(remote))
        git("remote", "add", "origin", str(remote))

        git(*shlex.split(spec)[1:])   # the spec is written as a shell line: "git add ..."
        git("commit", "-qm", "record(usage): one row")
        git("push", "-q", "origin", "main")

        # What a later wake would read: the file as it exists on the pushed branch, not on disk.
        return git("--git-dir", str(remote), "show", "main:channels/usage/ci-usage.jsonl",
                   cwd=remote)

    def test_a_row_survives_the_workflows_own_add_spec(self):
        for spec in ("git add channels/usage/", "git add channels/", "git add .", "git add -A"):
            text = self._survives(spec)
            rows = [json.loads(line) for line in text.splitlines() if line.strip()]
            self.assertEqual(len(rows), 1, spec)
            self.assertEqual(rows[0]["provider"], "deepseek", spec)
            self.assertEqual(rows[0]["input"], 11, spec)
            self.assertEqual(rows[0]["model_calls"], 1, spec)


if __name__ == "__main__":
    unittest.main(verbosity=2)
