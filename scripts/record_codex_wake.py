#!/usr/bin/env python3
"""File one verified Codex wake in the existing item ledger, awaiting review.

This helper only appends channels/items.jsonl in a checkout. Publish the actual
work first, then run this helper, inspect its diff and publish the ledger append.
Reports, handoffs and wake bookkeeping alone are not completed work. The helper
never grants an accomplished/reviewed state, sends messages or invokes models.

Manifest keys: run_id (codex-YYYYMMDDTHHMMSSZ-8hex), started_utc,
artifact_commit (full SHA), artifact_paths, title, validation. The artifact's
commit subject must be `land(wake): Codex work from run <run_id>`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys
import urllib.parse
import urllib.request


REPOSITORY = "LindsayRidgeway/llm-symposium"
RUN_RE = re.compile(r"codex-(\d{8}T\d{6}Z)-[0-9a-f]{8}\Z")
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
META_PREFIXES = (
    "channels/conversation/", "channels/reports/", "channels/usage/",
    "channels/codex/", "channels/tarik-codex/", "channels/tarik-codex-wakes/", "channels/tarik-cloud/",
    "channels/tarik-goose-results/",
    "channels/handoffs/", "to-do-lists/",
)
META_FILES = {
    "channels/items.jsonl", "channels/tasks.md", "channels/action-queue.md",
    "channels/reject-queue.md", "channels/agenda.md",
}
META_NAME_RE = re.compile(r"(?:^|[-_.])(?:wake|run|handoff|report)(?:s)?(?:[-_.]|$)", re.I)


def _utc(value):
    if isinstance(value, str):
        try:
            value = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
        except ValueError:
            raise ValueError("timestamp must be an actual UTC YYYY-MM-DDTHH:MM:SSZ") from None
    if not isinstance(value, dt.datetime) or value.tzinfo is None:
        raise ValueError("an aware UTC timestamp is required")
    return value.astimezone(dt.timezone.utc)


def _path(value):
    if not isinstance(value, str) or not value or "\\" in value or any(ord(c) < 32 for c in value):
        raise ValueError("invalid artifact path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in (".", "..", ".git") for part in value.split("/")) or str(path) != value:
        raise ValueError("artifact paths must be normalized repository-relative paths")
    return value


def is_artifact(path):
    """A conservative work boundary: operational bookkeeping cannot count itself."""
    return (path not in META_FILES and not path.startswith(META_PREFIXES)
            and not (PurePosixPath(path).suffix in (".md", ".txt", ".json", ".jsonl")
                     and META_NAME_RE.search(PurePosixPath(path).name)))


def validate_manifest(data):
    keys = {"run_id", "started_utc", "artifact_commit", "artifact_paths", "title", "validation"}
    if not isinstance(data, dict) or set(data) != keys:
        raise ValueError("manifest requires exactly run_id, started_utc, artifact_commit, artifact_paths, title, validation")
    match = RUN_RE.fullmatch(data["run_id"]) if isinstance(data["run_id"], str) else None
    if not match:
        raise ValueError("run_id must be codex-YYYYMMDDTHHMMSSZ-8hex")
    started = _utc(data["started_utc"])
    if started.strftime("%Y%m%dT%H%M%SZ") != match.group(1):
        raise ValueError("run_id and started_utc disagree")
    if not isinstance(data["artifact_commit"], str) or not SHA_RE.fullmatch(data["artifact_commit"]):
        raise ValueError("artifact_commit must be a full lowercase commit SHA")
    paths = data["artifact_paths"]
    if not isinstance(paths, list) or not 1 <= len(paths) <= 20:
        raise ValueError("one to twenty published artifact paths are required")
    paths = [_path(path) for path in paths]
    if len(set(paths)) != len(paths) or not all(is_artifact(path) for path in paths):
        raise ValueError("artifact paths must be distinct substantive work, not reports, handoffs or bookkeeping")
    for key, limit in (("title", 160), ("validation", 2000)):
        if not isinstance(data[key], str) or not data[key].strip() or len(data[key]) > limit or "\x00" in data[key]:
            raise ValueError("a nonempty bounded " + key + " is required")
    return dict(data)


def _get_json(url, opener=None):
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "Tarik-Codex-wake-recorder",
    })
    with (opener or urllib.request.urlopen)(request, timeout=30) as response:
        raw = response.read(5_000_001)
    if len(raw) > 5_000_000:
        raise ValueError("publication response too large to verify")
    return json.loads(raw)


def verify_publication(sha, opener=None):
    """Independent read-only GitHub evidence; no API key or paid service is used."""
    base = "https://api.github.com/repos/" + REPOSITORY
    repo = _get_json(base, opener)
    branch = repo.get("default_branch")
    if not isinstance(branch, str) or not branch:
        raise ValueError("default branch could not be verified")
    commit = _get_json(base + "/commits/" + sha, opener)
    comparison = _get_json(base + "/compare/" + sha + "..." + urllib.parse.quote(branch, safe=""), opener)
    return {"sha": commit.get("sha"), "message": commit.get("commit", {}).get("message", ""),
            "default_branch": branch, "on_default_branch": comparison.get("status") in ("ahead", "identical"),
            "files": commit.get("files", [])}


def _ledger_module(repo_root):
    path = Path(repo_root) / "channels/item_ledger.py"
    spec = importlib.util.spec_from_file_location("codex_existing_item_ledger", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record_wake(manifest, repo_root, *, verify_commit=None, now=None, ledger=None):
    """Append one compatible waiting-for-review row; verification is injectable for tests.

    verify_commit(sha) must return independently captured publication evidence in
    verify_publication's shape. A manifest's own assertions are never evidence.
    Serialize writers and publish this append with the fresh ledger blob SHA.
    """
    data = validate_manifest(manifest)
    repo_root = Path(repo_root)
    ledger = ledger or _ledger_module(repo_root)
    ledger_path = repo_root / "channels/items.jsonl"
    known = ledger.load(ledger_path)
    existing = known.get(data["run_id"])
    if existing is not None:
        expected = {"platform": "codex", "amigo": "tarik", "artifact_commit": data["artifact_commit"],
                    "paths": data["artifact_paths"], "started_utc": data["started_utc"]}
        if any(existing.get(key) != value for key, value in expected.items()):
            raise ValueError("run_id already belongs to different evidence")
        return {"status": "already_recorded", "item": existing}
    # A retry carrying the same already-counted artifact cannot invent a new item.
    if any(row.get("platform") == "codex" and row.get("artifact_commit") == data["artifact_commit"]
           for row in known.values()):
        raise ValueError("this artifact commit is already counted by a Codex wake")
    evidence = (verify_commit or verify_publication)(data["artifact_commit"])
    expected_subject = "land(wake): Codex work from run " + data["run_id"]
    if (not isinstance(evidence, dict) or evidence.get("sha") != data["artifact_commit"]
            or evidence.get("on_default_branch") is not True or not evidence.get("default_branch")
            or evidence.get("message", "").split("\n", 1)[0] != expected_subject):
        raise ValueError("actual artifact commit/run publication on the default branch was not verified")
    files = evidence.get("files", [])
    changed = {entry.get("filename") for entry in files if isinstance(entry, dict)
               and entry.get("status") in ("added", "modified", "renamed", "removed")
               and isinstance(entry.get("changes"), int) and entry["changes"] > 0}
    if not set(data["artifact_paths"]).issubset(changed):
        raise ValueError("every artifact path must have a real published change in the verified commit")
    if any(ledger.is_generated_path(path, repo_root) for path in data["artifact_paths"]):
        raise ValueError("generated indexes are not independent artifacts")
    finished = _utc(now() if callable(now) else now or dt.datetime.now(dt.timezone.utc))
    if finished < _utc(data["started_utc"]):
        raise ValueError("completion precedes wake start")
    row = {"id": data["run_id"], "filed_utc": finished.strftime("%Y-%m-%dT%H:%M:%SZ"),
           "amigo": "tarik", "platform": "codex", "source": "codex",
           "started_utc": data["started_utc"], "title": data["title"].strip(),
           "scope": ledger.scope_for_paths(data["artifact_paths"]), "paths": data["artifact_paths"],
           "artifact_commit": data["artifact_commit"],
           "evidence": "https://github.com/" + REPOSITORY + "/commit/" + data["artifact_commit"],
           "validation": data["validation"].strip(), "cost_usd": None,
           "state": None, "state_utc": None, "reason": None, "reviewer": None}
    ledger.append([row], ledger_path)
    return {"status": "recorded", "item": row}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        result = record_wake(json.loads(args.manifest.read_text(encoding="utf-8")), args.repo_root)
    except Exception as error:
        print("Codex wake not recorded: " + type(error).__name__, file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
