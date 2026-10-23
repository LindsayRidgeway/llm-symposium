"""The landing census must count fates the way the logs actually spell them.

The report `channels/reports/2026-10-23-dmitri-where-the-finished-work-goes.md` rests on numbers
this script prints, so the two log shapes that carry the whole finding — the `left unlanded` line
that names the file, and the draft-branch line that carries the run id — are pinned here. The
failure being measured was a single file stalling deliveries for eight days, so a census that
silently returned zero for either shape would have reported "nothing wrong" with confidence.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import landing_outcome_census as census  # noqa: E402

LOG = """\
2026-10-21 11:29:10,285 WARNING run 20261021T152546Z-92d03b8d claimed to land 2 path(s) it did not change: docs/gallery/index.html
2026-10-21 11:29:10,308 INFO run 20261021T152546Z-92d03b8d landing: conflict
2026-10-21 11:29:12,043 WARNING landing: patch does not apply to main cleanly, left unlanded: error: patch failed: channels/items.jsonl:1949
2026-10-21 13:35:44,614 INFO landed draft on branch drafts/tick-20261021T172604Z-18547ba5 (2 file(s))
2026-10-21 15:28:45,208 INFO run 20261021T192610Z-8b7277ec landing: landed
2026-10-22 01:38:07,223 INFO run 20261022T052727Z-d406cb2b landing: refused_dirty_tree: insights/2026-09-09-rover-build-03-manual-transcription.md
2026-10-22 03:44:58,007 INFO run 20261022T072756Z-55db92d8 landing: commit_failed: the diff applied but HEAD did not move (git commit rc=1)
"""


class CensusTest(unittest.TestCase):
    def setUp(self):
        self.result = census.census(LOG.splitlines())

    def test_outcome_states_are_counted(self):
        self.assertEqual(self.result["outcomes"]["landed"], 1)
        self.assertEqual(self.result["outcomes"]["conflict"], 1)
        self.assertEqual(self.result["outcomes"]["refused_dirty_tree"], 1)
        self.assertEqual(self.result["outcomes"]["commit_failed"], 1)

    def test_apply_failure_names_its_file(self):
        self.assertEqual(self.result["cause_paths"]["channels/items.jsonl"], 1)

    def test_apply_failure_kind_is_distinguished(self):
        self.assertEqual(self.result["cause_kinds"]["hunk_context_moved"], 1)

    def test_draft_branch_line_carries_the_run(self):
        self.assertIn("20261021T172604Z-18547ba5", self.result["draft_runs"])

    def test_unlanded_apply_is_attributed_to_the_run_before_it(self):
        # The `left unlanded` line names no run, so it belongs to the run whose landing line
        # came last -- 92d03b8d, whose conflict is exactly why the fallback ran.
        self.assertIn("20261021T152546Z-92d03b8d", self.result["lost_runs"])

    def test_claim_mismatch_is_not_counted_as_an_apply_failure(self):
        self.assertEqual(self.result["cause_kinds"]["claimed_paths_not_changed"], 1)
        self.assertEqual(sum(self.result["cause_paths"].values()), 1)

    def test_final_fates_do_not_count_a_landed_run_as_a_draft(self):
        result = dict(self.result)
        result["draft_runs"] = set(result["draft_runs"]) | {"20261021T192610Z-8b7277ec"}
        result["final"] = census.final_fates(result)
        self.assertEqual(result["final"]["20261021T192610Z-8b7277ec"], "MAIN")

    def test_failing_path_handles_both_git_shapes(self):
        self.assertEqual(census.failing_path("error: patch failed: channels/tasks.md:12"),
                         "channels/tasks.md")
        self.assertEqual(census.failing_path("error: scripts/x.py: does not exist in index"),
                         "scripts/x.py")
        self.assertEqual(census.failing_path(
            "error: 2b/changes.patch:151: trailing whitespace."), "2b/changes.patch")
        self.assertIsNone(census.failing_path("error: corrupt patch at line 4"))


if __name__ == "__main__":
    unittest.main()
