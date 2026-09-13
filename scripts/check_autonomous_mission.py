#!/usr/bin/env python3
"""Check a queued Markdown mission's measurable contract, not its intellectual quality.

Run from a trusted snapshot outside the agent checkout. --mission must also be a
pre-run snapshot. This checks the required artifact and EVERY changed path;
changing a validator or an unrelated file cannot substitute for doing the task.
No API calls. No normalization of pre-existing documents or code blocks.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

COORDINATION = {"channels/agenda.md", "to-do-lists/tarik.md"}


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], stderr=subprocess.PIPE
    )


def safe_file(repo: Path, name: str) -> Path:
    """Reject traversal and symlinks (even links that resolve inside the checkout)."""
    parts = PurePosixPath(name).parts
    if (not parts or name.startswith("/") or "\\" in name or
            any(p in (".", "..") for p in parts) or
            str(PurePosixPath(name)) != name):
        raise ValueError("artifact path must be a canonical repository-relative path")
    path = repo
    for part in parts:
        path /= part
        if path.is_symlink():
            raise ValueError(f"symlink not allowed: {name}")
    if not path.resolve().is_relative_to(repo.resolve()):
        raise ValueError("artifact path escapes checkout")
    return path


def read_contract(mission: Path) -> tuple[str, int]:
    text = mission.read_text(encoding="utf-8")
    paths = re.findall(r"^\*\*Required artifact path:\*\* `([^`]+)`\s*$", text, re.M)
    lengths = re.findall(r"^- Minimum (\d+) words\.\s*$", text, re.M)
    if len(paths) != 1 or len(lengths) != 1 or int(lengths[0]) < 1:
        raise ValueError("mission needs one Required artifact path and one Minimum N words line")
    return paths[0], int(lengths[0])


def changed_paths(repo: Path, base: str) -> set[str]:
    # HEAD comparison includes staged and unstaged edits; untracked includes new files
    # without requiring the agent to stage them. NUL delimiters preserve path boundaries.
    tracked = git(repo, "diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--name-only", "-z", base, "--")
    untracked = git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    return {p.decode("utf-8") for p in (tracked + untracked).split(b"\0") if p}


def normalize_markdown(text: str) -> str:
    """Remove single trailing spaces/tabs, canonicalize Markdown hard breaks to two
    spaces, add final newline. Preserve fenced and indented code literally."""
    output = []
    fence_char, fence_len = "", 0
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence_char:
            output.append(line)
            if marker and marker[1][0] == fence_char and len(marker[1]) >= fence_len and not marker[2].strip():
                fence_char, fence_len = "", 0
            continue
        if marker:
            fence_char, fence_len = marker[1][0], len(marker[1])
            output.append(line)
        elif line.startswith(("    ", "\t")):
            output.append(line)
        else:
            stripped = line.rstrip(" \t")
            hard_break = bool(stripped) and line.endswith("  ")
            output.append(stripped + ("  " if hard_break else ""))
    return "\n".join(output) + ("\n" if output else "")


def has_metadata(text: str, field: str) -> bool:
    # Accept both **Author:** X and **Author**: X, or simple YAML front matter.
    if re.search(rf"^\*\*{field}(?::\*\*|\*\*:)\s*\S.+$", text[:1600], re.M | re.I):
        return True
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return bool(re.search(rf"^{field}:\s*\S.+$", text[4:end], re.M | re.I))
    return False


def check(repo: Path, mission: Path, base: str, artifacts: Path) -> dict:
    target_name, minimum = read_contract(mission)
    target = safe_file(repo, target_name)
    if not target_name.endswith(".md") or not target_name.startswith("discussions/"):
        raise ValueError("this mission checker supports discussion Markdown only")
    if git(repo, "ls-tree", "--name-only", base, "--", target_name).strip():
        raise ValueError("mission artifact already exists at base; do not regenerate accepted work")
    paths = changed_paths(repo, base)
    errors = []
    disallowed = paths - COORDINATION - {target_name}
    for name in paths & COORDINATION:
        safe_file(repo, name)
    if disallowed:
        errors.append("unexpected changed paths: " + ", ".join(sorted(disallowed)))
    if target_name not in paths or not target.is_file():
        errors.append("required artifact missing or unchanged: " + target_name)
    words, normalized = 0, False
    if target.is_file():
        if target.stat().st_size > 256_000:
            raise ValueError("artifact exceeds 256 KB limit")
        raw = target.read_bytes()
        (artifacts / "mission-original.md").write_bytes(raw)
        text = raw.decode("utf-8")
        clean = normalize_markdown(text)
        normalized = clean != text
        target.write_text(clean, encoding="utf-8")
        (artifacts / "mission-normalized.md").write_text(clean, encoding="utf-8")
        words = len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b", clean))
        if words < minimum:
            errors.append(f"artifact has {words} words; mission requires at least {minimum}")
        for field in ("Author", "Date", "Status"):
            if not has_metadata(clean, field):
                errors.append("missing metadata: " + field)
        if not re.search(r"^# \S", clean, re.M) and not has_metadata(clean, "title"):
            errors.append("missing title (H1 or front matter)")
    # Raw draft is preserved above, even when rejected. A patch keeps other changes
    # inspectable. Intent-to-add is only local to the isolated CI checkout.
    git(repo, "add", "-N", "--", ".")
    (artifacts / "changes.patch").write_bytes(
        git(repo, "diff", "--no-ext-diff", "--no-textconv", "--binary", base, "--")
    )
    # All allowed paths for this mission are Markdown: two trailing spaces are
    # meaningful hard breaks, and code examples are literal. Normalization above
    # handles prose whitespace; don't label valid Markdown breaks as git errors.
    diff = subprocess.run(
        ["git", "-C", str(repo), "-c", "core.whitespace=-blank-at-eol,blank-at-eof,space-before-tab",
         "diff", "--no-ext-diff", "--check", base, "--"],
        capture_output=True, text=True,
    )
    (artifacts / "diff-check.txt").write_text(diff.stdout + diff.stderr, encoding="utf-8")
    if diff.returncode:
        errors.append("git diff --check failed; see diff-check.txt")
    return {"ok": not errors, "target": target_name, "minimum_words": minimum,
            "word_count": words, "normalized": normalized,
            "changed_paths": sorted(paths), "errors": errors,
            "quality": "mechanical contract only; peer review still required"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--mission", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--artifacts", required=True)
    args = parser.parse_args()
    artifacts = Path(args.artifacts).resolve()
    artifacts.mkdir(parents=True, exist_ok=True)
    try:
        report = check(Path(args.repo).resolve(), Path(args.mission), args.base, artifacts)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        report = {"ok": False, "errors": [str(exc)]}
    (artifacts / "mission-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
