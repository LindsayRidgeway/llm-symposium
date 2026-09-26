#!/usr/bin/env python3
"""The local friction pass — the trigger that replaces the retired daily runner.

`symposium.yml` was retired on 2026-09-25. It ran the four-model peer review on a *clock*, and
wrote `discussions/*-review.md` in mode `"w"`, so every run overwrote the run before it: a week of
daily runs left exactly one copy. The human's instruction was that the friction work belongs where
it has a shell and can run tests, and the agenda item that records this says the deliverable is the
*trigger*, not another transcript: "Do not rebuild the runner in another shape."

So this script answers one question — **has anything landed since the last pass?** — and, only if
the answer is yes, invokes the same four model reviews (`.github/scripts/runner.py`) and regenerates
the gallery matrix (`scripts/matrix_producer.py`). It does not reimplement the prompts. It keeps the
reviews: after the runner writes its four files, they are copied into
`discussions/friction/<date>-<shortsha>.md`, because the runner overwrites them and this is the part
that was missing.

Three rules it holds to, each one a defect that already cost the commons something:

1. **A trigger, not a clock.** Run it as often as you like; the second run in a row does nothing.
   `--check` reports and never acts.
2. **Never overwrite a review.** Output is dated and keyed to the commit it reviewed. Two passes
   can never occupy the same path.
3. **The pass must not trigger itself.** Its own outputs — the four review files, its archive, its
   state file, the verification log — are excluded from "what landed", or the first pass would
   make every later one think new work existed.

Usage (from the repository root):

    python3 scripts/friction_pass.py --check      # is work waiting? exits 0 either way
    python3 scripts/friction_pass.py              # run the pass if work is waiting
    python3 scripts/friction_pass.py --force      # run it even if nothing landed
    python3 scripts/friction_pass.py --dry-run    # say what would run; change nothing
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import subprocess
import sys
from pathlib import Path

# The four review files the runner writes. Kept in one place so the archive step and the
# self-trigger guard cannot drift apart.
REVIEW_FILES = (
    "discussions/gemini-review.md",
    "discussions/openai-review.md",
    "discussions/claude-review.md",
    "discussions/deepseek-review.md",
)

# Written by the pass itself, or by the landing/verification machinery. A change to any of these
# is not "work that landed" and must not re-trigger a pass.
SELF_OUTPUT_PREFIXES = (
    "runs/",                          # run markers and this pass's own state file
    "discussions/friction/",          # the archive this pass writes
    "tests/last-verification.txt",    # the verification suite's own log
    "probes/results/",                # probe output
)
SELF_OUTPUT_FILES = tuple(REVIEW_FILES)

STATE_PATH = "runs/friction-pass.json"
RUNNER = ".github/scripts/runner.py"
MATRIX = "scripts/matrix_producer.py"
MAX_PATHS_REPORTED = 40


# --------------------------------------------------------------------------- git, thinly

def _git(repo: Path, *args: str) -> str:
    """stdout of a git command, or "" if git refused. Never raises: a pass that cannot read
    the tree should say so, not take the wake down with it."""
    try:
        out = subprocess.run(
            ["git", *args], cwd=str(repo), capture_output=True, text=True, timeout=60
        )
    except Exception:
        return ""
    return out.stdout if out.returncode == 0 else ""


def head_sha(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD").strip()


def short_sha(sha: str, n: int = 8) -> str:
    return (sha or "unknown")[:n]


def has_commits(repo: Path) -> bool:
    return bool(head_sha(repo))


def last_commit_touching(repo: Path, path: str) -> str:
    """The newest commit that changed `path`, or "" if git has never seen it."""
    return _git(repo, "rev-list", "-1", "HEAD", "--", path).strip()


def changed_paths(repo: Path, since_sha: str) -> list[str]:
    """Every path changed by a commit after `since_sha`. Committed work only: the trigger
    fires on what landed, which is what a review has to be about."""
    if not since_sha:
        return []
    out = _git(repo, "diff", "--name-only", f"{since_sha}..HEAD")
    return [line.strip() for line in out.splitlines() if line.strip()]


# --------------------------------------------------------------------------- the trigger

def is_self_output(path: str) -> bool:
    return path in SELF_OUTPUT_FILES or any(path.startswith(p) for p in SELF_OUTPUT_PREFIXES)


def load_state(repo: Path) -> dict:
    try:
        state = json.loads((repo / STATE_PATH).read_text(encoding="utf-8"))
        return state if isinstance(state, dict) else {}
    except Exception:
        return {}


def save_state(repo: Path, state: dict) -> None:
    path = repo / STATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def all_paths(repo: Path) -> list[str]:
    """Every path ever committed. Used only when this pass has no marker at all: there is then
    no honest "since", and everything on record is unreviewed by it."""
    out = _git(repo, "log", "--name-only", "--pretty=format:")
    return sorted({line.strip() for line in out.splitlines() if line.strip()})


def fallback_since(repo: Path) -> str:
    """What to compare against when this pass has never recorded a marker.

    The newest commit that touched a review file — i.e. where the retired runner left off. Empty
    means git has never seen a review file, so this pass has never had a predecessor at all.
    """
    # Newest of the four, as git orders them.
    return _git(repo, "rev-list", "--max-count=1", "HEAD", *REVIEW_FILES).strip()


def resolvable(repo: Path, sha: str) -> bool:
    """Does the marker still name a commit? After a history rewrite it may not, and a marker
    that cannot resolve would otherwise make `git diff marker..HEAD` fail silently and read as
    'nothing landed' for ever."""
    return bool(_git(repo, "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}").strip())


def due(repo: Path, state: dict | None = None) -> dict:
    """Is there landed work this pass has not looked at? Pure enough to test directly."""
    state = load_state(repo) if state is None else state
    if not has_commits(repo):
        return {"due": False, "since": "", "paths": [], "reason": "not a git repository (or no commits)"}

    since = state.get("last_sha") or fallback_since(repo)
    if since and not resolvable(repo, since):
        since = fallback_since(repo)
    head = head_sha(repo)
    if since and since == head:
        return {"due": False, "since": since, "paths": [],
                "reason": f"nothing landed since {short_sha(since)}"}

    if since:
        paths = [p for p in changed_paths(repo, since) if not is_self_output(p)]
        origin = f"since {short_sha(since)}"
        if not paths:
            return {"due": False, "since": since, "paths": [],
                    "reason": f"nothing landed {origin} (only the pass's own output changed)"}
    else:
        paths = [p for p in all_paths(repo) if not is_self_output(p)]
        origin = "— this pass has never run, so nothing on record has been through it"
        if not paths:
            return {"due": False, "since": "", "paths": [], "reason": f"nothing on record {origin}"}
    return {"due": True, "since": since, "paths": paths,
            "reason": f"{len(paths)} path(s) to review {origin}"}


# --------------------------------------------------------------------------- the pass

def archive_path(repo: Path, when: _dt.date, sha: str) -> Path:
    """Dated and keyed to the reviewed commit, so two passes can never share a path."""
    return repo / "discussions" / "friction" / f"{when.isoformat()}-{short_sha(sha)}.md"


def _run(cmd: list[str], repo: Path) -> int:
    print(f"  $ {' '.join(cmd)}")
    try:
        return subprocess.run(cmd, cwd=str(repo)).returncode
    except Exception as exc:                      # noqa: BLE001 — a failed step is reported, not fatal
        print(f"  ! {cmd[0]} could not be run: {exc}")
        return 1


def archive_reviews(repo: Path, when: _dt.date, sha: str, paths: list[str]) -> tuple[str, int]:
    """Copy whatever the runner wrote into one dated file. Returns (relpath, n_sections).

    Nothing is archived when the runner produced nothing — a pass that reached no model has no
    review to keep, and the marker must not advance (or the next wake would skip the work).
    """
    sections = []
    for rel in REVIEW_FILES:
        src = repo / rel
        if not src.exists():
            continue
        body = src.read_text(encoding="utf-8", errors="replace").strip()
        if not body:
            continue
        model = Path(rel).stem.replace("-review", "")
        sections.append((model, body))
    if not sections:
        return "", 0

    out = archive_path(repo, when, sha)
    out.parent.mkdir(parents=True, exist_ok=True)
    head = [
        f"# Friction pass — {when.isoformat()} — {short_sha(sha)}",
        "",
        f"Run against the tree at `{sha}`. Triggered by {len(paths)} landed path(s) since the "
        f"previous pass; this file is the archive of that pass, because "
        f"`.github/scripts/runner.py` writes `discussions/*-review.md` in mode `\"w\"` and would "
        f"otherwise overwrite itself on the next one.",
        "",
        "## What had landed",
        "",
    ] + [f"- `{p}`" for p in paths[:MAX_PATHS_REPORTED]]
    if len(paths) > MAX_PATHS_REPORTED:
        head.append(f"- … and {len(paths) - MAX_PATHS_REPORTED} more")
    head += [""]
    for model, body in sections:
        head += [f"## {model}", "", body, ""]
    out.write_text("\n".join(head).rstrip() + "\n", encoding="utf-8")
    return str(out.relative_to(repo)), len(sections)


def run_pass(repo: Path, force: bool = False, dry_run: bool = False,
             skip_matrix: bool = False, when: _dt.date | None = None) -> dict:
    """Check, then run if work is waiting. Returns a result dict; never raises for a failed step."""
    when = when or _dt.date.today()
    state = load_state(repo)
    verdict = due(repo, state)
    result = {"ran": False, "due": verdict["due"], "since": verdict["since"],
              "paths": verdict["paths"], "reason": verdict["reason"],
              "archive": "", "sections": 0, "steps": []}

    if not verdict["due"] and not force:
        result["reason"] = verdict["reason"]
        return result
    if dry_run:
        result["reason"] = "dry run — nothing executed"
        return result

    head = head_sha(repo) or verdict["since"]
    print(f"friction pass: {verdict['reason']}")

    steps = [(sys.executable, RUNNER)]
    if not skip_matrix:
        steps.append((sys.executable, MATRIX))
    for cmd in steps:
        code = _run(list(cmd), repo)
        result["steps"].append({"cmd": " ".join(cmd), "exit": code})

    rel, n = archive_reviews(repo, when, head, verdict["paths"])
    result["archive"], result["sections"] = rel, n
    result["ran"] = True

    if not rel:
        result["reason"] = ("no review was produced — no model answered; marker not advanced, so "
                            "the next pass retries this same work")
        return result

    state.update({
        "last_sha": head,
        "last_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "last_archive": rel,
        "passes": int(state.get("passes", 0)) + 1,
    })
    save_state(repo, state)
    result["reason"] = f"pass complete — {n} review section(s) archived to {rel}"
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".", help="repository root (default: current directory)")
    ap.add_argument("--check", action="store_true", help="report whether work is waiting; change nothing")
    ap.add_argument("--force", action="store_true", help="run even if nothing has landed")
    ap.add_argument("--dry-run", action="store_true", help="say what would run; change nothing")
    ap.add_argument("--skip-matrix", action="store_true", help="run the reviews only")
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists() and not has_commits(repo):
        print("friction pass: not a git repository — nothing to trigger on")
        return 0

    if args.check:
        v = due(repo)
        print(json.dumps(v, indent=2))
        return 0

    res = run_pass(repo, force=args.force, dry_run=args.dry_run, skip_matrix=args.skip_matrix)
    print(json.dumps({k: res[k] for k in ("ran", "due", "since", "archive", "sections", "reason")},
                     indent=2))
    # A pass that did nothing because nothing landed is the healthy case, and it must not read as
    # a failure to whatever called this.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
