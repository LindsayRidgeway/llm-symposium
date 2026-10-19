#!/usr/bin/env python3
"""Tests for the pre-delivery secret-egress scanner (RT-4's mechanical boundary).

Registered in `.github/workflows/test-and-report.yml`; run directly with
`python3 tests/test_secret_egress_scan.py`.

The point of these tests is not that a substring search works. It is that the
scanner reports a leak **without reproducing it**: every assertion about a
finding is paired with an assertion that the secret itself is absent from the
output. A scanner that seals the repository and posts the key in the failure
message is a worse outcome than no scanner.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.secret_egress_scan import (  # noqa: E402
    MIN_SECRET_LEN,
    fingerprint,
    load_ignores,
    scan_paths,
    secret_values,
)

SCRIPT = REPO_ROOT / "scripts" / "secret_egress_scan.py"

FAKE_SECRET = "rt4-fake-provider-key-9c31ab7e"


def _armed(**values: str) -> dict[str, str]:
    return secret_values(tuple(values), environ=values)


class SecretValuesTests(unittest.TestCase):
    def test_short_values_are_not_armed(self) -> None:
        """A two-letter env value would match ordinary prose everywhere."""
        armed = _armed(SHORT="abc")
        self.assertEqual(armed, {})

    def test_placeholder_values_are_not_armed(self) -> None:
        self.assertEqual(_armed(OPENAI_API_KEY="changeme"), {})
        self.assertEqual(_armed(OPENAI_API_KEY="  SECRET  "), {})

    def test_real_value_is_armed_and_stripped(self) -> None:
        armed = _armed(OPENAI_API_KEY=f"  {FAKE_SECRET}\n")
        self.assertEqual(armed, {"OPENAI_API_KEY": FAKE_SECRET})

    def test_length_floor_is_the_documented_one(self) -> None:
        self.assertGreaterEqual(MIN_SECRET_LEN, 8)


class ScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_clean_tree_reports_nothing(self) -> None:
        self._write("docs/clean.md", "Nothing to see here.\n")
        report = scan_paths([self.root], _armed(OPENAI_API_KEY=FAKE_SECRET), root=self.root)
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["scanned"], 1)
        self.assertEqual(report["errors"], [])

    def test_exact_env_value_is_found_with_the_right_line(self) -> None:
        self._write("channels/draft.md", "line one\nline two\nkey=" + FAKE_SECRET + "\n")
        report = scan_paths([self.root], _armed(OPENAI_API_KEY=FAKE_SECRET), root=self.root)
        self.assertEqual(len(report["findings"]), 1)
        finding = report["findings"][0]
        self.assertEqual(finding["kind"], "env-value")
        self.assertEqual(finding["detector"], "OPENAI_API_KEY")
        self.assertEqual(finding["line"], 3)
        self.assertEqual(finding["file"], "channels/draft.md")
        self.assertEqual(finding["fingerprint"], fingerprint(FAKE_SECRET.encode()))

    def test_finding_never_contains_the_secret(self) -> None:
        """The report is one step from a public log; it must not carry the value."""
        self._write("artifact.txt", FAKE_SECRET + "\n")
        report = scan_paths([self.root], _armed(TELEGRAM_BOT_TOKEN=FAKE_SECRET), root=self.root)
        serialized = json.dumps(report)
        self.assertNotIn(FAKE_SECRET, serialized)

    def test_fingerprint_is_not_reversible_and_is_stable(self) -> None:
        fp = fingerprint(FAKE_SECRET.encode())
        self.assertEqual(len(fp), 12)
        self.assertNotIn(FAKE_SECRET[:4], fp.replace(FAKE_SECRET[:4], ""))  # not a substring leak
        self.assertEqual(fp, fingerprint(FAKE_SECRET.encode()))
        self.assertNotEqual(fp, fingerprint((FAKE_SECRET + "x").encode()))

    def test_binary_files_are_skipped_and_counted(self) -> None:
        """sessions.db is the case RT-4 measured; a NUL byte must not be a clean bill."""
        (self.root / "sessions.db").write_bytes(b"SQLite format 3\x00" + FAKE_SECRET.encode())
        report = scan_paths([self.root], _armed(OPENAI_API_KEY=FAKE_SECRET), root=self.root)
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["skipped_binary"], ["sessions.db"])

    def test_skip_dirs_are_not_walked(self) -> None:
        self._write(".git/config", FAKE_SECRET + "\n")
        self._write("keep.md", "fine\n")
        report = scan_paths([self.root], _armed(OPENAI_API_KEY=FAKE_SECRET), root=self.root)
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["scanned"], 1)

    def test_credential_shape_is_found_without_an_armed_variable(self) -> None:
        """A secret that was never in this process's environment is still a leak."""
        # 36 characters after the prefix: the pattern is deliberately exact, so a
        # 34-character string is not matched. That is the cost of near-zero false
        # positives and it is asserted here rather than left implicit.
        self._write("notes.md", "token: ghp_" + "a1b2c3d4" * 4 + "e5f6\n")
        report = scan_paths([self.root], {}, root=self.root)
        self.assertEqual(len(report["findings"]), 1)
        self.assertEqual(report["findings"][0]["kind"], "pattern")
        self.assertEqual(report["findings"][0]["detector"], "github-classic-pat")

    def test_private_key_header_is_found(self) -> None:
        self._write("id.txt", "-----BEGIN OPENSSH PRIVATE KEY-----\n")
        report = scan_paths([self.root], {}, root=self.root)
        self.assertEqual([f["detector"] for f in report["findings"]], ["pem-private-key"])

    def test_prose_mentioning_the_variable_name_is_not_a_finding(self) -> None:
        self._write("doc.md", "Set OPENAI_API_KEY before running. Do not commit it.\n")
        report = scan_paths([self.root], _armed(OPENAI_API_KEY=FAKE_SECRET), root=self.root)
        self.assertEqual(report["findings"], [])

    def test_missing_path_is_an_error_not_a_pass(self) -> None:
        report = scan_paths([self.root / "does-not-exist"], {}, root=self.root)
        self.assertEqual(report["findings"], [])
        self.assertTrue(report["errors"])
        self.assertIn("no such path", report["errors"][0])


class CommandLineTests(unittest.TestCase):
    """End-to-end: exit codes are the contract the landing step will read."""

    def _run(self, args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        base_env = {k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
        if env:
            base_env.update(env)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=base_env,
            check=False,
        )

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_exit_1_on_finding_and_the_secret_stays_out_of_stdout_and_stderr(self) -> None:
        (self.root / "leak.md").write_text("k=" + FAKE_SECRET + "\n", encoding="utf-8")
        proc = self._run([str(self.root)], env={"OPENAI_API_KEY": FAKE_SECRET})
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertNotIn(FAKE_SECRET, proc.stdout)
        self.assertNotIn(FAKE_SECRET, proc.stderr)
        self.assertIn("OPENAI_API_KEY", proc.stdout)
        self.assertIn("do not deliver", proc.stdout)

    def test_exit_0_when_clean(self) -> None:
        (self.root / "clean.md").write_text("ordinary text\n", encoding="utf-8")
        proc = self._run([str(self.root)])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("CLEAN", proc.stdout)

    def test_json_mode_is_parseable_and_says_what_was_armed(self) -> None:
        (self.root / "clean.md").write_text("ordinary text\n", encoding="utf-8")
        proc = self._run(["--json", str(self.root)], env={"DEEPSEEK_API_KEY": FAKE_SECRET})
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["armed"], ["DEEPSEEK_API_KEY"])
        self.assertEqual(payload["findings"], [])
        self.assertEqual(payload["scanned"], 1)

    def test_unarmed_scan_says_so_rather_than_reporting_a_clean_bill(self) -> None:
        """Zero findings with zero armed variables is a much weaker sentence."""
        (self.root / "clean.md").write_text("ordinary text\n", encoding="utf-8")
        proc = self._run([str(self.root)])
        self.assertIn("no environment secret was armed", proc.stdout)

    def test_exit_2_when_nothing_to_scan(self) -> None:
        proc = self._run([])
        self.assertEqual(proc.returncode, 2)


class IgnoreFileTests(unittest.TestCase):
    """A suppression is only acceptable if it carries a written reason."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "fixture.md").write_text("-----BEGIN RSA PRIVATE KEY-----" + "\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_suppression_with_a_reason_removes_the_finding_and_keeps_the_reason(self) -> None:
        ignore_file = self.root / ".secret-egress-ignore"
        ignore_file.write_text(
            "pem-private-key fixture.md  # fixture: asserts detection, holds no key material\n",
            encoding="utf-8",
        )
        entries, errors = load_ignores(ignore_file)
        self.assertEqual(errors, [])
        report = scan_paths([self.root], {}, root=self.root, ignores=entries)
        self.assertEqual(report["findings"], [])
        self.assertEqual(len(report["suppressed"]), 1)
        self.assertIn("fixture", report["suppressed"][0]["reason"])

    def test_suppression_without_a_reason_is_an_error_not_a_pass(self) -> None:
        ignore_file = self.root / ".secret-egress-ignore"
        ignore_file.write_text("pem-private-key fixture.md\n", encoding="utf-8")
        entries, errors = load_ignores(ignore_file)
        self.assertEqual(entries, [])
        self.assertTrue(errors)
        self.assertIn("without a reason", errors[0])

    def test_absent_ignore_file_is_not_an_error(self) -> None:
        entries, errors = load_ignores(self.root / "nothing-here")
        self.assertEqual((entries, errors), ([], []))


if __name__ == "__main__":
    unittest.main(verbosity=2)
