#!/usr/bin/env python3
"""The scheduled jam check decides from arguments, not from the room (Desi, 2026-11-26).

`scripts/jam_watch.py` is the mechanical half of the founder's de-jamming procedure, moved onto the
07:45 job so it stops costing him a conversation. Its whole value is that the decision is a pure
function of what the previous checks recorded: two snapshots a human had to hold by hand become a
history on disk, and "the head hasn't moved across two wakes" becomes arithmetic.

So the arithmetic is what is tested here — the heads, the history and the lander's dropped paths are
all arguments. Nothing in this file reads the commons, which is why it can be run at any hour.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module():
    spec = importlib.util.spec_from_file_location("jm", ROOT / "scripts" / "jam_watch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


jm = module()


def head(block, ident):
    return {"block": block, "id": ident}


class TheHeadIsTheFirstItem(unittest.TestCase):
    def test_the_key_is_the_item_not_its_date(self):
        a = {"block": "value", "id": "x", "when": "2026-11-26", "kind": "value", "size": 3}
        b = {"block": "value", "id": "x", "when": "2026-11-27"}
        self.assertEqual(jm.key(a), jm.key(b))

    def test_no_head_is_a_key_of_none(self):
        self.assertIsNone(jm.key(None))
        self.assertIsNone(jm.key({}))


class AStreakCountsUnchangedChecks(unittest.TestCase):
    def test_two_previous_checks_on_the_same_head_is_the_trigger(self):
        hist = [{"seat": "desi", "head": head("value", "a")},
                {"seat": "desi", "head": head("value", "a")}]
        self.assertEqual(jm.streak(hist, "desi", ("value", "a"), 2), 2)

    def test_a_changed_head_breaks_the_streak(self):
        hist = [{"seat": "desi", "head": head("value", "a")},
                {"seat": "desi", "head": head("value", "b")}]
        self.assertEqual(jm.streak(hist, "desi", ("value", "a"), 2), 0)

    def test_another_seat_does_not_count_for_this_one(self):
        hist = [{"seat": "gemini", "head": head("value", "a")},
                {"seat": "desi", "head": head("value", "a")}]
        self.assertEqual(jm.streak(hist, "desi", ("value", "a"), 2), 1)


class TheThreeTriggers(unittest.TestCase):
    def test_an_unmoved_head_fires_with_the_count(self):
        heads = {"desi": head("reading", "readmine")}
        hist = [{"seat": "desi", "head": head("reading", "readmine")},
                {"seat": "desi", "head": head("reading", "readmine")}]
        fired = jm.verdicts(heads, hist, need=2)
        self.assertEqual([t["trigger"] for t in fired], ["unmoved"])
        self.assertEqual(fired[0]["checks"], 2)
        self.assertIn("3 consecutive", fired[0]["because"])

    def test_a_moving_head_fires_nothing(self):
        heads = {"desi": head("value", "port-two")}
        hist = [{"seat": "desi", "head": head("value", "port-one")}]
        self.assertEqual(jm.verdicts(heads, hist, need=2), [])

    def test_a_seat_with_no_head_is_reported_rather_than_skipped(self):
        fired = jm.verdicts({"desi": None}, [])
        self.assertEqual(fired[0]["trigger"], "unmoved")
        self.assertIn("no head at all", fired[0]["because"])

    def test_a_dropped_path_from_the_lander_fires(self):
        fired = jm.verdicts({}, [], dropped=[{"seat": "gwen", "run": "r1", "path": " D tests/x.py"}])
        self.assertEqual(fired[0]["trigger"], "dropped")
        self.assertEqual(fired[0]["seat"], "gwen")

    def test_an_empty_value_queue_is_a_defect_not_a_rest(self):
        fired = jm.verdicts({}, [], empty=["all"])
        self.assertEqual(fired[0]["trigger"], "empty-queue")


class TheHistoryIsOnDisk(unittest.TestCase):
    def test_history_reads_jsonl_and_skips_damage(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "jam-watch.jsonl"
            p.write_text('{"seat": "desi", "head": {"block": "value", "id": "a"}}\n'
                         'not json\n\n'
                         '{"seat": "gemini", "head": {}}\n', encoding="utf-8")
            rows = jm.history(p)
        self.assertEqual([r["seat"] for r in rows], ["desi", "gemini"])

    def test_a_missing_record_is_an_empty_history_not_an_error(self):
        self.assertEqual(jm.history(Path("/nonexistent/jam-watch.jsonl")), [])

    def test_the_record_a_run_appends_is_one_row_per_seat(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "channels").mkdir()
            (repo / "channels" / "jam-watch.jsonl").write_text("", encoding="utf-8")
            rows = []
            for seat in jm.SEATS:
                rows.append({"date": "2026-11-26", "seat": seat, "head": {}, "fired": []})
            with (repo / "channels" / "jam-watch.jsonl").open("a", encoding="utf-8") as fh:
                for row in rows:
                    fh.write(json.dumps(row) + "\n")
            got = jm.history(repo / "channels" / "jam-watch.jsonl")
        self.assertEqual(len(got), len(jm.SEATS))
        self.assertEqual({r["seat"] for r in got}, set(jm.SEATS))


class TheValueQueueIsReadAsAQueue(unittest.TestCase):
    def test_open_items_mean_no_finding(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "channels").mkdir()
            (repo / "channels" / "value-queue.json").write_text(json.dumps(
                {"items": [{"id": "a", "done": True}, {"id": "b"}]}), encoding="utf-8")
            self.assertEqual(jm.empty_value_queues(repo), [])

    def test_every_item_done_is_the_empty_queue(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "channels").mkdir()
            (repo / "channels" / "value-queue.json").write_text(json.dumps(
                {"items": [{"id": "a", "done": True}]}), encoding="utf-8")
            self.assertEqual(jm.empty_value_queues(repo), ["all"])

    def test_a_missing_queue_file_is_not_evidence_of_emptiness(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(jm.empty_value_queues(Path(td)), [])


class ItRunsWhereNothingIsJammed(unittest.TestCase):
    def test_the_live_commons_measures(self):
        # Not an assertion about the verdict — that changes hour to hour — but that the check can
        # measure at all. A scheduled check that exits 2 has told nobody anything.
        heads = jm.heads_now(ROOT)
        self.assertEqual(set(heads), set(jm.SEATS))
        self.assertGreaterEqual(sum(1 for h in heads.values() if h), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
