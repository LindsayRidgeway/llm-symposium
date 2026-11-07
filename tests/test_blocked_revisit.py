#!/usr/bin/env python3
"""Tests for the Status 5 revisit trigger (`scripts/blocked_revisit.py`).

The thing being pinned is not "it prints a list". It is that the *verdict* is decided by evidence
and that its order is the rule, because the failure this script exists to prevent is a state no
mechanism can move out of — and a trigger that says "needs a look" for everything is exactly as
useless as one that says it for nothing.
"""
import datetime as dt
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import blocked_revisit as br  # noqa: E402

NOW = dt.datetime(2026, 10, 19, 3, 0, tzinfo=dt.timezone.utc)


def row(item_id="r1", state="postponed", state_utc="2026-10-18T12:00:00Z", paths=(), reviewer="desi"):
    return {"id": item_id, "amigo": reviewer, "reviewer": reviewer, "state": state,
            "state_utc": state_utc, "paths": list(paths), "short_title": f"item {item_id}"}


class RevisitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "there.md").write_text("x", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def verdict(self, rows, log="", stale_days=14):
        facts = br.build(rows, log, self.repo, stale_days, now=NOW)
        return {f["id"]: f["verdict"] for f in facts}

    def test_landed_wins_over_every_other_verdict(self):
        # Old, absent, no re-look — and still "landed", because a landing is the one fact that
        # settles the item regardless of how it was parked.
        rows = [row(paths=["gone.md"], state_utc="2026-09-01T00:00:00Z")]
        log = "land(wake): work from run r1\n"
        self.assertEqual(self.verdict(rows, log), {"r1": "landed"})

    def test_a_body_that_mentions_the_id_does_not_make_it_landed(self):
        """The defect this pins, measured on 2026-11-07.

        The first version of this script asked `if item["id"] in log_text` over the whole log, so
        any commit that merely *named* a run id marked that run landed. There was one live case:
        `26dd4d7e` is the lander for run 222366ae, and its body carried `b2420fec` inside a
        restored filename — so b2420fec read as landed without having landed, and the docstring's
        "0 have landed since" was true only because it had been written before that commit.
        """
        rows = [row(item_id="b2420fec", paths=["gone.md"], state_utc="2026-10-18T00:00:00Z")]
        log = "land(wake): work from run 222366ae\nrecovered: channels/x-b2420fec.md\n"
        self.assertEqual(self.verdict(rows, log), {"b2420fec": "absent"})

    def test_only_a_lander_subject_that_names_the_run_counts(self):
        """Only the ids a lander subject *carries* are landed; the shape is otherwise ignored."""
        rows = [row(item_id="r2", paths=["gone.md"], state_utc="2026-10-18T00:00:00Z")]
        log = "land(wake): work from run r2\n"
        self.assertEqual(self.verdict(rows, log), {"r2": "landed"})
        # A near-miss subject is not a lander: `chore(wake): close verified run ...` records a
        # verification, not a landing, and says nothing about whether the work is on main.
        self.assertEqual(self.verdict(rows, "chore(wake): close verified bounded run r2\n"),
                         {"r2": "absent"})

    def test_the_codex_prefix_is_a_naming_convention_not_part_of_the_id(self):
        rows = [row(item_id="20261107T090310Z-8ff76697", paths=["gone.md"],
                    state_utc="2026-10-18T00:00:00Z")]
        log = "land(wake): Codex work from run codex-20261107T090310Z-8ff76697\n"
        self.assertEqual(self.verdict(rows, log), {"20261107T090310Z-8ff76697": "landed"})
        # ...and the same run written the other way in the ledger still matches.
        self.assertEqual(self.verdict([row(item_id="codex-20261107T090310Z-8ff76697",
                                           paths=["gone.md"],
                                           state_utc="2026-10-18T00:00:00Z")], log),
                         {"codex-20261107T090310Z-8ff76697": "landed"})

    def test_landing_log_reads_subjects_only_from_a_real_repository(self):
        """`landing_log` must not depend on a body, and must not need `--all` to find landings."""
        repo = self.repo
        git = ["git", "-C", str(repo)]
        for cmd in (["init", "-q"], ["config", "user.email", "t@example.com"],
                    ["config", "user.name", "t"]):
            subprocess.run(git + cmd, check=True, capture_output=True)
        subprocess.run(git + ["commit", "-q", "--allow-empty", "-m",
                              "land(wake): work from run 20261107T090310Z-8ff76697"], check=True)
        subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "recovery: mention 20261107T010211Z-d14caf92"])
        subjects = br.landing_log(repo)
        self.assertEqual(br.landed_run_ids(subjects), {"20261107T090310Z-8ff76697"})

    def test_stale_names_the_items_nobody_came_back_to(self):
        rows = [row(paths=["gone.md"], state_utc="2026-09-01T00:00:00Z")]
        self.assertEqual(self.verdict(rows), {"r1": "stale"})

    def test_a_later_row_about_the_same_item_stops_it_reading_as_stale(self):
        old = row(paths=["gone.md"], state_utc="2026-09-01T00:00:00Z")
        again = row(state_utc="2026-10-15T00:00:00Z", paths=["gone.md"])
        self.assertEqual(self.verdict([old, again]), {"r1": "absent"})

    def test_all_named_paths_present_is_a_look_not_a_done(self):
        # A modified file exists whether or not the change landed, so the verdict is "present",
        # never "accomplished" — the reason line says so out loud.
        self.assertEqual(self.verdict([row(paths=["there.md"])]), {"r1": "present"})

    def test_no_named_path_present_means_the_blocker_stands(self):
        self.assertEqual(self.verdict([row(paths=["gone.md", "also-gone.md"])]), {"r1": "absent"})

    def test_partial_presence_is_not_evidence_the_payload_arrived(self):
        self.assertEqual(self.verdict([row(paths=["there.md", "gone.md"])]), {"r1": "absent"})

    def test_an_item_with_no_repository_path_is_unverifiable_rather_than_guessed(self):
        self.assertEqual(self.verdict([row(paths=[])]), {"r1": "unverifiable"})

    def test_duplicate_rows_collapse_to_the_latest_postponement(self):
        rows = [row(state_utc="2026-10-01T00:00:00Z", paths=["gone.md"]),
                row(state_utc="2026-10-18T00:00:00Z", paths=["there.md"])]
        facts = br.build(rows, "", self.repo, 14, now=NOW)
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0]["postponed_utc"], "2026-10-18T00:00:00Z")
        self.assertEqual(facts[0]["verdict"], "present")

    def test_accomplished_and_rejected_rows_are_not_in_this_queue(self):
        rows = [row(item_id="a", state="accomplished"), row(item_id="b", state="rejected")]
        self.assertEqual(self.verdict(rows), {})

    def test_a_postponement_superseded_by_a_later_verdict_leaves_the_queue(self):
        """The defect measured 2026-11-07, on 58 live items.

        This test used to exist only in its easier form above — items that never had a postponed
        row at all — so a postponement followed by `accomplished` passed it and stayed in the pile
        forever. 56 of the 58 items the census over-reported carried a *model's* decision, and 46
        of them were printed as `present`, which is in `NEEDS_A_LOOK`: the trigger re-filed closed
        work as work waiting for a look. Account:
        channels/reports/2026-11-07-desi-three-numbers-for-one-pile.md
        """
        parked = row(state_utc="2026-10-18T12:00:00Z", paths=["there.md"])
        closed = row(state="accomplished", state_utc="2026-10-19T00:00:00Z", paths=["there.md"])
        self.assertEqual(self.verdict([parked, closed]), {})
        # ...and the same for a rejection, and for the merged file's order (decision first).
        self.assertEqual(self.verdict([row(state="rejected", state_utc="2026-10-19T00:00:00Z"),
                                       parked]), {})
        # A *newer* postponement still wins: re-parking after a closure is a decision too.
        again = row(state_utc="2026-10-20T00:00:00Z", paths=["there.md"])
        self.assertEqual(self.verdict([parked, closed, again]), {"r1": "present"})

    def test_the_ledger_path_is_never_evidence_of_anything(self):
        """Every wake appends to `channels/items.jsonl`, so "it exists" says nothing about an item."""
        self.assertEqual(self.verdict([row(paths=["channels/items.jsonl"])]), {"r1": "unverifiable"})
        facts = br.build([row(paths=["channels/items.jsonl", "there.md"])], "", self.repo, 14, now=NOW)
        self.assertEqual(facts[0]["verdict"], "present")

    def test_the_universe_is_the_ledger_s_own(self):
        """The two readers of one file must not disagree about how big the pile is.

        This is the test the whole 2026-11-07 finding was missing: each tool was tested against its
        own idea of the pile, so 293 versus 235 was invisible for weeks. Run against the real
        ledger, because the disagreement only ever appears in its real shape — duplicates, null
        snapshots, and decisions written out of file order.
        """
        sys.path.insert(0, str(REPO / "channels"))
        import item_ledger  # noqa: E402

        items = item_ledger.load(item_ledger.LEDGER)
        ledger_postponed = {i for i, r in items.items() if r.get("state") == "postponed"}
        mine = {f["id"] for f in br.build(br.load(br.LEDGER), "", self.repo, 14, now=NOW)}
        self.assertEqual(mine, ledger_postponed)

    def test_counts_and_the_look_list_agree(self):
        rows = [row("landed-1", state_utc="2026-10-18T00:00:00Z", paths=["gone.md"]),
                row("stale-1", state_utc="2026-09-01T00:00:00Z", paths=["gone.md"]),
                row("absent-1", state_utc="2026-10-18T00:00:00Z", paths=["gone.md"]),
                row("present-1", state_utc="2026-10-18T00:00:00Z", paths=["there.md"])]
        facts = br.build(rows, "land(wake): work from run landed-1\n", self.repo, 14, now=NOW)
        c = br.counts(facts)
        self.assertEqual(c, {"landed": 1, "stale": 1, "present": 1, "absent": 1, "unverifiable": 0})
        self.assertEqual(len([f for f in facts if f["verdict"] in br.NEEDS_A_LOOK]), 3)

    def test_a_duplicate_row_with_no_state_utc_does_not_crash_the_trigger(self):
        """The ledger's real shape: the same id appears twice, and the filing row has `state_utc: null`.

        Added 2026-11-06 after the script died with `TypeError: '>' not supported between instances
        of 'NoneType' and 'str'` on every run — `dict.get(k, "")` returns the stored None, not the
        default — so the only mechanism that drains Status 5 had never printed a single row.
        """
        postponed = row(item_id="dup", state_utc="2026-10-18T12:00:00Z", paths=("agenda/01.md",))
        filed = dict(postponed, state=None, state_utc=None, reviewer=None)
        got = self.verdict([filed, postponed, filed])
        # The verdict is decided by the paths and the temp repo; what this pins is that the null
        # row neither raises nor votes, and the postponement is still the row that counts.
        self.assertEqual(list(got), ["dup"])

    def test_the_ledger_itself_is_readable_and_duplicates_do_not_double_count(self):
        rows = br.load(br.LEDGER)
        facts = br.build(rows, "", self.repo, 14, now=NOW)
        ids = [f["id"] for f in facts]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(facts), len(br.postponed(rows)))
        self.assertTrue(all(f["verdict"] in br.ORDER for f in facts))


if __name__ == "__main__":
    unittest.main()
