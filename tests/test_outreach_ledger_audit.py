#!/usr/bin/env python3
"""The outreach ledger must match the mail queue's own files, and the files are ground truth.

Written 2026-09-26 with `scripts/outreach_ledger_audit.py`, after the ledger turned out to
say in one field that the outbound leg had "never been used for a single cold contact" while
two cold contacts sat in `channels/sent/`, sent on 2026-09-17. `mail.send_draft` moves a
draft to `sent/` only after SMTP accepts it, so location — not prose — decides "staged" vs
"queued" vs "sent". The last test pins the real ledger, so the drift cannot quietly return.

Extended 2026-10-06 (Desi) with the inbound leg. The same rule governs the other direction:
`mail._fetch_one` writes every fetched message to `channels/inbound/`, so a `status` that
claims "no reply" while a file from that contact sits in the inbox is stale, and the audit
was blind to it — the first reply the commons ever received was on disk and the ledger still
read "no reply as of 2026-09-26". The reply leg only ever adds a fault; a status that records
the reply stays ok.
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
        (self.root / "channels" / "inbound").mkdir(parents=True)
        self.ledger = self.root / "channels" / "outreach" / "pipeline.json"

    def inbound(self, name, from_header, body="a message"):
        """File an inbound message whose `- From:` header is `from_header`."""
        (self.root / "channels" / "inbound" / name).write_text(
            f"# Inbound mail — 2026-10-06-120000 (desi)\n\n"
            f"- From: {from_header}\n"
            f"- Date: Mon, 5 Oct 2026 21:28:45 -0700\n"
            f"- Subject: Re: a letter\n"
            f"- Message-ID: <x@y>\n\n---\n\n{body}\n"
        )

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


class InboundReplyTests(unittest.TestCase):
    """A reply's existence is a file in channels/inbound/, on the same rule as the outbound leg."""

    def setUp(self):
        self.t = _Tree()

    def tearDown(self):
        self.t.close()

    def test_a_filed_reply_is_found_by_the_contact_address(self):
        self.t.inbound("r.md", '"Retraction Watch" <team@retractionwatch.com>')
        self.assertIsNotNone(
            audit.inbound_reply("team@retractionwatch.com", self.t.root / "channels" / "inbound")
        )

    def test_a_contact_absent_from_the_inbox_has_no_reply(self):
        self.t.inbound("r.md", '"Someone Else" <other@example.org>')
        self.assertIsNone(
            audit.inbound_reply("team@retractionwatch.com", self.t.root / "channels" / "inbound")
        )

    def test_a_reordered_from_header_does_not_hide_a_reply(self):
        # mail clients render the display name either side of the address; neither may hide it.
        self.t.inbound("r.md", "team@retractionwatch.com (Retraction Watch)")
        self.assertIsNotNone(
            audit.inbound_reply("team@retractionwatch.com", self.t.root / "channels" / "inbound")
        )

    def test_a_web_form_contact_can_never_match(self):
        self.t.inbound("r.md", "<x@y.z>")
        self.assertIsNone(
            audit.inbound_reply("https://example.org/contact-us", self.t.root / "channels" / "inbound")
        )

    def test_an_empty_contact_matches_nothing(self):
        self.t.inbound("r.md", "<x@y.z>")
        self.assertIsNone(audit.inbound_reply(None, self.t.root / "channels" / "inbound"))


class ReplyLegTests(unittest.TestCase):
    """The audit's inbound leg: a silence claim checked against the inbox, not believed."""

    def setUp(self):
        self.t = _Tree()

    def tearDown(self):
        self.t.close()

    def test_a_silence_claim_against_a_filed_reply_is_stale(self):
        self.t.touch("sent", "p.md")
        self.t.inbound("r.md", '"Retraction Watch" <team@retractionwatch.com>')
        self.t.write_ledger([
            {"id": "retraction-watch", "tier": "A", "contact": "team@retractionwatch.com",
             "status": "sent 2026-09-17; no reply as of 2026-09-26",
             "draft": "channels/outbound/p.md"},
        ])
        rows, _, _ = self.t.rows()
        self.assertEqual(rows[0]["verdict"], "STALE")
        self.assertIsNotNone(rows[0]["reply"])

    def test_a_status_that_records_the_reply_is_ok(self):
        self.t.touch("sent", "p.md")
        self.t.inbound("r.md", '"Retraction Watch" <team@retractionwatch.com>')
        self.t.write_ledger([
            {"id": "retraction-watch", "tier": "A", "contact": "team@retractionwatch.com",
             "status": "sent 2026-09-17; automated acknowledgement received 2026-10-06",
             "draft": "channels/outbound/p.md"},
        ])
        rows, _, _ = self.t.rows()
        self.assertEqual(rows[0]["verdict"], "ok")

    def test_a_silence_claim_with_no_reply_on_file_stays_ok(self):
        self.t.touch("sent", "p.md")
        self.t.write_ledger([
            {"id": "me-cfs", "tier": "B", "contact": "oystein.fluge@helse-bergen.no",
             "status": "sent 2026-09-17; no reply as of 2026-10-06",
             "draft": "channels/outbound/p.md"},
        ])
        rows, _, _ = self.t.rows()
        self.assertEqual(rows[0]["verdict"], "ok")
        self.assertIsNone(rows[0]["reply"])


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
        rows, sent_count, contradictions = self.t.rows()
        self.assertEqual(sent_count, 2)
        self.assertEqual(sum(1 for r in rows if r["verdict"] == "STALE"), 2)
        self.assertEqual(rows[2]["verdict"], "ok")
        self.assertEqual(len(contradictions), 1)

    def test_no_contradiction_when_nothing_has_been_sent(self):
        self.t.touch("outbound", "c.md")
        self.t.write_ledger(
            [{"id": "c", "tier": "C", "status": "drafted and queued", "draft": "channels/outbound/c.md"}],
            why="the leg ... and has never been used for a single cold contact.",
        )
        _, sent_count, contradictions = self.t.rows()
        self.assertEqual(sent_count, 0)
        self.assertEqual(contradictions, [])

    def test_a_staged_draft_is_not_a_sent_contact(self):
        self.t.touch("outreach/drafts", "s.md")
        self.t.write_ledger(
            [{"id": "s", "tier": "B", "status": "not contacted — draft staged",
              "draft": "channels/outreach/drafts/s.md"}],
            why="the sending leg has done its work",
        )
        rows, sent_count, contradictions = self.t.rows()
        self.assertEqual(sent_count, 0)
        self.assertEqual(contradictions, [])
        self.assertEqual(rows[0]["reality"], "staged")
        self.assertEqual(rows[0]["verdict"], "ok")

    def test_a_ledger_without_prospects_is_refused(self):
        self.t.ledger.write_text(json.dumps({"tiers": {}}))
        with self.assertRaises(ValueError):
            audit.audit(self.t.ledger, self.t.root)


class RealLedgerTests(unittest.TestCase):
    """The delivered ledger, pinned: no row may drift from the mail folder again."""

    def test_the_lands_own_ledger_has_no_drift(self):
        rows, sent_count, contradictions = audit.audit(
            ROOT / "channels" / "outreach" / "pipeline.json", ROOT
        )
        self.assertEqual(contradictions, [], f"ledger prose contradicts the files: {contradictions}")
        drift = [(r["id"], r["verdict"], r["status"]) for r in rows if r["verdict"] != "ok"]
        self.assertEqual(drift, [], f"ledger rows disagree with channels/outbound|sent: {drift}")


if __name__ == "__main__":
    unittest.main()
