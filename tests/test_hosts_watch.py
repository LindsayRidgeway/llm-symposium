#!/usr/bin/env python3
"""Tests for `scripts/hosts_watch.py`. Offline — canned text, no network.

Why these exist. The script's only value is that a wake can trust its report
without re-reading four web pages by hand. Two things can quietly break that:
the HTML-to-text step (a page that renders as one long line, so `mentions`
finds nothing and "not mentioned" reads as "model is fine"), and the yardstick
itself — `ROUTES` drifting away from what the commons actually runs. Both are
pinned here. The network path is deliberately not tested.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import hosts_watch as hw  # noqa: E402

DOC = ROOT / "research" / "hosts-watch.md"


class StripHtmlTest(unittest.TestCase):
    def test_tags_and_scripts_go(self):
        raw = "<html><script>var x=1;</script><style>p{}</style><p>Hello</p><li>World</li></html>"
        out = hw.strip_html(raw)
        self.assertIn("Hello", out)
        self.assertIn("World", out)
        self.assertNotIn("var x", out)
        self.assertNotIn("<p>", out)

    def test_lines_survive_so_grep_can_work(self):
        out = hw.strip_html("<div>a</div><div>b</div>")
        self.assertGreaterEqual(len(out.splitlines()), 2)


class MentionsTest(unittest.TestCase):
    TEXT = (
        "claude-sonnet-4-5-20250929 Deprecated September 30, 2026 November 30, 2026\n"
        "claude-opus-5-5 Active N/A Not sooner than September 22, 2027\n"
        "claude-sonnet-4-5-20250929 Deprecated September 30, 2026 November 30, 2026\n"
    )

    def test_finds_a_snapshotted_form_of_our_name(self):
        hits = hw.mentions(self.TEXT, "claude-sonnet-4-5")
        self.assertTrue(hits)
        self.assertTrue(all("sonnet-4-5" in h for h in hits))

    def test_does_not_match_a_different_model(self):
        self.assertEqual(hw.mentions(self.TEXT, "gemini-3.8-flash"), [])

    def test_dedupes_identical_lines(self):
        hits = hw.mentions(self.TEXT, "claude-sonnet-4-5")
        self.assertEqual(len(hits), len(set(hits)))

    def test_limit_is_respected(self):
        text = "\n".join(f"gpt-5.6-sol row {i}" for i in range(20))
        self.assertLessEqual(len(hw.mentions(text, "gpt-5.6-sol", limit=3)), 3)


class DatesTest(unittest.TestCase):
    def test_extracts_and_sorts(self):
        self.assertEqual(
            hw.dates_in("retired 2027-04-01 and 2026-11-30 and 2026-11-30"),
            ["2026-11-30", "2027-04-01"],
        )

    def test_none(self):
        self.assertEqual(hw.dates_in("no dates here"), [])


class ReportTest(unittest.TestCase):
    def test_unfetched_page_is_reported_not_crashed(self):
        rows = hw.report({k: None for k in hw.PAGES})
        self.assertEqual(len(rows), len(hw.ROUTES))
        self.assertTrue(all(not r["fetched"] for r in rows))

    def test_fetched_page_carries_hits(self):
        pages = {k: "" for k in hw.PAGES}
        pages["anthropic"] = "claude-sonnet-4-5-20250929 retired 2026-11-30"
        rows = hw.report(pages)
        claude = [r for r in rows if r["model"] == "claude-sonnet-4-5"][0]
        self.assertTrue(claude["fetched"])
        self.assertIn("2026-11-30", claude["dates"])


class YardstickTest(unittest.TestCase):
    """A watch whose yardstick is wrong reports "fine" about a dead model."""

    def test_every_route_names_a_known_page(self):
        for _amigo, _route, _model, key in hw.ROUTES:
            self.assertIn(key, hw.PAGES)

    def test_all_four_hosts_are_watched(self):
        self.assertEqual({r[0] for r in hw.ROUTES}, {"Claude", "Tarik", "Gemini", "Desi"})

    def test_every_configured_model_is_named_in_the_record(self):
        # research/hosts-watch.md is the human-readable half and must not drift
        # from the machine half. If a route changes, this test fails on purpose.
        text = DOC.read_text(encoding="utf-8")
        for _amigo, _route, model, _key in hw.ROUTES:
            self.assertIn(model, text, f"{model} missing from research/hosts-watch.md")

    def test_the_record_is_dated_and_lists_its_sources(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("**Read:** 2026-", text)
        self.assertIn("## Sources, exactly as read", text)

    def test_offline_run_does_not_touch_the_network(self):
        self.assertEqual(hw.main([]), 0)


if __name__ == "__main__":
    unittest.main()
