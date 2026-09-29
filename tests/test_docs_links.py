#!/usr/bin/env python3
"""Tests for scripts/check_docs_links.py.

Two things are asserted, and the second is the reason the file exists.

1. The detector works: it finds a relative link with no file behind it, reports the right
   line, checks `src` as well as `href`, and does not confuse a runtime-built link
   (`href="${url}"` inside a `<script>`) or an external/anchor/mailto target for a broken one.

2. The published tree is clean, and stays clean. This is a guard, not a snapshot: the
   magazine already shipped a link to a file that 404s on the published site (the Sumi-e
   "Gallery Prompt Methodology" link, fixed 2026-09-17), because nothing checked that a
   served page's own links resolved. From now on, adding a link to a page that does not
   exist fails a test instead of reaching the site.

Run: python3 tests/test_docs_links.py
"""

import importlib.util
import os
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = importlib.util.spec_from_file_location(
    "check_docs_links", os.path.join(REPO, "scripts", "check_docs_links.py"))
cdl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cdl)

DOCS = os.path.join(REPO, "docs")


def _write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


class TestDetector(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_resolving_relative_link_is_not_broken(self):
        _write(self.root, "index.html", '<a href="ok.html">ok</a>')
        _write(self.root, "ok.html", "<p>fine</p>")
        checked, broken = cdl.check_tree(self.root)
        self.assertEqual(broken, [])
        self.assertEqual(checked, 1)

    def test_a_missing_target_is_reported_with_its_line(self):
        _write(self.root, "index.html", "<h1>t</h1>\n<a href=\"gone.html\">x</a>\n")
        checked, broken = cdl.check_tree(self.root)
        self.assertEqual(len(broken), 1)
        path, line, target = broken[0]
        self.assertTrue(path.endswith("index.html"))
        self.assertEqual(line, 2)
        self.assertEqual(target, "gone.html")

    def test_src_is_checked_too(self):
        _write(self.root, "index.html", '<img src="pic.png">')
        _checked, broken = cdl.check_tree(self.root)
        self.assertEqual([t for _f, _l, t in broken], ["pic.png"])

    def test_runtime_template_links_are_ignored(self):
        """The interactive works build hrefs at runtime; those are not static links."""
        _write(self.root, "w.html",
               "<p>hi</p>\n<script>\n"
               "  a.innerHTML = '<a href=\"${url}\">go</a>';\n"
               "  b.href = `${RAW_URL}`;\n"
               "</script>\n")
        checked, broken = cdl.check_tree(self.root)
        self.assertEqual(broken, [])
        self.assertEqual(checked, 0)

    def test_external_and_nonfile_schemes_are_ignored(self):
        _write(self.root, "index.html",
               '<a href="https://example.com/x.html">e</a>\n'
               '<a href="//cdn.example.com/y.js">p</a>\n'
               '<a href="#section">f</a>\n'
               '<a href="mailto:a@b.c">m</a>\n'
               '<a href="tel:+15551234">t</a>\n'
               '<a href="javascript:void(0)">j</a>\n'
               '<a href="data:text/plain,x">d</a>\n')
        checked, broken = cdl.check_tree(self.root)
        self.assertEqual(broken, [])
        self.assertEqual(checked, 0)

    def test_a_real_tree_of_html_is_walked(self):
        _write(self.root, "a/index.html", '<a href="b.html">b</a>')
        _write(self.root, "a/b.html", "<p>b</p>")
        _write(self.root, "a/c.html", '<a href="missing.html">m</a>')
        checked, broken = cdl.check_tree(self.root)
        self.assertEqual(checked, 2)
        self.assertEqual([t for _f, _l, t in broken], ["missing.html"])


class TestPublishedTree(unittest.TestCase):
    """The guard: docs/ must have no relative link without a file behind it."""

    def test_no_broken_links_in_docs(self):
        checked, broken = cdl.check_tree(DOCS)
        detail = "\n".join(f"  {os.path.relpath(f, REPO)}:{ln} -> {t}" for f, ln, t in broken)
        self.assertEqual(broken, [], f"broken relative links in docs/:\n{detail}")

    def test_the_check_is_not_vacuous(self):
        """A checker that finds nothing because it read nothing is worse than none."""
        checked, _broken = cdl.check_tree(DOCS)
        self.assertGreater(checked, 400, f"only {checked} relative links seen — is the walk wrong?")

    def test_the_regression_that_motivated_it(self):
        """The Sumi-e method link must point at something that exists, not a phantom .html."""
        paper = os.path.join(DOCS, "papers", "hands-mind-origin-gallery-matrix.html")
        with open(paper, encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn('href="../gallery/prompt-methodology.html"', text)
        self.assertTrue(os.path.exists(os.path.join(DOCS, "gallery", "prompt-methodology.md")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
