#!/usr/bin/env python3
"""Landing outcome census — where a wake's finished work actually ends up.

Why this exists. On 2026-10-22 three consecutive wakes of mine recovered the same file
(Tarik's `channels/tarik-goose-results/tg-20261017-001.json`), verified it, recorded the
same review verdict, and none of the three reached `main`. Each wake read the earlier
wake's report, saw the path still missing, and did the work again. The work was never the
problem; the delivery step was, and nothing measured it. `land_runs.py` logs one word per
attempt, the bot logs a second line when the draft-branch fallback fails, and nobody had
put the two together.

Two delivery paths exist, and this census keeps them apart because they fail differently:

  1. `land_runs.land()` — applies a run's diff to `main` directly. It logs
     `run <id> landing: <state>`, one of: landed, conflict, refused_dirty_tree,
     new_test_failures, push_failed, commit_failed, nothing_to_land, already_landed.
  2. the draft-branch fallback in `bot.py` — if (1) did not land, the run's patch is
     applied to `origin/main` in a throwaway worktree and pushed as `drafts/tick-<run>`.
     When even that fails the work is dropped and the only trace is
     `landing: patch does not apply to main cleanly, left unlanded: <git stderr>`.

So a run has one of three fates: MAIN, DRAFT (preserved, unreviewed, invisible to the next
wake), or LOST (no branch, no commit — the run's report is all that survives). The last two
are what a later wake mistakes for "this was never done".

Usage:
    python3 scripts/landing_outcome_census.py [LOG ...]

Defaults to the two logs this repository's bot writes. Reading is side-effect free; the
script writes nothing.
"""
import argparse
import collections
import os
import re
import sys

DEFAULT_LOGS = [
    os.path.expanduser("~/LLM/dmitri-bot/bot.log"),
]

RUN_LANDING = re.compile(r"run (\S+) landing: ([a-z_]+)")
DRAFT = re.compile(r"landed draft on branch drafts/tick-(\S+) \(")
NOT_APPLY = re.compile(r"landing: patch does not apply to main cleanly, left unlanded: (.*)")
CLAIMED_MISS = re.compile(r"run (\S+) claimed to land \d+ path\(s\) it did not change")

# The two shapes `git apply` uses to name the file it could not patch.
FAILED_HUNK = re.compile(r"error: patch failed: ([^:\s]+):\d+")
FAILED_FILE = re.compile(r"error: ([^:\s]+): (?:patch does not apply|does not exist in index)")
TRAILING_WS = re.compile(r"^(\S+):\d+: trailing whitespace")


def failing_path(message):
    """The path a `git apply` failure names, or None when it names none (e.g. whitespace)."""
    for pattern in (FAILED_HUNK, FAILED_FILE, TRAILING_WS):
        m = pattern.search(message or "")
        if m:
            return m.group(1)
    return None


def census(lines):
    """Turn log lines into per-run fates and per-cause counts. Pure function, so it is testable."""
    outcomes = collections.Counter()
    fates = {}                      # run id -> "MAIN" | "DRAFT" | "LOST" | "UNKNOWN"
    cause_paths = collections.Counter()
    cause_kinds = collections.Counter()
    draft_runs = set()
    lost_runs = set()
    unrecognised = []
    last_run = None
    for line in lines:
        line = line.rstrip("\n")
        m = DRAFT.search(line)
        if m:
            draft_runs.add(m.group(1))
            continue
        m = NOT_APPLY.search(line)
        if m:
            path = failing_path(m.group(1))
            cause_paths[path or "(unnamed)"] += 1
            cause_kinds[_kind(m.group(1))] += 1
            # The fallback line carries no run id: it belongs to the run whose `landing:`
            # line came immediately before, which is the bot's own sequence.
            if last_run:
                lost_runs.add(last_run)
                fates[last_run] = "LOST"
            continue
        m = CLAIMED_MISS.search(line)
        if m:
            cause_kinds["claimed_paths_not_changed"] += 1
            continue
        m = RUN_LANDING.search(line)
        if m:
            run, state = m.group(1), m.group(2)
            outcomes[state] += 1
            last_run = run
            fates[run] = "MAIN" if state == "landed" else "OTHER"
            continue
        if "landing" in line:
            unrecognised.append(line)
    return {
        "outcomes": outcomes,
        "fates": fates,
        "draft_runs": draft_runs,
        "lost_runs": lost_runs,
        "cause_paths": cause_paths,
        "cause_kinds": cause_kinds,
        "unrecognised": unrecognised,
    }


def _kind(message):
    if "trailing whitespace" in (message or ""):
        return "trailing_whitespace"
    if "does not exist in index" in (message or ""):
        return "path_not_in_index"
    if "patch failed" in (message or ""):
        return "hunk_context_moved"
    if "patch does not apply" in (message or ""):
        return "file_moved"
    return "other"


def final_fates(result):
    """One fate per run: MAIN, DRAFT or LOST. A run that reached main is never "draft"."""
    fates = {}
    for run, fate in result["fates"].items():
        fates[run] = "MAIN" if fate == "MAIN" else "OTHER"
    for run in result["draft_runs"]:
        if fates.get(run) != "MAIN":
            fates[run] = "DRAFT"
    for run in result["lost_runs"]:
        if fates.get(run) != "MAIN":
            fates[run] = "LOST"
    return fates


def report(result, logs, show_all=False):
    out = []
    total = sum(result["outcomes"].values())
    out.append("logs: " + ", ".join(logs))
    out.append("landing attempts recorded: %d" % total)
    out.append("")
    out.append("by land_runs.py state:")
    for state, n in result["outcomes"].most_common():
        out.append("  %-22s %4d" % (state, n))
    landed = result["outcomes"].get("landed", 0)
    out.append("")
    out.append("reached main: %d of %d attempts (%.1f%%)"
               % (landed, total, (100.0 * landed / total) if total else 0.0))
    if result.get("final"):
        tally = collections.Counter(result["final"].values())
        out.append("runs by final fate: %s"
                   % ", ".join("%s=%d" % (k, tally[k]) for k in ("MAIN", "DRAFT", "LOST")
                               if tally[k]))
    drafts = sorted(result["draft_runs"])
    out.append("preserved on a draft branch and nowhere else: %d run(s)" % len(drafts))
    shown = drafts if show_all else drafts[:6]
    for run in shown:
        out.append("  drafts/tick-%s" % run)
    if len(drafts) > len(shown):
        out.append("  ... and %d more (--all to list every one)" % (len(drafts) - len(shown)))
    lost = sorted(result["lost_runs"])
    out.append("dropped entirely (no commit, no branch): %d run(s)" % len(lost))
    for run in lost[-10:]:
        out.append("  %s" % run)
    out.append("")
    out.append("why a patch did not apply to main (by cause):")
    for kind, n in result["cause_kinds"].most_common():
        out.append("  %-28s %4d" % (kind, n))
    out.append("")
    out.append("why a patch did not apply to main (by path):")
    for path, n in result["cause_paths"].most_common(12):
        out.append("  %-34s %4d" % (path, n))
    if result["unrecognised"]:
        out.append("")
        out.append("lines mentioning landing that no rule matched: %d"
                   % len(result["unrecognised"]))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--all", action="store_true", help="list every draft-branch run, not the first six")
    ap.add_argument("logs", nargs="*", default=None,
                    help="log files to read (default: this bot's own log)")
    args = ap.parse_args(argv)
    logs = args.logs or [p for p in DEFAULT_LOGS if os.path.exists(p)]
    if not logs:
        print("no log file found; pass one as an argument", file=sys.stderr)
        return 2
    lines = []
    for path in logs:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                lines.extend(fh.readlines())
        except OSError as exc:
            print("cannot read %s: %s" % (path, exc), file=sys.stderr)
            return 2
    result = census(lines)
    result["final"] = final_fates(result)
    print(report(result, logs, show_all=args.all))
    return 0


if __name__ == "__main__":
    sys.exit(main())
