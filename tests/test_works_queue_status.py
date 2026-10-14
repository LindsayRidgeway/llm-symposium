#!/usr/bin/env python3
"""Tests for `scripts/works_queue_status.py`.

Why these exist. The tool is a *gate*: it decides whether a `works/queue/` candidate's Status line
tells the truth about the published section. A gate that is itself wrong is worse than none — it
either passes a lying record or fails an honest one, and either way the pipeline stops being
readable. So each fatal check is pinned by a fixture that must trip it, and the real checkout is
asserted clean, which is what stops 07 and 08 from silently drifting back.

Offline. Fixtures live in a temp directory; the only real path read is this checkout, read-only.
"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import works_queue_status as wqs  # noqa: E402

INDEX = """<html><body>
  <h3><a href="warming.html">Warming</a></h3>
  <h3><a href="trials.html">Trials</a></h3>
</body></html>
"""


def build(tmp: Path, candidates: dict, index: str = INDEX, pages=("warming.html",),
          screen: str | None = None):
    q = tmp / "works" / "queue"
    q.mkdir(parents=True)
    for name, body in candidates.items():
        (q / name).write_text(body, encoding="utf-8")
    if screen is not None:
        (q / "00-candidates-screened.md").write_text(screen, encoding="utf-8")
    (tmp / "docs" / "works").mkdir(parents=True)
    (tmp / "docs" / "works" / "index.html").write_text(index, encoding="utf-8")
    for p in pages:
        (tmp / "docs" / "works" / p).write_text("<html></html>", encoding="utf-8")
    return tmp


SCREEN_HEADER = ("| # | Candidate | Verdict |\n|---|---|---|\n")


class Classify(unittest.TestCase):
    def test_verdicts(self):
        self.assertEqual(wqs.verdict_of("**Status:** SHIPPED 2026-09-13 → x"), "SHIPPED")
        self.assertEqual(wqs.verdict_of("**Status: STOPPED, 2026-09-27.**"), "STOPPED")
        self.assertEqual(wqs.verdict_of("**Status:** candidate, verified"), "OPEN")

    def test_artifact_extracted_from_status_only(self):
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {"01-warming.md":
                                "**Status:** SHIPPED → `docs/works/warming.html`.\nBody mentions "
                                "docs/works/trials.html but must not count.\n"})
            row = wqs.read_candidate(t / "works" / "queue" / "01-warming.md")
            self.assertEqual(row["artifact"], "docs/works/warming.html")


class FatalChecks(unittest.TestCase):
    def test_missing_status_is_fatal(self):
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {"07-x.md": "# 07 — x\n\n**Raised:** 2026-09-13\n"})
            fatal, _, _ = wqs.audit(t)
            self.assertTrue(any("no Status line" in f for f in fatal), fatal)

    def test_shipped_without_artifact_is_fatal(self):
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {"01-x.md": "**Status:** SHIPPED 2026-01-01\n"})
            fatal, _, _ = wqs.audit(t)
            self.assertTrue(any("names no docs/works" in f for f in fatal), fatal)

    def test_shipped_artifact_absent_on_disk_is_fatal(self):
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {"01-x.md": "**Status:** SHIPPED → `docs/works/ghost.html`\n"})
            fatal, _, _ = wqs.audit(t)
            self.assertTrue(any("not on disk" in f for f in fatal), fatal)

    def test_shipped_artifact_not_linked_is_fatal(self):
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {"01-x.md": "**Status:** SHIPPED → `docs/works/orphan.html`\n"},
                      pages=("orphan.html",))
            fatal, _, _ = wqs.audit(t)
            self.assertTrue(any("not linked" in f for f in fatal), fatal)

    def test_00_meta_file_is_skipped(self):
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {"00-candidates-screened.md": "# screening record, no status\n"})
            fatal, _, rows = wqs.audit(t)
            self.assertEqual(fatal, [])
            self.assertEqual(rows, [])

    def test_clean_tree_has_no_fatal(self):
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {"01-warming.md": "**Status:** SHIPPED → `docs/works/warming.html`\n"})
            fatal, _, _ = wqs.audit(t)
            self.assertEqual(fatal, [])


class Advisory(unittest.TestCase):
    def test_unclaimed_released_page_is_advisory_not_fatal(self):
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {"01-warming.md": "**Status:** SHIPPED → `docs/works/warming.html`\n"})
            fatal, advisory, _ = wqs.audit(t)
            self.assertEqual(fatal, [])
            self.assertTrue(any("docs/works/trials.html" in a for a in advisory), advisory)


class ScreenVerdicts(unittest.TestCase):
    """The screening row's verdict cell has no fixed grammar; the classifier must not guess."""

    def test_states(self):
        self.assertEqual(wqs.screen_state("**shipped 2026-09-16 as Works entry 6** — x"), "SHIPPED")
        self.assertEqual(wqs.screen_state("already shipped inside `docs/works/unjoined.html`"), "SHIPPED")
        self.assertEqual(wqs.screen_state("reject — high harm if simplified wrong"), "REJECTED")
        self.assertEqual(wqs.screen_state("**open** — the one candidate still live"), "OPEN")
        self.assertEqual(wqs.screen_state("**keep** — started tonight"), "OPEN")
        self.assertEqual(wqs.screen_state("~~reject~~ revived — see the file"), "REJECTED")
        self.assertEqual(wqs.screen_state("a sentence with no state word at all"), "UNKNOWN")
        self.assertEqual(wqs.screen_state(""), "UNKNOWN")

    def test_parse_skips_header_and_states_the_twelve(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "00-candidates-screened.md"
            p.write_text(SCREEN_HEADER
                         + "| 1 | Thing | **open** — still live |\n"
                         + "| 2 | Other | **shipped** — `docs/works/warming.html` |\n",
                         encoding="utf-8")
            rows = wqs.parse_screen(p)
            self.assertEqual([r["n"] for r in rows], [1, 2])
            self.assertEqual(rows[1]["paths"], ["docs/works/warming.html"])


class ScreenFatalChecks(unittest.TestCase):
    """The 2026-10-14 defect one level up: a screened verdict that no longer matches the artifact."""

    def test_open_row_naming_a_shipped_candidate_is_fatal(self):
        """Row 6 read 'already queued (candidate 02)' a month after candidate 02 shipped."""
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t),
                      {"01-warming.md": "**Status:** SHIPPED → `docs/works/warming.html`\n"},
                      screen=SCREEN_HEADER + "| 6 | Clinical trials near me | already queued "
                                             "(candidate 01) |\n")
            fatal, _, _ = wqs.audit(t)
            self.assertTrue(any("still reads OPEN" in f for f in fatal), fatal)

    def test_shipped_row_naming_no_path_is_fatal(self):
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {},
                      screen=SCREEN_HEADER + "| 1 | Thing | **shipped 2026-01-01** |\n")
            fatal, _, _ = wqs.audit(t)
            self.assertTrue(any("names no artifact path" in f for f in fatal), fatal)

    def test_shipped_row_naming_absent_path_is_fatal(self):
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {},
                      screen=SCREEN_HEADER + "| 1 | Thing | **shipped** — `docs/works/ghost.html` |\n")
            fatal, _, _ = wqs.audit(t)
            self.assertTrue(any("not on disk" in f for f in fatal), fatal)

    def test_open_row_with_no_candidate_is_advisory(self):
        """Row 1's real shape: an honest 'keep' the screen cannot check — printed, not failed."""
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {},
                      screen=SCREEN_HEADER + "| 1 | Guidance reachability (item 17) | **open** |\n")
            fatal, advisory, _ = wqs.audit(t)
            self.assertEqual(fatal, [])
            self.assertTrue(any("names no candidate to check" in a for a in advisory), advisory)


class MainExit(unittest.TestCase):
    def test_exit_code_is_a_gate(self):
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {"07-x.md": "# 07 — x\n"})
            self.assertEqual(wqs.main(["--root", str(t)]), 1)
        with tempfile.TemporaryDirectory() as t:
            t = build(Path(t), {"01-x.md": "**Status:** SHIPPED → `docs/works/warming.html`\n"})
            self.assertEqual(wqs.main(["--root", str(t)]), 0)


class RealCheckout(unittest.TestCase):
    def test_this_repository_has_no_violations(self):
        """Pins the 2026-10-14 fixes: 08 SHIPPED, 07 given a Status line. Regressions fail here."""
        fatal, _, rows = wqs.audit(ROOT)
        self.assertEqual(fatal, [], f"works/queue status violations: {fatal}")
        self.assertTrue(rows, "expected candidate rows in this checkout")

    def test_the_screening_record_is_read_too(self):
        """Pins the 2026-10-14 corrections: no screened row claims a state it no longer has."""
        rows = wqs.parse_screen(ROOT / "works" / "queue" / "00-candidates-screened.md")
        self.assertEqual(len(rows), 12, "expected all twelve screened candidates to be parsed")
        states = {r["n"]: r["state"] for r in rows}
        self.assertEqual(states[3], "SHIPPED", "row 3 shipped as the entry-8 companion tool")
        self.assertEqual(states[4], "SHIPPED", "row 4 shipped as entry 15")
        self.assertEqual(states[6], "SHIPPED", "row 6 shipped as entry 5")
        self.assertEqual(states[1], "OPEN", "row 1 is the one candidate still live")


if __name__ == "__main__":
    unittest.main(verbosity=2)
