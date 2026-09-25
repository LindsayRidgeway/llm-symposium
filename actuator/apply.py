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


_C_ESCAPES = {"a": 7, "b": 8, "f": 12, "n": 10, "r": 13, "t": 9, "v": 11, "\\": 92, '"': 34}


def _unquote_git_path(token: str) -> str:
    """Decode a git C-style quoted path token, e.g. '"a/file name.py"'.

    Git writes a diff header path as a C-quoted string whenever the path holds
    a space, a quote, a control byte or (under the default core.quotepath) a
    non-ASCII byte — but it *accepts* the quoted spelling even when quoting was
    not required. A submitted patch can therefore write the engine's path as
    "a/actuator/apply.py" and have git apply it. The scanner must read the
    quoted form too, or the self-modification guard fails open (R-006).
    """
    if len(token) < 2 or token[0] != '"' or token[-1] != '"':
        return token
    body = token[1:-1]
    out = bytearray()
    i = 0
    while i < len(body):
        c = body[i]
        if c != "\\":
            out.extend(c.encode("utf-8"))
            i += 1
            continue
        i += 1
        if i >= len(body):
            break
        esc = body[i]
        i += 1
        if esc in _C_ESCAPES:
            out.append(_C_ESCAPES[esc])
        elif esc in "01234567":
            digits = esc
            while i < len(body) and len(digits) < 3 and body[i] in "01234567":
                digits += body[i]
                i += 1
            out.append(int(digits, 8) & 0xFF)
        else:
            out.extend(esc.encode("utf-8"))
    return out.decode("utf-8", "surrogateescape")


def _quote_end(text: str, start: int) -> int:
    """Index just past the closing quote of the C-quoted string at ``start``."""
    i = start + 1
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == '"':
            return i + 1
        i += 1
    return len(text)


def _header_tokens(line: str) -> list[str]:
    """The two path tokens of a 'diff --git <src> <dst>' line.

    Each token is either a C-quoted string (which may contain spaces) or a run
    of non-space bytes. Nothing after the second token is read.
    """
    tokens: list[str] = []
    i = len("diff --git ")
    while i < len(line) and len(tokens) < 2:
        if line[i] == " ":
            i += 1
            continue
        if line[i] == '"':
            j = _quote_end(line, i)
            tokens.append(line[i:j])
            i = j
        else:
            j = i
            while j < len(line) and line[j] != " ":
                j += 1
            tokens.append(line[i:j])
            i = j
    return tokens


def _as_repo_path(token: str, *, require_ab: bool) -> str | None:
    """Unquote a header token and strip its a/ or b/ prefix.

    With ``require_ab`` (used for ---/+++ fallback lines, whose 'a/' or 'b/'
    prefix is what distinguishes them from a removed line that merely begins
    with '--'), a token without the prefix is rejected as None.
    """
    path = _unquote_git_path(token)
    for prefix in ("a/", "b/"):
        if path.startswith(prefix):
            return path[len(prefix):]
    return None if require_ab else path


def touched_files(patch_text: str) -> list[str]:
    """Repo-relative paths of the files a patch touches (from diff headers).

    Paths are canonicalized: equivalent spellings such as 'actuator//apply.py'
    collapse to 'actuator/apply.py', so the self-modification guard cannot be
    dodgeable by path tricks and the verifier never touches a path outside
    the repository. Both source and destination paths are inspected so deletion
    or renaming of protected files cannot evade the guard. Git's C-quoted
    spellings — including '"a/actuator/apply.py"', which git accepts and applies
    even though it need not quote — are unquoted first, so quoting cannot hide a
    touched path either (R-006).
    """
    files: list[str] = []

    def add(path: str | None) -> None:
        if path and path not in ("dev/null", "/dev/null") and path not in files:
            files.append(path)

    for m in re.finditer(r"^diff --git (.*)$", patch_text, re.MULTILINE):
        for token in _header_tokens(m.group(0)):
            add(_as_repo_path(token, require_ab=False))
    if not files:
        for m in re.finditer(r"^(?:---|\+\+\+) (.*)$", patch_text, re.MULTILINE):
            rest = m.group(1)
            if rest.startswith('"'):
                token = rest[: _quote_end(rest, 0)]
            else:
                token = re.split(r"[\t ]", rest, maxsplit=1)[0]
            add(_as_repo_path(token, require_ab=True))
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
