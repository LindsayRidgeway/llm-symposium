"""Offline checks for selecting and running a single GitHub push's requests."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/tarik_cloud_transport_runner.py"
SPEC = importlib.util.spec_from_file_location("tarik_cloud_transport_runner", SCRIPT)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)

BEFORE, AFTER = "a" * 40, "b" * 40
PREFIX = "channels/tarik-cloud/requests/"
EVENT = {"ref": "refs/heads/main", "before": BEFORE, "after": AFTER,
         "created": False, "deleted": False, "forced": False,
         "repository": {"full_name": runner.REPOSITORY}}
ENV = {"GITHUB_EVENT_NAME": "push", "GITHUB_REPOSITORY": runner.REPOSITORY,
       "GITHUB_RUN_ATTEMPT": "1", "GITHUB_TOKEN": "offline-read-token-NEVER-PRINT"}


def compare(files=()):
    return {"status": "ahead", "ahead_by": 1, "behind_by": 0,
            "total_commits": 1, "commits": [{"sha": AFTER}],
            "base_commit": {"sha": BEFORE}, "merge_base_commit": {"sha": BEFORE},
            "files": [{"filename": path, "status": status} for path, status in files]}


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.event, self.env = copy.deepcopy(EVENT), ENV.copy()
        self.fetch = mock.Mock(return_value=compare())
        self.process = mock.Mock(return_value={"status": "delivered", "log_status": "recorded"})
        blocker = mock.patch("socket.create_connection", side_effect=AssertionError("No real network"))
        blocker.start()
        self.addCleanup(blocker.stop)

    def request(self, request_id="one", **fields):
        data = {"id": request_id, "type": "send_telegram", "source": "codex", "body": "Test only."}
        data.update(fields)
        path = self.root / PREFIX / (request_id + ".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def run_push(self, **kwargs):
        options = dict(environ=self.env, compare_fetch=self.fetch, process_request=self.process)
        options.update(kwargs)
        return runner.run(self.event, self.root, **options)

    def test_selection_requires_exact_added_safe_request_paths(self):
        payload = compare([
            (PREFIX + "z-9.json", "added"), (PREFIX + "a.json", "added"),
            (PREFIX + "modified.json", "modified"), (PREFIX + "renamed.json", "renamed"),
            (PREFIX + "copied.json", "copied"), (PREFIX + "removed.json", "removed"),
            (PREFIX + "UPPER.json", "added"), (PREFIX + "nested/a.json", "added"),
            (PREFIX + "../escape.json", "added"), (PREFIX + "x.json/extra", "added"),
            (".github/workflows/tarik-cloud-transport.yml", "added"),
            ("scripts/tarik_cloud_transport.py", "added")])
        self.assertEqual(runner.select_request_paths(EVENT, payload, "1"),
                         [PREFIX + "a.json", PREFIX + "z-9.json"])

    def test_workflow_and_script_only_push_does_not_call_worker_or_write(self):
        self.fetch.return_value = compare([(".github/workflows/tarik-cloud-transport.yml", "added"),
                                           ("scripts/tarik_cloud_transport.py", "modified")])
        result = self.run_push()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["counts"]["selected"], 0)
        self.process.assert_not_called()
        self.assertEqual(list(self.root.iterdir()), [])

    def test_reruns_refused_before_compare_or_worker(self):
        for attempt in ("2", "3", "01", "", None, True):
            with self.subTest(attempt=attempt):
                self.env["GITHUB_RUN_ATTEMPT"] = attempt
                result = self.run_push()
                self.assertEqual(result["reason"], "rerun_refused")
        self.fetch.assert_not_called()
        self.process.assert_not_called()

    def test_event_and_environment_gates_precede_api(self):
        mutations = [{"ref": "refs/heads/other"}, {"deleted": True}, {"created": True},
                     {"forced": True}, {"before": "0" * 40}, {"after": "../evil"},
                     {"after": BEFORE}, {"repository": {"full_name": "other/repo"}}]
        for changes in mutations:
            with self.subTest(changes=changes):
                self.event = dict(EVENT, **changes)
                self.assertEqual(self.run_push()["status"], "rejected")
        self.event = copy.deepcopy(EVENT)
        for key, value in (("GITHUB_EVENT_NAME", "workflow_dispatch"),
                           ("GITHUB_REPOSITORY", "other/repo"), ("GITHUB_TOKEN", "")):
            with self.subTest(key=key):
                self.env = dict(ENV, **{key: value})
                self.assertEqual(self.run_push()["status"], "rejected")
        self.fetch.assert_not_called()
        self.process.assert_not_called()

    def test_incomplete_or_nonlinear_compare_cannot_select_requests(self):
        variants = []
        for changes in ({"total_commits": 2}, {"status": "diverged"}, {"behind_by": 1},
                        {"ahead_by": 2}, {"commits": [{"sha": "c" * 40}]},
                        {"base_commit": {"sha": "c" * 40}},
                        {"merge_base_commit": {"sha": "c" * 40}}, {"files": None},
                        {"base_commit": None}, {"merge_base_commit": []},
                        {"files": [{"filename": PREFIX + "one.json", "status": []}]}):
            variants.append(dict(compare([(PREFIX + "one.json", "added")]), **changes))
        for size in (300, 301):
            variants.append(compare([(f"unrelated/{n}.txt", "modified") for n in range(size)]))
        for payload in variants:
            with self.subTest(payload=payload):
                with self.assertRaises(runner.RunnerError):
                    runner.select_request_paths(EVENT, payload, "1")
        self.process.assert_not_called()

    def test_duplicate_or_ambiguous_added_files_rejected(self):
        payload = compare([(PREFIX + "one.json", "added")] * 2)
        with self.assertRaises(runner.RunnerError):
            runner.select_request_paths(EVENT, payload, 1)
        payload = compare([(PREFIX + "one.json", "added")])
        payload["files"][0]["previous_filename"] = PREFIX + "old.json"
        with self.assertRaises(runner.RunnerError):
            runner.select_request_paths(EVENT, payload, 1)

    def test_filename_id_mismatch_blocks_all_requests_before_send(self):
        self.request("a")
        mismatched = self.request("z")
        data = json.loads(mismatched.read_text())
        data["id"] = "different"
        mismatched.write_text(json.dumps(data))
        self.fetch.return_value = compare([(PREFIX + "a.json", "added"), (PREFIX + "z.json", "added")])
        result = self.run_push()
        self.assertEqual(result["reason"], "request_id_mismatch")
        self.process.assert_not_called()

    def test_sync_request_requires_existing_thread_field(self):
        path = self.request("sync", type="sync_mail")
        path.write_text(json.dumps({"id": "sync", "type": "sync_mail", "source": "codex"}))
        self.fetch.return_value = compare([(PREFIX + "sync.json", "added")])
        self.assertEqual(self.run_push()["status"], "rejected")
        self.process.assert_not_called()
        path.write_text(json.dumps({"id": "sync", "type": "sync_mail", "source": "codex", "reply_to": "sent-test"}))
        self.process.return_value = {"status": "completed", "recorded": 0}
        result = self.run_push()
        self.assertEqual(result["counts"]["synced"], 1)

    def test_success_reports_counts_without_request_bodies_or_tokens(self):
        self.request("one", body="PRIVATE-BODY-NEVER-PRINT")
        self.fetch.return_value = compare([(PREFIX + "one.json", "added")])
        result = self.run_push()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["counts"]["delivered"], 1)
        self.assertEqual(result["counts"]["processed"], 1)
        self.fetch.assert_called_once_with(BEFORE, AFTER, ENV["GITHUB_TOKEN"])
        self.assertNotIn("PRIVATE-BODY-NEVER-PRINT", json.dumps(result))
        self.assertNotIn(ENV["GITHUB_TOKEN"], json.dumps(result))

    def test_existing_receipt_calls_worker_without_transport_or_delivery_count(self):
        self.request("one")
        receipt = self.root / "channels/tarik-cloud/receipts/one.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({"status": "delivered", "operation": "send_telegram",
                                       "log_status": "recorded"}))
        self.fetch.return_value = compare([(PREFIX + "one.json", "added")])
        with mock.patch.object(runner.worker, "_telegram", side_effect=AssertionError("Must not resend")) as telegram:
            result = self.run_push(process_request=runner.worker.process_request)
        telegram.assert_not_called()
        self.assertEqual(result["counts"]["existing_receipts"], 1)
        self.assertEqual(result["counts"]["delivered"], 0)

    def test_delivery_with_failed_or_interrupted_log_is_not_reported_complete(self):
        self.request("one")
        self.fetch.return_value = compare([(PREFIX + "one.json", "added")])
        for log_status in ("failed", None):
            with self.subTest(log_status=log_status):
                receipt = {"status": "delivered"}
                if log_status is not None:
                    receipt["log_status"] = log_status
                self.process.return_value = receipt
                result = self.run_push()
                self.assertEqual(result["status"], "failed")
                self.assertEqual(result["counts"]["delivered"], 1)
                self.assertEqual(result["counts"]["continuity_failures"], 1)

    def test_existing_delivery_with_missing_continuity_fails_without_resending(self):
        self.request("one")
        receipt_file = self.root / "channels/tarik-cloud/receipts/one.json"
        receipt_file.parent.mkdir(parents=True)
        self.fetch.return_value = compare([(PREFIX + "one.json", "added")])
        for log_status in ("failed", None):
            with self.subTest(log_status=log_status):
                receipt = {"status": "delivered", "operation": "send_telegram"}
                if log_status is not None:
                    receipt["log_status"] = log_status
                receipt_file.write_text(json.dumps(receipt))
                with mock.patch.object(runner.worker, "_telegram", side_effect=AssertionError("Must not resend")) as telegram:
                    result = self.run_push(process_request=runner.worker.process_request)
                telegram.assert_not_called()
                self.assertEqual(result["status"], "failed")
                self.assertEqual(result["counts"]["existing_receipts"], 1)
                self.assertEqual(result["counts"]["delivered"], 0)
                self.assertEqual(result["counts"]["continuity_failures"], 1)

    def test_symlink_request_or_receipt_storage_refused(self):
        path = self.request("one")
        self.fetch.return_value = compare([(PREFIX + "one.json", "added")])
        saved = self.root / "saved.json"
        path.rename(saved)
        path.symlink_to(saved)
        self.assertEqual(self.run_push()["reason"], "unsafe_storage")
        self.process.assert_not_called()
        path.unlink()
        saved.rename(path)
        target = self.root / "receipt-target"
        target.mkdir()
        (self.root / "channels/tarik-cloud/receipts").symlink_to(target, target_is_directory=True)
        self.assertEqual(self.run_push()["reason"], "unsafe_storage")
        self.process.assert_not_called()

    def test_api_and_worker_errors_are_classified_without_raw_messages(self):
        self.fetch.side_effect = RuntimeError("leaked-token-BODY")
        result = self.run_push()
        self.assertEqual(result["reason"], "compare_unavailable")
        self.assertNotIn("leaked-token-BODY", json.dumps(result))
        self.fetch.side_effect = None
        self.fetch.return_value = compare([(PREFIX + "one.json", "added")])
        self.request("one")
        self.process.side_effect = RuntimeError("leaked-token-BODY")
        result = self.run_push()
        self.assertEqual(result["reason"], "worker_unavailable")
        self.assertNotIn("leaked-token-BODY", json.dumps(result))

    def test_uncertain_delivery_fails_safely(self):
        self.request("one")
        self.fetch.return_value = compare([(PREFIX + "one.json", "added")])
        self.process.return_value = {"status": "uncertain", "reason": "delivery_unknown"}
        result = self.run_push()
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["counts"]["uncertain"], 1)

    def test_fetch_compare_uses_fixed_get_and_bounded_response(self):
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(compare()).encode()
        with mock.patch.object(runner.urllib.request, "urlopen", return_value=response) as opener:
            self.assertEqual(runner.fetch_compare(BEFORE, AFTER, ENV["GITHUB_TOKEN"]), compare())
        request = opener.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.full_url,
                         f"https://api.github.com/repos/{runner.REPOSITORY}/compare/{BEFORE}...{AFTER}")
        response.__enter__.return_value.read.assert_called_once_with(runner.MAX_API_BYTES + 1)

    def test_main_reads_event_file_and_prints_only_classified_result(self):
        event_path = self.root / "event.json"
        event_path.write_text(json.dumps(EVENT))
        stdout = io.StringIO()
        with mock.patch.dict(runner.os.environ, dict(ENV, GITHUB_EVENT_PATH=str(event_path)), clear=True), \
                mock.patch.object(runner, "fetch_compare", return_value=compare()), \
                contextlib.redirect_stdout(stdout):
            code = runner.main(["--repo-root", str(self.root)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["counts"]["processed"], 0)
        self.assertNotIn(ENV["GITHUB_TOKEN"], stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
