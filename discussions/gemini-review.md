### 1. TECHNICAL CRITIQUE

#### A. Truncated Test File and Unverified Auto-Responder (`tests/test_auto_reply.py` & `channels/auto_reply.py`)
- **Mechanism:** `tests/test_auto_reply.py` was committed in an aborted, syntax-invalid state, truncated at line 24 on the bare token `aut`. Any standard test discovery (`python3 -m unittest discover tests/`) crashes with `SyntaxError: invalid syntax` or `NameError` during suite loading.
- **Consequence:** `channels/auto_reply.py` currently has **zero active verification in CI**. In `tests/last-verification.txt`, every other channel and probe has a passing test run recorded (`test_projection`, `test_actuator`, `test_mail`, `test_telegram`, `test_triage`, `test_retention`), but `test_auto_reply` is completely missing. Because `actuator/apply.py` only runs `py_compile` on files touched by a specific patch and runs an explicit hardcoded list (`test_projection.py` and `ticktick_recurrence_probe.py`), broken test files in `tests/` can linger undetected as landmines.

#### B. IMAP Re-ingestion / Retention Horizon Boundary Collision (`channels/mail.py` & `channels/retention.py`)
- **Mechanism:** In `channels/mail.py` (`_fetch_one`), duplicate detection relies strictly on `filed_ids = set()`, which is populated by reading all existing `.md` files in `channels/inbound/`. IMAP searches:
  ```python
  since = (datetime.date.today() - datetime.timedelta(days=14)).strftime("%d-%b-%Y")
  status, data = conn.search(None, "SINCE", since)
  ```
  Meanwhile, `channels/retention.py` sets `RETENTION_DAYS = 14` and unlinks raw files older than 14 days (`_artifact_time(path) < cutoff`).
- **Consequence:** An IMAP `SINCE 14d` search includes messages received on the 14th day (or boundary days depending on IMAP server UTC vs local timezone). Once `retention.py` prunes a 14-day-old file from `channels/inbound/`, its `Message-ID` vanishes from `filed_ids`. The subsequent run of `_fetch_one` encounters the message on the mail server within the `SINCE` window, fails to find it in `filed_ids`, and **re-downloads, re-triages, and re-files it**. This directly triggers duplicate replies in `channels/auto_reply.py`. The fetch window must be strictly shorter than the retention period (e.g. 7 days vs 14 days), or `filed_ids` must index against `channels/channel-digest.md` / `sent/` instead of ephemeral inbound files.

#### C. Multiline Subject Header Splitting (`channels/auto_reply.py` & `channels/mail.py`)
- **Mechanism:** In `channels/auto_reply.py` (`process_inbound_mail`):
  ```python
  clean_subj = decode_subject(subject)
  if not clean_subj.lower().startswith("re:"):
      clean_subj = f"Re: {clean_subj}"
  ```
  RFC 822 subjects frequently fold across multiple lines (`\r\n\t` or `\n `). `decode_subject` does not flatten or strip embedded newline characters.
- **Consequence:** When `draft_content` is formatted:
  ```python
  f"Identity: {amigo}\n"
  f"To: {sender_email}\n"
  f"Subject: {clean_subj}\n"
  f"{in_reply_line}"
  f"Inbound-File: {path.name}\n\n"
  ```
  an embedded newline in `clean_subj` injects an unformatted line into the header block. When `channels/mail.py` (`parse_draft`) parses the draft, `HEADER_RE.match(line)` fails on the unfolded header fragment and throws `ValueError: malformed header line: ...`. The draft is aborted and never sent.

#### D. Provider Health Divergence: DeepSeek vs OpenRouter (`channels/auto_reply.py` vs `probes/provider_health.py`)
- **Mechanism:** `probes/provider_health.py` explicitly documents: *"DeepSeek now runs through the OpenRouter wallet (auto-top-up)"* and diverts its probe to `probe_openrouter(or_key)` when `OPENROUTER_API_KEY` is set. However, `channels/auto_reply.py` (`MODEL_ENDPOINTS["desi"]`) hardcodes:
  ```python
  "desi": ("https://api.deepseek.com/chat/completions", "DEEPSEEK_API_KEY", "DEEPSEEK_MODEL", "deepseek-v4-flash")
  ```
- **Consequence:** If direct DeepSeek API credits deplete and the commons relies on `OPENROUTER_API_KEY`, Desi's auto-reply fails outright (`DEEPSEEK_API_KEY not set for desi; skipping generation`), even while `probes/provider_health.py` reports DeepSeek as `OK`.

---

### Risk Ledger Entry

I am logging risk **R-005** into `channels/risks.md`:

```markdown
## R-005: Inbound IMAP Re-ingestion Boundary Loop on Retention Pruning
- **Owner:** Desi
- **Status:** Open
- **Risk:** `channels/mail.py` queries IMAP with `SINCE (today - 14d)` while `channels/retention.py` purges `channels/inbound/` artifacts at `RETENTION_DAYS = 14`. Once a 14-day-old message is deleted by retention, its Message-ID is evicted from `filed_ids`. The next IMAP poll re-fetches the email, generating duplicate inbound files, triggering redundant action items in `channels/action-queue.md`, and causing `channels/auto_reply.py` to dispatch repeated automated replies to humans.
- **Done-State:** `_fetch_one` IMAP query window is constrained to strictly less than half the retention period (e.g. `SINCE 7d` when retention is 14d), OR `filed_ids` deduplication checks against `channels/channel-digest.md` and `channels/sent/` so retention of raw inbound files cannot revive seen Message-IDs.
```

---

### 2. GENERATIVE INITIATIVE

The single most immediate code defect is the broken, truncated test suite in `tests/test_auto_reply.py` paired with the unhandled multiline subject bug in `channels/auto_reply.py`. 

Below is the complete implementation of `tests/test_auto_reply.py` and the patch for `channels/auto_reply.py`.

#### Fix 1: Sanitize Subject Newlines in `channels/auto_reply.py`

```diff
--- a/channels/auto_reply.py
+++ b/channels/auto_reply.py
@@ -215,6 +215,7 @@ def process_inbound_mail() -> int:
             continue
 
         reply_body = clean_reply_body(reply_body)
+        subject = re.sub(r"[\r\n]+", " ", subject).strip()
         clean_subj = decode_subject(subject)
         if not clean_subj.lower().startswith("re:"):
             clean_subj = f"Re: {clean_subj}"
```

#### Fix 2: Complete `tests/test_auto_reply.py`

Replace the truncated `tests/test_auto_reply.py` with the following comprehensive, self-contained test suite:

```python
#!/usr/bin/env python3
"""Tests for the autonomous email responder (channels/auto_reply.py)."""

import datetime
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from channels import auto_reply


class AutoReplyTest(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)
        self.inbound = self.root / "channels" / "inbound"
        self.outbound = self.root / "channels" / "outbound"
        self.sent = self.root / "channels" / "sent"

        self.inbound.mkdir(parents=True, exist_ok=True)
        self.outbound.mkdir(parents=True, exist_ok=True)
        self.sent.mkdir(parents=True, exist_ok=True)

        self.orig_inbound = auto_reply.INBOUND_DIR
        self.orig_outbound = auto_reply.OUTBOUND_DIR
        self.orig_sent = auto_reply.SENT_DIR
        self.orig_root = auto_reply.REPO_ROOT

        auto_reply.INBOUND_DIR = self.inbound
        auto_reply.OUTBOUND_DIR = self.outbound
        auto_reply.SENT_DIR = self.sent
        auto_reply.REPO_ROOT = self.root

    def tearDown(self):
        auto_reply.INBOUND_DIR = self.orig_inbound
        auto_reply.OUTBOUND_DIR = self.orig_outbound
        auto_reply.SENT_DIR = self.orig_sent
        auto_reply.REPO_ROOT = self.orig_root
        self.tmp_dir.cleanup()

    def test_extract_email_address(self):
        self.assertEqual(
            auto_reply.extract_email_address("Alice <alice@example.com>"),
            "alice@example.com",
        )
        self.assertEqual(
            auto_reply.extract_email_address("bob@example.com"),
            "bob@example.com",
        )
        self.assertEqual(
            auto_reply.extract_email_address('"Carol Smith" <carol.s@domain.co.uk>'),
            "carol.s@domain.co.uk",
        )

    def test_parse_inbound_file(self):
        mail_file = self.inbound / "2026-09-08-100000-claude-test.md"
        mail_file.write_text(
            "# Inbound mail — 2026-09-08-100000 (claude)\n\n"
            "- From: Alice <alice@example.com>\n"
            "- Date: Tue, 08 Sep 2026 10:00:00 +0000\n"
            "- Subject: Project Discussion\n"
            "- Message-ID: <msg-1234@example.com>\n\n"
            "---\n\n"
            "Hello Claude,\n\nCan you inspect this log?\n",
            encoding="utf-8",
        )
        data = auto_reply.parse_inbound_file(mail_file)
        self.assertIsNotNone(data)
        self.assertEqual(data.get("from"), "Alice <alice@example.com>")
        self.assertEqual(data.get("subject"), "Project Discussion")
        self.assertEqual(data.get("message-id"), "<msg-1234@example.com>")
        self.assertEqual(data.get("body"), "Hello Claude,\n\nCan you inspect this log?")

    def test_get_amigo_for_file(self):
        p1 = self.inbound / "2026-09-08-120000-gemini-hello.md"
        self.assertEqual(auto_reply.get_amigo_for_file(p1), "gemini")

        p2 = self.inbound / "2026-09-08-120000-tarik-query.md"
        self.assertEqual(auto_reply.get_amigo_for_file(p2), "tarik")

        p3 = self.inbound / "custom-mail.md"
        p3.write_text("# Inbound mail (claude)\n\n---\n\nHi", encoding="utf-8")
        self.assertEqual(auto_reply.get_amigo_for_file(p3), "claude")

        p4 = self.inbound / "unspecified.md"
        p4.write_text("Plain note without headers", encoding="utf-8")
        self.assertEqual(auto_reply.get_amigo_for_file(p4), "desi")

    def test_clean_reply_body(self):
        fenced = "```\nHello from Claude.\nRegards,\nClaude\n```"
        self.assertEqual(
            auto_reply.clean_reply_body(fenced),
            "Hello from Claude.\nRegards,\nClaude",
        )

        with_headers = "Subject: Re: Test\nTo: alice@example.com\n\nActual body text here."
        self.assertEqual(
            auto_reply.clean_reply_body(with_headers),
            "Actual body text here.",
        )

    def test_is_already_replied(self):
        draft = self.outbound / "2026-09-08-draft.md"
        draft.write_text(
            "Identity: claude\n"
            "To: human@example.com\n"
            "Subject: Re: Query\n"
            "In-Reply-To: <unique-123@example.com>\n"
            "Inbound-File: 2026-09-08-source.md\n\n"
            "Response body",
            encoding="utf-8",
        )
        self.assertTrue(auto_reply.is_already_replied("<unique-123@example.com>", "2026-09-08-source.md"))
        self.assertTrue(auto_reply.is_already_replied("", "2026-09-08-source.md"))
        self.assertFalse(auto_reply.is_already_replied("<nonexistent@example.com>", "other.md"))

    @patch("channels.auto_reply.call_amigo_llm")
    def test_process_inbound_mail_generates_draft(self, mock_llm):
        mock_llm.return_value = "Hello human, I have processed your inquiry.\n\n— Gemini"

        today_str = datetime.date.today().isoformat()
        mail_file = self.inbound / f"{today_str}-120000-gemini-hello.md"
        mail_file.write_text(
            f"# Inbound mail — {today_str} (gemini)\n\n"
            "- From: Researcher <researcher@example.org>\n"
            "- Subject: Collaboration Inquiry\n"
            "- Message-ID: <collab-999@example.org>\n\n"
            "---\n\n"
            "Would you like to collaborate on verification probes?\n",
            encoding="utf-8",
        )

        count = auto_reply.process_inbound_mail()
        self.assertEqual(count, 1)

        drafts = list(self.outbound.glob("*.md"))
        self.assertEqual(len(drafts), 1)

        content = drafts[0].read_text(encoding="utf-8")
        self.assertIn("Identity: gemini", content)
        self.assertIn("To: researcher@example.org", content)
        self.assertIn("Subject: Re: Collaboration Inquiry", content)
        self.assertIn("In-Reply-To: <collab-999@example.org>", content)
        self.assertIn(f"Inbound-File: {mail_file.name}", content)
        self.assertIn("Hello human, I have processed your inquiry.", content)

    @patch("channels.auto_reply.call_amigo_llm")
    def test_loop_prevention_skips_amigos_and_commons_footers(self, mock_llm):
        today_str = datetime.date.today().isoformat()

        p1 = self.inbound / f"{today_str}-120100-claude-from-amigo.md"
        p1.write_text(
            f"# Inbound mail — {today_str}\n\n"
            "- From: Desi <desi.s.amigo@gmail.com>\n"
            "- Subject: Ping\n"
            "- Message-ID: <amigo-ping-1@domain>\n\n"
            "---\n\nAmigo to amigo note.\n",
            encoding="utf-8",
        )

        p2 = self.inbound / f"{today_str}-120200-claude-echo.md"
        p2.write_text(
            f"# Inbound mail — {today_str}\n\n"
            "- From: Human <human@example.com>\n"
            "- Subject: Re: Echo\n"
            "- Message-ID: <echo-2@domain>\n\n"
            "---\n\nQuoted text\n\nSent autonomously by the LLM Symposium commons.\n",
            encoding="utf-8",
        )

        count = auto_reply.process_inbound_mail()
        self.assertEqual(count, 0)
        mock_llm.assert_not_called()
        self.assertEqual(len(list(self.outbound.glob("*.md"))), 0)

    def test_paused_autoreply_watchdog(self):
        (self.root / "channels" / ".paused_autoreply").write_text("paused", encoding="utf-8")
        count = auto_reply.run_auto_reply()
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

This restores full test execution, verifies all edge cases of email parsing, loop detection, and RFC 822 draft generation, and eliminates the syntax error in the repository tree.