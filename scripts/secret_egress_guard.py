#!/usr/bin/env python3
"""Detect exact secret-like environment values before autonomous artifacts publish.

This guard is deliberately simple: collect process environment values whose names
look secret-bearing, then byte-scan worker logs, checker artifacts, changed
repository files, Goose transcripts, and session databases for those exact
values. It never records a secret value in its report. When requested it replaces
matching bytes in the files it scans so a failed run's uploaded diagnostics do
not become the leak.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable, NamedTuple
import re
import subprocess

SECRET_NAME = re.compile(
    r"(API_?KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|PRIVATE_?KEY|ACCESS_?KEY|AUTH)",
    re.I,
)
MIN_SECRET_LENGTH = 8
REDACTION_PREFIX = b"[REDACTED "


class SecretValue(NamedTuple):
    name: str
    value: bytes


def looks_secret_name(name: str) -> bool:
    return bool(SECRET_NAME.search(name))


def collect_secret_values(env: dict[str, str] | None = None) -> list[SecretValue]:
    """Return exact environment values worth guarding, without duplicates.

    Short flags and placeholders are ignored to avoid turning ordinary words such
    as "true" or "local" into false-positive blockers.
    """
    source = os.environ if env is None else env
    values: list[SecretValue] = []
    seen: set[bytes] = set()
    for name, value in sorted(source.items()):
        if not looks_secret_name(name):
            continue
        if not value or len(value) < MIN_SECRET_LENGTH:
            continue
        if value.lower() in {"true", "false", "none", "null", "undefined", "changeme", "test"}:
            continue
        raw = value.encode("utf-8", errors="surrogateescape")
        if raw in seen:
            continue
        seen.add(raw)
        values.append(SecretValue(name=name, value=raw))
    return values


def sanitized_environment(env: dict[str, str] | None = None) -> dict[str, str]:
    """Return env with secret-looking variables removed for deterministic tools."""
    source = os.environ if env is None else env
    return {k: v for k, v in source.items() if not looks_secret_name(k)}


def _redaction(name: str) -> bytes:
    safe = re.sub(r"[^A-Za-z0-9_:-]", "_", name).encode("ascii", errors="ignore")
    return REDACTION_PREFIX + safe + b"]"


def iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for root in paths:
        if not root.exists():
            continue
        if root.is_file():
            yield root
            continue
        if root.is_dir():
            for path in root.rglob("*"):
                if ".git" in path.parts:
                    continue
                if path.is_file() and not path.is_symlink():
                    yield path


def _git_bytes(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.DEVNULL)


def changed_repository_paths(repo: Path, base: str | None = None) -> list[Path]:
    """Files a worker could publish, plus common local transcript/session files."""
    names: set[str] = set()
    try:
        if base:
            diff = _git_bytes(repo, "diff", "--no-ext-diff", "--no-textconv", "--name-only", "-z", base, "--")
        else:
            diff = _git_bytes(repo, "diff", "--no-ext-diff", "--no-textconv", "--name-only", "-z", "--")
        names.update(p.decode("utf-8", errors="surrogateescape") for p in diff.split(b"\0") if p)
        others = _git_bytes(repo, "ls-files", "--others", "--exclude-standard", "-z")
        names.update(p.decode("utf-8", errors="surrogateescape") for p in others.split(b"\0") if p)
    except (OSError, subprocess.CalledProcessError):
        pass

    paths = [repo / name for name in sorted(names)]
    # Goose transcripts and session databases are often ignored/untracked, so
    # include them explicitly even when git would not list them for publication.
    for extra in (repo / ".goose", repo / "sessions.db"):
        if extra.exists():
            paths.append(extra)
    for db in repo.glob("**/sessions.db"):
        if ".git" not in db.parts and db not in paths:
            paths.append(db)
    return paths


def scan_files(paths: Iterable[Path], secrets: list[SecretValue], *, redact: bool = False,
               label: str = "file", root: Path | None = None) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    if not secrets:
        return findings
    for path in iter_files(paths):
        try:
            data = path.read_bytes()
        except OSError:
            continue
        matched = [secret for secret in secrets if secret.value in data]
        if not matched:
            continue
        rel = str(path)
        if root is not None:
            try:
                rel = str(path.resolve().relative_to(root.resolve()))
            except ValueError:
                rel = str(path)
        findings.append({
            "scope": label,
            "path": rel,
            "env_names": [secret.name for secret in matched],
        })
        if redact:
            redacted = data
            for secret in matched:
                redacted = redacted.replace(secret.value, _redaction(secret.name))
            try:
                path.write_bytes(redacted)
            except OSError:
                pass
    return findings


def scan_run(repo: Path, artifacts: Path, base: str | None = None, *,
             env: dict[str, str] | None = None, redact: bool = True) -> dict[str, object]:
    """Scan one autonomous run boundary and return a secret-free report."""
    repo = repo.resolve()
    artifacts = artifacts.resolve()
    secrets = collect_secret_values(env)
    artifact_findings = scan_files([artifacts], secrets, redact=redact, label="artifact", root=artifacts)
    repo_findings = scan_files(changed_repository_paths(repo, base), secrets, redact=redact,
                               label="repository", root=repo)
    findings = artifact_findings + repo_findings
    return {
        "ok": not findings,
        "secret_value_count": len(secrets),
        "finding_count": len(findings),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--base")
    parser.add_argument("--no-redact", action="store_true")
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    report = scan_run(Path(args.repo), Path(args.artifacts), args.base, redact=not args.no_redact)
    text = json.dumps(report, indent=2) + "\n"
    if args.report:
        Path(args.report).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
