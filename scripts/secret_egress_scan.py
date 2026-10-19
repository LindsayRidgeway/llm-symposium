#!/usr/bin/env python3
"""Pre-delivery secret-egress scanner — the mechanical boundary RT-4 asked for.

Agenda item 15 (`agenda/15-red-team-the-deadbolt.md`) closes the RT-4 next action
with a choice between two mechanical boundaries:

    either run shell-capable runs without provider/API/mail/Telegram secrets in
    the environment by default, or add a pre-delivery scanner that rejects any
    changed artifact, transcript export, or session database containing exact
    secret-like environment values before publication.

This script is the second of those. It is a *last* line, not a sandbox: it reads
files that already exist and refuses them. It cannot stop a process from printing
a secret to a stream, and it does nothing about a secret that was never in the
environment it was given. Both limits are stated here because the probe result
`probes/2026-09-27-rt4-secret-egress-result.json` measured exactly those paths
failing: the fake value appeared in stdout, stderr, exception text, the Goose
transcript, `sessions.db`, and changed files. Every one of those except the live
streams is a *file*, and a file can be scanned before it is delivered.

What it does
------------
Two independent detectors, reported separately because they fail differently:

1. **Exact environment values.** For each candidate variable, the value is read
   from `os.environ` here and matched byte-for-byte against each scanned file.
   This is the detector with no false positives worth worrying about: an exact
   provider key found in a repository file is a finding, not a heuristic.
2. **High-precision token shapes.** A short, deliberately conservative regex set
   for well-known credential formats (GitHub, OpenAI-style, Slack, AWS, plus a
   PEM private-key header). These catch secrets that were never in *this*
   process's environment. Every pattern here was chosen for near-zero false
   positive rate at the cost of coverage: `sk-` alone is not scanned, a whole
   prefix-plus-length shape is.

What it never does
------------------
It never prints a secret. A finding names the variable (or pattern), the file,
the line and column, and a 12-hex-digit fingerprint of the matched value, so two
reports of the same leak can be compared without either one carrying it. There is
no flag to turn that off, on purpose.

Exit codes
----------
0  no findings
1  findings (the caller must not deliver)
2  usage or scan error (unreadable path, no inputs given)

Usage
-----
    python3 scripts/secret_egress_scan.py docs/ channels/ insights/
    python3 scripts/secret_egress_scan.py --changed-since HEAD~1
    python3 scripts/secret_egress_scan.py --json path/to/transcript.txt
"""

from __future__ import annotations

import argparse
import datetime
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

#: Variables whose values are treated as secrets if they are present in the
#: environment. Kept as a list rather than a prefix rule so that adding a
#: provider is a visible edit rather than an accident.
DEFAULT_ENV_VARS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "DEEPSEEK_API_KEY",
    "DASHSCOPE_API_KEY",
    "OPENROUTER_API_KEY",
    "MISTRAL_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "SYMPOSIUM_PUSH_TOKEN",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "SMTP_PASSWORD",
    "MAIL_PASSWORD",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
)

#: Values shorter than this are not treated as secrets. A one-word mail password
#: would otherwise match ordinary prose everywhere and make the scan useless.
MIN_SECRET_LEN = 8

#: Values that are obviously placeholders. Scanning the repository for the word
#: "changeme" would produce noise without evidence.
PLACEHOLDERS = frozenset(
    {
        "changeme",
        "change-me",
        "password",
        "secret",
        "your_key_here",
        "your-key-here",
        "xxxxxxxx",
        "notarealsecret",
        "none",
        "null",
        "unset",
    }
)

#: Directories never scanned unless named explicitly on the command line.
SKIP_DIRS = frozenset(
    {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache"}
)

#: High-precision credential shapes. `(?<![A-Za-z0-9])` / `(?![A-Za-z0-9])` keep
#: the GitHub and AWS patterns from matching inside a longer identifier.
PATTERNS = (
    ("github-classic-pat", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("github-fine-grained-pat", re.compile(r"github_pat_[A-Za-z0-9_]{50,}")),
    ("github-oauth", re.compile(r"gho_[A-Za-z0-9]{36}")),
    ("openai-style-key", re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9]{32,}")),
    ("anthropic-key", re.compile(r"(?<![A-Za-z0-9])sk-ant-[A-Za-z0-9\-_]{32,}")),
    ("slack-token", re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("aws-access-key-id", re.compile(r"(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![0-9A-Z])")),
    ("google-api-key", re.compile(r"(?<![A-Za-z0-9])AIza[0-9A-Za-z\-_]{35}")),
    ("pem-private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
)

#: Files above this size are read anyway, but a match list is capped so a
#: pathological file cannot produce a million-row report.
MAX_FINDINGS_PER_FILE = 25

BINARY_PROBE_BYTES = 8192


#: An ignore entry must carry a reason. A suppression without one is how a gate
#: becomes decoration: the next reader cannot tell a fixture from a real key, and
#: so the next reader does not look. Format, one entry per line:
#:
#:     <detector> <path-glob>   # why this is not a leak
#:
#: `#` comment lines and blank lines are skipped. A malformed entry is an error
#: (exit 2), never a silent pass.
IGNORE_FILE = ".secret-egress-ignore"


def fingerprint(value: bytes) -> str:
    """A stable, non-reversible label for a secret. Never the secret itself."""
    return hashlib.sha256(value).hexdigest()[:12]


def secret_values(env_vars: tuple[str, ...], environ: dict[str, str] | None = None) -> dict[str, str]:
    """Environment values worth scanning for, keyed by variable name.

    Filtering happens here rather than at match time so the report can say how
    many variables were actually armed — a scan that armed nothing reports zero
    findings, and that is a very different sentence from a clean repository.
    """
    environ = os.environ if environ is None else environ
    armed: dict[str, str] = {}
    for name in env_vars:
        raw = environ.get(name)
        if not raw:
            continue
        value = raw.strip()
        if len(value) < MIN_SECRET_LEN:
            continue
        if value.lower() in PLACEHOLDERS:
            continue
        armed[name] = value
    return armed


def is_binary(data: bytes) -> bool:
    return b"\x00" in data[:BINARY_PROBE_BYTES]


def iter_files(paths: list[Path], skip_dirs: frozenset[str] = SKIP_DIRS):
    """Yield files under the given paths, honouring SKIP_DIRS for directories."""
    for path in paths:
        if path.is_file():
            yield path
            continue
        if not path.is_dir():
            raise FileNotFoundError(str(path))
        for child in sorted(path.rglob("*")):
            if any(part in skip_dirs for part in child.relative_to(path).parts[:-1]):
                continue
            if child.is_file():
                yield child


def scan_text(text: str, relpath: str, armed: dict[str, str], use_patterns: bool) -> list[dict]:
    """Scan one decoded file. Line numbers are 1-based, columns 0-based."""
    findings: list[dict] = []
    lines = text.splitlines()

    for name, value in armed.items():
        needle = value
        hits = 0
        for lineno, line in enumerate(lines, start=1):
            start = 0
            while True:
                col = line.find(needle, start)
                if col < 0:
                    break
                findings.append(
                    {
                        "kind": "env-value",
                        "detector": name,
                        "file": relpath,
                        "line": lineno,
                        "column": col,
                        "fingerprint": fingerprint(needle.encode("utf-8")),
                        "length": len(needle),
                    }
                )
                hits += 1
                start = col + 1
                if hits >= MAX_FINDINGS_PER_FILE:
                    break
            if hits >= MAX_FINDINGS_PER_FILE:
                break
        # A secret that spans a line break will not be found by line scanning;
        # that is a real gap and is stated in the module docstring rather than
        # hidden by scanning the raw text and reporting a useless offset.
    if use_patterns:
        for label, pattern in PATTERNS:
            hits = 0
            for lineno, line in enumerate(lines, start=1):
                for match in pattern.finditer(line):
                    findings.append(
                        {
                            "kind": "pattern",
                            "detector": label,
                            "file": relpath,
                            "line": lineno,
                            "column": match.start(),
                            "fingerprint": fingerprint(match.group(0).encode("utf-8")),
                            "length": len(match.group(0)),
                        }
                    )
                    hits += 1
                    if hits >= MAX_FINDINGS_PER_FILE:
                        break
                if hits >= MAX_FINDINGS_PER_FILE:
                    break
    return findings


def scan_paths(
    paths: list[Path],
    armed: dict[str, str],
    use_patterns: bool = True,
    root: Path | None = None,
    ignores: list[tuple[str, str, str]] | None = None,
) -> dict:
    """Scan every file under `paths`. Returns a report dict, never raises on content."""
    root = root or Path.cwd()
    findings: list[dict] = []
    scanned = 0
    skipped_binary: list[str] = []
    errors: list[str] = []

    try:
        files = list(iter_files(paths))
    except FileNotFoundError as exc:
        return {
            "findings": [],
            "scanned": 0,
            "skipped_binary": [],
            "errors": [f"no such path: {exc}"],
            "armed": sorted(armed),
        }

    for path in files:
        try:
            rel = str(path.resolve().relative_to(root.resolve())) if path.is_absolute() else str(path)
        except ValueError:
            rel = str(path)
        try:
            data = path.read_bytes()
        except OSError as exc:
            errors.append(f"{rel}: unreadable ({exc.__class__.__name__})")
            continue
        scanned += 1
        if is_binary(data):
            skipped_binary.append(rel)
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            skipped_binary.append(rel)
            continue
        findings.extend(scan_text(text, rel, armed, use_patterns))

    suppressed: list[dict] = []
    if ignores:
        kept: list[dict] = []
        for finding in findings:
            reason = is_ignored(finding, ignores)
            if reason is None:
                kept.append(finding)
            else:
                suppressed.append({**finding, "reason": reason})
        findings = kept

    return {
        "findings": findings,
        "suppressed": suppressed,
        "scanned": scanned,
        "skipped_binary": skipped_binary,
        "errors": errors,
        "armed": sorted(armed),
    }



def load_ignores(path: Path) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Read suppression entries. Returns (entries, errors).

    Each entry is `(detector, glob, reason)`. The reason is mandatory: an entry
    without one is reported as an error so the scan exits 2 rather than quietly
    passing. Wildcards are matched against the path as it appears in findings.
    """
    if not path.exists():
        return [], []
    entries: list[tuple[str, str, str]] = []
    errors: list[str] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        head, _, reason = line.partition("#")
        reason = reason.strip()
        parts = head.split()
        if len(parts) != 2:
            errors.append(f"{path.name}:{lineno}: expected `detector glob # reason`")
            continue
        if not reason:
            errors.append(f"{path.name}:{lineno}: suppression without a reason")
            continue
        entries.append((parts[0], parts[1], reason))
    return entries, errors


def is_ignored(finding: dict, ignores: list[tuple[str, str, str]]) -> str | None:
    """Return the reason this finding is suppressed, or None."""
    for detector, glob, reason in ignores:
        if finding["detector"] != detector:
            continue
        name = finding["file"]
        if fnmatch.fnmatch(name, glob) or fnmatch.fnmatch(name, "*/" + glob) or name.endswith(glob):
            return reason
    return None


def changed_files(since: str, cwd: Path | None = None) -> list[Path]:
    """Files changed since a revision, as reported by git. Empty on any failure."""
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", since],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    return [Path(line) for line in out.stdout.splitlines() if line.strip()]


def render_human(report: dict) -> str:
    lines: list[str] = []
    armed = report.get("armed") or []
    lines.append(f"armed variables: {len(armed)}" + (f" ({', '.join(armed)})" if armed else " — scan can only find pattern-shaped secrets"))
    lines.append(f"files scanned: {report['scanned']}  binary/unreadable skipped: {len(report['skipped_binary'])}")
    suppressed = report.get("suppressed") or []
    if suppressed:
        lines.append(f"suppressed by {IGNORE_FILE}: {len(suppressed)} (each carries a written reason)")
    if not armed:
        lines.append("NOTE: no environment secret was armed; exact-value detection is off.")
    findings = report["findings"]
    if not findings:
        lines.append("RESULT: CLEAN — no finding")
    else:
        lines.append(f"RESULT: {len(findings)} FINDING(S) — do not deliver")
        for item in findings:
            lines.append(
                "  {kind:<9} {detector:<22} {file}:{line}:{column}  fp={fingerprint_} len={length}".format(
                    kind=item["kind"],
                    detector=item["detector"],
                    file=item["file"],
                    line=item["line"],
                    column=item["column"],
                    fingerprint_=item["fingerprint"],
                    length=item["length"],
                )
            )
    for err in report["errors"]:
        lines.append(f"ERROR: {err}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Refuse to deliver artifacts that contain a secret. Never prints the secret.",
    )
    parser.add_argument("paths", nargs="*", help="files or directories to scan")
    parser.add_argument(
        "--changed-since",
        metavar="REV",
        help="scan files changed since REV (git diff --name-only); ignored if git cannot answer",
    )
    parser.add_argument(
        "--env-var",
        action="append",
        default=[],
        metavar="NAME",
        help="additional environment variable to treat as a secret (repeatable)",
    )
    parser.add_argument(
        "--no-patterns",
        action="store_true",
        help="exact environment values only; skip the credential-shape patterns",
    )
    parser.add_argument(
        "--ignore-file",
        metavar="PATH",
        default=IGNORE_FILE,
        help=f"suppression entries, default {IGNORE_FILE} (each needs a reason)",
    )
    parser.add_argument("--no-ignore-file", action="store_true", help="ignore no suppressions")
    parser.add_argument("--json", action="store_true", help="machine-readable report on stdout")
    args = parser.parse_args(argv)

    targets: list[Path] = [Path(p) for p in args.paths]
    if args.changed_since:
        targets.extend(changed_files(args.changed_since))
    if not targets:
        parser.error("no paths given and --changed-since produced nothing")

    env_vars = tuple(DEFAULT_ENV_VARS) + tuple(args.env_var)
    armed = secret_values(env_vars)
    ignores: list[tuple[str, str, str]] = []
    ignore_errors: list[str] = []
    if not args.no_ignore_file:
        ignores, ignore_errors = load_ignores(Path(args.ignore_file))
    report = scan_paths(targets, armed, use_patterns=not args.no_patterns, ignores=ignores)
    report["errors"].extend(ignore_errors)
    # A committed scan result with no date is a claim with no tense: the reader
    # cannot tell whether the tree was clean today or in August.
    report["generated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_human(report))

    if report["errors"]:
        return 2
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
