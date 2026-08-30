#!/usr/bin/env python3
"""Symposium Actuator — apply model-submitted patch requests, autonomously.

The headless runner (`.github/scripts/runner.py`) can write new artifacts but
cannot patch existing code. This engine closes that gap, per the architectural
call in `discussions/00-meta-review-of-the-reviews.md`: models build the
actuator; no human applies patches.

Submission
----------
A model session drops a unified diff in `actuator/requests/` as
`YYYY-MM-DD-<arch>-<hash>.patch`. The runner's intake hook extracts fenced
```` ```diff ```` blocks from reviews automatically; engineering sessions may
write patch files directly.

Pipeline (per request, in order)
-------------------------------
1.  Self-modification guard: a patch may not touch this engine (`apply.py`).
2.  `git apply --check` — malformed patches are rejected; if the reverse
    applies cleanly, the change is already in effect and the request is
    no-op'd into `applied/`.
3.  Apply to the working tree, then verify: py_compile any touched `.py`,
    run `tests/test_projection.py` and `probes/ticktick_recurrence_probe.py`.
4.  Green -> move to `actuator/applied/` + log.  Red -> reverse-apply, move
    to `actuator/rejected/` + log the failure.

Run from the repository root:  python3 actuator/apply.py
Stdlib only. Invoked by `.github/workflows/actuator.yml`.
"""
from __future__ import annotations

import datetime
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUESTS_DIR = REPO_ROOT / "actuator" / "requests"
APPLIED_DIR = REPO_ROOT / "actuator" / "applied"
REJECTED_DIR = REPO_ROOT / "actuator" / "rejected"
LOG_PATH = REPO_ROOT / "actuator" / "log.md"
ENGINE = "actuator/apply.py"

# Offline verification suite (same commands the CI verification workflow runs).
VERIFY_SUITE = [
    ("tests/test_projection.py", sys.executable, "tests/test_projection.py"),
    ("probes/ticktick_recurrence_probe.py", sys.executable, "probes/ticktick_recurrence_probe.py"),
]
GIT_TIMEOUT = 60
SUITE_TIMEOUT = 240


def _now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _run(cmd, cwd=REPO_ROOT, timeout=GIT_TIMEOUT):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)


def _canonical(path: str) -> str:
    """Normalize a diff-header path to a repo-relative path.

    Diff headers may carry equivalent spellings (e.g. 'actuator//apply.py',
    'actuator/./apply.py') that git treats as the same file but that string
    comparison would miss. Resolving against REPO_ROOT collapses them, so
    the self-modification guard and the verifier see the real path — and
    any path that escapes the repository is revealed as such.
    """
    resolved = (REPO_ROOT / path).resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        # Outside the repository: return the absolute path so it is never
        # mistaken for a repo file and is visibly rejected downstream.
        return resolved.as_posix()


def touched_files(patch_text: str) -> list[str]:
    """Repo-relative paths of the files a patch touches (from diff headers).

    Paths are canonicalized: equivalent spellings such as 'actuator//apply.py'
    collapse to 'actuator/apply.py', so the self-modification guard cannot be
    dodgeable by path tricks and the verifier never touches a path outside
    the repository.
    """
    files = []
    for m in re.finditer(r"^diff --git a/(\S+) b/(\S+)\s*$", patch_text, re.MULTILINE):
        files.append(m.group(2))
    if not files:
        for m in re.finditer(r"^\+\+\+ b/(\S+)\s*$", patch_text, re.MULTILINE):
            p = m.group(1)
            if p not in files:
                files.append(p)
    return [_canonical(p) for p in files]


def verify(patch_text: str) -> tuple[bool, str]:
    """Run py_compile + offline suite against the current working tree."""
    results = []
    for path in touched_files(patch_text):
        candidate = REPO_ROOT / path
        if not candidate.resolve().is_relative_to(REPO_ROOT.resolve()):
            return False, f"Path traversal detected: {path}"
        if path.endswith(".py") and candidate.exists():
            r = _run([sys.executable, "-m", "py_compile", path], timeout=SUITE_TIMEOUT)
            results.append(f"py_compile {path}: {'OK' if r.returncode == 0 else 'FAIL'}")
            if r.returncode != 0:
                return False, "\n".join(results) + "\n" + r.stderr[-2000:]
    for label, *cmd in VERIFY_SUITE:
        if (REPO_ROOT / label).exists():
            try:
                r = _run(cmd, timeout=SUITE_TIMEOUT)
            except subprocess.TimeoutExpired:
                return False, f"{label}: TIMEOUT"
            results.append(f"{label}: {'OK' if r.returncode == 0 else 'FAIL'}")
            if r.returncode != 0:
                return False, "\n".join(results) + "\n" + (r.stdout + r.stderr)[-2000:]
    return True, "\n".join(results)


def log_entry(entry: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.write_text("# Actuator Log\n\n*Append-only ledger of actuator actions.*\n\n", encoding="utf-8")
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(entry.rstrip() + "\n\n")


def process_request(patch_path: Path) -> str:
    """Validate, verify, apply (or reject) one patch request. Returns status."""
    name = patch_path.name
    try:
        patch_text = patch_path.read_text(encoding="utf-8")
    except Exception as e:
        _move(patch_path, REJECTED_DIR)
        return f"REJECTED {name}: unreadable patch ({e})"

    if ENGINE in touched_files(patch_text):
        _move(patch_path, REJECTED_DIR)
        return f"REJECTED {name}: self-modification guard — patches may not touch {ENGINE}"

    rel = patch_path.relative_to(REPO_ROOT).as_posix()

    check = _run(["git", "apply", "--check", rel])
    if check.returncode != 0:
        reverse = _run(["git", "apply", "--reverse", "--check", rel])
        if reverse.returncode == 0:
            # Change already in effect — no-op, don't retry.
            _move(patch_path, APPLIED_DIR)
            return f"APPLIED {name}: already in effect (no-op)"
        _move(patch_path, REJECTED_DIR)
        return f"REJECTED {name}: git apply --check failed\n{check.stderr.strip()[:2000]}"

    apply = _run(["git", "apply", rel])
    if apply.returncode != 0:
        _move(patch_path, REJECTED_DIR)
        return f"REJECTED {name}: git apply failed\n{apply.stderr.strip()[:2000]}"

    ok, detail = verify(patch_text)
    if ok:
        _move(patch_path, APPLIED_DIR)
        return f"APPLIED {name}: verification passed\n{detail}"

    # Verification failed — reverse the apply, reject with the reason.
    rev = _run(["git", "apply", "-R", rel])
    rev_note = "reverted" if rev.returncode == 0 else "REVERT FAILED — manual review required"
    _move(patch_path, REJECTED_DIR)
    return f"REJECTED {name}: verification failed ({rev_note})\n{detail}"


def _move(src: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest_dir / src.name))


def main() -> int:
    if not REQUESTS_DIR.exists():
        print("actuator: no requests directory — nothing to do")
        return 0
    requests = sorted(REQUESTS_DIR.glob("*.patch"))
    if not requests:
        print("actuator: no patch requests pending")
        return 0

    stamp = _now()
    print(f"actuator: {len(requests)} request(s) pending — processing in order")
    for patch_path in requests:
        try:
            touched = touched_files(patch_path.read_text(encoding="utf-8"))
        except Exception:
            touched = []
        status = process_request(patch_path)
        print(f"- {status}")
        log_entry(
            f"## {stamp} — {patch_path.name}\n\n"
            f"{status}\n\n"
            f"touched: {', '.join(touched) or 'n/a'}"
        )
    print("actuator: done")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.TimeoutExpired as e:
        print(f"actuator: FATAL timeout {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:  # noqa: BLE001 — surface anything; CI sees it
        print(f"actuator: FATAL {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)
