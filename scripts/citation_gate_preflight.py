#!/usr/bin/env python3
"""Ask the landing gate's question before the landing machine asks it.

Measured 2026-10-23: three consecutive wakes (01:19Z, 03:19Z and 07:19Z) were refused with "this
run's diff introduced new failures: test_cited_path_gate.py", and each was cut off at its action cap,
so each one's entire artefact was lost. In every case the cause was the same: one sentence in a new
report citing a dated artefact that no reader can open — usually the review's own finding ("this
report never landed"), which the gate could not tell from an invented claim.

The gate is right to ask. It is wrong to ask only after the run has ended. This runs the same two
live checks, from the same code as `tests/test_cited_path_gate.py`, and prints exactly the rows it
would refuse, so a wake can answer them while it still has turns.

Exit 0 means the gate is satisfied by this tree; exit 1 means there is a row to answer, and the
answer is either to land the evidence or to add an entry to `channels/unlanded-artefacts.json`.

Usage:
    python3 scripts/citation_gate_preflight.py
    python3 scripts/citation_gate_preflight.py --root /path/to/other/worktree
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import cited_paths_audit as audit  # noqa: E402
import tests.test_cited_path_gate as gate  # noqa: E402  the rule lives in one place only


def check(root=ROOT):
    """`(refusals, register_problems)` — what the gate would say about this tree, before it says it."""
    found = audit.audit(root)
    register = gate.declaration_register(os.path.join(root, gate.REGISTER_PATH))
    declared = gate.declared_unlanded(baseline=gate.BASELINE, extra=gate.UNLANDED_ARTEFACTS,
                                      register=register)
    refusals = [("lost", citing, target, "land the evidence, or declare the artefact in "
                                        "channels/unlanded-artefacts.json")
                for citing, target in gate.new_rows(found["by_class"]["lost"], gate.BASELINE, declared)]
    refusals += [("moved", citing, target, "cite where the thing is now; the census prints the real path")
                 for citing, target in gate.new_moved_rows(found["by_class"]["moved"],
                                                           gate.MOVED_BASELINE)]
    present = sorted(t for t in declared if os.path.exists(os.path.join(root, t)))
    for target in present:
        refusals.append(("paid", "-", target, "this artefact is on disk now; delete its declaration"))
    return refusals, gate.register_problems(register)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=ROOT, help="tree to check (default: this checkout)")
    args = ap.parse_args(argv)
    refusals, problems = check(args.root)
    if not refusals and not problems:
        print("the citation gate would pass this tree: nothing to declare, nothing to answer")
        return 0
    for kind, citing, target, fix in refusals:
        print(f"REFUSED ({kind}): {citing} cites {target}\n    fix: {fix}")
    for problem in problems:
        print(f"REGISTER: {problem}")
    print(f"\n{len(refusals)} row(s) and {len(problems)} register problem(s) — "
          f"the landing gate will refuse this diff until they are answered.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
