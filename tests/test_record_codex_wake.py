"""Offline integration checks against the commons' actual item-ledger module."""
import datetime as dt
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


recorder = module_at("record_codex_wake", ROOT / "scripts/record_codex_wake.py")
ledger = module_at("actual_item_ledger", Path(os.environ.get("TARIK_TEST_LEDGER_SOURCE", ROOT / "channels/item_ledger.py")))


class CodexWakeRecordTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.repo = Path(folder.name)
        self.ledger_path = self.repo / "channels/items.jsonl"
        self.ledger_path.parent.mkdir()
        self.old = {"id": "20261016T120000Z-deadbeef", "filed_utc": "2026-10-16T12:01:00Z",
                    "amigo": "tarik", "scope": "internal", "paths": ["scripts/old.py"],
                    "title": "Earlier Goose work", "state": "accomplished", "reviewer": "desi"}
        self.prefix = (json.dumps(self.old) + "\n").encode()
        self.ledger_path.write_bytes(self.prefix)
        self.verifier = mock.Mock(side_effect=self.publication)
        blocker = mock.patch("socket.create_connection", side_effect=AssertionError("No network in offline tests"))
        blocker.start()
        self.addCleanup(blocker.stop)

    def manifest(self, **updates):
        manifest = {"run_id": "codex-20261016T120000Z-deadbeef",
                    "started_utc": "2026-10-16T12:00:00Z", "artifact_commit": "a" * 40,
                    "artifact_paths": ["scripts/real_improvement.py"],
                    "title": "Published a real implementation improvement",
                    "validation": "Offline behavior tests passed; resulting published diff inspected."}
        manifest.update(updates)
        return manifest

    def publication(self, sha):
        return {"sha": sha, "default_branch": "main", "on_default_branch": True,
                "message": "land(wake): Codex work from run codex-20261016T120000Z-deadbeef",
                "files": [{"filename": "scripts/real_improvement.py", "status": "modified", "changes": 9}]}

    def record(self, manifest=None, **kwargs):
        options = dict(verify_commit=self.verifier, ledger=ledger,
                       now=dt.datetime(2026, 10, 16, 12, 5, tzinfo=dt.timezone.utc))
        options.update(kwargs)
        return recorder.record_wake(manifest or self.manifest(), self.repo, **options)

    def test_verified_codex_work_enters_existing_tariks_counts_as_waiting(self):
        result = self.record()
        self.assertEqual(result["status"], "recorded")
        self.verifier.assert_called_once_with("a" * 40)
        items = ledger.load(self.ledger_path)
        self.assertEqual(len(items), 2)
        row = items[self.manifest()["run_id"]]
        self.assertEqual(row["amigo"], "tarik")
        self.assertEqual(row["platform"], "codex")
        self.assertEqual(row["source"], "codex")
        self.assertEqual(row["artifact_commit"], "a" * 40)
        self.assertEqual(row["filed_utc"], "2026-10-16T12:05:00Z")
        self.assertEqual(row["validation"], self.manifest()["validation"])
        self.assertIsNone(row["state"])
        self.assertIsNone(row["reviewer"])
        self.assertIsNone(row["cost_usd"])
        self.assertEqual(ledger.letter_for(row), "W")
        totals = ledger.counts(items)
        self.assertEqual(totals["V"]["by_amigo"]["tarik"]["total"], 2)
        self.assertEqual(totals["W"]["by_amigo"]["tarik"]["total"], 1)
        self.assertEqual(totals["A"]["by_amigo"]["tarik"]["total"], 1)
        self.assertTrue(self.ledger_path.read_bytes().startswith(self.prefix))
        self.assertEqual(items[self.old["id"]], self.old)

    def test_retry_does_not_append_or_reverify_or_undo_later_review(self):
        self.record()
        reviewed = dict(ledger.load(self.ledger_path)[self.manifest()["run_id"]],
                        state="postponed", reason="Independent review deferred integration", reviewer="desi")
        ledger.append([reviewed], self.ledger_path)
        before = self.ledger_path.read_bytes()
        second = self.record()
        self.assertEqual(second["status"], "already_recorded")
        self.assertEqual(second["item"], reviewed)
        self.assertEqual(self.verifier.call_count, 1)
        self.assertEqual(self.ledger_path.read_bytes(), before)

    def test_same_native_timestamp_and_suffix_cannot_collide_with_goose(self):
        self.record()
        items = ledger.load(self.ledger_path)
        self.assertIn("20261016T120000Z-deadbeef", items)
        self.assertIn("codex-20261016T120000Z-deadbeef", items)
        with mock.patch.object(ledger, "HOME", self.repo / "empty-home"), \
                mock.patch.object(ledger, "landed_run_ids", return_value=set()):
            ledger.collect(path=self.ledger_path, amigo="tarik")
        self.assertEqual(len(ledger.load(self.ledger_path)), 2)
        self.assertEqual(ledger.load(self.ledger_path)[self.old["id"]], self.old)

    def test_one_artifact_cannot_be_recounted_under_another_run_id(self):
        self.record()
        before = self.ledger_path.read_bytes()
        with self.assertRaises(ValueError):
            self.record(self.manifest(run_id="codex-20261016T120000Z-12345678"))
        self.assertEqual(self.ledger_path.read_bytes(), before)

    def test_existing_run_cannot_be_reassigned_to_different_evidence(self):
        self.record()
        before = self.ledger_path.read_bytes()
        with self.assertRaises(ValueError):
            self.record(self.manifest(artifact_commit="b" * 40))
        self.assertEqual(self.ledger_path.read_bytes(), before)

    def test_unpublished_or_mismatched_commit_cannot_create_a_row(self):
        base = self.publication("a" * 40)
        variations = [{"on_default_branch": False}, {"sha": "b" * 40}, {"default_branch": ""},
                      {"message": "A report saying the work is done"},
                      {"message": "land(wake): Codex work from run codex-20261016T120000Z-12345678"}]
        for variation in variations:
            with self.subTest(variation=variation), self.assertRaises(ValueError):
                self.record(verify_commit=lambda sha: dict(base, **variation))
        self.assertEqual(self.ledger_path.read_bytes(), self.prefix)

    def test_claimed_artifact_must_be_an_actual_nonempty_published_change(self):
        for files in ([], [{"filename": "other.py", "status": "added", "changes": 8}],
                      [{"filename": "scripts/real_improvement.py", "status": "modified", "changes": 0}],
                      [{"filename": "scripts/real_improvement.py", "status": "unchanged", "changes": 8}]):
            with self.subTest(files=files), self.assertRaises(ValueError):
                self.record(verify_commit=lambda sha: dict(self.publication(sha), files=files))
        self.assertEqual(self.ledger_path.read_bytes(), self.prefix)

    def test_verified_substantive_removal_counts_as_work_awaiting_review(self):
        path = "scripts/obsolete_implementation.py"
        evidence = self.publication("a" * 40)
        evidence["files"] = [{"filename": path, "status": "removed", "changes": 20}]
        result = self.record(self.manifest(artifact_paths=[path], title="Removed obsolete implementation"),
                             verify_commit=lambda sha: evidence)
        self.assertEqual(result["status"], "recorded")
        self.assertEqual(result["item"]["paths"], [path])
        self.assertEqual(ledger.letter_for(result["item"]), "W")
        self.assertTrue(self.ledger_path.read_bytes().startswith(self.prefix))

    def test_reports_handoffs_and_codex_metadata_cannot_count_as_work(self):
        for path in ("channels/conversation/tarik.md", "channels/items.jsonl",
                     "channels/reports/codex-report.md", "channels/tarik-codex/state.json",
                     "channels/codex/wakes/one.json", "channels/handoffs/task.md",
                     "governance/tarik-codex-wakes.md", "notes/wake-report.txt"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.record(self.manifest(artifact_paths=[path]))
        self.verifier.assert_not_called()
        self.assertEqual(self.ledger_path.read_bytes(), self.prefix)

    def test_actual_codex_report_and_claim_paths_cannot_count_as_artifacts(self):
        run_id = self.manifest()["run_id"]
        paths = ["channels/tarik-codex-wakes/" + run_id + ".json",
                 "channels/tarik-codex-wakes/claims/" + run_id + ".json",
                 "channels/tarik-goose-results/" + run_id + ".json"]
        for candidate in ([path] for path in paths):
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                self.record(self.manifest(artifact_paths=candidate))
        with self.assertRaises(ValueError):
            self.record(self.manifest(artifact_paths=paths))
        self.verifier.assert_not_called()
        self.assertEqual(self.ledger_path.read_bytes(), self.prefix)

    def test_empty_artifact_or_unsupported_claim_fields_fail_before_verification(self):
        for change in ({"artifact_paths": []}, {"artifact_commit": ""}, {"validation": ""},
                       {"artifact_paths": ["../outside"]}, {"state": "accomplished"},
                       {"started_utc": "2026-10-16T11:00:00Z"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.record(self.manifest(**change))
        self.verifier.assert_not_called()
        self.assertEqual(self.ledger_path.read_bytes(), self.prefix)

    def test_generated_index_cannot_count_as_reviewable_artifact(self):
        artifact = self.repo / "scripts/real_improvement.py"
        artifact.parent.mkdir()
        artifact.write_text("# GENERATED. DO NOT EDIT.\n")
        with self.assertRaises(ValueError):
            self.record()
        self.assertEqual(self.ledger_path.read_bytes(), self.prefix)

    def test_external_scope_uses_existing_ledger_classifier(self):
        path = "docs/new-work.html"
        evidence = self.publication("a" * 40)
        evidence["files"] = [{"filename": path, "status": "added", "changes": 10}]
        result = self.record(self.manifest(artifact_paths=[path]), verify_commit=lambda sha: evidence)
        self.assertEqual(result["item"]["scope"], "external")

    def test_publication_verifier_uses_fixed_readonly_public_endpoints(self):
        sha = "a" * 40
        urls = []
        responses = [{"default_branch": "main"},
                     {"sha": sha, "commit": {"message": "commit subject"}, "files": []},
                     {"status": "ahead"}]

        def opener(request, timeout):
            urls.append(request.full_url)
            self.assertEqual(request.get_method(), "GET")
            self.assertIsNone(request.get_header("Authorization"))
            return io.BytesIO(json.dumps(responses[len(urls) - 1]).encode())

        result = recorder.verify_publication(sha, opener=opener)
        base = "https://api.github.com/repos/LindsayRidgeway/llm-symposium"
        self.assertEqual(urls, [base, base + "/commits/" + sha, base + "/compare/" + sha + "...main"])
        self.assertTrue(result["on_default_branch"])

    def test_verification_failure_leaves_the_existing_ledger_untouched(self):
        verifier = mock.Mock(side_effect=RuntimeError("verification unavailable"))
        with self.assertRaises(RuntimeError):
            self.record(verify_commit=verifier)
        self.assertEqual(self.ledger_path.read_bytes(), self.prefix)


if __name__ == "__main__":
    unittest.main()
