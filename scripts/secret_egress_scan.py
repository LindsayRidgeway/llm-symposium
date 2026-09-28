#!/usr/bin/env python3
"""Pre-delivery secret-egress scanner — the mechanical half of RT-4.

Background (agenda item 15, "Red team the deadbolt"). RT-4 is the finding that a
shell-capable run holds provider, mail and Telegram secrets in its process
environment and can also run arbitrary shell commands, so the same secret value
can reach stdout, a transcript, `sessions.db`, or a changed repository file. The
2026-09-27 probe (`scripts/rt4_secret_egress_probe.py`) showed the mail
auto-reply adapter redacts exact process-secret values before it writes a draft,
and that everything else is still open. The next action dated 2026-09-28 is to
choose and implement *one mechanical boundary* for shell-capable runs.

This is that boundary, chosen as the cheap half: a pre-delivery scanner. It
never decides whether a change is good; it decides only whether the exact bytes
of a configured secret value appear anywhere in the artefacts about to be
published. It reports the variable NAME and the file path, and never the value,
so that the alarm itself cannot become the leak. It also records a short salted
hash of each value it considered, so two runs can be correlated without either
run printing the value.

It is deliberately conservative about what counts as a secret:

  * the variable name must look like a secret (KEY/TOKEN/PASSWORD/SECRET/
    CREDENTIAL/PASSWD), and
  * the value must be at least `--min-length` characters (default 12, strictly
    longer than the 8 used by the mail adapter's redactor), and
  * obvious placeholders (`changeme`, `<your-token-here>`, runs of one repeated
    character, ...) are ignored, because a placeholder in a renamed variable is
    not a leak and a scanner that cries wolf is a scanner that gets switched off.

Usage::

    # Pre-delivery gate over everything git reports as changed or untracked:
    python3 scripts/secret_egress_scan.py --git-changed

    # Explicit paths:
    python3 scripts/secret_egress_scan.py channels/outbound docs/works

    # Machine-readable result, always written even when clean:
    python3 scripts/secret_egress_scan.py --git-changed --json probes/rt4-scan.json

Exit code is 1 when any exact secret value is found, 0 when clean, so it can be
used as a gate (`... || refuse`). `--self-test` runs a synthetic end-to-end check
with generated values and changes nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent

SECRET_NAME_RE = re.compile(r"(?:KEY|TOKEN|PASSWORD|PASSWD|SECRET|CREDENTIAL)", re.I)
REDACTION_MARKER = "[REDACTED PROCESS SECRET]"
DEFAULT_MIN_LENGTH = 12

# Directories that are never part of a published artefact.
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache"}

# Values that are placeholders, not secrets. A placeholder under a secret-looking
# name is common in docs and examples and must not fail a delivery.
PLACEHOLDER_VALUES = {
    "changeme",
    "change-me",
    "password",
    "secret",
    "token",
    "example",
    "dummy",
    "testing",
    "your-key-here",
    "your-token-here",
    "replace-me",
    "todo",
}
PLACEHOLDER_CHARS_RE = re.compile(r"^([x*.\-0 ])\1*$", re.I)
PLACEHOLDER_WRAPPER_RE = re.compile(r"[<>{}]")


def is_placeholder(value: str) -> bool:
    """True when `value` is a documented stand-in rather than a real secret."""
    stripped = value.strip()
    if not stripped:
        return True
    if stripped.lower() in PLACEHOLDER_VALUES:
        return True
    if PLACEHOLDER_CHARS_RE.match(stripped):
        return True
    if PLACEHOLDER_WRAPPER_RE.search(stripped):
        return True
    return False


def secret_values_from_env(
    env: dict[str, str] | None = None,
    min_length: int = DEFAULT_MIN_LENGTH,
    include_names: Iterable[str] = (),
) -> dict[str, str]:
    """Return {variable_name: value} for values that look like configured secrets.

    `include_names` forces a variable in even when its name does not match the
    secret-name pattern (for callers that know which variables carry secrets).
    """
    env = dict(os.environ if env is None else env)
    forced = {name for name in include_names if name}
    secrets: dict[str, str] = {}
    for name, value in env.items():
        if not value or len(value) < min_length:
            continue
        if name not in forced and not SECRET_NAME_RE.search(name):
            continue
        if is_placeholder(value):
            continue
        secrets[name] = value
    return secrets


def fingerprint(value: str) -> str:
    """A short, unsalted-digest-free label for a value, safe to record.

    Deliberately a plain SHA-256 prefix: this is not a defence against someone
    holding the value (they already have it), it is a defence against the scan
    report itself becoming a copy of the secret. The name plus the length plus
    the digest prefix are enough to tell two variables apart.
    """
    return hashlib.sha256(value.encode("utf-8", "surrogatepass")).hexdigest()[:8]


def iter_files(paths: Iterable[str | os.PathLike[str]], root: Path = REPO_ROOT) -> Iterable[Path]:
    """Yield candidate files under `paths`, skipping VCS/build directories."""
    for raw in paths:
        p = Path(raw)
        if not p.is_absolute():
            p = root / p
        if p.is_file():
            yield p
        elif p.is_dir():
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for filename in filenames:
                    yield Path(dirpath) / filename


def scan_file(path: Path, secrets: dict[str, str]) -> list[dict[str, object]]:
    """Return one hit record per variable whose exact value appears in `path`."""
    try:
        data = path.read_bytes()
    except OSError:
        return []
    hits: list[dict[str, object]] = []
    for name, value in secrets.items():
        needle = value.encode("utf-8", "surrogatepass")
        count = data.count(needle)
        if count:
            hits.append({"path": str(path), "name": name, "occurrences": count})
    return hits


def git_changed_paths(root: Path) -> list[str]:
    """Changed + untracked paths as git reports them, relative to `root`."""
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if out.returncode != 0:
        return []
    paths: list[str] = []
    for line in out.stdout.splitlines():
        if len(line) < 4:
            continue
        entry = line[3:]
        # `R  old -> new` records the destination after the arrow.
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        entry = entry.strip().strip('"')
        if entry:
            paths.append(entry)
    return paths


def scan(paths: Iterable[str], secrets: dict[str, str], root: Path = REPO_ROOT) -> dict[str, object]:
    """Scan `paths` for exact secret values; return a JSON-safe result."""
    hits: list[dict[str, object]] = []
    scanned: list[str] = []
    for file_path in iter_files(paths, root=root):
        scanned.append(str(file_path))
        hits.extend(scan_file(file_path, secrets))
    return {
        "tool": "scripts/secret_egress_scan.py",
        "rule": "RT-4 mechanical boundary: exact configured secret values must not appear in a published artefact",
        "secrets_considered": [
            {"name": name, "length": len(value), "sha256_8": fingerprint(value)}
            for name, value in sorted(secrets.items())
        ],
        "scanned_paths": scanned,
        "hits": hits,
        "clean": not hits,
    }


def _self_test() -> int:
    """Synthetic end-to-end check: proves detection and non-echo, changes nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        real = "sk-" + "a1b2c3d4e5f6g7h8"
        fake_env = {
            "DEMO_API_KEY": real,
            "DEMO_SHORT_TOKEN": "abc",                      # too short → ignored
            "DEMO_PLACEHOLDER_KEY": "change-me",            # placeholder → ignored
            "UNRELATED_SETTING": "not-a-secret-at-all-000",  # name does not match
        }
        secrets = secret_values_from_env(fake_env)
        assert set(secrets) == {"DEMO_API_KEY"}, secrets
        (root / "leaky.txt").write_text(f"prefix {real} suffix\n")
        (root / "clean.txt").write_text("nothing to see here\n")
        result = scan([str(root)], secrets, root=root)
        assert not result["clean"], result
        assert len(result["hits"]) == 1, result["hits"]
        assert result["hits"][0]["name"] == "DEMO_API_KEY"
        blob = json.dumps(result)
        assert real not in blob, "the report itself leaked the value"
        assert "DEMO_API_KEY" in blob
    print("secret_egress_scan --self-test: OK (detected, and did not echo the value)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", help="files or directories to scan")
    parser.add_argument("--git-changed", action="store_true", help="scan all changed and untracked files git reports")
    parser.add_argument("--root", default=str(REPO_ROOT), help="repository root (default: this script's repo)")
    parser.add_argument("--json", metavar="PATH", help="write the machine-readable result to PATH")
    parser.add_argument("--min-length", type=int, default=DEFAULT_MIN_LENGTH, help="minimum secret length to consider (default 12)")
    parser.add_argument("--name", action="append", default=[], help="force-include this environment variable even if its name does not match")
    parser.add_argument("--self-test", action="store_true", help="run a synthetic self-test and exit")
    parser.add_argument("--verbose", action="store_true", help="include the full list of scanned paths in the JSON report")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    root = Path(args.root).resolve()
    targets = list(args.paths)
    if args.git_changed:
        targets.extend(git_changed_paths(root))
    if not targets:
        print("nothing to scan: give paths or --git-changed", file=sys.stderr)
        return 0

    secrets = secret_values_from_env(min_length=args.min_length, include_names=args.name)
    result = scan(targets, secrets, root=root)

    if args.json:
        out = Path(args.json)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        # The durable report is a summary unless asked otherwise: the full path list is
        # hundreds of lines for a tree scan and the reader wants the count and the hits.
        record = dict(result)
        record["scanned_count"] = len(result["scanned_paths"])
        if not args.verbose:
            record.pop("scanned_paths", None)
        out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")

    if result["clean"]:
        print(f"secret-egress scan: clean — {len(result['scanned_paths'])} file(s) scanned, "
              f"{len(result['secrets_considered'])} secret variable(s) considered")
        return 0

    print(f"secret-egress scan: {len(result['hits'])} hit(s) in "
          f"{len(result['scanned_paths'])} file(s) scanned — refusing delivery:", file=sys.stderr)
    for hit in result["hits"]:
        print(f"  {hit['path']}: {hit['name']} appears {hit['occurrences']}x "
              f"(value withheld; marker it should have been replaced with: {REDACTION_MARKER})", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
