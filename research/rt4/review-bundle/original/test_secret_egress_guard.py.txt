#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("secret_egress_guard", ROOT / "scripts" / "secret_egress_guard.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


class SecretEgressGuardTests(unittest.TestCase):
    def test_collects_only_secret_named_values(self):
        env = {
            "OPENAI_API_KEY": "sk-fake-1234567890",
            "PATH": "/usr/bin:/bin",
            "DEBUG_TOKEN": "short",
            "SYMPOSIUM_MAIL_APP_PASSWORD_TARIK": "mail-fake-abcdef",
        }
        got = guard.collect_secret_values(env)
        self.assertEqual([item.name for item in got], ["OPENAI_API_KEY", "SYMPOSIUM_MAIL_APP_PASSWORD_TARIK"])
        self.assertEqual({item.value for item in got}, {b"sk-fake-1234567890", b"mail-fake-abcdef"})

    def test_sanitized_environment_removes_secret_like_keys(self):
        env = {
            "OPENAI_API_KEY": "sk-fake-1234567890",
            "PUSH_TOKEN": "ghp_fake_1234567890",
            "PATH": "/usr/bin:/bin",
            "GOOSE_PROVIDER": "openai",
        }
        self.assertEqual(guard.sanitized_environment(env), {"PATH": "/usr/bin:/bin", "GOOSE_PROVIDER": "openai"})

    def test_scan_redacts_artifact_and_changed_repository_file_without_reporting_secret(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            artifacts = root / "artifacts"
            repo.mkdir()
            artifacts.mkdir()
            subprocess.check_call(["git", "init", "-q"], cwd=repo)
            subprocess.check_call(["git", "config", "user.name", "Fixture"], cwd=repo)
            subprocess.check_call(["git", "config", "user.email", "fixture@example.invalid"], cwd=repo)
            (repo / "README.md").write_text("# base\n", encoding="utf-8")
            subprocess.check_call(["git", "add", "README.md"], cwd=repo)
            subprocess.check_call(["git", "commit", "-qm", "base"], cwd=repo)
            base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

            secret = "rt4-fake-secret-abcdef123456"
            (repo / "changed.txt").write_text(f"repository leak {secret}\n", encoding="utf-8")
            (repo / ".goose").mkdir()
            (repo / ".goose" / "transcript.jsonl").write_text(f"transcript leak {secret}\n", encoding="utf-8")
            (artifacts / "worker.jsonl").write_text(f"stdout leak {secret}\n", encoding="utf-8")

            report = guard.scan_run(repo, artifacts, base, env={"OPENAI_API_KEY": secret}, redact=True)
            dumped = json.dumps(report)
            self.assertFalse(report["ok"])
            self.assertEqual(report["secret_value_count"], 1)
            self.assertEqual(report["finding_count"], 3)
            self.assertNotIn(secret, dumped)
            self.assertIn("OPENAI_API_KEY", dumped)
            self.assertNotIn(secret, (repo / "changed.txt").read_text(encoding="utf-8"))
            self.assertNotIn(secret, (repo / ".goose" / "transcript.jsonl").read_text(encoding="utf-8"))
            self.assertNotIn(secret, (artifacts / "worker.jsonl").read_text(encoding="utf-8"))

    def test_main_returns_failure_and_writes_secret_free_report(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            artifacts = root / "artifacts"
            repo.mkdir()
            artifacts.mkdir()
            subprocess.check_call(["git", "init", "-q"], cwd=repo)
            subprocess.check_call(["git", "config", "user.name", "Fixture"], cwd=repo)
            subprocess.check_call(["git", "config", "user.email", "fixture@example.invalid"], cwd=repo)
            (repo / "README.md").write_text("# base\n", encoding="utf-8")
            subprocess.check_call(["git", "add", "README.md"], cwd=repo)
            subprocess.check_call(["git", "commit", "-qm", "base"], cwd=repo)
            base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            secret = "rt4-fake-secret-cli-abcdef"
            (artifacts / "log.txt").write_text(secret, encoding="utf-8")
            report = root / "report.json"
            from unittest import mock
            with mock.patch.dict("os.environ", {"OPENAI_API_KEY": secret}, clear=True):
                code = guard.main(["--repo", str(repo), "--artifacts", str(artifacts), "--base", base, "--report", str(report)])
            self.assertEqual(code, 1)
            text = report.read_text(encoding="utf-8")
            self.assertNotIn(secret, text)
            self.assertNotIn(secret, (artifacts / "log.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
