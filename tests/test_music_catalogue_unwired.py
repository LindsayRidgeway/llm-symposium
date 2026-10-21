#!/usr/bin/env python3
# Owner: Desi
"""Pin the music conservatory's reachability gate (2026-10-21).

Why this file exists. The gate landed in `60559c4f` as *two* paths — the script and
`docs/music/index.html` — although the item that asked for it named three. The third,
this file, never reached `main`, so the script that decides whether a piece is
reachable was the only shipped gate with no test holding it still, and a reviewer could
only run it and believe it.

What this file is *not*. It is not pytest. `pytest` is not installed in this project and
never has been: every file under `tests/` is run as a plain `python3 tests/test_*.py`,
by hand, by CI, and by `scripts/landing_suite_check.py`. A pytest-style version of this
file was written on 2026-10-21 and **the landing gate refused the run that wrote it** —
`ModuleNotFoundError: No module named 'pytest'` — which is the second time that trap has
cost a wake (the first is recorded in `.github/workflows/test-and-report.yml`, 2026-10-12).
So: `unittest`, no fixtures, `tempfile` for trees, `redirect_stdout` for output.

What it checks. All six rules, in both directions — a clean tree must be silent and a
defective one must be loud — because a gate tested only on a clean tree is
indistinguishable from a gate that always passes. The three rules that predate this
review are pinned as found; the three added in it (broken score download, dark score,
published scratch file) are pinned as designed. Finally the live repository is measured:
the gate's verdict is about this tree, so it has to hold here.

Written by Desi, who did not write the gate itself.

**The live-tree assertions, repaired 2026-10-21 (third refusal).** The first version of this
file measured `docs/music/` *as it sat on disk* and asserted the result was empty. Three
consecutive runs were then refused at the landing gate with
`this run's diff introduced new failures: test_music_catalogue_unwired.py`, none of which
had touched `docs/music/` — and the cause was not in any of those diffs. The shared checkout
carried an **uncommitted** edit to `docs/music/index.html` (four repertoire cards temporarily
missing) and three tracked `.abc.tmp` files. A test whose verdict depends on another amigo's
half-saved work is a test that charges their edit to whoever lands next, and a landing gate
that cannot tell whose change it is refuses everybody.

The repair keeps the property and drops the hostage: `committed_view()` measures the tree the
*landing* would create — the working tree, with every tracked path that differs from `HEAD`
restored to its committed content — so
  * another amigo's uncommitted edit to a page, card or script cannot fail this file;
  * a deletion the run actually made **is** measured (a delete is on disk as absence, and
    restoring it would hide the run's own cleanup — the three `.abc.tmp` removals in this very
    diff are measured this way);
  * a file the run added is measured as added.
Only *modification in place* is discounted, and it is printed, so it is visible rather than
silent. Two tests below pin both halves of that rule against a throwaway git repository.
"""

from __future__ import annotations

import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import music_catalogue_unwired as gate  # noqa: E402

CARD = ('<article class="repertoire-card"><button data-tune="{tune}">▶ Audition</button>'
        '<h3 class="repertoire-card-title">{title}</h3></article>')

APP_JS = """// engine
const COMPOSITIONS = {
  adagio: {
    id: "adagio",
    abc: "T: Adagio\\nK: Am\\n",
  },
};
"""


def make_tree(root: Path, *, page_linked: bool = True, tune: str = "adagio",
              extra_page: str | None = None, score: str | None = None,
              score_link: str | None = None, scratch: bool = False,
              score_title: str = "Adagio", app_js: str = APP_JS) -> Path:
    """A minimal conservatory: one catalogued piece page, one engine key, one score."""
    music = root / "docs" / "music"
    music.mkdir(parents=True, exist_ok=True)
    (music / "app.js").write_text(app_js, encoding="utf-8")
    (music / "index.html").write_text(
        "<html><body>"
        + (CARD.format(tune=tune, title="Adagio") if page_linked else "")
        + ('<a href="piece.html">piece</a>' if page_linked else "")
        + "</body></html>",
        encoding="utf-8")
    links = f'<a href="{score_link}" download>Download ABC</a>' if score_link else ""
    (music / "piece.html").write_text(
        f"<html><body><h1>Adagio</h1>{links}</body></html>", encoding="utf-8")
    if score is not None:
        (music / score).write_text(f"X: 1\nT: {score_title}\nK: Am\n", encoding="utf-8")
    if extra_page:
        (music / extra_page).write_text("<html><body>extra</body></html>", encoding="utf-8")
    if scratch:
        (music / "piece.abc.tmp").write_text("X: 2\nT: Scratch\n", encoding="utf-8")
    return root


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: {proc.stderr.strip()}")
    return proc.stdout


def committed_view(dest: Path, repo: Path = ROOT) -> tuple[Path, list[str]]:
    """Copy `docs/music/` out of `repo`, substituting committed content for edited-in-place paths.

    Returns the copy's root (to pass as `--root`) and the paths that were substituted, so a test
    can print or assert what it discounted. Deletions and additions are left exactly as they are on
    disk: absence is a state the landing would really produce, and so is a new file.
    """
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(repo / "docs" / "music", dest / "docs" / "music")
    if not (repo / ".git").exists():
        return dest, []
    changed = [p for p in _git(repo, "diff", "--name-only", "HEAD", "--", "docs/music").splitlines()
               if p.strip()]
    replaced = []
    for rel in changed:
        rel = rel.strip()
        on_disk = repo / rel
        if not on_disk.is_file():
            continue  # deleted here, or a directory: the working tree is the truth
        show = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(repo),
                              capture_output=True, text=True)
        if show.returncode != 0:
            continue  # not in HEAD at all: the run added it, so measure it as added
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if on_disk.read_bytes() != show.stdout.encode():
            target.write_bytes(on_disk.read_bytes())
            replaced.append(rel)
        target.write_text(show.stdout, encoding="utf-8")
    return dest, replaced


class MusicCatalogueGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="music-gate-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        saved = dict(gate.KNOWN_DARK)
        self.addCleanup(lambda: (gate.KNOWN_DARK.clear(), gate.KNOWN_DARK.update(saved)))

    def problems(self):
        return gate.report(self.tmp)

    # ------------------------------------------------ the tree is clean when it is clean

    def test_clean_tree_reports_nothing(self):
        make_tree(self.tmp, score="piece.abc", score_link="piece.abc")
        self.assertEqual(self.problems(), [])

    def test_main_exits_zero_on_a_clean_tree(self):
        make_tree(self.tmp, score="piece.abc", score_link="piece.abc")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(gate.main(["--root", str(self.tmp)]), 0)
        self.assertIn("0 problem(s)", out.getvalue())

    # ------------------------------------------------ rule 1: uncatalogued pages

    def test_page_the_catalogue_never_links_is_reported(self):
        make_tree(self.tmp, extra_page="orphan-page.html")
        found = self.problems()
        self.assertTrue(any("NOT CATALOGUED" in line and "orphan-page.html" in line
                            for line in found), found)

    def test_exempt_page_is_not_reported(self):
        make_tree(self.tmp, extra_page="sandbox.html")
        self.assertEqual(self.problems(), [])

    # ------------------------------------------------ rule 2: dead audition buttons

    def test_audition_for_an_unknown_tune_is_reported(self):
        make_tree(self.tmp, tune="notAKey")
        found = self.problems()
        self.assertTrue(any("DEAD AUDITION" in line and "notAKey" in line for line in found), found)

    # ------------------------------------------------ rule 3: dangling catalogue cards

    def test_card_promising_an_absent_page_is_reported(self):
        make_tree(self.tmp)
        index = self.tmp / "docs" / "music" / "index.html"
        index.write_text(index.read_text(encoding="utf-8")
                         + '<a href="never-landed.html">x</a>', encoding="utf-8")
        found = self.problems()
        self.assertTrue(any("DANGLING CARD" in line and "never-landed.html" in line
                            for line in found), found)

    # ------------------------------------------------ rule 4: broken score downloads

    def test_page_offering_an_absent_score_is_reported(self):
        make_tree(self.tmp, score_link="never-landed.abc")
        found = self.problems()
        self.assertTrue(any("BROKEN SCORE" in line and "never-landed.abc" in line
                            for line in found), found)

    def test_page_offering_a_present_score_is_silent(self):
        make_tree(self.tmp, score="piece.abc", score_link="piece.abc")
        self.assertFalse(any("BROKEN SCORE" in line for line in self.problems()))

    # ------------------------------------------------ rule 5: dark scores

    def test_score_with_no_page_and_no_title_anywhere_is_dark(self):
        make_tree(self.tmp, score="dark-one.abc", score_title="Nobody Knows This")
        found = self.problems()
        self.assertTrue(any("DARK SCORE" in line and "dark-one.abc" in line for line in found),
                        found)

    def test_score_with_a_page_of_its_own_is_reachable(self):
        # The page exists, so rule 1 will complain the catalogue does not link it — but the score
        # itself is offered, and that is what rule 5 measures.
        make_tree(self.tmp, score="piece.abc", score_title="Nobody Knows This")
        self.assertFalse(any("DARK SCORE" in line for line in self.problems()))

    def test_score_whose_title_is_in_the_engine_is_reachable(self):
        make_tree(self.tmp, score="tune-file.abc", score_title="Adagio")
        self.assertFalse(any("DARK SCORE" in line for line in self.problems()))

    def test_score_whose_title_is_in_the_catalogue_is_reachable(self):
        make_tree(self.tmp, score="tune-file.abc", score_title="Adagio",
                  app_js="const COMPOSITIONS = {\n};\n")
        self.assertFalse(any("DARK SCORE" in line for line in self.problems()))

    def test_known_dark_score_is_printed_but_not_counted(self):
        make_tree(self.tmp, score="dark-one.abc", score_title="Nobody Knows This")
        gate.KNOWN_DARK["dark-one.abc"] = "owner: the music wing, item 03"
        self.assertEqual(self.problems(), [])
        self.assertTrue(any("dark-one.abc" in line and "item 03" in line
                            for line in gate.known(self.tmp)))

    def test_known_entry_for_a_score_that_is_gone_is_not_printed(self):
        make_tree(self.tmp)
        self.assertEqual(gate.known(self.tmp), [])

    def test_a_new_dark_score_still_fails_even_when_others_are_known(self):
        gate.KNOWN_DARK["some-other.abc"] = "owner: someone"
        make_tree(self.tmp, score="dark-one.abc", score_title="Nobody Knows This")
        self.assertTrue(any("DARK SCORE" in line for line in self.problems()))

    # ------------------------------------------------ rule 6: published scratch files

    def test_tmp_file_in_the_published_directory_is_reported(self):
        make_tree(self.tmp, scratch=True)
        found = self.problems()
        self.assertTrue(any("SCRATCH PUBLISHED" in line and "piece.abc.tmp" in line
                            for line in found), found)

    def test_scratch_check_does_not_count_a_tmp_elsewhere(self):
        make_tree(self.tmp)
        elsewhere = self.tmp / "scripts"
        elsewhere.mkdir()
        (elsewhere / "note.tmp").write_text("scratch outside docs", encoding="utf-8")
        self.assertEqual(self.problems(), [])

    # ------------------------------------------------ exit code is the gate's verdict

    def test_main_exits_one_on_a_defective_tree(self):
        make_tree(self.tmp, scratch=True)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(gate.main(["--root", str(self.tmp)]), 1)
        self.assertIn("1 problem(s)", out.getvalue())

    # ------------------------------------------------ the real tree, measured

    def test_the_live_tree_passes_its_own_gate(self):
        """The gate's verdict is about this repository, so it must hold here too."""
        self.assertEqual(gate.report(), [])

    def test_the_live_tree_has_no_scratch_files_in_docs_music(self):
        self.assertEqual(gate.scratch_files(), [])

    def test_every_live_score_is_either_reachable_or_recorded_as_known(self):
        dark = {name for name, _title in gate.dark_scores()}
        self.assertLessEqual(dark, set(gate.KNOWN_DARK),
                             f"unrecorded dark scores: {sorted(dark - set(gate.KNOWN_DARK))}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
