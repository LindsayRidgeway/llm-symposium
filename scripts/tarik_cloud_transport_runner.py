#!/usr/bin/env python3
"""Process newly added Tarik requests from one main-branch GitHub push.

Only classified counts reach stdout. Credentials, request bodies, API responses,
and exception messages are never printed. Re-running a job cannot resend mail.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import urllib.request

REPOSITORY = "LindsayRidgeway/llm-symposium"
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
REQUEST_RE = re.compile(r"channels/tarik-cloud/requests/([a-z0-9][a-z0-9-]{0,79})\.json\Z")
FILE_STATUSES = {"added", "removed", "modified", "renamed", "copied", "changed", "unchanged"}
MAX_API_BYTES = 8 * 1024 * 1024
MAX_REQUEST_BYTES = 64 * 1024

_spec = importlib.util.spec_from_file_location(
    "tarik_cloud_transport_worker", Path(__file__).with_name("tarik_cloud_transport.py"))
worker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(worker)


class RunnerError(ValueError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def _validate_event(event, run_attempt):
    if type(run_attempt) not in (int, str) or str(run_attempt) != "1":
        raise RunnerError("rerun_refused")
    if not isinstance(event, dict) or event.get("ref") != "refs/heads/main":
        raise RunnerError("invalid_push")
    repository = event.get("repository")
    if not isinstance(repository, dict) or repository.get("full_name") != REPOSITORY:
        raise RunnerError("repository_mismatch")
    if any(event.get(flag) is not False for flag in ("created", "deleted", "forced")):
        raise RunnerError("invalid_push")
    before, after = event.get("before"), event.get("after")
    if any(not isinstance(sha, str) or not SHA_RE.fullmatch(sha) or sha == "0" * 40
           for sha in (before, after)) or before == after:
        raise RunnerError("invalid_push")
    return before, after


def select_request_paths(event, compare_payload, run_attempt):
    """Return exact, newly added request paths; reject incomplete comparisons."""
    before, after = _validate_event(event, run_attempt)
    payload = compare_payload
    if not isinstance(payload, dict):
        raise RunnerError("invalid_compare")
    commits, files = payload.get("commits"), payload.get("files")
    count = payload.get("total_commits")
    if not isinstance(commits, list) or not isinstance(files, list) or type(count) is not int:
        raise RunnerError("invalid_compare")
    # Compare's unpaginated commits cap is 250; its file list caps at 300.
    # Exactly 300 files cannot prove completeness, so refuse that boundary too.
    if len(files) >= 300 or count < 1 or count != len(commits):
        raise RunnerError("incomplete_compare")
    if payload.get("status") != "ahead" or payload.get("behind_by") != 0 or payload.get("ahead_by") != count:
        raise RunnerError("nonlinear_compare")
    base, merge_base = payload.get("base_commit"), payload.get("merge_base_commit")
    if (not isinstance(base, dict) or not isinstance(merge_base, dict) or
            base.get("sha") != before or merge_base.get("sha") != before or
            not all(isinstance(commit, dict) and isinstance(commit.get("sha"), str)
                    and SHA_RE.fullmatch(commit["sha"]) for commit in commits) or
            commits[-1]["sha"] != after):
        raise RunnerError("compare_mismatch")
    selected, seen = [], set()
    for entry in files:
        if (not isinstance(entry, dict) or not isinstance(entry.get("filename"), str)
                or not isinstance(entry.get("status"), str) or entry["status"] not in FILE_STATUSES):
            raise RunnerError("invalid_compare")
        filename = entry["filename"]
        if filename in seen or (entry["status"] == "added" and "previous_filename" in entry):
            raise RunnerError("invalid_compare")
        seen.add(filename)
        if entry["status"] == "added" and REQUEST_RE.fullmatch(filename):
            selected.append(filename)
    return sorted(selected)


def fetch_compare(before, after, token):
    """Read one bounded, unpaginated comparison from the fixed repository."""
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPOSITORY}/compare/{before}...{after}",
        headers={"Accept": "application/vnd.github+json", "Authorization": "Bearer " + token,
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "tarik-cloud-transport"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(MAX_API_BYTES + 1)
    if len(data) > MAX_API_BYTES:
        raise RunnerError("incomplete_compare")
    return json.loads(data)


def _safe_path(root, relative, *, directory=False):
    path = root
    parts = Path(relative).parts
    for index, part in enumerate(parts):
        path = path / part
        if path.is_symlink():
            raise RunnerError("unsafe_storage")
        if path.exists():
            expect_directory = directory or index < len(parts) - 1
            if (expect_directory and not path.is_dir()) or (not expect_directory and not path.is_file()):
                raise RunnerError("unsafe_storage")
    return path


def _requests(root, paths):
    requests = []
    for relative in paths:
        path = _safe_path(root, relative)
        if path.stat().st_size > MAX_REQUEST_BYTES:
            raise RunnerError("invalid_request")
        request = worker.validate_request(json.loads(path.read_text(encoding="utf-8")))
        if request["id"] != REQUEST_RE.fullmatch(relative).group(1):
            raise RunnerError("request_id_mismatch")
        _safe_path(root, "channels/tarik-cloud/receipts/" + request["id"] + ".json")
        requests.append(request)
    for relative in ("channels/tarik-cloud/receipts", "channels/tarik-cloud/mail-receipts"):
        directory = _safe_path(root, relative, directory=True)
        if directory.exists() and any(p.is_symlink() or not p.is_file() for p in directory.iterdir()):
            raise RunnerError("unsafe_storage")
    _safe_path(root, "channels/conversation/tarik.md")
    return requests


def run(event, repo_root, *, environ=None, compare_fetch=None, process_request=None):
    """Run a push with injectable compare/worker functions for offline checks.

    compare_fetch(before, after, token) returns GitHub's comparison JSON.
    process_request(request, repo_root, environ=...) has the worker API.
    """
    environ = os.environ if environ is None else environ
    counts = dict(selected=0, processed=0, delivered=0, synced=0, failed=0,
                  uncertain=0, existing_receipts=0, continuity_failures=0)
    try:
        if environ.get("GITHUB_EVENT_NAME") != "push":
            raise RunnerError("event_not_push")
        if environ.get("GITHUB_REPOSITORY") != REPOSITORY:
            raise RunnerError("repository_mismatch")
        before, after = _validate_event(event, environ.get("GITHUB_RUN_ATTEMPT"))
        token = environ.get("GITHUB_TOKEN", "").strip()
        if not token:
            raise RunnerError("missing_read_token")
        try:
            payload = (compare_fetch or fetch_compare)(before, after, token)
        except RunnerError:
            raise
        except Exception:
            raise RunnerError("compare_unavailable") from None
        paths = select_request_paths(event, payload, environ.get("GITHUB_RUN_ATTEMPT"))
        counts["selected"] = len(paths)
        if not paths:
            return {"status": "completed", "counts": counts}
        root = Path(repo_root).resolve(strict=True)
        if not root.is_dir():
            raise RunnerError("unsafe_storage")
        try:
            requests = _requests(root, paths)
        except RunnerError:
            raise
        except (ValueError, OSError, UnicodeError):
            raise RunnerError("invalid_request_or_storage") from None
        for request in requests:
            existing = (root / "channels/tarik-cloud/receipts" / (request["id"] + ".json")).exists()
            try:
                receipt = (process_request or worker.process_request)(request, root, environ=environ)
            except Exception:
                raise RunnerError("worker_unavailable") from None
            counts["processed"] += 1
            if existing:
                counts["existing_receipts"] += 1
            status = receipt.get("status") if isinstance(receipt, dict) else None
            if status not in {"delivered", "completed", "failed", "uncertain", "attempting"}:
                raise RunnerError("invalid_worker_result")
            if status == "delivered" and receipt.get("log_status") != "recorded":
                counts["continuity_failures"] += 1
            if status in {"uncertain", "attempting"}:
                counts["uncertain"] += 1
            elif status == "failed":
                counts["failed"] += 1
            elif not existing:
                counts["delivered" if status == "delivered" else "synced"] += 1
        status = "failed" if any(counts[key] for key in
                                 ("failed", "uncertain", "continuity_failures")) else "completed"
        return {"status": status, "counts": counts}
    except RunnerError as error:
        return {"status": "rejected", "reason": error.reason, "counts": counts}
    except Exception:
        return {"status": "rejected", "reason": "invalid_event_or_storage", "counts": counts}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        result = run(event, args.repo_root)
    except Exception:
        result = {"status": "rejected", "reason": "event_unavailable"}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
