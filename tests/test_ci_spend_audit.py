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
    def test_clocked_spender_that_records_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script(".github/scripts/worker.py", SPENDER_THAT_RECORDS)
                  .workflow("daily.yml",
                            "on:\n  schedule:\n    - cron: '0 1 * * *'\n"
                            "jobs:\n  j:\n    steps:\n      - run: |\n"
                            "          python .github/scripts/worker.py\n"
                            "          git add channels/usage/\n"
                            "          git commit -m 'record usage'\n"
                            "          git push origin main\n"))
            rows = fx.audit()
            self.assertEqual(len(rows), 1)
            self.assertTrue(rows[0]["spends"])
            self.assertTrue(rows[0]["records"])
            self.assertTrue(rows[0]["persists"])
            self.assertEqual(rows[0]["verdict"], "on the clock, recorded")

    def test_clocked_spender_that_does_not_record_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script(".github/scripts/worker.py", SPENDER)
                  .workflow("daily.yml",
                            "on:\n  schedule:\n    - cron: '0 1 * * *'\n"
                            "jobs:\n  j:\n    steps:\n      - run: python .github/scripts/worker.py\n"))
            rows = fx.audit()
            self.assertEqual(rows[0]["verdict"], "FAIL: on the clock and unrecorded")
            self.assertEqual(audit.main(["--json"]) if False else
                             audit._verdict(True, False, ["schedule"]),
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


class PersistenceDetection(unittest.TestCase):
    """The third question: does the row reach `main`, or die in the runner's filesystem?

    Not hypothetical. `channels/usage/README.md` spent three weeks saying the recorder was
    "closed in code, open in data", and the reason was invisible in any single workflow file:
    a script that records correctly, and a job that never commits what it wrote.
    """

    def test_every_way_of_staging_the_ledger_counts(self):
        for pathspec in (".", "-A", "--all", "channels/", "channels", "channels/usage/",
                         "channels/usage", "channels/usage/ci-usage.jsonl",
                         "channels/usage/*.jsonl"):
            self.assertTrue(audit._covers_ledger(pathspec), pathspec)

    def test_other_pathspecs_do_not(self):
        for pathspec in ("tests/last-verification.txt", "probes/results/",
                         "docs/", "channels/usage-notes/", "actuator/requests/",
                         "channels/usage-archive/"):
            self.assertFalse(audit._covers_ledger(pathspec), pathspec)

    def test_all_three_git_commands_are_required(self):
        stage = "git add channels/usage/\n"
        commit = "git commit -m 'row'\n"
        push = "git push origin main\n"
        self.assertTrue(audit.persistence(stage + commit + push)["persists"])
        for missing in (stage + commit, stage + push, commit + push):
            self.assertFalse(audit.persistence(missing)["persists"],
                             f"these three are not enough on their own:\n{missing}")

    def test_a_conditional_push_counts(self):
        """Regression: the real workflows write `if git push …; then`. A `^git` anchor called
        two working pushes absent and turned a correct workflow into a FAIL."""
        text = ("git add channels/usage/\n"
                "git commit -m 'row'\n"
                "if git push \"$PUSH_URL\" main; then echo ok; fi\n")
        self.assertTrue(audit.persistence(text)["persists"])

    def test_commented_out_steps_do_not_count(self):
        """The repository is built out of retired steps. Reading one as live is the defect."""
        text = ("# git add channels/usage/\n"
                "# git commit -m 'row'\n"
                "# git push origin main\n")
        keep = audit.persistence(text)
        self.assertFalse(keep["persists"])

    def test_a_recorder_that_cannot_persist_fails_the_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = (Fixture(tmp)
                  .script(".github/scripts/worker.py", SPENDER_THAT_RECORDS)
                  .workflow("manual.yml",
                            "on:\n  workflow_dispatch:\n"
                            "jobs:\n  j:\n    steps:\n      - run: |\n"
                            "          python .github/scripts/worker.py\n"
                            "          git add tests/last-verification.txt\n"
                            "          git commit -m 'not the ledger'\n"
                            "          git push origin main\n"))
            row = fx.audit()[0]
            self.assertTrue(row["records"])
            self.assertFalse(row["persists"])
            self.assertEqual(row["verdict"], "FAIL: records rows the runner throws away")

    def test_verdict_does_not_borrow_the_clock_failure(self):
        self.assertEqual(audit._verdict(True, True, ["schedule"], False),
                         "FAIL: records rows the runner throws away")
        self.assertEqual(audit._verdict(True, True, ["schedule"], True),
                         "on the clock, recorded")
        self.assertEqual(audit._verdict(True, False, ["schedule"], False),
                         "FAIL: on the clock and unrecorded")


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
        self.assertEqual(row["on_clock"], [])

    def test_every_recorder_persists_its_rows(self):
        """Measured 2026-10-20: every workflow that writes usage rows also stages, commits and
        pushes the ledger. This is the fact the to-do item "persist the CI usage rows" was
        written without — it was rebuilt from a missing-file reading, and the file had never
        been written because nothing on a clock spends, not because no step commits it.
        If a future edit drops the staging line, this fails and the audit stops passing.

        Rewritten 2026-10-21. It used to pin the *list* of recorders —
        `["autonomous-goose-tarik.yml", "channel-poll.yml", "symposium.yml"]` — and that made a
        repair unlandable: the 2026-10-21 07:14Z wake taught `check-tarik-model.yml` to record,
        which is the one thing this audit exists to want, and the gate refused the landing
        because this line said the set must not grow. The rule is "every recorder persists";
        the roster of recorders is not a fact worth pinning, and pinning it turned the check
        into a machine that refuses the fix it asks for.
        """
        recorders = {n: r for n, r in self.rows.items() if r["records"]}
        self.assertGreaterEqual(len(recorders), 3,
                                "the audit found fewer recorders than main has; it is reading "
                                "something other than these workflows")
        for name, row in recorders.items():
            self.assertTrue(row["persists"], f"{name} records rows it never commits back")
            self.assertEqual(row["verdict"], "manual, recorded")
        # What *is* stable under a workflow starting or stopping recording: which workflows can
        # spend. That list changing means a workflow was added or removed, which is a fact.
        spenders = sorted(n for n, r in self.rows.items() if r["spends"])
        self.assertEqual(spenders, ["autonomous-goose-tarik.yml", "channel-poll.yml",
                                    "check-tarik-model.yml", "symposium.yml"])

    def test_the_persistence_evidence_names_the_git_commands(self):
        """Per workflow, the three commands must be findable in its own text — the report
        quotes them, so they must not be inferred from the absence of a failure."""
        for name in ("autonomous-goose-tarik.yml", "channel-poll.yml", "symposium.yml"):
            keep = audit.persistence(audit._read(audit.WORKFLOWS / name))
            self.assertTrue(keep["stages"], name)
            self.assertTrue(keep["commits"], name)
            self.assertTrue(keep["pushes"], name)
            self.assertTrue(keep["evidence"], name)

    def test_an_unrecorded_spender_is_named_not_hidden(self):
        """The rule is *disclosure*, not the persistence of the defect.

        Until 2026-10-21 this test named `check-tarik-model.yml` and asserted `records` was
        False. When the 07:14Z wake taught that workflow to record — the only remaining
        unrecorded spender in the repository, and the very thing `ci_spend_audit.py` reports —
        the failure gate refused the landing, because this line had made the bug an
        expectation. A test that a repair must break is a test that forbids repair.

        What survives a repair: a workflow that can spend and does not record must be
        manual-only (an unrecorded *clocked* spender is a FAIL, pinned above), and it must be
        visible in the rendered table as `records NO`, so reading the report finds it.
        """
        buf = io.StringIO()
        with redirect_stdout(buf):
            out = audit.render(list(self.rows.values()))
        unrecorded = {n: r for n, r in self.rows.items() if r["spends"] and not r["records"]}
        for name, row in unrecorded.items():
            self.assertEqual(row["on_clock"], [], f"{name} spends on a clock and records nothing")
            line = next(l for l in out.splitlines() if l.startswith(name))
            self.assertIn("NO", line, f"{name} records nothing and the report does not say so")

    def test_render_says_the_clock_is_clear(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            audit.main([])
        out = buf.getvalue()
        self.assertIn("On the clock and spending: none", out)
        self.assertIn("Unrecorded on-the-clock spend: 0", out)


class HistoryTest(unittest.TestCase):
    """`--history`: does the ledger's zero mean "nobody pressed the button" or "a row was lost"?

    The repository text cannot tell those apart — both leave `channels/usage/ci-usage.jsonl`
    empty — so these cases pin the only thing that can: the public run history, injected here
    as a dict of URLs. The failure this class exists to prevent is the comfortable verdict. On
    2026-10-18 the audit said "the ledger's zero is explained" from workflow text alone; four
    days later the history showed that not one spender had run since 2026-09-24, so the zero
    also meant the persistence claim in three workflows had never been exercised once.
    """

    def rows(self):
        return [{"workflow": "spend.yml", "spends": True},
                {"workflow": "free.yml", "spends": False}]

    def fake(self, runs, wid=111, blind=False):
        def get(url):
            if blind:
                return None
            if "/actions/workflows?" in url:
                return {"workflows": [{"id": wid, "path": ".github/workflows/spend.yml"}]}
            if "/actions/workflows/%d/runs" % wid in url:
                return {"workflow_runs": runs}
            return None
        return get

    def test_free_workflows_are_not_asked_about(self):
        hist = audit.history(rows=self.rows(), get=self.fake([]), ledger=[])
        self.assertEqual([h["workflow"] for h in hist], ["spend.yml"])

    def test_never_dispatched_is_not_a_failure(self):
        hist = audit.history(rows=self.rows(), get=self.fake([]), ledger=[])
        self.assertEqual(hist[0]["verdict"], "never dispatched")
        self.assertFalse(audit.main.__name__ and hist[0]["verdict"].startswith("FAIL"))

    def test_a_run_before_the_recorders_proves_nothing_either_way(self):
        hist = audit.history(rows=self.rows(), ledger=[],
                             get=self.fake([{"id": 9, "created_at": "2026-09-24T17:54:26Z"}]))
        self.assertIn("before the recorders", hist[0]["verdict"])
        self.assertNotIn("FAIL", hist[0]["verdict"])

    def test_a_run_after_the_recorders_with_no_row_is_a_failure(self):
        hist = audit.history(rows=self.rows(), ledger=[],
                             get=self.fake([{"id": 4242, "created_at": "2026-10-22T01:00:00Z"}]))
        self.assertTrue(hist[0]["verdict"].startswith("FAIL"))
        self.assertIn("4242", hist[0]["verdict"], "a failure must name the run to chase")

    def test_a_row_naming_the_run_is_evidence(self):
        ledger = [{"workflow": "spend.yml", "run_id": "4242", "provider": "openai"}]
        hist = audit.history(rows=self.rows(), ledger=ledger,
                             get=self.fake([{"id": 4242, "created_at": "2026-10-22T01:00:00Z"}]))
        self.assertEqual(hist[0]["verdict"], "ran 2026-10-22, row in the ledger")
        self.assertEqual(hist[0]["ledger_rows"], 1)

    def test_a_direct_api_row_counts_under_its_source_name(self):
        # `check-tarik-model.yml` writes rows through `record_api_call`, which names a `source`
        # (`check-tarik-model`, no `.yml`) and carries no run id. Matching only `workflow` would
        # report its spend as lost while its rows sat in the file.
        ledger = [{"source": "spend", "provider": "openai"}]
        hist = audit.history(rows=self.rows(), ledger=ledger,
                             get=self.fake([{"id": 77, "created_at": "2026-10-23T01:00:00Z"}]))
        self.assertEqual(hist[0]["verdict"], "ran 2026-10-23, row in the ledger")

    def test_no_network_is_unknown_never_a_failure(self):
        hist = audit.history(rows=self.rows(), get=self.fake([], blind=True), ledger=[])
        self.assertEqual(hist[0]["verdict"], "unknown")
        out = audit.render_history(hist, [])
        self.assertIn("Cannot see the run history", out)
        self.assertNotIn("FAIL", out)

    def test_render_counts_what_was_proved(self):
        hist = audit.history(rows=self.rows(),
                             get=self.fake([{"id": 5, "created_at": "2026-10-23T01:00:00Z"}]),
                             ledger=[{"workflow": "spend.yml", "run_id": "5"}])
        out = audit.render_history(hist, [{"workflow": "spend.yml"}])
        self.assertIn("Ledger rows on disk: 1", out)
        self.assertIn("Spenders proved to have recorded something: 1 of 1", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
