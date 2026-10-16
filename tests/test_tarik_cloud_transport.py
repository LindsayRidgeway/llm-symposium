"""Offline behavioral checks for Tarik's fixed-identity cloud transport.

All transports are injected fakes. No test reads real credentials or connects to
Telegram, Gmail, GitHub, or any other service.
"""

import contextlib
from datetime import datetime, timezone
from email.message import EmailMessage
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from urllib.parse import parse_qs


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "tarik_cloud_transport.py"
SPEC = importlib.util.spec_from_file_location("tarik_cloud_transport", SCRIPT)
transport = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(transport)

BOT = "tarik_s_commons_bot"
MAILBOX = "tarik.s.commons@gmail.com"
HUMAN_EMAIL = "ldridgeway@gmail.com"
HUMAN_CHAT = "1733127278"
TOKEN = "test-telegram-token-DO-NOT-PERSIST"
PASSWORD = "test-mail-password-DO-NOT-PERSIST"
ENV = {
    "TELEGRAM_BOT_TOKEN_TARIK": TOKEN,
    "SYMPOSIUM_MAIL_USER_TARIK": MAILBOX,
    "SYMPOSIUM_MAIL_APP_PASSWORD_TARIK": PASSWORD,
}
NOW = lambda: datetime(2026, 10, 16, 12, 0, 0, tzinfo=timezone.utc)


class JsonResponse:
    def __init__(self, data):
        self.data = json.dumps(data).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.data


class Telegram:
    def __init__(self, username=BOT, failure=None):
        self.username = username
        self.failure = failure
        self.methods = []
        self.sent = []

    def __call__(self, request, timeout=30):
        method = request.full_url.rsplit("/", 1)[-1]
        self.methods.append(method)
        if method == "getMe":
            return JsonResponse({"ok": True, "result": {
                "id": 111, "is_bot": True, "username": self.username,
            }})
        if method == "sendMessage":
            raw = (request.data or b"").decode("utf-8")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {key: values[0] for key, values in parse_qs(raw).items()}
            self.sent.append(payload)
            if self.failure:
                raise self.failure
            return JsonResponse({"ok": True, "result": {
                "message_id": 456,
                "chat": {"id": int(HUMAN_CHAT)},
                "from": {"id": 111, "is_bot": True, "username": BOT},
            }})
        raise AssertionError("Forbidden/unexpected Telegram method: " + method)


class SMTP:
    def __init__(self, failure=None):
        self.failure = failure
        self.messages = []
        self.logins = []
        self.connections = []

    def __call__(self, host, port, timeout=30):
        self.connections.append((host, port))
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def ehlo(self):
        return 250, b"ok"

    def starttls(self, context=None):
        return 220, b"ready"

    def login(self, username, password):
        self.logins.append((username, password))
        return 235, b"ok"

    def send_message(self, message, from_addr=None, to_addrs=None):
        self.messages.append((message, from_addr, to_addrs))
        if self.failure:
            raise self.failure
        return {}

    def quit(self):
        return 221, b"bye"


class IMAP:
    def __init__(self, messages=None):
        self.messages = messages or {}
        self.calls = []
        self.logins = []

    def __call__(self, host, port, timeout=30):
        self.calls.append(("connect", host, port))
        return self

    def login(self, username, password):
        self.logins.append((username, password))
        return "OK", [b"authenticated"]

    def select(self, mailbox="INBOX", readonly=False):
        self.calls.append(("select", mailbox, readonly))
        return "OK", [str(len(self.messages)).encode("ascii")]

    def response(self, code):
        self.calls.append(("response", code))
        return "UIDVALIDITY", [b"750"]

    def uid(self, command, *args):
        self.calls.append(("uid", command, *args))
        if command.lower() == "search":
            return "OK", [b" ".join(str(uid).encode("ascii") for uid in self.messages)]
        if command.lower() == "fetch":
            uid = args[0]
            if isinstance(uid, bytes):
                uid = uid.decode("ascii")
            raw = self.messages[str(uid)]
            return "OK", [(b"1 (UID " + str(uid).encode("ascii") + b" BODY[])", raw), b")"]
        raise AssertionError("Unexpected IMAP UID operation: " + command)

    def logout(self):
        self.calls.append(("logout",))
        return "BYE", [b"bye"]


def mail(sender, body, subject="Continuity reply", uid="one", reply_to=None, references=None):
    message = EmailMessage()
    message["From"] = sender
    message["To"] = MAILBOX
    message["Subject"] = subject
    message["Message-ID"] = "<" + uid + "@example.test>"
    if reply_to is not None:
        message["In-Reply-To"] = reply_to
    if references is not None:
        message["References"] = references
    message.set_content(body)
    return message.as_bytes()


class CloudTransportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.log = self.root / "channels/conversation/tarik.md"
        self.log.parent.mkdir(parents=True)
        self.before = b"Existing continuity record.\n\n"
        self.log.write_bytes(self.before)
        self.telegram = Telegram()
        self.smtp = SMTP()
        self.imap = IMAP()
        # Accidental non-injected network access is an immediate test failure.
        patcher = mock.patch("socket.create_connection", side_effect=AssertionError("Real network is forbidden"))
        patcher.start()
        self.addCleanup(patcher.stop)

    def request(self, kind="send_telegram", request_id="test-one", **extra):
        data = {"id": request_id, "type": kind, "source": "codex"}
        if kind in ("send_telegram", "send_mail"):
            data["body"] = "Continuity test, with a second line.\nNo secrets here."
        if kind == "send_mail":
            data["subject"] = "Tarik cloud continuity test"
        if kind == "sync_mail":
            data["reply_to"] = "outgoing-one"
        data.update(extra)
        return data

    def process(self, request, **kwargs):
        options = dict(environ=ENV.copy(), opener=self.telegram,
                       smtp_factory=self.smtp, imap_factory=self.imap, now=NOW)
        options.update(kwargs)
        return transport.process_request(request, self.root, **options)

    def all_persisted_text(self):
        return "\n".join(path.read_text(errors="replace") for path in self.root.rglob("*") if path.is_file())

    def open_reply_thread(self):
        receipt = self.process(self.request("send_mail", request_id="outgoing-one"))
        self.assertEqual(receipt["status"], "delivered")
        return receipt["remote_message_id"]

    def test_sync_requires_safe_explicit_reply_context(self):
        request = self.request("sync_mail")
        del request["reply_to"]
        with self.assertRaises(ValueError):
            transport.validate_request(request)
        for reply_to in ("../outside", "/tmp/outside", "a\\b", "", "bad\nid"):
            with self.subTest(reply_to=reply_to), self.assertRaises(ValueError):
                transport.validate_request(self.request("sync_mail", reply_to=reply_to))

    def test_sync_rejects_missing_undelivered_and_mismatched_outgoing_receipts(self):
        cases = [None,
                 {"status": "failed", "operation": "send_mail"},
                 {"status": "uncertain", "operation": "send_mail"},
                 {"status": "attempting", "operation": "send_mail"},
                 {"status": "delivered", "operation": "send_telegram"},
                 {"status": "delivered", "operation": "send_mail",
                  "remote_message_id": "<other-message@example.test>"}]
        for index, prior in enumerate(cases):
            with self.subTest(prior=prior):
                reference = "prior-" + str(index)
                if prior is not None:
                    path = self.root / "channels/tarik-cloud/receipts" / (reference + ".json")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(prior))
                result = self.process(self.request("sync_mail", request_id="sync-gate-" + str(index),
                                                   reply_to=reference))
                self.assertEqual(result["status"], "failed")
                self.assertEqual(result["reason"], "reply_context_not_delivered")
        self.assertEqual(self.imap.calls, [], "Invalid reply contexts must not open the mailbox")
        self.assertEqual(self.log.read_bytes(), self.before)

    def test_request_rejects_foreign_source_and_arbitrary_recipient_fields(self):
        for extra in ({"source": "goose"}, {"source": "lindsay"},
                      {"to": "other@example.test"}, {"recipient": HUMAN_EMAIL},
                      {"chat_id": "999"}, {"from": MAILBOX},
                      {"attachments": ["/etc/passwd"]}):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                transport.validate_request(self.request(**extra))

    def test_request_ids_cannot_escape_receipt_directory(self):
        for request_id in ("../outside", "a/b", "a\\b", "/tmp/outside", ".", "..",
                           "bad\nid", "bad\x00id", "", "x" * 500):
            with self.subTest(request_id=request_id), self.assertRaises(ValueError):
                transport.validate_request(self.request(request_id=request_id))

    def test_mail_subject_rejects_header_injection(self):
        for subject in ("hello\r\nBcc: other@example.test", "hello\nTo: other@example.test", "hello\rCc: x"):
            with self.subTest(subject=subject), self.assertRaises(ValueError):
                transport.validate_request(self.request("send_mail", subject=subject))

    def test_wrong_telegram_identity_cannot_send_or_append(self):
        telegram = Telegram(username="someone_elses_bot")
        try:
            self.process(self.request(), opener=telegram)
        except (ValueError, RuntimeError):
            pass
        self.assertEqual(telegram.sent, [])
        self.assertEqual(self.log.read_bytes(), self.before)

    def test_wrong_mailbox_cannot_login_send_or_append(self):
        bad_env = dict(ENV, SYMPOSIUM_MAIL_USER_TARIK="other@example.test")
        try:
            self.process(self.request("send_mail"), environ=bad_env)
        except (ValueError, RuntimeError):
            pass
        self.assertEqual(self.smtp.logins, [])
        self.assertEqual(self.smtp.messages, [])
        self.assertEqual(self.log.read_bytes(), self.before)

    def test_telegram_success_appends_continuity_and_fixed_recipient(self):
        request = self.request()
        receipt = self.process(request)
        self.assertEqual(receipt["status"], "delivered")
        self.assertEqual(len(self.telegram.sent), 1)
        self.assertEqual(str(self.telegram.sent[0]["chat_id"]), HUMAN_CHAT)
        after = self.log.read_bytes()
        self.assertTrue(after.startswith(self.before))
        appended = after[len(self.before):].decode("utf-8")
        self.assertIn(request["body"], appended)
        self.assertIn("codex", appended.lower())
        self.assertIn("telegram", appended.lower())
        self.assertIn(BOT, json.dumps(receipt) + appended)
        self.assertNotIn("getUpdates", self.telegram.methods)

    def test_repeated_request_id_does_not_resend_or_append(self):
        request = self.request()
        first = self.process(request)
        saved_log = self.log.read_bytes()
        second = self.process(request)
        self.assertEqual(first, second)
        self.assertEqual(len(self.telegram.sent), 1)
        self.assertEqual(self.log.read_bytes(), saved_log)

    def test_prior_attempting_receipt_blocks_uncertain_resend(self):
        request = self.request()
        receipt_file = self.root / "channels/tarik-cloud/receipts/test-one.json"
        receipt_file.parent.mkdir(parents=True)
        receipt_file.write_text(json.dumps({"id": request["id"], "status": "attempting",
                                           "source": "codex", "operation": request["type"]}))
        receipt = self.process(request)
        self.assertIn(receipt["status"], ("uncertain", "attempting"))
        self.assertEqual(self.telegram.sent, [])
        self.assertEqual(self.log.read_bytes(), self.before)

    def test_smtp_success_uses_only_fixed_mail_identity_and_human(self):
        request = self.request("send_mail")
        receipt = self.process(request)
        self.assertEqual(receipt["status"], "delivered")
        self.assertEqual(len(self.smtp.messages), 1)
        message, envelope_from, envelope_to = self.smtp.messages[0]
        self.assertEqual(str(message["From"]), MAILBOX)
        self.assertEqual(str(message["To"]), HUMAN_EMAIL)
        self.assertIsNone(message["Cc"])
        self.assertIsNone(message["Bcc"])
        if envelope_from is not None:
            self.assertEqual(envelope_from, MAILBOX)
        if envelope_to is not None:
            self.assertEqual([envelope_to] if isinstance(envelope_to, str) else list(envelope_to), [HUMAN_EMAIL])
        self.assertTrue(self.log.read_bytes().startswith(self.before))
        self.assertIn(request["body"], self.log.read_text())
        self.assertIn(MAILBOX, json.dumps(receipt) + self.log.read_text())

    def test_smtp_failure_never_marks_sent_or_duplicates_on_retry(self):
        smtp = SMTP(failure=RuntimeError("transport disconnected after DATA"))
        request = self.request("send_mail")
        try:
            result = self.process(request, smtp_factory=smtp)
        except (ValueError, RuntimeError):
            result = {}
        self.assertNotIn(result.get("status"), ("sent", "delivered"))
        self.assertEqual(self.log.read_bytes(), self.before)
        try:
            retry = self.process(request, smtp_factory=smtp)
        except (ValueError, RuntimeError):
            retry = {}
        self.assertNotIn(retry.get("status"), ("sent", "delivered"))
        self.assertEqual(len(smtp.messages), 1, "An uncertain SMTP send must never be retried automatically")
        self.assertNotIn('"status": "sent"', self.all_persisted_text())
        self.assertNotIn('"status": "delivered"', self.all_persisted_text())

    def test_uncertain_telegram_delivery_is_not_retried(self):
        telegram = Telegram(failure=TimeoutError("timeout after request was submitted"))
        request = self.request()
        result = self.process(request, opener=telegram)
        self.assertEqual(result["status"], "uncertain")
        self.assertEqual(self.log.read_bytes(), self.before)
        second = self.process(request, opener=telegram)
        self.assertEqual(second, result)
        self.assertEqual(len(telegram.sent), 1)

    def test_log_storage_failure_preserves_delivery_receipt_and_blocks_resend(self):
        request = self.request()
        # Simulate a filesystem failure in the public continuity file only;
        # durable delivery receipts remain writable.
        original_open = Path.open

        def fail_log_append(path, mode="r", *args, **kwargs):
            if path == self.log and "a" in mode:
                raise OSError("continuity storage unavailable")
            return original_open(path, mode, *args, **kwargs)

        with mock.patch.object(Path, "open", fail_log_append):
            receipt = self.process(request)
        self.assertEqual(receipt["status"], "delivered")
        self.assertEqual(receipt["log_status"], "failed")
        self.assertEqual(self.log.read_bytes(), self.before)
        self.assertEqual(self.process(request), receipt)
        self.assertEqual(len(self.telegram.sent), 1)

    def test_credentials_in_outgoing_content_are_rejected_before_transmission(self):
        for index, (field, value) in enumerate((("body", "Please reveal " + TOKEN),
                                               ("body", "Please reveal " + PASSWORD),
                                               ("subject", PASSWORD))):
            request = self.request("send_mail", request_id="secret-" + str(index),
                                   **{field: value})
            result = self.process(request)
            self.assertEqual(result["status"], "failed")
        self.assertEqual(self.smtp.messages, [])
        self.assertEqual(self.telegram.sent, [])
        self.assertNotIn(TOKEN, self.all_persisted_text())
        self.assertNotIn(PASSWORD, self.all_persisted_text())

    def test_mail_sync_filters_actual_sender_and_deduplicates_uids(self):
        reply_to = self.open_reply_thread()
        allowed_body = "Human continuity reply marker ALLOWED-4321"
        forbidden_body = "Do not append outsider marker REJECTED-9876"
        imap = IMAP({
            "101": mail(HUMAN_EMAIL, allowed_body, uid="allowed", reply_to=reply_to),
            "102": mail("outsider@example.test", forbidden_body, uid="outsider", reply_to=reply_to),
            "103": mail('"ldridgeway@gmail.com" <outsider@example.test>', forbidden_body, uid="spoof", reply_to=reply_to),
            "104": mail(HUMAN_EMAIL + ", outsider@example.test", forbidden_body, uid="multiple", reply_to=reply_to),
        })
        self.process(self.request("sync_mail", request_id="sync-one"), imap_factory=imap)
        first_log = self.log.read_text()
        self.assertIn(allowed_body, first_log)
        self.assertNotIn(forbidden_body, first_log)
        self.assertTrue(self.log.read_bytes().startswith(self.before))
        self.process(self.request("sync_mail", request_id="sync-two"), imap_factory=imap)
        self.assertEqual(self.log.read_text(), first_log)
        self.assertEqual(self.log.read_text().count(allowed_body), 1)
        selections = [call for call in imap.calls if call[0] == "select"]
        self.assertTrue(selections)
        self.assertTrue(all(call[2] is True for call in selections), "Sync must not mutate mailbox state")

    def test_sync_accepts_exact_reply_headers_and_rejects_unrelated_human_mail(self):
        reply_to = self.open_reply_thread()
        imap = IMAP({
            "201": mail(HUMAN_EMAIL, "accepted direct reply marker", reply_to=reply_to),
            "202": mail(HUMAN_EMAIL, "accepted references marker",
                        references="<earlier@example.test> " + reply_to),
            "203": mail(HUMAN_EMAIL, "rejected unrelated marker"),
            "204": mail(HUMAN_EMAIL, "rejected other thread marker", reply_to="<other@example.test>"),
            "205": mail(HUMAN_EMAIL, "rejected substring thread marker",
                        reply_to=reply_to[:-1] + ".attacker>"),
        })
        result = self.process(self.request("sync_mail"), imap_factory=imap)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["recorded"], 2)
        appended = self.log.read_text()
        self.assertIn("accepted direct reply marker", appended)
        self.assertIn("accepted references marker", appended)
        self.assertNotIn("rejected unrelated marker", appended)
        self.assertNotIn("rejected other thread marker", appended)
        self.assertNotIn("rejected substring thread marker", appended)
        self.assertNotIn("**Lindsay:**", appended)
        self.assertIn("Claimed sender " + HUMAN_EMAIL, appended)
        self.assertIn("authentication unverified", appended)
        search_calls = [call for call in imap.calls if call[:2] == ("uid", "search")]
        self.assertEqual(len(search_calls), 1)
        self.assertIn("FROM", search_calls[0])
        self.assertIn(HUMAN_EMAIL, search_calls[0])
        self.assertIn("In-Reply-To", search_calls[0])
        self.assertIn("References", search_calls[0])
        self.assertIn(reply_to, search_calls[0])

    def test_sync_removes_whole_credential_urls_including_secret_paths(self):
        reply_to = self.open_reply_thread()
        body = ("https://identity.example.test/reset/path-secret-123?next=query-secret-456#fragment-secret-789\n"
                "https://identity.example.test/safe?token=token-secret-123\n"
                "https://user:opaque-secret-999@identity.example.test/path\n"
                "Benign link https://example.test/documentation remains useful.")
        imap = IMAP({"301": mail(HUMAN_EMAIL, body, reply_to=reply_to,
                                subject="https://identity.example.test/auth/subject-secret-777")})
        result = self.process(self.request("sync_mail"), imap_factory=imap)
        self.assertEqual(result["status"], "completed")
        text = self.all_persisted_text()
        for secret in ("path-secret-123", "query-secret-456", "fragment-secret-789",
                       "token-secret-123", "opaque-secret-999", "subject-secret-777"):
            self.assertNotIn(secret, text)
        self.assertIn("https://example.test/documentation", text)
        self.assertIn("credential URL removed", text)

    def test_interrupted_inbound_append_surfaces_uncertainty_without_duplicate(self):
        reply_to = self.open_reply_thread()
        imap = IMAP({"401": mail(HUMAN_EMAIL, "must not append this again", reply_to=reply_to)})
        path = self.root / "channels/tarik-cloud/mail-receipts/750-401.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"status": "attempting", "operation": "receive_mail",
                                    "source": "codex", "reply_message_id": reply_to,
                                    "remote_message_id": "750:401"}))
        before_sync = self.log.read_bytes()
        result = self.process(self.request("sync_mail", request_id="sync-interrupted"), imap_factory=imap)
        self.assertEqual(result["status"], "uncertain")
        self.assertIn("750:401", result["uncertain_message_ids"])
        self.assertEqual(json.loads(path.read_text())["status"], "uncertain")
        self.assertEqual(self.log.read_bytes(), before_sync)
        fetches = [call for call in imap.calls if call[:2] == ("uid", "fetch")]
        self.assertEqual(fetches, [])
        second = self.process(self.request("sync_mail", request_id="sync-interrupted-again"), imap_factory=imap)
        self.assertEqual(second["status"], "uncertain")
        self.assertIn("750:401", second["uncertain_message_ids"])
        self.assertEqual(self.log.read_bytes(), before_sync)

    def test_new_inbound_append_failure_is_uncertain_and_never_retried(self):
        reply_to = self.open_reply_thread()
        imap = IMAP({"402": mail(HUMAN_EMAIL, "inbound failed append marker", reply_to=reply_to)})
        before_sync = self.log.read_bytes()
        original_open = Path.open

        def fail_log_append(path, mode="r", *args, **kwargs):
            if path == self.log and "a" in mode:
                raise OSError("continuity storage unavailable")
            return original_open(path, mode, *args, **kwargs)

        with mock.patch.object(Path, "open", fail_log_append):
            result = self.process(self.request("sync_mail", request_id="sync-storage-error"), imap_factory=imap)
        self.assertEqual(result["status"], "uncertain")
        self.assertEqual(result["reason"], "inbound_append_unknown")
        path = self.root / "channels/tarik-cloud/mail-receipts/750-402.json"
        self.assertEqual(json.loads(path.read_text())["status"], "uncertain")
        second = self.process(self.request("sync_mail", request_id="sync-storage-retry"), imap_factory=imap)
        self.assertEqual(second["status"], "uncertain")
        self.assertIn("750:402", second["uncertain_message_ids"])
        self.assertEqual(self.log.read_bytes(), before_sync)

    def test_probe_does_not_send_poll_updates_or_persist_secrets(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = transport.probe(environ=ENV.copy(), opener=self.telegram,
                                     smtp_factory=self.smtp, imap_factory=self.imap)
        self.assertIsInstance(result, dict)
        self.assertEqual(self.telegram.sent, [])
        self.assertNotIn("getUpdates", self.telegram.methods)
        self.assertEqual(self.smtp.messages, [])
        combined = stdout.getvalue() + stderr.getvalue() + json.dumps(result) + self.all_persisted_text()
        self.assertNotIn(TOKEN, combined)
        self.assertNotIn(PASSWORD, combined)

    def test_failure_details_do_not_persist_or_print_credentials(self):
        smtp = SMTP(failure=RuntimeError("error " + TOKEN + " " + PASSWORD))
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                result = self.process(self.request("send_mail"), smtp_factory=smtp)
            except (ValueError, RuntimeError) as error:
                result = {"error": str(error)}
        combined = stdout.getvalue() + stderr.getvalue() + json.dumps(result) + self.all_persisted_text()
        self.assertNotIn(TOKEN, combined)
        self.assertNotIn(PASSWORD, combined)


if __name__ == "__main__":
    unittest.main()
