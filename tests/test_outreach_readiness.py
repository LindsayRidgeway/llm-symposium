#!/usr/bin/env python3
"""Pin the outreach readiness check (agenda item 22, Track 1).

`scripts/outreach_readiness.py` answers the question `scripts/outreach_ledger_audit.py`
cannot: not "does each ledger row's claim match the file?" but "is every file accounted for
by a row?". It was written after the 2026-10-03 04:19Z wake staged a byte-identical second
copy of the Internet Archive pitch as `internet_archive.md` — a file no ledger row names, and
so invisible to the ledger audit by construction — and after finding a stale re-render of the
Long Now pitch for a venue the ledger already marks sent.

These tests pin, in order:

  * the four drift classes the check must catch (orphan, duplicate, missing, unknown identity);
  * that reach is classified, not failed on, and classified correctly (machine / session-only
    / unknown / no-header-defaults-to-the-generic-mailbox);
  * that the check is green on the real repository, so it is a live gate and not a shrine;
  * that a drift-free fixture is actually drift-free (the check is not vacuous).
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import outreach_readiness as orr  # noqa: E402


def _tree(tmp: Path, prospects: list[dict], drafts: dict[str, str]) -> Path:
    """Build a minimal channels/ tree with a ledger and a drafts/ directory."""
    (tmp / "channels" / "outreach").mkdir(parents=True, exist_ok=True)
    (tmp / "channels" / "outbound").mkdir(parents=True, exist_ok=True)
    (tmp / "channels" / "sent").mkdir(parents=True, exist_ok=True)
    (tmp / "channels" / "outreach" / "pipeline.json").write_text(
        json.dumps({"prospects": prospects}), encoding="utf-8")
    for name, text in drafts.items():
        (tmp / "channels" / "outreach" / "drafts" / name).write_text(text, encoding="utf-8")
    return tmp


def _run(tmp: Path, sender: str = "desi") -> dict:
    return orr.audit(
        ledger_path=tmp / "channels" / "outreach" / "pipeline.json",
        drafts_dir=tmp / "channels" / "outreach" / "drafts",
        outbound_dir=tmp / "channels" / "outbound",
        sent_dir=tmp / "channels" / "sent",
        sender=sender,
    )


DRAFT = "Identity: {ident}\nTo: someone@example.org\nSubject: hi\n\nBody.\n"


class DriftClasses(unittest.TestCase):
    def test_orphan_is_caught(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = _tree(Path(d),
                        prospects=[{"id": "a", "draft": "channels/outreach/drafts/a.md"}],
                        drafts={"a.md": DRAFT.format(ident="desi"),
                                "b.md": DRAFT.format(ident="desi")})
            r = _run(tmp)
            self.assertEqual(r["orphans"], ["b.md"])
            self.assertTrue(orr.drift(r))

    def test_duplicate_content_is_caught(self):
        same = DRAFT.format(ident="desi")
        with tempfile.TemporaryDirectory() as d:
            tmp = _tree(Path(d),
                        prospects=[{"id": "a", "draft": "channels/outreach/drafts/a.md"}],
                        drafts={"a.md": same, "copy-of-a.md": same})
            r = _run(tmp)
            self.assertEqual([sorted(g) for g in r["duplicates"]], [["a.md", "copy-of-a.md"]])
            self.assertTrue(orr.drift(r))

    def test_missing_file_is_caught(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = _tree(Path(d),
                        prospects=[{"id": "a", "draft": "channels/outreach/drafts/gone.md"}],
                        drafts={})
            r = _run(tmp)
            self.assertEqual([m["id"] for m in r["missing"]], ["a"])
            self.assertTrue(orr.drift(r))

    def test_unknown_identity_is_caught(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = _tree(Path(d),
                        prospects=[{"id": "a", "draft": "channels/outreach/drafts/a.md"}],
                        drafts={"a.md": DRAFT.format(ident="nobody")})
            r = _run(tmp)
            self.assertEqual(r["unknown_identity"], ["a.md"])
            self.assertTrue(orr.drift(r))

    def test_a_clean_tree_has_no_drift(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = _tree(Path(d),
                        prospects=[{"id": "a", "draft": "channels/outreach/drafts/a.md"}],
                        drafts={"a.md": DRAFT.format(ident="desi")})
            r = _run(tmp)
            self.assertEqual((r["orphans"], r["duplicates"], r["missing"], r["unknown_identity"]),
                             ([], [], [], []))
            self.assertFalse(orr.drift(r))

    def test_a_draft_living_in_sent_is_not_missing(self):
        # A sent draft moves to channels/sent/; the ledger still names its old outbound path.
        with tempfile.TemporaryDirectory() as d:
            tmp = _tree(Path(d),
                        prospects=[{"id": "a", "draft": "channels/outbound/a.md"}],
                        drafts={})
            (tmp / "channels" / "sent" / "a.md").write_text(DRAFT.format(ident="desi"), encoding="utf-8")
            r = _run(tmp)
            self.assertEqual(r["missing"], [])
            self.assertFalse(orr.drift(r))


class Reach(unittest.TestCase):
    def test_reach_classes(self):
        self.assertEqual(orr.classify_reach("desi", "desi")[0], "machine")
        self.assertEqual(orr.classify_reach("gemini", "desi")[0], "session-only")
        self.assertEqual(orr.classify_reach("nobody", "desi")[0], "unknown")
        # no Identity header -> mail.py sends it as the generic identity (Desi's)
        self.assertEqual(orr.classify_reach("", "desi")[0], "machine")

    def test_session_only_is_reported_but_not_drift(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = _tree(Path(d),
                        prospects=[{"id": "a", "draft": "channels/outreach/drafts/a.md"}],
                        drafts={"a.md": DRAFT.format(ident="gemini")})
            r = _run(tmp)
            self.assertEqual(r["session_only"], 1)
            self.assertEqual(r["machine_reach"], 0)
            self.assertFalse(orr.drift(r), "another amigo's signature is a standing state, not drift")

    def test_read_identity_reads_only_the_header_block(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.md"
            p.write_text("To: a@b.c\nSubject: s\n\nIdentity: gemini\n", encoding="utf-8")
            self.assertEqual(orr.read_identity(p), "")  # a body line is not a header
            p.write_text("Identity: gemini\nTo: a@b.c\nSubject: s\n\nbody\n", encoding="utf-8")
            self.assertEqual(orr.read_identity(p), "gemini")


class AgainstTheRealRepository(unittest.TestCase):
    """The real ledger and the real drafts/ must agree — this is the live gate."""

    def test_the_real_repository_has_no_drift(self):
        r = orr.audit()
        self.assertFalse(
            orr.drift(r),
            "outreach drift in the live repository:\n" + orr.format_report(r, "test", "test"),
        )

    def test_the_real_ledger_is_the_outreach_ledger(self):
        r = orr.audit()
        self.assertGreaterEqual(r["rows"], 5, "the real ledger should carry the qualified prospects")

    def test_a_non_ledger_json_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "not.json"
            bad.write_text('{"hello": "world"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                orr.audit(ledger_path=bad, drafts_dir=Path(d), outbound_dir=Path(d), sent_dir=Path(d))


if __name__ == "__main__":
    unittest.main(verbosity=2)
