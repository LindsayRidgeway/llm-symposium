#!/usr/bin/env python3
"""Tests for scripts/music_catalogue_unwired.py — the music conservatory's reachability gate.

Written 2026-10-21 (Desi) because the gate landed without its test: the script is on main and
the test was claimed by wakes that ran out of turns before landing it, so nothing stopped the
gate from drifting. Each test pins one of the gate's contracts against a throwaway
docs/music/ tree, plus three that pin the state of this checkout.

The rule the fixtures encode, and the reason the gate exists at all: a file that exists is not
a piece a reader can reach. Every check fails closed — an unlisted file is a problem, an
unargued exemption is a problem, and a known defect is still printed on every run.

Run: python3 tests/test_music_catalogue_unwired.py
"""

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import scripts.music_catalogue_unwired as gate  # noqa: E402

APP_JS = """window.COMPOSITIONS = {
  nightfall: {
    title: "Nightfall",
  },
};
"""

# Check 7, added 2026-11-09, closes the loop the engine opens: an engine key nothing offers is a tune
# no reader can play. Every fixture therefore needs the one key in APP_JS to be *offered* somewhere,
# or a clean-report test fails for a reason that has nothing to do with what it is testing. This card
# is the offering; tests that supply their own index append it.
CARD_NIGHTFALL = (
    '<article class="repertoire-card">'
    '<h3 class="repertoire-card-title">Nightfall</h3>'
    '<button data-tune="nightfall">Play</button></article>'
)
DEFAULT_INDEX = "<html><body><h1>Catalogue</h1></body></html>" + CARD_NIGHTFALL


class MusicCatalogueGateTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _tree(self, index=DEFAULT_INDEX, app=APP_JS, files=None):
        """A minimal docs/music/ tree. ``files`` maps name -> contents."""
        music = self.root / "docs" / "music"
        music.mkdir(parents=True, exist_ok=True)
        (music / "index.html").write_text(index, encoding="utf-8")
        (music / "app.js").write_text(app, encoding="utf-8")
        for name, body in (files or {}).items():
            (music / name).write_text(body, encoding="utf-8")
        return self.root

    @staticmethod
    def _lines(problems, prefix):
        return [p for p in problems if p.startswith(prefix)]

    # --- check 1: a page on disk that the catalogue never links ---------------

    def test_uncatalogued_page_is_a_problem(self):
        root = self._tree(files={"orphan.html": "<html>a finished piece</html>"})
        failures = self._lines(gate.report(root), "NOT CATALOGUED")
        self.assertEqual(len(failures), 1)
        self.assertIn("orphan.html", failures[0])

    def test_linked_page_is_not_a_problem(self):
        root = self._tree(
            index='<html><a href="carol.html">Carol</a></html>' + CARD_NIGHTFALL,
            files={"carol.html": "<html>a finished piece</html>"},
        )
        self.assertEqual(gate.uncatalogued(root), [])
        self.assertEqual(gate.report(root), [])

    def test_not_pieces_exemption_is_named_not_silent(self):
        # sandbox.html is a tool, not a work: it must not fail the gate, and the exemption must
        # be an argument the reader can see, not a silence.
        self.assertIn("sandbox.html", gate.NOT_PIECES)
        root = self._tree(files={"sandbox.html": "<html>the composer's bench</html>"})
        self.assertEqual(gate.uncatalogued(root), [])
        self.assertEqual(gate.report(root), [])

    # --- check 2: the audition button must point at a tune that exists --------

    # The two fixtures below are written as *catalogue cards*, not bare divs, because that is what
    # `audition_ids()` reads: it walks `<article class="repertoire-card">…</article>`. Written the
    # other way (a `<div data-tune=…>`), the dead-button test asserted a problem the gate never
    # produces and the live-button test passed for the wrong reason — a button outside a card is
    # invisible to the check, so "no problem" meant "not looked at". This file had never been run
    # by anything when that was found (2026-10-25, Dmitri): it did not land on 2026-10-21 with the
    # script it tests, so no CI and no wake had executed it. Fixed here rather than argued away.

    def test_dead_audition_button_is_a_problem(self):
        root = self._tree(
            index=(
                '<html><article class="repertoire-card">'
                '<h3 class="repertoire-card-title">Ghost</h3>'
                '<button data-tune="ghost-tune">Play</button></article></html>'
            )
        )
        failures = self._lines(gate.report(root), "DEAD AUDITION")
        self.assertEqual(len(failures), 1)
        self.assertIn("ghost-tune", failures[0])

    def test_live_audition_button_is_not_a_problem(self):
        root = self._tree(
            index=(
                '<html><article class="repertoire-card">'
                '<h3 class="repertoire-card-title">Nightfall</h3>'
                '<button data-tune="nightfall">Play</button></article></html>'
            )
        )
        self.assertEqual(gate.audition_ids(root), [("nightfall", "Nightfall")])
        self.assertEqual(gate.report(root), [])

    # --- check 3: the catalogue must not promise a page that never landed -----

    def test_dangling_card_is_a_problem(self):
        root = self._tree(index='<html><a href="never-landed.html">A card</a></html>')
        failures = self._lines(gate.report(root), "DANGLING CARD")
        self.assertEqual(len(failures), 1)
        self.assertIn("never-landed.html", failures[0])

    # --- check 4: a page must not offer a score that never landed ------------

    def test_broken_score_download_is_a_problem(self):
        root = self._tree(
            index='<html><a href="piece.html">Piece</a></html>' + CARD_NIGHTFALL,
            files={"piece.html": '<html><a href="piece.abc" download>Score</a></html>'},
        )
        failures = self._lines(gate.report(root), "BROKEN SCORE")
        self.assertEqual(len(failures), 1)
        self.assertIn("piece.html -> piece.abc", failures[0])

    def test_present_score_download_is_not_a_problem(self):
        root = self._tree(
            index='<html><a href="piece.html">Piece</a></html>' + CARD_NIGHTFALL,
            files={
                "piece.html": '<html><a href="piece.abc" download>Score</a></html>',
                "piece.abc": "X: 1\nT: Piece\n",
            },
        )
        self.assertEqual(gate.report(root), [])

    # --- check 5: a scratch file in the published directory is published -----

    def test_scratch_file_is_a_problem(self):
        root = self._tree(files={"draft.abc.tmp": "X: 1\nT: Draft\n"})
        failures = self._lines(gate.report(root), "SCRATCH PUBLISHED")
        self.assertEqual(len(failures), 1)
        self.assertIn("draft.abc.tmp", failures[0])

    # --- check 6: a score nothing offers cannot be heard --------------------

    def test_dark_score_is_named_by_its_title(self):
        root = self._tree(files={"fresh.abc": "X: 7\nT: Fresh Tune\n% notes\n"})
        self.assertEqual(gate.dark_scores(root), [("fresh.abc", "Fresh Tune")])
        failures = self._lines(gate.report(root), "DARK SCORE")
        self.assertEqual(len(failures), 1)
        self.assertIn("T: Fresh Tune", failures[0])

    def test_score_reached_by_a_page_of_its_own_name_is_not_dark(self):
        # check 1 then has to carry it: the page exists, so the piece is reachable in principle.
        root = self._tree(
            index='<html><a href="fresh.html">Fresh</a></html>' + CARD_NIGHTFALL,
            files={"fresh.abc": "X: 7\nT: Fresh Tune\n", "fresh.html": "<html>Fresh</html>"},
        )
        self.assertEqual(gate.dark_scores(root), [])
        self.assertEqual(gate.report(root), [])

    def test_score_reached_by_its_title_in_the_engine_is_not_dark(self):
        root = self._tree(
            files={"fresh.abc": "X: 7\nT: Fresh Tune\n"},
            app=APP_JS.replace('title: "Nightfall"', 'title: "Fresh Tune"'),
        )
        self.assertEqual(gate.dark_scores(root), [])

    def test_untitled_score_is_dark_and_says_so(self):
        root = self._tree(files={"anon.abc": "X: 8\n% no title line\n"})
        self.assertEqual(gate.dark_scores(root), [("anon.abc", "")])
        self.assertIn("no T: title", gate.report(root)[0])

    # --- the known list prints, and never counts ---------------------------

    def test_known_dark_score_is_printed_and_not_counted(self):
        name = sorted(gate.KNOWN_DARK)[0]
        root = self._tree(files={name: "X: 9\nT: Some Piece\n"})
        self.assertEqual(gate.report(root), [])
        lines = gate.known(root)
        self.assertEqual(len(lines), 1)
        self.assertIn(name, lines[0])
        self.assertIn("owner", lines[0])

    # --- this checkout -----------------------------------------------------

    def test_this_checkout_has_no_music_catalogue_problems(self):
        problems = gate.report()
        self.assertEqual(problems, [], "music catalogue gate is red in this checkout:\n" + "\n".join(problems))

    def test_gate_exits_zero_and_prints_its_count(self):
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = gate.main([])
        self.assertEqual(code, 0)
        out = buf.getvalue()
        self.assertTrue(out.startswith("music catalogue gate: "), out)
        self.assertIn("0 problem(s)", out)

    def test_every_dark_score_in_this_checkout_is_acknowledged(self):
        dark = {name for name, _title in gate.dark_scores()}
        unaccounted = dark - set(gate.KNOWN_DARK)
        self.assertEqual(unaccounted, set(), "dark score(s) nobody has accounted for: " + ", ".join(sorted(unaccounted)))
        self.assertTrue(gate.known(), "every KNOWN_DARK entry has been wired — the known list should shrink")



    def test_single_quoted_missing_score_is_a_problem(self):
        root = self._tree(index="<a href='missing.abc' download>Score</a>")
        self.assertEqual(len(self._lines(gate.report(root), "BROKEN SCORE")), 1)

    def test_comment_only_anchor_does_not_catalogue_a_page(self):
        root = self._tree(index='<!-- <a href="ghost.html">Later</a> -->',
                          files={"ghost.html": "<p>A piece</p>"})
        self.assertEqual(gate.uncatalogued(root), ["ghost.html"])

    def test_plain_filename_text_does_not_catalogue_a_page(self):
        root = self._tree(index="<p>TODO: ghost.html</p>",
                          files={"ghost.html": "<p>A piece</p>"})
        self.assertEqual(gate.uncatalogued(root), ["ghost.html"])

    def test_html_anchor_forms_and_url_suffixes_resolve_to_existing_files(self):
        root = self._tree(index="<A HREF=./carol.html?mode=play#score>Carol</A>" + CARD_NIGHTFALL,
                          files={"carol.html": "<a href='carol.abc?download=1'>Score</a>",
                                 "carol.abc": "X:1\nT:Carol\nK:C\nCDEF|\n"})
        self.assertEqual(gate.report(root), [])

    def test_single_quoted_missing_page_is_dangling(self):
        root = self._tree(index="<a href='missing.html'>Missing</a>")
        self.assertEqual(gate.dangling_links(root), ["missing.html"])

    def test_commented_score_download_is_not_a_broken_link(self):
        root = self._tree(index='<!-- <a href="missing.abc">Old score</a> -->')
        self.assertEqual(gate.broken_score_links(root), [])

    def test_external_anchor_does_not_catalogue_a_local_page(self):
        root = self._tree(index='<a href="https://example.test/ghost.html">Elsewhere</a>',
                          files={"ghost.html": "<p>A piece</p>"})
        self.assertEqual(gate.uncatalogued(root), ["ghost.html"])
    def test_template_only_anchor_does_not_catalogue_a_piece(self):
        root = self._tree(index='<template><a href="ghost.html">Later</a></template>',
                          files={"ghost.html": "<p>A finished piece</p>"})
        self.assertEqual(gate.uncatalogued(root), ["ghost.html"])
        self.assertEqual(len(self._lines(gate.report(root), "NOT CATALOGUED")), 1)

    def test_nested_templates_do_not_hide_a_following_live_anchor(self):
        root = self._tree(
            index=('<TEMPLATE><template><a href="missing.html">Draft</a></template>'
                   '<a href="hidden.html">Hidden</a></TEMPLATE>'
                   '<a href="carol.html">Carol</a>'),
            files={"hidden.html": "<p>Hidden piece</p>", "carol.html": "<p>Carol</p>"})
        self.assertEqual(gate.uncatalogued(root), ["hidden.html"])
        self.assertEqual(gate.dangling_links(root), [])

    def test_template_score_link_is_inert_but_live_missing_score_still_fails(self):
        root = self._tree(index='<a href="piece.html">Piece</a>', files={
            "piece.html": ('<template><a href="inert.abc" download>Draft</a></template>'
                           '<a href="visible.abc" download>Score</a>')})
        self.assertEqual(gate.broken_score_links(root), ["piece.html -> visible.abc"])
if __name__ == "__main__":
    unittest.main(verbosity=2)
