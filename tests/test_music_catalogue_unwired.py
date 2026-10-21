#!/usr/bin/env python3
# Owner: Desi
"""Tests for scripts/music_catalogue_unwired.py — the music conservatory's reachability gate.

Why this file exists (2026-10-21). The gate landed in `60559c4f` as *two paths*: the script and
`docs/music/index.html`. Item `20261019T111859Z-35b1dd08` named three, and the third —
`tests/test_music_catalogue_unwired.py` — never reached `main`. So the script that decides whether
a piece is reachable was itself the only shipped script with no test holding it still, and a reviewer
could only run it and believe it.

This is the review's own check on that gate: every one of the six rules is exercised on a tree built
for the occasion, in both directions — clean tree silent, defective tree loud — because a gate tested
only on a clean tree is indistinguishable from a gate that always passes.

Written by Desi, who did not write the gate. The three checks that already existed are pinned as
found; the three added in this review (broken score download, dark score, published scratch file) are
pinned as designed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import music_catalogue_unwired as gate  # noqa: E402


CARD = '<article class="repertoire-card"><button data-tune="{tune}">▶ Audition</button>' \
       '<h3 class="repertoire-card-title">{title}</h3></article>'

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


def problems(root: Path) -> list[str]:
    return gate.report(root)


# ---------------------------------------------------------------- the tree is clean when it is clean

def test_clean_tree_reports_nothing(tmp_path):
    make_tree(tmp_path, score="piece.abc", score_link="piece.abc")
    assert problems(tmp_path) == []


def test_main_exits_zero_on_a_clean_tree(tmp_path, capsys):
    make_tree(tmp_path, score="piece.abc", score_link="piece.abc")
    assert gate.main(["--root", str(tmp_path)]) == 0
    assert "0 problem(s)" in capsys.readouterr().out


# ---------------------------------------------------------------- rule 1: uncatalogued pages

def test_page_the_catalogue_never_links_is_reported(tmp_path):
    make_tree(tmp_path, extra_page="orphan-page.html")
    found = problems(tmp_path)
    assert any("NOT CATALOGUED" in line and "orphan-page.html" in line for line in found)


def test_exempt_page_is_not_reported(tmp_path):
    make_tree(tmp_path, extra_page="sandbox.html")
    assert problems(tmp_path) == []


# ---------------------------------------------------------------- rule 2: dead audition buttons

def test_audition_for_an_unknown_tune_is_reported(tmp_path):
    make_tree(tmp_path, tune="notAKey")
    found = problems(tmp_path)
    assert any("DEAD AUDITION" in line and "notAKey" in line for line in found)


# ---------------------------------------------------------------- rule 3: dangling catalogue cards

def test_card_promising_an_absent_page_is_reported(tmp_path):
    make_tree(tmp_path)
    index = tmp_path / "docs" / "music" / "index.html"
    index.write_text(index.read_text(encoding="utf-8") + '<a href="never-landed.html">x</a>',
                     encoding="utf-8")
    found = problems(tmp_path)
    assert any("DANGLING CARD" in line and "never-landed.html" in line for line in found)


# ---------------------------------------------------------------- rule 4: broken score downloads

def test_page_offering_an_absent_score_is_reported(tmp_path):
    make_tree(tmp_path, score_link="never-landed.abc")
    found = problems(tmp_path)
    assert any("BROKEN SCORE" in line and "never-landed.abc" in line for line in found)


def test_page_offering_a_present_score_is_silent(tmp_path):
    make_tree(tmp_path, score="piece.abc", score_link="piece.abc")
    assert not any("BROKEN SCORE" in line for line in problems(tmp_path))


# ---------------------------------------------------------------- rule 5: dark scores

def test_score_with_no_page_and_no_title_anywhere_is_dark(tmp_path):
    make_tree(tmp_path, score="dark-one.abc", score_title="Nobody Knows This")
    found = problems(tmp_path)
    assert any("DARK SCORE" in line and "dark-one.abc" in line for line in found)


def test_score_with_a_page_of_its_own_is_reachable(tmp_path):
    # The page exists, so rule 1 will complain the catalogue does not link it — but the score itself
    # is offered, and that is what rule 5 measures.
    make_tree(tmp_path, score="piece.abc", score_title="Nobody Knows This")
    assert not any("DARK SCORE" in line for line in problems(tmp_path))


def test_score_whose_title_is_in_the_engine_is_reachable(tmp_path):
    make_tree(tmp_path, score="tune-file.abc", score_title="Adagio")
    assert not any("DARK SCORE" in line for line in problems(tmp_path))


def test_score_whose_title_is_in_the_catalogue_is_reachable(tmp_path):
    make_tree(tmp_path, score="tune-file.abc", score_title="Adagio",
              app_js="const COMPOSITIONS = {\n};\n")
    assert not any("DARK SCORE" in line for line in problems(tmp_path))


def test_known_dark_score_is_printed_but_not_counted(tmp_path, monkeypatch):
    make_tree(tmp_path, score="dark-one.abc", score_title="Nobody Knows This")
    monkeypatch.setitem(gate.KNOWN_DARK, "dark-one.abc", "owner: the music wing, item 03")
    assert problems(tmp_path) == []
    assert any("dark-one.abc" in line and "item 03" in line for line in gate.known(tmp_path))


def test_known_entry_for_a_score_that_is_gone_is_not_printed(tmp_path):
    make_tree(tmp_path)
    assert gate.known(tmp_path) == []


def test_a_new_dark_score_still_fails_even_when_others_are_known(tmp_path, monkeypatch):
    monkeypatch.setitem(gate.KNOWN_DARK, "some-other.abc", "owner: someone")
    make_tree(tmp_path, score="dark-one.abc", score_title="Nobody Knows This")
    assert any("DARK SCORE" in line for line in problems(tmp_path))


# ---------------------------------------------------------------- rule 6: published scratch files

def test_tmp_file_in_the_published_directory_is_reported(tmp_path):
    make_tree(tmp_path, scratch=True)
    found = problems(tmp_path)
    assert any("SCRATCH PUBLISHED" in line and "piece.abc.tmp" in line for line in found)


def test_scratch_check_does_not_count_a_tmp_elsewhere(tmp_path):
    make_tree(tmp_path)
    elsewhere = tmp_path / "scripts"
    elsewhere.mkdir()
    (elsewhere / "note.tmp").write_text("scratch outside docs", encoding="utf-8")
    assert problems(tmp_path) == []


# ---------------------------------------------------------------- exit code is the gate's verdict

def test_main_exits_one_on_a_defective_tree(tmp_path, capsys):
    make_tree(tmp_path, scratch=True)
    assert gate.main(["--root", str(tmp_path)]) == 1
    assert "1 problem(s)" in capsys.readouterr().out


# ---------------------------------------------------------------- the real tree, measured

def test_the_live_tree_passes_its_own_gate():
    """The gate's verdict is about this repository, so it must hold here too."""
    assert gate.report() == []


def test_the_live_tree_has_no_scratch_files_in_docs_music():
    assert gate.scratch_files() == []


def test_every_live_score_is_either_reachable_or_recorded_as_known():
    dark = {name for name, _title in gate.dark_scores()}
    assert dark <= set(gate.KNOWN_DARK), f"unrecorded dark scores: {sorted(dark - set(gate.KNOWN_DARK))}"
