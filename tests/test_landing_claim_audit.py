#!/usr/bin/env python3
"""Tests for `scripts/landing_claim_audit.py` — the alarm on machine-closed rows.

Written 2026-11-10 (Desi). The tool exists because two rules close a ledger row without a
reader, and both are statements about the repository read as statements about the work:
`auto:land` keys on the run id appearing in *any* landing commit, and `auto:path` asks
whether the paths the row names *exist* on main. A run that landed its report and lost the
file carrying its work satisfies both. Measured case: `20261108T225315Z-8533d17c`, whose
row is `accomplished` / `auto:land` while no commit from that run touched the test file.

So what these tests pin is the distinction the tool's verdict rests on: **touched by the
run's own commits**, not *present on disk*. The case that matters most is the one where the
named path is sitting in the working tree the whole time — the pre-existing file a deletion
patch meant to remove, or the file a lost modification left untouched. If those read as
clean, the alarm is decorative.

Offline. Every case is built in a throwaway git repository and ledger under a temp
directory; the real checkout is read once, by the CLI smoke test, and that asserts only that
the tool runs and prints a count — not what it finds, which changes with every landing.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import landing_claim_audit as lca  # noqa: E402

RUN_HOLLOW = "20261109T010101Z-aaaa0001"
RUN_PARTIAL = "20261109T020202Z-bbbb0002"
RUN_CLEAN = "20261109T030303Z-cccc0003"
RUN_UNSEEN = "20261109T040404Z-dddd0004"


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


def commit(repo: Path, subject: str, *paths: str, body: str = ""):
    """Write each path with unique content and commit it under `subject`."""
    for rel in paths:
        f = repo / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"{subject} :: {rel}\n")
    git(repo, "add", "-A")
    msg = subject if not body else f"{subject}\n\n{body}"
    git(repo, "commit", "-q", "-m", msg)


def make_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@example.invalid")
    git(repo, "config", "user.name", "Test")
    commit(repo, "seed", "a.md", "b.md", "c.md", "channels/items.jsonl")
    return repo


def write_ledger(path: Path, rows):
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write((row if isinstance(row, str) else json.dumps(row)) + "\n")


def row(run_id, paths, reviewer="auto:land", state="accomplished", amigo="desi", title=""):
    return {"id": run_id, "amigo": amigo, "state": state, "reviewer": reviewer,
            "paths": list(paths), "title": title}


class CommitsByRunTest(unittest.TestCase):
    """The mapping the whole audit reads: run id -> the paths that run's commits changed."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_repo(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def test_lander_subject_yields_the_paths_it_carried(self):
        commit(self.repo, f"land(wake): work from run {RUN_CLEAN}", "a.md", "channels/items.jsonl")
        carried = lca.commits_by_run(self.repo)
        self.assertEqual(carried[RUN_CLEAN], {"a.md", "channels/items.jsonl"})

    def test_a_subject_naming_two_runs_credits_both(self):
        # The measured delivery defect: a 10-09 diff sat uncommitted for three days and was
        # carried out inside another run's commit. The tool must see the path under both ids,
        # or the run whose work was carried reads as having touched nothing.
        commit(self.repo, f"land(wake): work from run {RUN_CLEAN} run {RUN_UNSEEN}",
               "b.md", "channels/items.jsonl")
        carried = lca.commits_by_run(self.repo)
        self.assertEqual(carried[RUN_CLEAN], {"b.md", "channels/items.jsonl"})
        self.assertEqual(carried[RUN_UNSEEN], {"b.md", "channels/items.jsonl"})

    def test_a_subject_without_a_run_id_creates_no_entry(self):
        commit(self.repo, "chore: tidy the desk", "c.md")
        carried = lca.commits_by_run(self.repo)
        self.assertNotIn("chore:", carried)
        self.assertEqual([k for k, v in carried.items() if "c.md" in v], [])

    def test_commits_outside_the_current_branch_still_count(self):
        # `--all` matters: a wake's work can land on a review branch and never reach main,
        # which is exactly the state the audit has to be able to describe.
        git(self.repo, "checkout", "-q", "-b", "side")
        commit(self.repo, f"land(wake): work from run {RUN_PARTIAL}", "b.md")
        git(self.repo, "checkout", "-q", "-")
        self.assertIn("b.md", lca.commits_by_run(self.repo).get(RUN_PARTIAL, set()))


class LatestRowsTest(unittest.TestCase):
    """The ledger is append-only, so which row is *in force* is a decision the tool makes."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self._tmp.name) / "items.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def test_last_write_wins(self):
        write_ledger(self.ledger, [
            row(RUN_HOLLOW, ["a.md"], title="first"),
            row(RUN_HOLLOW, ["b.md"], title="second"),
        ])
        rows = lca.latest_rows(self.ledger)
        self.assertEqual(rows[RUN_HOLLOW]["title"], "second")

    def test_a_reader_verdict_hides_the_machine_row_unless_asked(self):
        # The measured case: run 20261108T225315Z-8533d17c's false `auto:land` row vanished
        # from the audit the moment a reader verdicted it. `--machine-rows` is why the tool
        # can measure incidence and not only survivors.
        write_ledger(self.ledger, [
            row(RUN_HOLLOW, ["a.md"], reviewer="auto:land"),
            row(RUN_HOLLOW, ["a.md"], reviewer="claude", state="accomplished"),
        ])
        self.assertEqual(lca.latest_rows(self.ledger)[RUN_HOLLOW]["reviewer"], "claude")
        machine = lca.latest_rows(self.ledger, machine_only=True)
        self.assertEqual(machine[RUN_HOLLOW]["reviewer"], "auto:land")

    def test_a_non_machine_row_after_a_machine_row_does_not_erase_it(self):
        write_ledger(self.ledger, [
            row(RUN_HOLLOW, ["a.md"], reviewer="auto:path"),
            row(RUN_HOLLOW, ["a.md"], reviewer="gemini", state="accomplished"),
            row(RUN_PARTIAL, ["b.md"], reviewer="auto:path"),
        ])
        machine = lca.latest_rows(self.ledger, machine_only=True)
        self.assertEqual(set(machine), {RUN_HOLLOW, RUN_PARTIAL})
        self.assertEqual(machine[RUN_HOLLOW]["reviewer"], "auto:path")

    def test_malformed_lines_and_rows_without_an_id_are_skipped(self):
        write_ledger(self.ledger, [
            "{not json",
            json.dumps({"state": "accomplished", "reviewer": "auto:land"}),
            json.dumps(["a list, not a row"]),
            row(RUN_CLEAN, ["a.md"]),
        ])
        self.assertEqual(set(lca.latest_rows(self.ledger)), {RUN_CLEAN})


class AuditTest(unittest.TestCase):
    """Touched-by-the-run, not present-on-disk. Every case below has the path on disk."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_repo(self.tmp)
        self.ledger = self.tmp / "items.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def findings(self, rows, **kw):
        write_ledger(self.ledger, rows)
        return lca.audit(lca.latest_rows(self.ledger, **kw), lca.commits_by_run(self.repo))

    def test_a_preexisting_path_the_run_never_touched_is_hollow(self):
        # c.md is on disk and in main from the seed commit. A row naming it, certified because
        # the path exists, names nothing the run did — the deletion-patch inverse case.
        found = self.findings([row(RUN_HOLLOW, ["c.md"], reviewer="auto:path")])
        self.assertEqual([f["kind"] for f in found], ["hollow"])
        self.assertEqual(found[0]["touched"], [])
        self.assertEqual(found[0]["named"], ["c.md"])

    def test_a_run_that_touched_every_named_path_is_clean(self):
        commit(self.repo, f"land(wake): work from run {RUN_CLEAN}", "a.md", "channels/items.jsonl")
        self.assertEqual(self.findings([row(RUN_CLEAN, ["a.md", "channels/items.jsonl"])]), [])

    def test_a_landing_smaller_than_the_row_claims_is_partial(self):
        commit(self.repo, f"land(wake): work from run {RUN_PARTIAL}", "b.md", "channels/items.jsonl")
        found = self.findings([row(RUN_PARTIAL, ["b.md", "c.md"], reviewer="auto:land")])
        self.assertEqual([f["kind"] for f in found], ["partial"])
        self.assertEqual(found[0]["touched"], ["b.md"])
        self.assertEqual(found[0]["named"], ["b.md", "c.md"])

    def test_work_carried_by_another_runs_landing_commit_is_not_hollow(self):
        # Measured 2026-11-10: 20 of 20 hollow rows were this case. The lander batches several
        # runs' work into one commit and the subject names some run ids and not others, so the
        # work is on main under the *other* run's id. Reporting that as lost work would send a
        # reader hunting for a file that is sitting in the tree.
        commit(self.repo, f"land(wake): work from run {RUN_PARTIAL}", "b.md")
        found = self.findings([row(RUN_CLEAN, ["b.md"], reviewer="auto:path")])
        self.assertEqual([f["kind"] for f in found], ["carried"])
        self.assertEqual(found[0]["carried_by"], {"b.md": RUN_PARTIAL})
        self.assertEqual(found[0]["lost"], [])

    def test_one_path_no_landing_ever_touched_makes_the_row_hollow(self):
        # Carried is a statement about every named path. One path nothing accounts for is the
        # defect the tool exists for, whatever the rest of the row's story is.
        commit(self.repo, f"land(wake): work from run {RUN_PARTIAL}", "b.md")
        found = self.findings([row(RUN_CLEAN, ["b.md", "c.md"], reviewer="auto:path")])
        self.assertEqual([f["kind"] for f in found], ["hollow"])
        self.assertEqual(found[0]["lost"], ["c.md"])
        self.assertEqual(found[0]["carried_by"], {"b.md": RUN_PARTIAL})

    def test_who_carried_is_the_inverse_and_keeps_every_run(self):
        # A path may be touched by more than one run (the 10-09 diff carried out inside a 10-12
        # landing), so the inverse keeps a list rather than one owner.
        owners = lca.who_carried({"r1": {"a.md"}, "r2": {"a.md", "b.md"}})
        self.assertEqual(sorted(owners["a.md"]), ["r1", "r2"])
        self.assertEqual(owners["b.md"], ["r2"])

    def test_a_row_never_carries_itself(self):
        # In the hollow branch the run touched none of its named paths, so this cannot arise from
        # a real log — it is a guard: if the exclusion were dropped, a row could be its own alibi
        # and no hollow row would ever be reported again.
        commit(self.repo, f"land(wake): work from run {RUN_CLEAN}", "a.md")
        commits = {RUN_CLEAN: {"a.md"}}
        found = lca.audit({RUN_CLEAN: row(RUN_CLEAN, ["a.md"])}, commits,
                          owners=lca.who_carried(commits))
        self.assertEqual(found, [])

    def test_the_ledger_itself_never_counts_as_evidence(self):        # Every landing touches channels/items.jsonl, so its presence is no evidence at all.
        commit(self.repo, f"land(wake): work from run {RUN_HOLLOW}", "channels/items.jsonl")
        self.assertEqual(self.findings([row(RUN_HOLLOW, ["channels/items.jsonl"])]), [])
        found = self.findings([row(RUN_HOLLOW, ["channels/items.jsonl", "a.md"])])
        self.assertEqual([f["kind"] for f in found], ["hollow"])

    def test_rows_that_are_not_machine_closed_accomplishments_are_skipped(self):
        found = self.findings([
            row(RUN_HOLLOW, ["a.md"], state="open", reviewer=""),      # still waiting
            row(RUN_PARTIAL, ["a.md"], state="postponed"),             # a person's verdict
            row(RUN_CLEAN, ["a.md"], reviewer="desi"),                 # a reader, not a machine
        ])
        self.assertEqual(found, [])

    def test_a_row_naming_no_paths_has_nothing_to_be_hollow_about(self):
        self.assertEqual(self.findings([row(RUN_HOLLOW, [])]), [])

    def test_machine_rows_mode_sees_the_row_a_reader_replaced(self):
        commit(self.repo, f"land(wake): work from run {RUN_CLEAN}", "a.md")
        rows = [
            row(RUN_CLEAN, ["a.md"], reviewer="auto:land"),   # true
            row(RUN_CLEAN, ["a.md"], reviewer="desi"),        # a reader agreed; row in force
            row(RUN_HOLLOW, ["c.md"], reviewer="auto:path"),  # false, unread
            row(RUN_HOLLOW, ["c.md"], reviewer="tarik"),      # ...and now verdicted
        ]
        self.assertEqual(self.findings(rows), [])
        self.assertEqual([f["id"] for f in self.findings(rows, machine_only=True)], [RUN_HOLLOW])

    def test_a_title_is_truncated_and_amigo_is_carried_for_the_reader(self):
        found = self.findings([row(RUN_HOLLOW, ["c.md"], amigo="gemini", title="x" * 400)])
        self.assertEqual(found[0]["amigo"], "gemini")
        self.assertEqual(len(found[0]["title"]), 90)


class CliTest(unittest.TestCase):
    """Exit code 1 on any hollow row is the whole reason this can be an alarm."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_repo(self.tmp)
        self.ledger = self.tmp / "items.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def run_tool(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "landing_claim_audit.py"),
             "--repo", str(self.repo), "--ledger", str(self.ledger), *args],
            capture_output=True, text=True,
        )

    def test_exit_1_and_json_when_a_row_is_hollow(self):
        write_ledger(self.ledger, [row(RUN_HOLLOW, ["c.md"], reviewer="auto:path")])
        proc = self.run_tool("--json")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["checked"], 1)
        self.assertEqual([f["id"] for f in payload["hollow"]], [RUN_HOLLOW])
        self.assertEqual(payload["carried"], [])
        self.assertEqual(payload["partial"], [])

    def test_exit_0_when_every_machine_row_is_carried(self):
        commit(self.repo, f"land(wake): work from run {RUN_CLEAN}", "a.md")
        write_ledger(self.ledger, [row(RUN_CLEAN, ["a.md"])])
        proc = self.run_tool()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("1 machine-closed rows; 0 hollow, 0 carried", proc.stdout)

    def test_partial_alone_does_not_trip_the_alarm(self):
        # A partial landing is real work, smaller than claimed: worth printing, not worth
        # waking anyone at exit 1. Only a row that names nothing the run did is hollow.
        commit(self.repo, f"land(wake): work from run {RUN_PARTIAL}", "b.md")
        write_ledger(self.ledger, [row(RUN_PARTIAL, ["b.md", "c.md"])])
        proc = self.run_tool()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PARTIAL", proc.stdout)
        self.assertNotIn("HOLLOW", proc.stdout)

    def test_the_limit_is_printed_as_a_remainder(self):
        rows = [row(f"20261109T01010{i}Z-hollow{i:02d}", ["c.md"]) for i in range(4)]
        write_ledger(self.ledger, rows)
        proc = self.run_tool("--limit", "2")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("2 more hollow row(s); --show-all", proc.stdout)

    def test_the_real_checkout_runs(self):
        # A smoke test only: the findings move with every landing, so nothing here asserts them.
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "landing_claim_audit.py"), "--json"],
            capture_output=True, text=True, timeout=300,
        )
        self.assertIn(proc.returncode, (0, 1), proc.stderr)
        self.assertIn("checked", json.loads(proc.stdout))


if __name__ == "__main__":
    unittest.main(verbosity=2)
