#!/usr/bin/env python3
"""The lander's `--3way` fallback is executed in a throwaway repository, not asserted (Desi, 2026-11-18).

`scripts/patches/land-runs-three-way-apply.patch` changes three call sites in
`~/LLM/desi-bot/land_runs.py` (the delivery step, a bot file outside this repository) so that a patch
whose only stale hunk is the append-only `channels/items.jsonl` is merged instead of refused.

The claim being executed here is small and checkable without the lander:

  * a patch that appends a row to an append-only JSONL file, applied to a tree that has appended
    something else since, is refused by a plain `git apply` and accepted by `git apply --3way`;
  * `git apply --3way` also exits 0 when it merges **with conflict markers**, so the helper's guard
    (refuse a dirty three-way result; rehearse with `--check` before writing) is tested directly,
    because accepting that exit code would put `<<<<<<<` into a JSONL ledger;
  * the patch applies with `patch -p1` to the lander as installed, and the result byte-compiles.

When the lander is not installed — as on CI — the third group skips with its reason in the message
rather than passing on nothing. Run directly: `python3 tests/test_land_runs_three_way_apply_patch.py`
(pytest is not installed on the wake machines).
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "patches" / "land-runs-three-way-apply.patch"
LANDER = Path.home() / "LLM" / "desi-bot" / "land_runs.py"

ROWS = ['{"id":"a"}\n', '{"id":"b"}\n', '{"id":"c"}\n']


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def output(r):
    return (r.stdout or "") + (r.stderr or "")


class AScratchRepo:
    """A git repository in a temp directory, committed, with no interference from the caller's config."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name)
        git(self.path, "init", "-q", ".")
        git(self.path, "config", "user.email", "wake@example.invalid")
        git(self.path, "config", "user.name", "wake")

    def write(self, rel, text):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def commit(self, msg="base"):
        git(self.path, "add", "-A")
        r = git(self.path, "commit", "-qm", msg)
        assert r.returncode == 0, output(r)

    def close(self):
        self._tmp.cleanup()


class TheRescue(unittest.TestCase):
    """What `_apply` decides, shown on the two shapes a three-way apply can meet."""

    def setUp(self):
        self.repo = AScratchRepo()

    def tearDown(self):
        self.repo.close()

    def stale_append_patch(self):
        """A run's patch: it appends one row, then another body appends a different one."""
        self.repo.write("channels/items.jsonl", "".join(ROWS))
        self.repo.commit()
        self.repo.write("channels/items.jsonl", "".join(ROWS + ['{"id":"this-run"}\n']))
        patch = self.repo.path / "changes.patch"
        patch.write_text(git(self.repo.path, "diff").stdout)
        git(self.repo.path, "checkout", "--", "channels/items.jsonl")
        self.repo.write("channels/items.jsonl", "".join(ROWS + ['{"id":"another-body"}\n']))
        self.repo.commit("another body landed first")
        return patch

    def test_the_plain_apply_refuses_and_three_way_takes_it(self):
        patch = self.stale_append_patch()
        plain = git(self.repo.path, "apply", "--check", str(patch))
        self.assertNotEqual(plain.returncode, 0, "a plain apply should refuse a stale append")
        three = git(self.repo.path, "apply", "--3way", "--check", str(patch))
        self.assertEqual(three.returncode, 0, output(three))

    def test_a_clean_three_way_merge_writes_no_markers(self):
        """A stale patch whose changes do not overlap the other body's is merged, not refused."""
        self.repo.write("discussions/note.md", "one\ntwo\nthree\nfour\n")
        self.repo.commit()
        self.repo.write("discussions/note.md", "ONE\ntwo\nthree\nfour\n")
        patch = self.repo.path / "changes.patch"
        patch.write_text(git(self.repo.path, "diff").stdout)
        git(self.repo.path, "checkout", "--", "discussions/note.md")
        self.repo.write("discussions/note.md", "one\ntwo\nthree\nFOUR\n")
        self.repo.commit("another body edited the same page")
        plain = git(self.repo.path, "apply", "--check", str(patch))
        self.assertNotEqual(plain.returncode, 0, "the plain apply should refuse this patch")
        r = git(self.repo.path, "apply", "--3way", str(patch))
        self.assertEqual(r.returncode, 0, output(r))
        self.assertNotIn("with conflicts", output(r))
        text = (self.repo.path / "discussions/note.md").read_text()
        self.assertEqual(text, "ONE\ntwo\nthree\nFOUR\n", "both edits, no markers")

    def test_a_conflicting_three_way_merge_is_refused_before_it_writes(self):
        """The guard: `--3way` exits 0 with markers, and the helper must not accept that."""
        self.repo.write("channels/items.jsonl", "".join(ROWS))
        self.repo.commit()
        self.repo.write("channels/items.jsonl", "".join(ROWS + ['{"id":"this-run"}\n']))
        patch = self.repo.path / "changes.patch"
        patch.write_text(git(self.repo.path, "diff").stdout)
        git(self.repo.path, "checkout", "--", "channels/items.jsonl")
        # Same place, different row: a genuine same-line append conflict.
        self.repo.write("channels/items.jsonl", "".join(ROWS + ['{"id":"another-body"}\n']))
        self.repo.commit("another body landed first")
        rehearsal = git(self.repo.path, "apply", "--3way", "--check", str(patch))
        self.assertIn(
            "with conflicts",
            output(rehearsal),
            "if git ever stops reporting a dirty three-way merge, the guard in _apply needs to change",
        )
        self.assertFalse(
            (self.repo.path / "channels/items.jsonl").read_text().count("<<<<<<<"),
            "--check must not have written markers",
        )


class ThePatchFile(unittest.TestCase):
    def setUp(self):
        self.text = PATCH.read_text()

    def test_it_is_a_diff_against_the_lander(self):
        self.assertIn("--- a/land_runs.py", self.text)
        self.assertIn("+++ b/land_runs.py", self.text)
        self.assertIn("Base-sha256:", self.text)

    def test_it_replaces_all_three_sites_and_names_its_reason(self):
        removed = [l for l in self.text.splitlines()
                   if l.startswith("-") and not l.startswith("---")]
        self.assertEqual(len(removed), 4, "two lines in assess(), one in each land path: %r" % removed)
        self.assertTrue(all('git("apply"' in l for l in removed), removed)
        self.assertIn("--3way", self.text)
        self.assertIn("channels/items.jsonl", self.text)
        self.assertIn("Owner:", self.text)


@unittest.skipUnless(LANDER.is_file(), "land_runs.py is not installed here (expected on CI)")
class AppliesToTheInstalledLander(unittest.TestCase):
    def test_patch_applies_and_compiles(self):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            copy = work / "land_runs.py"
            copy.write_bytes(LANDER.read_bytes())
            r = subprocess.run(["patch", "-p1", "-i", str(PATCH)], cwd=work,
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, output(r))
            patched = copy.read_text()
            self.assertEqual(patched.count("def _apply("), 1)
            self.assertIn("if _apply(patch).returncode != 0", patched)
            self.assertIn("r = _apply(patch, cwd=wt)", patched)
            self.assertNotIn('r = git("apply", str(patch), cwd=wt)', patched)
            c = subprocess.run([sys.executable, "-m", "py_compile", str(copy)],
                               capture_output=True, text=True)
            self.assertEqual(c.returncode, 0, output(c))


if __name__ == "__main__":
    unittest.main(verbosity=2)
