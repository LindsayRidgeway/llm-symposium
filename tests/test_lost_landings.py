"""Tests for scripts/lost_landings.py — the tool that measures work refused whole by the lander.

The bug it exists for (2026-11-13): `git apply` is all-or-nothing, a wake almost always edits
`channels/items.jsonl`, that file moves under every other wake, and so the whole diff comes
back "conflict" — including the new files in it that could not have conflicted with anything,
because they did not exist yet. Four of Desi's runs on 2026-11-11 lost five verdict receipts
and three reports that way, and every surface reported them as fine.

These tests use synthetic patches and a temp tree. They must not depend on the bots' run
directories, which are outside the repository and change under us.
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import lost_landings as ll  # noqa: E402


NEW_FILE_PATCH = """diff --git a/channels/ledger-verdicts/x.json b/channels/ledger-verdicts/x.json
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/channels/ledger-verdicts/x.json
@@ -0,0 +1,2 @@
+{"item": "x", "state": "accomplished"}
+
diff --git a/channels/items.jsonl b/channels/items.jsonl
index 2222222..3333333 100644
--- a/channels/items.jsonl
+++ b/channels/items.jsonl
@@ -1,1 +1,2 @@
 {"id": "x"}
+{"id": "x", "state": "accomplished"}
"""


def test_split_patch_names_every_file_on_the_b_side():
    parts = ll.split_patch(NEW_FILE_PATCH)
    assert [p for p, _ in parts] == ["channels/ledger-verdicts/x.json", "channels/items.jsonl"]


def test_split_patch_does_not_split_on_a_dashes_line_inside_a_hunk():
    # A hunk body may add a line of `---`, which is data. A parser that splits on `+++`/`---`
    # turns one file into two and then applies half of each.
    text = NEW_FILE_PATCH.replace('+{"item": "x", "state": "accomplished"}', '+--- end of receipt ---')
    assert len(ll.split_patch(text)) == 2


def test_is_addition_distinguishes_a_new_file_from_a_modification():
    parts = dict(ll.split_patch(NEW_FILE_PATCH))
    assert ll.is_addition(parts["channels/ledger-verdicts/x.json"]) is True
    assert ll.is_addition(parts["channels/items.jsonl"]) is False


def _run_dir(tmp_path, patch_text, result):
    run_dir = tmp_path / "desi-bot" / "tick-state" / "runs" / "20261111T061555Z-78567de3"
    run_dir.mkdir(parents=True)
    (run_dir / "changes.patch").write_text(patch_text, encoding="utf-8")
    (run_dir / "result.json").write_text(json.dumps(result), encoding="utf-8")
    return run_dir


def test_read_runs_reads_the_land_outcome_and_the_bot_name(tmp_path):
    _run_dir(tmp_path, NEW_FILE_PATCH, {"land": "conflict", "changed_paths": ["channels/items.jsonl"]})
    runs = ll.read_runs(tmp_path)
    assert len(runs) == 1
    assert runs[0]["land"] == "conflict"
    assert runs[0]["bot"] == "desi-bot"
    assert runs[0]["changed"] == ["channels/items.jsonl"]


def test_read_runs_falls_back_to_the_patch_when_changed_paths_is_missing(tmp_path):
    _run_dir(tmp_path, NEW_FILE_PATCH, {"land": "conflict"})
    runs = ll.read_runs(tmp_path)
    assert runs[0]["changed"] == ["channels/ledger-verdicts/x.json", "channels/items.jsonl"]


def test_a_directory_on_the_land_line_is_not_counted_as_an_absent_path(tmp_path):
    # The 2026-11-11 shape: `LAND: channels/ledger-verdicts/` names a directory that exists
    # while the files under it do not. The directory is not the loss; the files are.
    tree = tmp_path / "tree"
    (tree / "channels" / "ledger-verdicts").mkdir(parents=True)
    assert ll.absent(["channels/ledger-verdicts/"], tree) == []
    assert ll.absent(["channels/ledger-verdicts/x.json"], tree) == ["channels/ledger-verdicts/x.json"]


def test_recoverable_offers_the_addition_and_refuses_the_modification(tmp_path):
    run_dir = _run_dir(tmp_path, NEW_FILE_PATCH, {"land": "conflict"})
    tree = tmp_path / "tree"
    (tree / "channels").mkdir(parents=True)
    (tree / "channels" / "items.jsonl").write_text("{}\n", encoding="utf-8")
    run = ll.read_runs(tmp_path)[0]
    assert [p for p, _ in ll.recoverable(run, tree)] == ["channels/ledger-verdicts/x.json"]
    assert Path(run_dir, "changes.patch").is_file()


def test_rescue_writes_the_new_file_and_leaves_the_conflicting_one_alone(tmp_path):
    patch_text = NEW_FILE_PATCH.replace('{"id": "x"}', '{"id": "someone elses line"}')
    _run_dir(tmp_path, patch_text, {"land": "conflict"})
    tree = tmp_path / "tree"
    (tree / "channels").mkdir(parents=True)
    (tree / "channels" / "items.jsonl").write_text('{"id": "moved on"}\n', encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tree, check=True)

    run = ll.read_runs(tmp_path)[0]
    outcome = dict(ll.rescue(run, tree))

    assert outcome["channels/ledger-verdicts/x.json"] == "applied"
    assert (tree / "channels" / "ledger-verdicts" / "x.json").is_file()
    # The modification no longer applies, and the tool must not revert the newer line to force it.
    assert (tree / "channels" / "items.jsonl").read_text(encoding="utf-8") == '{"id": "moved on"}\n'


def test_report_names_a_run_whose_land_failed_even_when_nothing_is_absent(tmp_path):
    # `refused_dirty_tree` with every path already present is not a loss, but it is still a
    # landing that did not happen, and the report must not hide it behind a zero.
    _run_dir(tmp_path, NEW_FILE_PATCH, {"land": "refused_dirty_tree: M x.md",
                                        "changed_paths": ["channels/items.jsonl"]})
    tree = tmp_path / "tree"
    (tree / "channels").mkdir(parents=True)
    (tree / "channels" / "items.jsonl").write_text("{}\n", encoding="utf-8")
    rows = ll.report(ll.read_runs(tmp_path), tree)
    assert rows and rows[0]["land"].startswith("refused_dirty_tree")
    assert rows[0]["missing"] == []


# --- a runner, added 2026-11-13 (Dmitri, 06:0xZ) ---------------------------------------
# This file was recovered out of run 20261113T030505Z-014fc599's patch, where it had sat since
# 03:05Z because the lander refused that run's whole diff over `channels/items.jsonl`. It landed
# without a runner: `python3 tests/test_lost_landings.py` printed nothing and exited 0, and
# `python3 -m unittest tests.test_lost_landings` reported "Ran 0 tests" — the exact defect
# (`tests/test_mail_repo_notifications.py`, 2026-11-13 07:05Z) that a guard which never runs is
# the defect it exists to measure, one level up. The tests below are pytest-style with `tmp_path`
# fixtures and plain `assert`, so the runner supplies the fixture and lets unittest's own loader
# report a count that a reader can check against the file.
import inspect  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402


def _fixtured_test(fn, needs_tmp_path):
    def method(self):
        if needs_tmp_path:
            with tempfile.TemporaryDirectory() as scratch:
                fn(Path(scratch))
        else:
            fn()
    method.__name__ = fn.__name__
    return method


def _suite():
    class LostLandingsTest(unittest.TestCase):
        pass

    for name, obj in sorted(globals().items()):
        if not name.startswith("test_") or not callable(obj):
            continue
        needs = "tmp_path" in inspect.signature(obj).parameters
        setattr(LostLandingsTest, name, _fixtured_test(obj, needs))
    return unittest.defaultTestLoader.loadTestsFromTestCase(LostLandingsTest)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(_suite())
    print(f"Ran {result.testsRun} tests")
    raise SystemExit(0 if result.wasSuccessful() and result.testsRun else 1)
