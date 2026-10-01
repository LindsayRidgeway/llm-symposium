#!/usr/bin/env python3
"""The outreach ledger must match the mail queue's own files, and the files are ground truth.

Written 2026-09-26 with `scripts/outreach_ledger_audit.py`, after the ledger turned out to
say in one field that the outbound leg had "never been used for a single cold contact" while
two cold contacts sat in `channels/sent/`, sent on 2026-09-17. `mail.send_draft` moves a
draft to `sent/` only after SMTP accepts it, so location — not prose — decides "staged" vs
"queued" vs "sent". The last test pins the real ledger, so the drift cannot quietly return.

Added 2026-10-01: the audit grew an orphan scan, after three institutional drafts sat in
`channels/outreach/drafts/` that no ledger row named and the report never mentioned them. The
`OrphanTests` below pin that a staged draft the ledger is blind to is reported, and the
`RealLedgerTests` pin that the delivered ledger has none.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import outreach_ledger_audit as audit  # noqa: E402


class _Tree:
    """A throwaway repo layout: channels/outbound/, channels/sent/, and a ledger."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "channels" / "outbound").mkdir(parents=True)
        (self.root / "channels" / "sent").mkdir(parents=True)
        (self.root / "channels" / "outreach").mkdir(parents=True)
        (self.root / "channels" / "outreach" / "drafts").mkdir(parents=True)
        self.ledger = self.root / "channels" / "outreach" / "pipeline.json"

    def write_ledger(self, prospects, why="the leg has done its work"):
        self.ledger.write_text(json.dumps({"_why_this_exists": why, "prospects": prospects}))

    def touch(self, folder, name, text="From: x\nTo: y\nSubject: z\n\nbody\n"):
        (self.root / "channels" / folder / name).write_text(text)

    def rows(self, why=None):
        if why is not None:
            data = json.loads(self.ledger.read_text())
            data["_why_this_exists"] = why
            self.ledger.write_text(json.dumps(data))
        return audit.audit(self.ledger, self.root)

    def close(self):
        self._tmp.cleanup()


class ClassifyTests(unittest.TestCase):
    def setUp(self):
        self.t = _Tree()

    def tearDown(self):
        self.t.close()

    def test_outbox_file_reads_as_queued(self):
        self.t.touch("outbound", "p.md")
        reality, path = audit.classify("channels/outbound/p.md",
                                        self.t.root / "channels/outbound",
                                        self.t.root / "channels/sent", self.t.root)
        self.assertEqual(reality, "queued")
        self.assertTrue(path.endswith("p.md"))

    def test_staged_draft_reads_as_staged(self):
        self.t.touch("outreach/drafts", "p.md")
        reality, path = audit.classify("channels/outreach/drafts/p.md",
                                        self.t.root / "channels/outbound",
                                        self.t.root / "channels/sent", self.t.root)
        self.assertEqual(reality, "staged")
        self.assertTrue(path.endswith("outreach/drafts/p.md"))

    def test_file_moved_to_sent_reads_as_sent(self):
        # The ledger still names the old outbound path; the file has moved. Location wins.
        self.t.touch("sent", "p.md")
        reality, _ = audit.classify("channels/outbound/p.md",
                                    self.t.root / "channels/outbound",
                                    self.t.root / "channels/sent", self.t.root)
        self.assertEqual(reality, "sent")

    def test_draft_in_neither_folder_is_dangling(self):
        reality, path = audit.classify("channels/outbound/gone.md",
                                       self.t.root / "channels/outbound",
                                       self.t.root / "channels/sent", self.t.root)
        self.assertEqual(reality, "dangling")
        self.assertIsNone(path)

    def test_no_draft_named_is_none(self):
        reality, path = audit.classify(None, self.t.root / "channels/outbound",
                                       self.t.root / "channels/sent", self.t.root)
        self.assertEqual(reality, "none")
        self.assertIsNone(path)


class VerdictTests(unittest.TestCase):
    def test_sent_file_with_queued_status_is_stale(self):
        self.assertEqual(audit.verdict("sent", "drafted and queued 2026-09-17"), "STALE")

    def test_sent_file_with_sent_status_is_ok(self):
        self.assertEqual(audit.verdict("sent", "sent 2026-09-17; no reply as of 2026-09-26"), "ok")

    def test_queued_file_with_sent_status_is_stale(self):
        self.assertEqual(audit.verdict("queued", "sent 2026-09-24"), "STALE")

    def test_queued_file_with_queued_status_is_ok(self):
        self.assertEqual(audit.verdict("queued", "drafted and queued 2026-09-24"), "ok")

    def test_staged_file_with_held_status_is_ok(self):
        self.assertEqual(audit.verdict("staged", "not contacted — draft staged"), "ok")

    def test_staged_file_claiming_it_was_sent_is_stale(self):
        self.assertEqual(audit.verdict("staged", "sent 2026-09-26"), "STALE")

    def test_dangling_is_always_flagged(self):
        self.assertEqual(audit.verdict("dangling", "sent last week"), "DANGLING")

    def test_no_draft_but_a_claim_of_one_is_flagged(self):
        self.assertEqual(audit.verdict("none", "drafted and queued 2026-09-24"), "NO-DRAFT")

    def test_not_contacted_with_no_draft_is_fine(self):
        self.assertEqual(audit.verdict("none", "not contacted — needs a verified address"), "ok")


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.t = _Tree()

    def tearDown(self):
        self.t.close()

    def test_two_sent_contacts_give_the_contradiction_and_two_stale_rows(self):
        self.t.touch("sent", "a.md")
        self.t.touch("sent", "b.md")
        self.t.touch("outbound", "c.md")
        self.t.write_ledger(
            [
                {"id": "a", "tier": "A", "status": "drafted and queued 2026-09-17",
                 "draft": "channels/outbound/a.md"},
                {"id": "b", "tier": "B", "status": "drafted and queued 2026-09-17",
                 "draft": "channels/outbound/b.md"},
                {"id": "c", "tier": "C", "status": "drafted and queued 2026-09-24",
                 "draft": "channels/outbound/c.md"},
            ],
            why="the sending leg ... and has never been used for a single cold contact.",
        )
        rows, sent_count, contradictions, orphans = self.t.rows()
        self.assertEqual(sent_count, 2)
        self.assertEqual(sum(1 for r in rows if r["verdict"] == "STALE"), 2)
        self.assertEqual(rows[2]["verdict"], "ok")
        self.assertEqual(len(contradictions), 1)
        self.assertEqual(orphans, [])  # every draft file here is named by the ledger

    def test_no_contradiction_when_nothing_has_been_sent(self):
        self.t.touch("outbound", "c.md")
        self.t.write_ledger(
            [{"id": "c", "tier": "C", "status": "drafted and queued", "draft": "channels/outbound/c.md"}],
            why="the leg ... and has never been used for a single cold contact.",
        )
        _, sent_count, contradictions, _orphans = self.t.rows()
        self.assertEqual(sent_count, 0)
        self.assertEqual(contradictions, [])

    def test_a_staged_draft_is_not_a_sent_contact(self):
        self.t.touch("outreach/drafts", "s.md")
        self.t.write_ledger(
            [{"id": "s", "tier": "B", "status": "not contacted — draft staged",
              "draft": "channels/outreach/drafts/s.md"}],
            why="the sending leg has done its work",
        )
        rows, sent_count, contradictions, orphans = self.t.rows()
        self.assertEqual(sent_count, 0)
        self.assertEqual(contradictions, [])
        self.assertEqual(rows[0]["reality"], "staged")
        self.assertEqual(rows[0]["verdict"], "ok")
        self.assertEqual(orphans, [])  # the staged draft is named, so it is not an orphan

    def test_a_ledger_without_prospects_is_refused(self):
        self.t.ledger.write_text(json.dumps({"tiers": {}}))
        with self.assertRaises(ValueError):
            audit.audit(self.t.ledger, self.t.root)


class OrphanTests(unittest.TestCase):
    """A staged draft no ledger row names is one the ledger cannot see."""

    def setUp(self):
        self.t = _Tree()

    def tearDown(self):
        self.t.close()

    def test_an_unnamed_staged_draft_is_reported(self):
        self.t.touch("outreach/drafts", "orphan.md")
        self.t.touch("outreach/drafts", "README.md", "# drafts\n")
        self.t.write_ledger([])  # a ledger that names nothing
        _rows, _sent, _con, orphans = self.t.rows()
        self.assertEqual(orphans, ["orphan.md"])  # README.md is not a draft

    def test_a_named_staged_draft_is_not_an_orphan(self):
        self.t.touch("outreach/drafts", "known.md")
        self.t.write_ledger([
            {"id": "k", "tier": "B", "status": "not contacted — draft staged",
             "draft": "channels/outreach/drafts/known.md"},
        ])
        _rows, _sent, _con, orphans = self.t.rows()
        self.assertEqual(orphans, [])

    def test_a_draft_named_but_missing_is_dangling_not_an_orphan(self):
        # The ledger names a file that is not there: that is DANGLING, a different fault,
        # and it must not be double-counted as an orphan (which is an unnamed *present* file).
        self.t.write_ledger([
            {"id": "gone", "tier": "B", "status": "not contacted — draft staged",
             "draft": "channels/outreach/drafts/gone.md"},
        ])
        rows, _sent, _con, orphans = self.t.rows()
        self.assertEqual(orphans, [])
        self.assertEqual(rows[0]["verdict"], "DANGLING")


class RealLedgerTests(unittest.TestCase):
    """The delivered ledger, pinned: no row may drift from the mail folder again."""

    def test_the_lands_own_ledger_has_no_drift(self):
        rows, sent_count, contradictions, orphans = audit.audit(
            ROOT / "channels" / "outreach" / "pipeline.json", ROOT
        )
        self.assertEqual(contradictions, [], f"ledger prose contradicts the files: {contradictions}")
        drift = [(r["id"], r["verdict"], r["status"]) for r in rows if r["verdict"] != "ok"]
        self.assertEqual(drift, [], f"ledger rows disagree with channels/outbound|sent: {drift}")

    def test_the_lands_own_ledger_has_no_orphan_drafts(self):
        # Every *.md staged or named under channels/outreach/drafts/ must be a row in the
        # ledger, or the ledger is blind to a message that has been prepared to send.
        _rows, _sent, _con, orphans = audit.audit(
            ROOT / "channels" / "outreach" / "pipeline.json", ROOT
        )
        self.assertEqual(orphans, [], f"staged drafts the ledger does not name: {orphans}")


if __name__ == "__main__":
    unittest.main()
